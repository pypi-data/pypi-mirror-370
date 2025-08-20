class MissingMetatronException(Exception):
    """A custom exception to notify users that Metatron is not installed"""
    
    def __init__(self, message="Missing Metatron module. Install package using internal extras (i.e pickley install ntscli-client[internal])"):
        self.message = message
        super().__init__(self.message)
