# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class SapioException(Exception):
    """
    A generic exception thrown by sapiopycommons methods. Typically caused by programmer error, but may also be from
    extremely edge case user errors. For expected user errors, use SapioUserErrorException.

    CommonsWebhookHandler's default behavior for this and any other exception that doesn't extend SapioException is
    to return a generic toaster message saying that an unexpected error has occurred.
    """
    pass


class SapioUserCancelledException(SapioException):
    """
    An exception thrown when the user cancels a client callback.

    CommonsWebhookHandler's default behavior is to simply end the webhook session with a true result without logging
    the exception.
    """
    pass


class SapioDialogTimeoutException(SapioException):
    """
    An exception thrown when the user leaves a client callback open for too long.

    CommonsWebhookHandler's default behavior is to display an OK popup notifying the user that the dialog has timed out.
    """
    pass


class SapioUserErrorException(SapioException):
    """
    An exception caused by user error (e.g. user provided a CSV when an XLSX was expected), which promises to return a
    user-friendly message explaining the error that should be displayed to the user.

    CommonsWebhookHandler's default behavior is to return the error message in a toaster popup.
    """
    pass


class SapioCriticalErrorException(SapioException):
    """
    A critical exception caused by user error, which promises to return a user-friendly message explaining the error
    that should be displayed to the user.

    CommonsWebhookHandler's default behavior is to return the error message in a display_error callback.
    """
    pass
