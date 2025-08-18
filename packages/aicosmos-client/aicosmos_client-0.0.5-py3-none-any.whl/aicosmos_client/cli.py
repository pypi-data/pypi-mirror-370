import asyncio
from typing import Dict

from client import AICosmosClient
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
    RichLog,
    Static,
)


class LoginScreen(Screen):
    CSS = """
    #login-container {
        width: 100%;
        height: 100%;
        border: solid $accent;
        padding: 1;
    }
    #login-title {
        width: 100%;
        text-align: center;
        margin-bottom: 1;
        text-style: bold;
    }
    #login-error {
        width: 100%;
        color: red;
        text-align: center;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="login-container"):
            yield Label("Welcome to AICosmos", id="login-title")
            yield Input(placeholder="server url", id="server_url")
            yield Input(placeholder="username", id="username")
            yield Input(
                placeholder="password",
                id="password",
                password=True,
            )
            yield Button("Login", id="login-button", variant="primary")
            yield Label("", id="login-error")
        yield Footer()

    @on(Button.Pressed, "#login-button")
    def on_login(self) -> None:
        server_url = self.query_one("#server_url", Input).value
        username = self.query_one("#username", Input).value
        password = self.query_one("#password", Input).value

        if not server_url:
            self.query_one("#login-error").update("Server url cannot be empty")
            return
        if not username:
            self.query_one("#login-error").update("User cannot be empty")
            return
        if not password:
            self.query_one("#login-error").update("Password cannot be empty")
            return

        try:
            self.app.client = AICosmosClient(
                base_url=server_url, username=username, password=password
            )
            self.app.push_screen("session")
        except ValueError:
            self.query_one("#login-error").update(
                "Login failed, please check your information"
            )


class SessionScreen(Screen):
    CSS = """
    #session-container {
        width: 100%;
        height: 100%;
        border: solid $accent;
        padding: 1;
    }
    #session-header {
        width: 100%;
        layout: horizontal;
        height: auto;
        margin-bottom: 1;
    }
    #session-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        content-align: center middle;
    }
    #session-actions {
        width: 100%;
        layout: horizontal;
        height: auto;
        margin-bottom: 1;
    }
    #create-session {
        width: 30%;
        margin-right: 1;
    }
    #logout-button {
        width: 30%;
    }
    .spacer {
        width: 40%;
    }
    .subtitle {
        width: 100%;
        margin-top: 1;
        margin-bottom: 1;
        text-style: underline;
    }
    #session-list {
        width: 100%;
        height: 60%;
        border: solid $panel;
    }
    #session-error {
        width: 100%;
        color: red;
        text-align: center;
        margin-top: 1;
    }
    """

    sessions = reactive([])

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="session-container"):
            with Container(id="session-header"):
                yield Label("Select Session", id="session-title")
            with Container(id="session-actions"):
                yield Button("Create Session", id="create-session", variant="primary")
                yield Static("", classes="spacer")
                yield Button("Log out", id="logout-button", variant="error")
            yield Label("Your sessions:", classes="subtitle")
            yield ListView(id="session-list")
            yield Label("", id="session-error")
        yield Footer()

    def sanitize_id(self, session_id: str) -> str:
        """Turn session id into valid HTML identifier"""
        if not isinstance(session_id, str):
            session_id = str(session_id)

        import re

        clean_id = re.sub(r"[^a-zA-Z0-9_-]", "", session_id)

        if clean_id and clean_id[0].isdigit():
            clean_id = "s_" + clean_id

        return clean_id or "invalid_session"

    def on_mount(self) -> None:
        self.load_sessions()

    @work(exclusive=True)
    async def load_sessions(self) -> None:
        self.query_one("#session-list").clear()
        try:
            self.sessions = self.app.client.get_my_sessions()
        except Exception as e:
            self.query_one("#session-list").append(
                ListItem(Label(f"Failed: {e}"), id="no-sessions")
            )
            return

        if not self.sessions:
            self.query_one("#session-list").append(
                ListItem(Label("No session found"), id="no-sessions")
            )
            return

        for session in self.sessions:
            session_id = session["session_id"]
            clean_id = self.sanitize_id(session_id)
            title = session["title"]
            if not title:
                title = f"Session {session_id[:6]}"
            self.query_one("#session-list").append(
                ListItem(Label(title), id=f"session-{clean_id}")
            )

    @on(Button.Pressed, "#create-session")
    @work(exclusive=True)
    async def create_session(self) -> None:
        try:
            session_id = self.app.client.create_session()
        except Exception as e:
            self.query_one("#session-error").update(f"Failed to create session: {e}")
            return

        self.app.current_session = session_id
        self.app.uninstall_screen("chat")
        self.app.install_screen(ChatScreen(), "chat")
        self.app.push_screen("chat")

    @on(ListView.Selected)
    def session_selected(self, event: ListView.Selected) -> None:
        """Handle session selection"""
        if not event.item or not event.item.id or event.item.id == "no-sessions":
            return

        selected_index = event.list_view.index
        if selected_index is None or selected_index >= len(self.sessions):
            return

        selected_session = self.sessions[selected_index]
        session_id = selected_session["session_id"]

        if session_id:
            self.app.current_session = session_id
            self.app.uninstall_screen("chat")
            self.app.install_screen(ChatScreen(), "chat")
            self.app.push_screen("chat")

    @on(Button.Pressed, "#logout-button")
    def logout(self) -> None:
        """Go back to login page"""
        self.app.pop_screen()
        self.app.push_screen("login")


class ChatScreen(Screen):
    CSS = """
    #chat-container {
        width: 100%;
        height: 100%;
        border: solid $accent;
        padding: 1;
    }

    #chat-header {
        width: 100%;
        layout: horizontal;
        height: 3;
        margin-bottom: 1;
    }

    #chat-title-container {
        width: 1fr;
        height: 100%;
        align: center middle;
    }

    #chat-title {
        text-align: center;
        text-style: bold;
    }

    #back-button {
        width: auto;
        height: 100%;
        dock: right;
    }

    #chat-content {
        width: 100%;
        height: 1fr;
        layout: vertical;
    }

    #chat-log {
        width: 100%;
        height: 1fr;
        border: solid $panel;
        padding: 1;
        overflow-y: auto;
        scrollbar-size: 1 1;
        scrollbar-color: $accent;
    }

    #input-container {
        width: 100%;
        height: auto;
        margin-top: 1;
        layout: horizontal;
    }

    #message-input {
        width: 1fr;
    }

    #send-button {
        width: auto;
        margin-left: 1;
    }

    #loading-indicator {
        width: auto;
        margin-left: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="chat-container"):
            with Container(id="chat-header"):
                with Container(id="chat-title-container"):
                    yield Label("Session", id="chat-title")
                yield Button("Back", id="back-button", variant="default")

            with Container(id="chat-content"):
                yield RichLog(id="chat-log", wrap=True, markup=True, auto_scroll=True)

                with Container(id="input-container"):
                    yield Input(placeholder="Enter your message...", id="message-input")
                    yield Button("Send", id="send-button", variant="primary")
                    yield LoadingIndicator(id="loading-indicator")
        yield Footer()

    def __init__(self):
        super().__init__()
        self.conversation = []

    def on_resize(self) -> None:
        """Recalculate message displays when window changes"""
        self.update_message_display()

    def update_message_display(self) -> None:
        """Update message displays when window changes"""
        log = self.query_one("#chat-log")
        log.clear()
        for message in self.conversation:
            log.write(self.format_message(message))
        log.scroll_end(animate=False)

    def calculate_max_line_length(self) -> int:
        """Max line length for current session"""
        log_widget = self.query_one("#chat-log")
        container_width = log_widget.content_size.width
        return container_width - 1

    def format_message(self, message: Dict) -> str:
        """Format each message, with two spaces as indent"""
        role = message["role"]
        content = message["content"]
        max_line_length = self.calculate_max_line_length() - 2

        import textwrap

        wrapped_lines = []
        for line in content.split("\n"):
            indented_line = textwrap.fill(
                line,
                width=max_line_length,
                initial_indent="  ",
                subsequent_indent="  ",
                replace_whitespace=False,
                drop_whitespace=False,
            )
            wrapped_lines.append(indented_line)

        wrapped_content = "\n".join(wrapped_lines)

        if role == "user":
            return f"[cyan][b]user[/b][/cyan]\n{wrapped_content}\n"
        elif role == "assistant":
            char_name = message.get("character_name", "assistant")
            return f"[green][b]{char_name}[/b][/green]\n{wrapped_content}\n"
        else:
            return f"[red][b]{role}[/b][/red]\n{wrapped_content}\n"

    def add_message(self, message: Dict) -> None:
        """Update history"""
        self.conversation.append(message)
        self.update_message_display()

    def on_show(self) -> None:
        """Hide loading indicator and show history"""
        self.query_one("#loading-indicator").display = False
        self.load_conversation()
        self.query_one("#message-input").focus()

    def on_mount(self) -> None:
        """Hide loading indicator and show history"""
        self.query_one("#loading-indicator").display = False
        self.load_conversation()
        self.query_one("#message-input").focus()

    @work(exclusive=True)
    async def load_conversation(self) -> None:
        """Fetch conversation history"""
        try:
            self.conversation = self.app.client.get_session_history(
                self.app.current_session
            )
        except Exception as e:
            self.query_one("#chat-log").write(f"[red]Error: {e}[/red]")
            return
        self.update_message_display()

    @on(Button.Pressed, "#send-button")
    @on(Input.Submitted, "#message-input")
    def send_message(self) -> None:
        """Send message to backend"""
        input_widget = self.query_one("#message-input")
        message = input_widget.value.strip()

        if not message:
            return

        input_widget.value = ""
        self.add_message({"role": "user", "content": message})
        self.process_response(message)

    @work(exclusive=True)
    async def process_response(self, message: str) -> None:
        """Wait for response from backend"""
        loading = self.query_one("#loading-indicator", LoadingIndicator)
        input_widget = self.query_one("#message-input")
        send_button = self.query_one("#send-button")

        loading.display = True
        input_widget.disabled = True
        send_button.disabled = True

        try:
            try:
                conversation_history = await asyncio.to_thread(
                    self.app.client.chat, self.app.current_session, message
                )
            except Exception as e:
                self.query_one("#chat-log").write(f"[red]Error: {e}[/red]")
                return
            new_messages = conversation_history[len(self.conversation) :]
            for msg in new_messages:
                self.add_message(msg)

        except Exception as e:
            self.query_one("#chat-log").write(f"[red]Query failed: {str(e)}[/red]")

        finally:
            loading.display = False
            input_widget.disabled = False
            send_button.disabled = False
            input_widget.focus()

    @on(Button.Pressed, "#back-button")
    def back_to_sessions(self) -> None:
        """Go back to sessions list"""
        self.app.pop_screen()


class AICosmosCLI(App):
    CSS = """
    Screen {
        align: center middle;
    }
    """

    FULL_SCREEN = True

    SCREENS = {"login": LoginScreen, "session": SessionScreen, "chat": ChatScreen}

    def __init__(self):
        super().__init__()
        self.client: AICosmosClient = None
        self.current_session: str = None

    def on_mount(self) -> None:
        self.push_screen("login")
