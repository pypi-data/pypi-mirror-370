from __future__ import annotations
import os
import json
from typing import Dict, List, Tuple, Callable, Optional
import dspy
from dotenv import load_dotenv

from ..clickhouse_db.db_interactions import ChatService
from ..clickhouse_db.types import ClickhouseHelper


class StudentConversationProcessor:
    """
    Background summarizer.
    - Uses an injected ClickHouse helper factory -> no hard dependency on your app.
    - Configures DSPy/Vertex from env.
    """
    def __init__(
        self,
        *,
        db_helper_factory: Callable[[], ClickhouseHelper],
        model_id: Optional[str] = None,
        vertex_credentials: Optional[str] = None,
        vertex_project: Optional[str] = None,
        vertex_location: Optional[str] = None,
        use_dotenv: bool = True,
    ) -> None:
        if use_dotenv:
            load_dotenv()

        # Store factory for thread-safety (new client per call)
        self._db_helper_factory = db_helper_factory

        # ---- LLM config (env-overridable) ----
        model_id = model_id or os.getenv("VERTEX_MODEL", "gemini-2.0-flash-001")
        vertex_credentials = vertex_credentials or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        vertex_project = vertex_project or os.getenv("VERTEX_PROJECT_ID")
        vertex_location = vertex_location or os.getenv("VERTEX_LOCATION", "us-central1")

        model_spec = f"vertex_ai/{model_id}"

        self.lm = dspy.LM(
            model_spec,
            vertex_credentials=vertex_credentials,
            vertex_project=vertex_project,
            vertex_location=vertex_location,
            cache_in_memory=False,
        )
        dspy.configure(lm=self.lm, enable_memory_cache=False)

    # ---------- helpers ----------

    @staticmethod
    def build_transcript(chats: List[Dict], max_chars: int = 24_000) -> str:
        lines = []
        for c in chats:
            speaker_raw = (c.get("speaker") or "").strip().lower()
            speaker = "Student" if speaker_raw.startswith("student") else "Counsellor"
            msg = (c.get("message") or "").strip()
            if msg:
                lines.append(f"{speaker}: {msg}")
        text = "\n".join(lines)
        return text[-max_chars:] if len(text) > max_chars else text

    @staticmethod
    def latest_session_meta(sessions: List[Dict]) -> Dict:
        if not sessions:
            return {"student_name": None, "country_name": None, "currency_code": None}
        latest = sessions[0]
        return {
            "student_name": latest.get("student_name"),
            "country_name": latest.get("country_name"),
            "currency_code": latest.get("currency_code"),
        }

    # ---------- DSPy signature ----------

    class StudentConversationSummary(dspy.Signature):
        """Summarize a student's conversations with an education counsellor."""
        metadata: dict = dspy.InputField(desc="Student bio: name, country, currency.")
        transcript: str = dspy.InputField(desc="Chronological transcript.")
        summary: str = dspy.OutputField(desc="Concise story for advisor handover.")
        details: dict = dspy.OutputField(desc="Structured JSON fields.")

    def summarize_student_story(self, all_info: Dict) -> Tuple[str, Dict]:
        transcript = self.build_transcript(all_info.get("chats", []))
        meta = self.latest_session_meta(all_info.get("sessions", []))

        summarize = dspy.ChainOfThought(self.StudentConversationSummary)
        pred = summarize(metadata=meta, transcript=transcript)

        details = pred.details if isinstance(pred.details, dict) else {}
        for key in (
            "personal_profile",
            "study_interest",
            "destination_preferences",
            "constraints",
            "changes_over_time",
        ):
            details.setdefault(key, "Not mentioned")

        return pred.summary, details

    # ---------- main entry ----------

    def process(self, session_id: str) -> None:
        """
        Pull chats for the session, summarize, and upsert into ClickHouse.
        Creates a fresh DB client per call using the injected factory.
        """
        # Fresh DB client each run
        db = self._db_helper_factory()
        local_service = ChatService(db)

        # 1) Gather data
        all_info = local_service.get_sessions_and_chats_from_session(session_id=session_id)

        # 2) Summarize
        summary, details = self.summarize_student_story(all_info)

        # 3) Metadata to store
        llm_metadata = {
            "provider": "Vertex AI",
            "model_name": os.getenv("VERTEX_MODEL", "gemini-2.0-flash-001"),
        }
        summary_details_blob = {
            "structured": details,
            "source": {
                "session_count": len(all_info.get("sessions", [])),
                "session_ids": [s["session_id"] for s in all_info.get("sessions", [])][:50],
            },
            "llm_metadata": llm_metadata,
        }

        # 4) Upsert summary
        local_service.insert_chat_summary(
            student_code=all_info.get("student_code"),
            summary=summary,
            summary_details=json.dumps(summary_details_blob),
            expert_rating=json.dumps({"score": 5, "rating_factors": "clarity,factual_accuracy"}),
        )
