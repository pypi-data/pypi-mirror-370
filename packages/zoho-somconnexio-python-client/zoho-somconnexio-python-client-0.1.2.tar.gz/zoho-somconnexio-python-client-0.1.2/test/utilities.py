import json


class FakeResponse:
    status_code = None
    content = ""
    reason = ""

    def __init__(self, status=200, reason="", content='{"test": "ok"}'):
        self.status_code = status
        self.content = content
        self.reason = reason
        self.text = "error"

    def json(self):
        return json.loads(self.content)
