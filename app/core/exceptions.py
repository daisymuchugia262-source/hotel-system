"""
Domain-specific exceptions.
Used by services to signal business-rule failures.
"""


class DomainError(Exception):
    """Base class for all domain errors."""


class ValidationError(DomainError):
    """Input data fails a business rule."""


class NotFoundError(DomainError):
    """Entity not found."""


class DuplicateError(DomainError):
    """Entity already exists."""


class PaymentError(DomainError):
    """Invalid payment operation."""


class InsufficientPaymentError(PaymentError):
    """Amount paid doesn't clear the balance yet."""


class OverpaymentError(PaymentError):
    """Payment exceeds balance and change isn't allowed."""


class OrderNotPayableError(DomainError):
    """Order can't accept payments (cancelled, etc.)."""


class AuthenticationError(DomainError):
    """Bad credentials."""


class PermissionDeniedError(DomainError):
    """User not allowed to do this."""
