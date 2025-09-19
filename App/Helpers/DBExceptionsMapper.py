from psycopg2 import errors

DB_ERROR_MAPPING = {
    errors.UniqueViolation: lambda e: ConflictError(str(e)),
    errors.ForeignKeyViolation: lambda e: BadRequestError(str(e)),
}

def map_db_exception(exc):
    """
    Cek type psycopg2 exception, kembalikan APIError yang sesuai.
    Jika tidak dikenali, kembalikan generic APIError
    """
    for db_exc_class, api_error_func in DB_ERROR_MAPPING.items():
        if isinstance(exc, db_exc_class):
            return api_error_func(exc)
    return APIError(str(exc))

class APIError(Exception):
    """Base class untuk semua error API"""
    status_code = 500
    message = "Something went wrong"

    def to_dict(self):
        return {"response": self.message, "messages": "error"}

class BadRequestError(APIError):
    status_code = 400
    def __init__(self, message="Bad Request"):
        self.message = message

class ConflictError(APIError):
    status_code = 409
    def __init__(self, message="Conflict"):
        self.message = message
