from sqlparse import split, format


class SQL:
    def __init__(self, sql: str):
        self._sql = sql

    def split(self) -> list[str]:
        return split(format(self._sql, strip_comments=True))
