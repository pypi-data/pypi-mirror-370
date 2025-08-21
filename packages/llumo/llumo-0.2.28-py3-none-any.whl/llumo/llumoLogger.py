import requests


class LlumoLogger:
    def __init__(self, apiKey: str, playground: str):
        self.apiKey = apiKey
        self.playground = playground
        self.workspaceID = None
        self.playgroundID = None
        self.userEmailID = None
        self._authenticate()

    def _authenticate(self):
        url = "https://app.llumo.ai/api/get-playground-name"
        try:
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.apiKey}",
                    "Content-Type": "application/json",
                },
                json={"playgroundName": self.playground},
                timeout=10,
            )

            response.raise_for_status()
            res_json = response.json()

            # Navigate into the nested "data" structure
            inner_data = res_json.get("data", {}).get("data", {})

            self.workspaceID = inner_data.get("workspaceID")
            self.playgroundID = inner_data.get("playgroundID")
            self.userEmailID = inner_data.get("createdBy")

            if not self.workspaceID or not self.playgroundID:
                raise RuntimeError(
                    f"Invalid response: workspaceID or playgroundID missing. Full response: {res_json}"
                )

        except requests.exceptions.RequestException as req_err:
            raise RuntimeError(
                f"Network or HTTP error during authentication: {req_err}"
            )
        except ValueError as json_err:
            raise RuntimeError(f"Invalid JSON in authentication response: {json_err}")
        except Exception as e:
            raise RuntimeError(f"Authentication failed: {e}")

    def getWorkspaceID(self):
        return self.workspaceID

    def getUserEmailID(self):
        return self.userEmailID

    def getPlaygroundID(self):
        return self.playgroundID
