class CLSPError(Exception):
    """
    Exception class for CLSP-related errors.

    Represents internal failures in Convex Least Squares Programming
    routines. Supports structured messaging and optional diagnostic
    augmentation.

    Parameters
    ----------
    message : str, optional
        Description of the error. Defaults to a generic CLSP message.

    code : int or str, optional
        Optional error code or identifier for downstream handling.

    Usage
    -----
    raise CLSPError("Matrix A and b are incompatible", code=101)
    """
    def __init__(self, message: str = "An error occurred in CLSP"):
        super().__init__(message)
