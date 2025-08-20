class DatabaseException(Exception):
    def __init__(self, text: str, user_id: int | None = None , original_exception=None):
        self.user_id = user_id
        self.text = text
        self.original_exception = original_exception

class InternalException(Exception):
    def __init__(self, text: str, user_id: int | None = None, telegram_id: int | None = None, original_exception=None):
        self.user_id = user_id
        self.text = text
        self.original_exception = original_exception