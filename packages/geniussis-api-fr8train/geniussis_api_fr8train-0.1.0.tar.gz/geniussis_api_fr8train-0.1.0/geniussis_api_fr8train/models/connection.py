from requests import Session
from urllib.parse import urlencode


class Connection:
    token: str
    session: Session
    base_url: str

    def __init__(
        self,
        base_url: str,
        token: str = "",
        session: Session = Session(),
    ):
        self.token = token
        self.base_url = base_url
        self.session = session

    def get(self, uri: str):
        response = self.session.get(
            f"{self.base_url}/api/v1/{uri}",
            headers={"Authorization": f"Bearer {self.token}"},
        )

        response.raise_for_status()
        return response.json()

    def post(self):
        pass
