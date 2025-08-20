from __future__ import annotations

import textwrap


class HttpError(Exception):
    def __init__(self, code: int, reason: str, path: str, method: str, json: str | None):
        super().__init__()
        self.code: int = code
        self.reason: str = reason
        self.path = path
        self.method = method
        self.json = json

    def __str__(self):
        begin = textwrap.dedent(
            f"""
            HTTP Error Code {self.code} : {self.reason}
            {self.method} {self.path}
        """
        )
        if self.json:
            if "apiKey" in self.json:
                end = ""
            else:
                end = textwrap.dedent(
                    f"""
                    ---- payload ---
                    {self.json}
                    ---
                    """
                )
        else:
            end = ""
        return begin + end
