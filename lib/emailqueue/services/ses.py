from emailqueue.services import Api as ServiceApi
import boto

class Api(ServiceApi):
    name = "Amazon SES"

    def __init__(self, service):
        self.service = service
        self._conn = None

    @property
    def connection(self):
        if self._conn is None:
            self._conn = boto.connect_ses(
                aws_access_key_id=self.service.key,
                aws_secret_access_key=self.service.secret)

        return self._conn

    def send(self, email):
        self.connection.send_raw_email(
            raw_message=email.message,
            source=email.address_from,
            destinations=email.address_to
        )
