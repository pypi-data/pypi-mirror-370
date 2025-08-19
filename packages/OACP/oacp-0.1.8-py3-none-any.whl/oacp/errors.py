"""OACP exception hierarchy."""


class OacpError(Exception):
    """Base exception for all OACP errors."""
    
    def __init__(
        self, 
        message: str, 
        run_id: str | None = None, 
        node_id: str | None = None,
        help_url: str | None = None
    ):
        super().__init__(message)
        self.run_id = run_id
        self.node_id = node_id
        self.help_url = help_url or "https://oacp.readthedocs.io/en/latest/troubleshooting.html"


class OacpConsensusError(OacpError):
    """Raised when consensus cannot be reached."""
    
    def __init__(
        self,
        message: str,
        votes_cast: int = 0,
        approvals: int = 0,
        rejections: int = 0,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.votes_cast = votes_cast
        self.approvals = approvals
        self.rejections = rejections


class OacpTimeout(OacpError):
    """Raised when vote window times out."""
    
    def __init__(self, message: str, timeout_seconds: int = 0, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds


class OacpStorageError(OacpError):
    """Raised when storage operations fail."""
    pass


class OacpRetryExhausted(OacpError):
    """Raised when retry attempts are exhausted."""
    
    def __init__(self, message: str, max_attempts: int = 0, **kwargs):
        super().__init__(message, **kwargs)
        self.max_attempts = max_attempts


class OacpInvalidVote(OacpError):
    """Raised for invalid voting operations."""
    
    def __init__(self, message: str, voter_id: str | None = None, **kwargs):
        super().__init__(message, **kwargs)
        self.voter_id = voter_id
