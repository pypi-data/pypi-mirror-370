# Craydel Database Wrapper

Craydel Database Wrapper is a lightweight Python SDK for storing, retrieving, and managing student–counsellor chat data in ClickHouse.  
It also includes AI-powered conversation summarization to make student profiles easier to understand and hand over between advisors.

---

## Installation

Install the required dependencies:

```bash
pip install craydel-database-wrapper

## With ClickHouse driver
pip install craydel-database-wrapper[clickhouse]

## With LLM summarizer support (Vertex AI + DSPy)
pip install craydel-database-wrapper[llm]

## With both ClickHouse + LLM support
pip install craydel-database-wrapper[clickhouse,llm]


```
## Usage

```python
import os
from clickhouse_connect import get_client

class MyClickhouseHelper:
    def __init__(self):
        self.client = get_client(
            host=os.getenv("CLICKHOUSE_HOST", "localhost"),
            port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
            username=os.getenv("CLICKHOUSE_USER", "default"),
            password=os.getenv("CLICKHOUSE_PASSWORD", ""),
            database=os.getenv("CLICKHOUSE_DATABASE", "default"),
        )

    def insert(self, table, rows, column_names):
        self.client.insert(table, rows, column_names=column_names)

    def query(self, sql, parameters=None):
        q = self.client.query(sql, parameters=parameters)
        return q  # has .result_rows and .column_names

    def command(self, sql, parameters=None):
        self.client.command(sql, parameters=parameters)
```
### Insert and fetch chats

```python
from craydel_database_wrapper import ChatService
from datetime import datetime

# Use your custom ClickHouse helper
db = MyClickhouseHelper()
chat = ChatService(db)

# Insert a new chat message
chat.insert_chat_message(
    session_id="12345",
    speaker="Student",
    message="I want to study in Canada",
    chat_details="Web",
    message_id="msg_001",
    created_at=datetime.utcnow(),
)

# Retrieve last messages in the session
last_messages = chat.get_last_messages(session_id="12345")
print("Last messages:", last_messages)

```

### Summarize a conversation

```python
from craydel_database_wrapper.services.chat_summarizer import StudentConversationProcessor

summarizer = StudentConversationProcessor()

# Run summarizer for a given session
summarizer.process("12345")

print("✅ Conversation summarized and saved to ClickHouse")

```

### env
```env
CLICKHOUSE_DATABASE=
CLICKHOUSE_HOST=
CLICKHOUSE_USER=
CLICKHOUSE_PASSWORD=
CLICKHOUSE_PORT=8123

GOOGLE_APPLICATION_CREDENTIALS=(google credential json)
VERTEX_MODEL=
VERTEX_PROJECT_ID=
VERTEX_LOCATION=

```

