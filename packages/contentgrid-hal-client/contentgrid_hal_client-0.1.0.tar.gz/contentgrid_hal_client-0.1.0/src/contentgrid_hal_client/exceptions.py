from requests.exceptions import HTTPError

class NotFound(HTTPError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class Unauthorized(HTTPError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class BadRequest(HTTPError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class IncorrectAttributeType(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NonExistantAttribute(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class MissingRequiredAttribute(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    
class MissingHALTemplate(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)