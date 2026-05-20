import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.core.security import create_access_token
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.mode import Mode
from app.schemas.auth import UserCreate
from app.services.auth import create_user


class ApiIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        self.database_path = Path(self.tempdir.name) / "integration.sqlite3"
        self.engine = create_engine(
            f"sqlite:///{self.database_path}",
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

        from app import main as main_module

        self.previous_worker_enabled = main_module.settings.reminder_worker_enabled
        main_module.settings.reminder_worker_enabled = False

        def override_get_db():
            db = self.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

        with self.SessionLocal() as db:
            user = create_user(db, UserCreate(email="owner@example.com", password="password123"))
            other_user = create_user(db, UserCreate(email="other@example.com", password="password123"))
            self.token = create_access_token(subject=user.email)
            self.user_work_mode_id = db.scalar(select(Mode.id).where(Mode.user_id == user.id, Mode.name == "work"))
            self.user_academic_mode_id = db.scalar(select(Mode.id).where(Mode.user_id == user.id, Mode.name == "academic"))
            self.other_work_mode_id = db.scalar(
                select(Mode.id).where(Mode.user_id == other_user.id, Mode.name == "work")
            )

        self.headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self) -> None:
        from app import main as main_module

        app.dependency_overrides.clear()
        self.client.close()
        main_module.settings.reminder_worker_enabled = self.previous_worker_enabled
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()
        self.tempdir.cleanup()

    def test_task_creation_rejects_foreign_mode_scope(self) -> None:
        response = self.client.post(
            "/api/v1/tasks",
            headers=self.headers,
            json={"title": "Cross-tenant mode attempt", "mode_id": self.other_work_mode_id},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["code"], "mode_not_found")

    def test_ai_command_creates_task_and_reminder(self) -> None:
        response = self.client.post(
            "/api/v1/ai/command",
            headers=self.headers,
            json={
                "message": "remind me in 30 minutes to submit the sprint recap",
                "mode_id": self.user_work_mode_id,
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["parsed"]["intent"], "create_task_with_reminder")
        self.assertEqual(body["created_task"]["mode_id"], self.user_work_mode_id)
        self.assertIsNotNone(body["created_reminder"])

    def test_ai_command_builds_execution_workflow(self) -> None:
        response = self.client.post(
            "/api/v1/ai/command",
            headers=self.headers,
            json={"message": "help me finish my MTech report this week"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["parsed"]["intent"], "build_execution_workflow")
        self.assertIsNotNone(body["created_project"])
        self.assertIsNotNone(body["created_goal"])
        self.assertEqual(body["created_project"]["mode_id"], self.user_academic_mode_id)
        self.assertGreaterEqual(len(body["created_schedules"]), 1)

    def test_command_center_today_overview_endpoint(self) -> None:
        response = self.client.get("/api/v1/command-center/today-overview", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("due_today", body)
        self.assertIn("completion_score", body)
