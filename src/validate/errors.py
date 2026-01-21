# Custom validation error exceptions, Each error type represents a specific validation failure, This allows precise error handling and reporting.
class ValidationError(Exception):
    pass
class InvalidDateSequenceError(ValidationError):
    pass
class AmountMismatchError(ValidationError):
    pass
class CountyMatchError(ValidationError):
    pass
class ExtractionError(ValidationError):
    pass
class MissingFieldError(ValidationError):
    pass
