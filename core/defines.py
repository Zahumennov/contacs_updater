from dataclasses import dataclass

TABLE_NAME = 'contacts'


@dataclass
class NimbleContact:
    first_name: str = None
    last_name: str = None
    email: str = None
