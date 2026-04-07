import enum


class RequestType(str, enum.Enum):
    """
    Request type
    - plumbing
    - electrician
    - other
    """

    PLUMBING = "plumbing"
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
