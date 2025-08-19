from datetime import datetime
from .types import ClickhouseHelper, SearchServiceClickhouseHelper
from ...utils.logging_trait import CanLog
from typing import List, Dict, Optional

class ChatService:
    """Manages all chat-related database operations."""

    def __init__(self, db_helper: ClickhouseHelper):
        self.db_helper = db_helper
        # Create an instance of the CanLog class
        self.logger = CanLog()

    def insert_user(self, session_id, student_code, student_name, student_email, student_phone, chat_type, ip_address,country_name, country_iso_code, currency_code, user_agent, created_at):
        self.db_helper.insert(
            'users',
            [(session_id, student_code, student_name, student_email, student_phone, chat_type, ip_address,country_name, country_iso_code, currency_code, user_agent, created_at)],
            column_names=['session_id', 'student_code', 'student_name', 'student_email', 'student_phone', 'chat_type', 'ip_address','country_name','country_iso_code', 'currency_code', 'user_agent', 'created_at']
        )
        log_msg = f"Inserted user | session_id: {session_id}, student_code: {student_code}"
        self.logger.log_message(log_msg)

    def insert_chat_message(
            self, session_id, speaker, message, chat_details,
            message_id, created_at, has_used_matchmaker=0, tool_used=""
    ):
        self.db_helper.insert(
            'detailed_student_chats',
            [(str(session_id), speaker, message, chat_details, str(message_id),
              has_used_matchmaker, tool_used, created_at)],
            column_names=[
                'session_id', 'speaker', 'message', 'chat_details',
                'message_id', 'has_used_matchmaker', 'tool_used', 'created_at'
            ]
        )
        self.logger.log_message(
            f"Inserted chat message | session_id: {session_id}, message_id: {message_id}, "
            f"has_used_matchmaker: {has_used_matchmaker}, tool_used: {tool_used}"
        )

    def insert_model_response_traceback(self, session_id, message_id, prediction_trajectory, prediction_reasoning, prediction_answer, created_at):
        self.db_helper.insert(
            'model_response_logs',
            [(str(session_id), str(message_id), prediction_trajectory, prediction_reasoning, prediction_answer, created_at)],
            column_names=['session_id', 'message_id', 'prediction_trajectory', 'prediction_reasoning', 'prediction_answer', 'created_at']
        )
        log_msg = f"Inserted model response traceback for | session_id: {session_id}, message_id: {message_id}"
        self.logger.log_message(log_msg)

    def insert_student_preferences_and_filters(self, student_code, session_id, search_code, student_name, preferences_and_filters, created_at):
        self.db_helper.insert(
            'student_preferences_and_filters',
            [(str(student_code), str(session_id), str(search_code), student_name, preferences_and_filters, created_at)],
            column_names=['student_code', 'session_id', 'search_code', 'student_name', 'preferences_and_filters', 'created_at']
        )
        log_msg = f"Inserted student preferences and filters for | student_code: {student_code}, search_code: {search_code}, session_id: {session_id}"
        self.logger.log_message(log_msg)

    def get_raw_currency_data(self) -> list:
        """
        Fetches the raw currency metadata rows from the database.
        Returns a list of rows, where each row is a tuple.
        """
        self.logger.log_message("Fetching raw currency metadata from the database.")
        query = "SELECT currency_code, currency_name, symbols, common_names, countries FROM currency_metadata"
        result = self.db_helper.query(query)
        self.logger.log_message("Successfully fetched currency metadata rows.")
        return result.result_rows

    def get_student_currency_code(self, session_id: str) -> list:
        """
        Fetches the raw currency code for the student from the user's table (the currency code here was derived from
        the decoded geolocation information). This will be used in the matchmaker tool for the 'defaulting action'
        when the student doesn't provide a currency (or a currency is undetected) in the chat.
        """
        self.logger.log_message("Fetching student's currency code from the database.")
        query = """SELECT currency_code FROM users WHERE session_id = %(session_id)s"""
        params = {"session_id": session_id}
        result = self.db_helper.query(query, params)
        self.logger.log_message("Successfully fetched currency code from the database.")
        return result.result_rows

    def insert_chat_summary(self, student_code, summary, summary_details, expert_rating):
        now = datetime.utcnow()
        existing = self.db_helper.query(
            "SELECT created_at FROM summarized_student_chats WHERE student_code = %(student_code)s",
            parameters={'student_code': student_code}
        ).result_rows

        created_at = existing[0][0] if existing else now

        self.db_helper.command(
            "ALTER TABLE summarized_student_chats DELETE WHERE student_code = %(student_code)s",
            parameters={'student_code': student_code}
        )
        self.db_helper.insert(
            "summarized_student_chats",
            [(student_code, summary, summary_details, expert_rating, created_at, now)],
            column_names=["student_code", "summary", "summary_details", "expert_rating", "created_at",
                          "last_updated_at"]
        )
        log_msg = f"Upserted chat summary | student_code: {student_code}"
        self.logger.log_message(log_msg)

    def insert_feedback_rating(self, message_id, score,created_at):
        self.db_helper.insert(
            'student_model_response_ratings',
            [(message_id, score, created_at)],
            column_names=['message_id', 'rating_score', 'created_at']
        )
        log_msg = f"Stored feedback rating | message_id: {message_id}, score: {score}"
        self.logger.log_message(log_msg)

    def insert_student_preferences(self, student_code, search_code, name, parsed_json_string):
        column_names = [
            "student_code",
            "search_code",
            "student_name",
            "preferences_and_filters",
            "created_at"
        ]

        current_time = datetime.utcnow()
        data = [(student_code, search_code, name, parsed_json_string, current_time)]

        self.db_helper.insert(
            "student_preferences_and_filters",
            data,
            column_names
        )

        log_msg = f"Inserted student preferences | student_code: {student_code}"
        self.logger.log_message(log_msg)

    def get_student_code_by_session(self, session_id: str) -> Optional[str]:
        """
        Return the student_code owning this session_id (or None if not found).
        """
        q = """
            SELECT student_code
            FROM users
            WHERE session_id = %(session_id)s
            LIMIT 1
        """
        rows = self.db_helper.query(q, parameters={"session_id": session_id}).result_rows
        return rows[0][0] if rows else None

    def get_user_sessions_by_code(self, student_code: str) -> List[Dict]:
        """
        Return all sessions for a student ordered by created_at DESC.
        Fields: session_id, student_code, student_name, country_name, currency_code, created_at
        """
        q = """
            SELECT session_id, student_code, student_name, country_name, country_iso_code,currency_code
            FROM users
            WHERE student_code = %(student_code)s
            ORDER BY created_at DESC
        """
        rows = self.db_helper.query(q, parameters={"student_code": student_code}).result_rows
        return [
            {
                "session_id": r[0],
                "student_code": r[1],
                "student_name": r[2],
                "country_name": r[3],
                "country_iso_code": r[4],
                "currency_code": r[5],
            }
            for r in rows
        ]

    def get_chats_by_session_ids(self, session_ids: List[str]) -> List[Dict]:
        """
        Return chats for the given session_ids ordered by created_at ASC.
        Fields: session_id, speaker, message, chat_details, message_id, created_at
        """
        if not session_ids:
            return []

        # Prefer parameterized IN with tuples if your helper supports it (ClickHouse does).
        q = """
            SELECT session_id, speaker, message,created_at, has_used_matchmaker, message_id
            FROM detailed_student_chats
            WHERE session_id IN %(session_ids)s
            ORDER BY created_at ASC
        """
        rows = self.db_helper.query(q, parameters={"session_ids": tuple(session_ids)}).result_rows
        return [
            {
                "session_id": r[0],
                "speaker": r[1],
                "message": r[2],
                "created_at": r[3],
                "has_used_matchmaker": r[4],
                "message_id": r[5]
            }
            for r in rows
        ]

    def get_sessions_and_chats_from_session(self, session_id: str) -> Dict:
        """
        Convenience: start from a session_id, resolve student_code,
        fetch all sessions for that student, and fetch all chats for those sessions.
        """
        student_code = self.get_student_code_by_session(session_id)
        if not student_code:
            return {"student_code": None, "sessions": [], "chats": []}

        sessions = self.get_user_sessions_by_code(student_code)
        session_ids = [s["session_id"] for s in sessions]
        chats = self.get_chats_by_session_ids(session_ids)

        return {
            "student_code": student_code,
            "sessions": sessions,
            "chats": chats,
        }

    def get_student_summary(self, session_id: str) -> Optional[Dict]:
        # Step 1: Get student_code from the session_id
        student_code = self.get_student_code_by_session(session_id)
        if not student_code:
            return None
        # Step 2: Get the latest summary for that student
        q = """
            SELECT student_code, summary
            FROM summarized_student_chats
            WHERE student_code = %(student_code)s
            ORDER BY last_updated_at DESC
            LIMIT 1
        """
        rows = self.db_helper.query(q, parameters={"student_code": student_code}).result_rows
        if not rows:
            return None

        return {
            "student_code": rows[0][0],
            "summary": rows[0][1]
        }

    def get_recommendations(self, message_id:str):

        q = """
            SELECT message_id, prediction_trajectory
            FROM model_response_logs
            WHERE message_id = %(message_id)s
        """
        rows = self.db_helper.query(q, parameters={"message_id": message_id}).result_rows
        return rows[0][1] if rows else None

    def get_student_welcome_back_summary(self, session_id:str):
        student_code = self.get_student_code_by_session(session_id)

        q = """
            SELECT summary
            FROM summarized_student_chats
            where student_code = %(student_code)s       
        """

        rows = self.db_helper.query(q, parameters={"student_code": student_code}).result_rows
        return rows[0][0] if rows else None

    def get_latest_student_name(self, session_id: str) -> str | None:
        # Optional helper to personalize greeting
        student_code = self.get_student_code_by_session(session_id)
        q = """
            SELECT student_name
            FROM users
            WHERE student_code = %(student_code)s
            ORDER BY created_at DESC
            LIMIT 1
        """
        rows = self.db_helper.query(q, parameters={"student_code": student_code}).result_rows
        return rows[0][0] if rows else None

    def get_last_messages(self, session_id: str, limit: int = 2) -> List[Dict]:
        """
        Fetch the last `limit` messages for a session, newest-first in SQL,
        then return as oldest-first for conversational context.
        """
        sql = """
               SELECT
                   speaker,
                   message,
                   created_at
               FROM detailed_student_chats
               WHERE session_id = %(session_id)s
                 AND speaker IN ('Student','Model')
               ORDER BY created_at DESC
               LIMIT %(limit)s
           """
        try:
            result = self.db_helper.query(
                sql,
                parameters={"session_id": session_id, "limit": limit}
            )
            rows = result.result_rows or []
            cols = result.column_names or []
            items = [dict(zip(cols, r)) for r in rows]

            # Oldest → newest (better for feeding into the model)
            items.reverse()
            return items
        except Exception as e:
            self.logger.log_message(f"get_last_messages failed for session_id={session_id}: {e}")
            return []


class SearchService:
    """Manages all search-service-related database operations."""

    def __init__(self, db_helper: SearchServiceClickhouseHelper):
        self.db_helper = db_helper
        # Create an instance of the CanLog class
        self.logger = CanLog()

    def get_course_categories(self) -> list:
        """
        Fetches the course categories details from the db
        """
        self.logger.log_message("Fetching course categories from the database.")
        query = "SELECT course_category_name, course_category_code FROM course_categories"
        result = self.db_helper.query(query)
        self.logger.log_message("Successfully fetched course categories  rows.")
        return result.result_rows

    def get_countries_from_campuses(self) -> list:
        """
        Fetches the country names & their iso2 codes from the db
        """
        self.logger.log_message("Fetching country names & their iso2 codes from the database.")
        query = "SELECT study_destination_iso2_code, country_name FROM campuses"
        result = self.db_helper.query(query)
        self.logger.log_message("Successfully fetched country names & their iso2 codes rows.")
        return result.result_rows

    def get_institutions(self) -> list:
        """
        Fetches the institutions details (name, code) from the db
        """
        self.logger.log_message("Fetching institutions details (name, code) from the database.")
        query = "SELECT DISTINCT institution_name, institution_code FROM campuses WHERE institution_code IS NOT NULL"
        result = self.db_helper.query(query)
        self.logger.log_message("Successfully fetched institutions details (name, code) rows.")
        return result.result_rows

    def get_cities(self) -> list:
        """
        Fetches the city details (study_destination_iso2_code, city_name, city_id from the db
        """
        self.logger.log_message("Fetching city details (study_destination_iso2_code, city_name, city_id) from the database.")
        query = "SELECT study_destination_iso2_code, city_name, city_id FROM campuses"
        result = self.db_helper.query(query)
        self.logger.log_message("Successfully fetched city details (study_destination_iso2_code, city_name, city_id) rows.")
        return result.result_rows