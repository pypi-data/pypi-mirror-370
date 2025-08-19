from __future__ import annotations
from datetime import datetime
from typing import List, Dict, Optional
from .types import ClickhouseHelper, SearchServiceClickhouseHelper
from ...utils.logging_trait import CanLog

class ChatService:
    """Manages all chat-related database operations."""
    def __init__(self, db_helper: ClickhouseHelper):
        self.db_helper = db_helper
        self.logger = CanLog()

    def insert_user(self, session_id, student_code, student_name, student_email,
                    student_phone, chat_type, ip_address, country_name,
                    country_iso_code, currency_code, user_agent, created_at):
        self.db_helper.insert(
            'users',
            [(session_id, student_code, student_name, student_email, student_phone,
              chat_type, ip_address, country_name, country_iso_code, currency_code,
              user_agent, created_at)],
            column_names=['session_id', 'student_code', 'student_name', 'student_email',
                          'student_phone', 'chat_type', 'ip_address', 'country_name',
                          'country_iso_code', 'currency_code', 'user_agent', 'created_at']
        )
        self.logger.log_message(f"Inserted user | session_id: {session_id}, student_code: {student_code}")

    def insert_chat_message(self, session_id, speaker, message, chat_details,
                            message_id, created_at, has_used_matchmaker=0, tool_used=""):
        self.db_helper.insert(
            'detailed_student_chats',
            [(str(session_id), speaker, message, chat_details, str(message_id),
              has_used_matchmaker, tool_used, created_at)],
            column_names=['session_id', 'speaker', 'message', 'chat_details',
                          'message_id', 'has_used_matchmaker', 'tool_used', 'created_at']
        )
        self.logger.log_message(
            f"Inserted chat message | session_id: {session_id}, message_id: {message_id}, "
            f"has_used_matchmaker: {has_used_matchmaker}, tool_used: {tool_used}"
        )

    def insert_model_response_traceback(self, session_id, message_id,
                                        prediction_trajectory, prediction_reasoning,
                                        prediction_answer, created_at):
        self.db_helper.insert(
            'model_response_logs',
            [(str(session_id), str(message_id), prediction_trajectory,
              prediction_reasoning, prediction_answer, created_at)],
            column_names=['session_id', 'message_id', 'prediction_trajectory',
                          'prediction_reasoning', 'prediction_answer', 'created_at']
        )
        self.logger.log_message(f"Inserted model response traceback | session_id: {session_id}, message_id: {message_id}")

    def insert_student_preferences_and_filters(self, student_code, session_id, search_code,
                                               student_name, preferences_and_filters, created_at):
        self.db_helper.insert(
            'student_preferences_and_filters',
            [(str(student_code), str(session_id), str(search_code), student_name,
              preferences_and_filters, created_at)],
            column_names=['student_code', 'session_id', 'search_code', 'student_name',
                          'preferences_and_filters', 'created_at']
        )
        self.logger.log_message(
            f"Inserted student preferences/filters | student_code: {student_code}, search_code: {search_code}"
        )

    def get_raw_currency_data(self) -> list:
        self.logger.log_message("Fetching currency metadata.")
        q = "SELECT currency_code, currency_name, symbols, common_names, countries FROM currency_metadata"
        return self.db_helper.query(q).result_rows

    def get_student_currency_code(self, session_id: str) -> list:
        self.logger.log_message("Fetching student's currency code.")
        q = "SELECT currency_code FROM users WHERE session_id = %(session_id)s"
        return self.db_helper.query(q, {"session_id": session_id}).result_rows

    def insert_chat_summary(self, student_code, summary, summary_details, expert_rating):
        now = datetime.utcnow()
        existing = self.db_helper.query(
            "SELECT created_at FROM summarized_student_chats WHERE student_code = %(student_code)s",
            {"student_code": student_code}
        ).result_rows
        created_at = existing[0][0] if existing else now

        self.db_helper.command(
            "ALTER TABLE summarized_student_chats DELETE WHERE student_code = %(student_code)s",
            {"student_code": student_code}
        )
        self.db_helper.insert(
            "summarized_student_chats",
            [(student_code, summary, summary_details, expert_rating, created_at, now)],
            ["student_code", "summary", "summary_details", "expert_rating", "created_at", "last_updated_at"]
        )
        self.logger.log_message(f"Upserted chat summary | student_code: {student_code}")

    def insert_feedback_rating(self, message_id, score, created_at):
        self.db_helper.insert(
            'student_model_response_ratings',
            [(message_id, score, created_at)],
            ['message_id', 'rating_score', 'created_at']
        )
        self.logger.log_message(f"Stored feedback rating | message_id: {message_id}, score: {score}")

    def insert_student_preferences(self, student_code, search_code, name, parsed_json_string):
        self.db_helper.insert(
            "student_preferences_and_filters",
            [(student_code, search_code, name, parsed_json_string, datetime.utcnow())],
            ["student_code", "search_code", "student_name", "preferences_and_filters", "created_at"]
        )
        self.logger.log_message(f"Inserted student preferences | student_code: {student_code}")

    def get_student_code_by_session(self, session_id: str) -> Optional[str]:
        q = "SELECT student_code FROM users WHERE session_id = %(session_id)s LIMIT 1"
        rows = self.db_helper.query(q, {"session_id": session_id}).result_rows
        return rows[0][0] if rows else None

    def get_user_sessions_by_code(self, student_code: str) -> List[Dict]:
        q = """
        SELECT session_id, student_code, student_name, country_name, country_iso_code, currency_code
        FROM users
        WHERE student_code = %(student_code)s
        ORDER BY created_at DESC
        """
        rows = self.db_helper.query(q, {"student_code": student_code}).result_rows
        return [
            {"session_id": r[0], "student_code": r[1], "student_name": r[2],
             "country_name": r[3], "country_iso_code": r[4], "currency_code": r[5]}
            for r in rows
        ]

    def get_chats_by_session_ids(self, session_ids: List[str]) -> List[Dict]:
        if not session_ids:
            return []
        q = """
        SELECT session_id, speaker, message, created_at, has_used_matchmaker, message_id
        FROM detailed_student_chats
        WHERE session_id IN %(session_ids)s
        ORDER BY created_at ASC
        """
        rows = self.db_helper.query(q, {"session_ids": tuple(session_ids)}).result_rows
        return [
            {"session_id": r[0], "speaker": r[1], "message": r[2],
             "created_at": r[3], "has_used_matchmaker": r[4], "message_id": r[5]}
            for r in rows
        ]

    def get_sessions_and_chats_from_session(self, session_id: str) -> Dict:
        student_code = self.get_student_code_by_session(session_id)
        if not student_code:
            return {"student_code": None, "sessions": [], "chats": []}
        sessions = self.get_user_sessions_by_code(student_code)
        chats = self.get_chats_by_session_ids([s["session_id"] for s in sessions])
        return {"student_code": student_code, "sessions": sessions, "chats": chats}

    def get_student_summary(self, session_id: str) -> Optional[Dict]:
        student_code = self.get_student_code_by_session(session_id)
        if not student_code:
            return None
        q = """
        SELECT student_code, summary
        FROM summarized_student_chats
        WHERE student_code = %(student_code)s
        ORDER BY last_updated_at DESC
        LIMIT 1
        """
        rows = self.db_helper.query(q, {"student_code": student_code}).result_rows
        return {"student_code": rows[0][0], "summary": rows[0][1]} if rows else None

    def get_recommendations(self, message_id: str):
        q = """
        SELECT message_id, prediction_trajectory
        FROM model_response_logs
        WHERE message_id = %(message_id)s
        """
        rows = self.db_helper.query(q, {"message_id": message_id}).result_rows
        return rows[0][1] if rows else None

    def get_student_welcome_back_summary(self, session_id: str):
        student_code = self.get_student_code_by_session(session_id)
        q = "SELECT summary FROM summarized_student_chats WHERE student_code = %(student_code)s"
        rows = self.db_helper.query(q, {"student_code": student_code}).result_rows
        return rows[0][0] if rows else None

    def get_latest_student_name(self, session_id: str) -> Optional[str]:
        student_code = self.get_student_code_by_session(session_id)
        q = """
        SELECT student_name
        FROM users
        WHERE student_code = %(student_code)s
        ORDER BY created_at DESC
        LIMIT 1
        """
        rows = self.db_helper.query(q, {"student_code": student_code}).result_rows
        return rows[0][0] if rows else None

    def get_last_messages(self, session_id: str, limit: int = 2) -> List[Dict]:
        sql = """
        SELECT speaker, message, created_at
        FROM detailed_student_chats
        WHERE session_id = %(session_id)s AND speaker IN ('Student','Model')
        ORDER BY created_at DESC
        LIMIT %(limit)s
        """
        try:
            res = self.db_helper.query(sql, {"session_id": session_id, "limit": limit})
            rows, cols = res.result_rows or [], res.column_names or []
            items = [dict(zip(cols, r)) for r in rows]
            items.reverse()
            return items
        except Exception as e:
            self.logger.log_message(f"get_last_messages failed for session_id={session_id}: {e}")
            return []

class SearchService:
    def __init__(self, db_helper: SearchServiceClickhouseHelper):
        self.db_helper = db_helper
        self.logger = CanLog()

    def get_course_categories(self) -> list:
        q = "SELECT course_category_name, course_category_code FROM course_categories"
        return self.db_helper.query(q).result_rows

    def get_countries_from_campuses(self) -> list:
        q = "SELECT study_destination_iso2_code, country_name FROM campuses"
        return self.db_helper.query(q).result_rows

    def get_institutions(self) -> list:
        q = "SELECT DISTINCT institution_name, institution_code FROM campuses WHERE institution_code IS NOT NULL"
        return self.db_helper.query(q).result_rows

    def get_cities(self) -> list:
        q = "SELECT study_destination_iso2_code, city_name, city_id FROM campuses"
        return self.db_helper.query(q).result_rows
