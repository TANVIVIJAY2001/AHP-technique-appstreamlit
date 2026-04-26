# persistence/repositories/decision_repo.py
from typing import Optional, Dict, Any

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError


class DecisionRepo:
    def __init__(self, engine: Engine):
        self.engine = engine

    def create_decision(self, title: str, purpose: str = "", owner_team: str = "") -> str:
        sql = """
        INSERT INTO decisions (title, purpose, owner_team)
        VALUES (:title, :purpose, :owner_team)
        RETURNING decision_id::text AS decision_id
        """
        try:
            with self.engine.begin() as conn:
                row = conn.execute(
                    text(sql),
                    {"title": title, "purpose": purpose, "owner_team": owner_team},
                ).mappings().first()
            return str(row["decision_id"])
        except IntegrityError:
            existing = self.get_decision_by_title(title)
            if existing:
                return existing["decision_id"]
            raise

    def get_decision_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT decision_id::text AS decision_id, title, purpose, status, owner_team, created_at, updated_at
        FROM decisions
        WHERE title = :title
        ORDER BY created_at DESC
        LIMIT 1
        """
        with self.engine.begin() as conn:
            row = conn.execute(text(sql), {"title": title}).mappings().first()
        return dict(row) if row else None

    def get_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT decision_id::text AS decision_id, title, purpose, status, owner_team, created_at, updated_at
        FROM decisions
        WHERE decision_id = :decision_id
        """
        with self.engine.begin() as conn:
            row = conn.execute(text(sql), {"decision_id": decision_id}).mappings().first()
        return dict(row) if row else None

    def list_decisions(self, limit: int = 50) -> list[Dict[str, Any]]:
        sql = """
        SELECT decision_id::text AS decision_id, title, purpose, status, owner_team, created_at, updated_at
        FROM decisions
        ORDER BY created_at DESC
        LIMIT :limit
        """
        with self.engine.begin() as conn:
            rows = conn.execute(text(sql), {"limit": limit}).mappings().all()
        return [dict(r) for r in rows]
