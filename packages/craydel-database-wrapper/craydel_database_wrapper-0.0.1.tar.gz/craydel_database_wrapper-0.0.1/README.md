# Craydel Database Wrapper

is a lightweight Python SDK for storing, retrieving, and managing student–counsellor chat data in ClickHouse.
It also includes AI-powered conversation summarization to make student profiles easier to understand and hand over between advisors.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```
pip install dspy==2.6.27
pip install python-dotenv==1.1.1
google-cloud-aiplatform==1.106.0
pip install clickhouse-connect
```
## Usage

### Insert and fetch chats

```python
from craydel_zoe_llm import ChatService, ClickhouseHelper
from datetime import datetime

# Setup database helper + chat service
db = ClickhouseHelper()
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
from craydel_zoe_llm.services.chat_summarizer import StudentConversationProcessor

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