r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""


class Config:
    def __init__(self):
        self.api_key = None
        self.attribution = None
        self.secs_post_timeout = 5
        self.raise_final_request_attempt = True
        self.tx_uuid = None
        self.version = "0.3.3"
