from __future__ import annotations
from typing import Callable, Dict, List, Tuple, Optional
import json

from ..clickhouse_db.db_interactions import ChatService
from ..clickhouse_db.types import ClickhouseHelper

GenerateFn = Callable[[str], str]  # takes a prompt, returns a string summary

class StudentConversationProcessor:
    """
    Summarizes student conversations and upserts into ClickHouse.
    No LLM dependency: you must pass `generate_fn(prompt:str)->str`.
    """

    def __init__(
        self,
        *,
        db_helper_factory: Callable[[], ClickhouseHelper],
        generate_fn: GenerateFn,
    ) -> None:
        self._db_helper_factory = db_helper_factory
        self._generate = generate_fn

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

    def summarize_student_story(self, all_info: Dict) -> Tuple[str, Dict]:
        transcript = self.build_transcript(all_info.get("chats", []))
        meta = self.latest_session_meta(all_info.get("sessions", []))

        prompt = (
            "Summarize the following student–counsellor conversation into a concise handover for advisors.\n"
            "Return a short summary paragraph and JSON fields for:\n"
            "personal_profile, study_interest, destination_preferences, constraints, changes_over_time.\n\n"
            f"Meta: {json.dumps(meta, ensure_ascii=False)}\n"
            f"Transcript:\n{transcript}\n"
        )
        text = self._generate(prompt) or ""

        # You can parse out structured JSON if your generator returns it;
        # here we split simple cases: first paragraph = summary, rest = details JSON (if present).
        summary = text.strip()
        details: Dict = {}
        try:
            # naive parse last JSON object if present
            last_brace = text.rfind("{")
            if last_brace != -1:
                maybe_json = text[last_brace:]
                details = json.loads(maybe_json)
                summary = text[:last_brace].strip()
        except Exception:
            pass

        for key in ("personal_profile", "study_interest", "destination_preferences", "constraints", "changes_over_time"):
            details.setdefault(key, "Not mentioned")

        return summary, details

    def process(self, session_id: str) -> None:
        db = self._db_helper_factory()
        chat = ChatService(db)

        all_info = chat.get_sessions_and_chats_from_session(session_id=session_id)
        summary, details = self.summarize_student_story(all_info)

        summary_blob = {
            "structured": details,
            "source": {
                "session_count": len(all_info.get("sessions", [])),
                "session_ids": [s["session_id"] for s in all_info.get("sessions", [])][:50],
            },
        }

        chat.insert_chat_summary(
            student_code=all_info.get("student_code"),
            summary=summary,
            summary_details=json.dumps(summary_blob),
            expert_rating=json.dumps({"score": 5, "rating_factors": "clarity,factual_accuracy"}),
        )
