class DomainValidationError(ValueError):
    pass


class InvalidStatusTransitionError(DomainValidationError):
    pass