import enum


class RequestType(str, enum.Enum):
    """
    Request type
    - plumber
    - electrician
    - other
    """

    PLUMBER = "plumber"
    ELECTRICIAN = "electrician"
    OTHER = "other"


class RequestStatus(str, enum.Enum):
    """
    Request status
    - new
    - in_progress
    - completed
    - cancelled
    """

    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
