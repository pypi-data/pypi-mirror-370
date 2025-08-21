from .module_imports import key
from uplink.retry.when import status_5xx
from uplink import (
    Consumer,
    post,
    returns,
    headers,
    retry,
    Body,
    json,
)


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class Emails(Consumer):
    def __init__(self, Resource, *args, **kw):
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @json
    @post("manual/paths/invoke")
    def send(self, email_message: Body):
        """This call will send an email message with the specified recipient, subject, and html/text body."""
