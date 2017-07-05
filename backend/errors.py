class InvalidAuth(Exception): pass
class Interval(Exception): pass
class NotAllowed(Exception): pass
class NotFound(Exception): pass
class Existed(Exception): pass
class BadRequest(Exception): pass
class ServerError(Exception): pass

BadRequest_400 = 400
Forbidden_403 = 403
Conflict_409 = 409
InternalServerError_500 = 500
