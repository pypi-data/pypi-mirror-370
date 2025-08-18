import requests


class AICosmosClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.session = requests.Session()
        self.base_url = base_url
        self.username: str = username
        self.password: str = password
        self.access_token: str = None

        self._login()

    def _login(self):
        login_data = {
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            response = self.session.post(
                f"{self.base_url}/user/login", data=login_data, headers=headers
            )
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                return
            else:
                raise ValueError(f"Status code: {response.status_code}")
        except Exception as e:
            raise ValueError(f"Error: {e}")

    def _get_auth_headers(self):
        if not self.access_token:
            raise ValueError("Not logged in")
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _get_session_status(self, session_id):
        try:
            response = self.session.get(
                f"{self.base_url}/sessions/{session_id}/status",
                headers=self._get_auth_headers(),
            )
            success = response.status_code == 200
            if success:
                return response.json()
            else:
                raise ValueError(f"Status code: {response.status_code}")
        except Exception as e:
            raise ValueError(f"Error: {e}")

    def create_session(self):
        if not self.access_token:
            raise ValueError("Not logged in")
        try:
            response = self.session.post(
                f"{self.base_url}/sessions/create", headers=self._get_auth_headers()
            )
            if response.status_code == 200:
                response_json = response.json()
                return response_json["session_id"]
            else:
                raise ValueError(f"Status code: {response.status_code}")
        except Exception as e:
            raise ValueError(f"Error: {e}")

    def delete_session(self, session_id: str):
        if not self.access_token:
            raise ValueError("Not logged in")
        try:
            response = self.session.delete(
                f"{self.base_url}/sessions/{session_id}",
                headers=self._get_auth_headers(),
            )
            if response.status_code == 200:
                return
            else:
                raise ValueError(f"Status code: {response.status_code}")
        except Exception as e:
            raise ValueError(f"Error: {e}")

    def get_my_sessions(self):
        if not self.access_token:
            raise ValueError("Not logged in")
        try:
            response = self.session.get(
                f"{self.base_url}/sessions/my_sessions",
                headers=self._get_auth_headers(),
            )
            if response.status_code == 200:
                sessions = response.json()
                self.active_sessions = sessions
                return [
                    {
                        "session_id": session["session_id"],
                        "title": session["environment_info"].get("title", None),
                    }
                    for session in sessions
                ]
            else:
                raise ValueError(f"Status code: {response.status_code}")
        except Exception as e:
            raise ValueError(f"Error: {e}")

    def get_session_history(self, session_id: str):
        session = self._get_session_status(session_id)
        return session.get("conversation", [])

    def chat(self, session_id: str, prompt: str):
        if not self.access_token:
            raise ValueError("Not logged in")
        data = {
            "user_input": prompt,
            "session_id": session_id,
        }
        try:
            response = self.session.post(
                f"{self.base_url}/chat",
                json=data,
                headers=self._get_auth_headers(),
            )
            success = response.status_code == 200
            if success:
                return response.json()["conversation_history"]
            else:
                raise ValueError(f"Status code: {response.status_code}")
        except Exception as e:
            raise ValueError(f"Error: {e}")
