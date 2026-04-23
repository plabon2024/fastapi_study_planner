from enum import Enum

class SessionStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    missed = "missed"