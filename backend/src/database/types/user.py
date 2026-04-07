import enum


class UserRole(str, enum.Enum):
    """
    User role
    - resident
    - admin
    - plumber
    - electrician
    """

    RESIDENT = "resident"
    ADMIN = "admin"
    PLUMBER = "plumber"
    ELECTRICIAN = "electrician"
