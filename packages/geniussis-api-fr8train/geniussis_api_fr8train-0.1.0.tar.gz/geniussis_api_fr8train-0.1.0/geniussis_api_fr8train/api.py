import geniussis_api_fr8train.factories.authentication as AuthenticationFactory
from geniussis_api_fr8train.models.connection import Connection


class Api:
    conn: Connection

    def __init__(self):
        self.conn = AuthenticationFactory.build_api_connector()

        self.affiliations = self.Affiliations(self.conn)

    class Affiliations:
        conn: Connection

        def __init__(self, conn: Connection):
            self.conn = conn

        def list_affiliations(self):
            response = self.conn.get("affiliations")

            return response
