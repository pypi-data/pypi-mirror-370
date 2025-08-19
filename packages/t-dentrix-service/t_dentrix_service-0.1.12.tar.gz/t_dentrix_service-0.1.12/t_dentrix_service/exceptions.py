"""Module for custom exceptions."""


class LocationNameNotFoundError(Exception):
    """Exception raised when we fail to find a certain location name among dentrix Location info response."""


class DentrixLocationIdNotFound(Exception):
    """Exception raised when the location id given could not be found within Dentrix."""


class NotLoggedInError(Exception):
    """Exception raised whenever an operation is made without being successfully logged in."""


class FailedToUploadDocumentError(Exception):
    """Exception raised when it was not possible to upload a document to document manager."""


class DocumentNotSupportedException(Exception):
    """Exception raised when the document that is being uploaded to document manager isn't supported by it."""


class DocumentIsEmptyException(Exception):
    """Exception raised when the document being uploaded by the document manager is empty."""


class NoResultsError(Exception):
    """Exception when no results come up when searching patient."""


class PatientNotFoundError(Exception):
    """Exception when the exact patient could not be found in search."""


class InvalidRequestException(Exception):
    """Exception raised when the request isn't valid or could not be processed."""


class ConnectionRefusedException(Exception):
    """Exception raised when request is understood, but it has been refused or access is not allowed."""


class NotFoundException(Exception):
    """Exception raised when the requested resource is either missing or does not exist."""


class ConnectionTimeoutException(Exception):
    """Exception raised when the server timed out while processing the request."""


class RateLimitExceededException(Exception):
    """Exception raised when the server Rate limit is exceeded."""


class UnexpectedServerError(Exception):
    """Exception raised when an unexpected error occurred."""


class NoBillingStatementsInfoError(Exception):
    """Exception raise when we aren't able to get billing statement information from Dentrix."""


class BillingStatementsOpenError(Exception):
    """Raised when an exception is raised while opening the billing statements."""


class NoLedgerBalanceError(Exception):
    """Exception raised when no ledger balance info is found on Dentrix."""
