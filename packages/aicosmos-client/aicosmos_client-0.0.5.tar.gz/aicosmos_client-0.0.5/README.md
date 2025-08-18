# Client for AICosmos

This package implements the client for AICosmos. Before using this package, please make sure that you have a valid account for AICosmos. 

### AICosmosClient
By using this client, you can chat with our backend in "base" mode. To login, you will need the server's address, your username and your password. You can either start a new session, or use an existing one.

Our framework is a little bit different from "chat completions", where you give an llm the conversation history. Instead, your conversation history, along with other tool execution results, are stored in our database. This gives your a clean and simple interface to use, without worrying about constructing complicated contexts.

```Python
from aicosmos_client.client import AICosmosClient 

# login
client = AICosmosClient(
    base_url="http://xxx.xxx", username="xxx", password="xxxxxx"
)

# create a new session
try:
    new_session_id = client.create_session()
except Exception as e:
    print(f"Error creating new session: {e}")
    exit(0)

# lookup all the sessions
try:
    my_sessions = client.get_my_sessions()
except Exception as e:
    print(f"Error getting my sessions: {e}")
    exit(0)
# [{"session_id", "title"}, ...]
print(my_sessions)

# enjoy the conversation
try:
    conversation_history = client.chat(new_session_id, "Hello")
except Exception as e:
    print(f"Error chatting: {e}")
    exit(0)
print(conversation_history)
```

## AICosmosCLI
To show that the client is enough to build an application, we offer you an command-line interface!

```Python
from aicosmos_client.cli import AICosmosCLI

AICosmosCLI().run()
```
