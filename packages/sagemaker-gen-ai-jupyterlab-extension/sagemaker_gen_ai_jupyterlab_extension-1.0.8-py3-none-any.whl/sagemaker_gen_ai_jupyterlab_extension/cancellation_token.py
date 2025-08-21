class CancellationToken:
    """Token that can be used to signal cancellation of an operation."""
    def __init__(self):
        self._is_cancelled = False
    
    @property
    def isCancellationRequested(self) -> bool:
        return self._is_cancelled
    
    def cancel(self):
        self._is_cancelled = True

class CancellationTokenSource:
    """Source for creating and controlling cancellation tokens."""
    def __init__(self):
        self._token = CancellationToken()
    
    @property
    def token(self) -> CancellationToken:
        return self._token
    
    def cancel(self):
        self._token.cancel()