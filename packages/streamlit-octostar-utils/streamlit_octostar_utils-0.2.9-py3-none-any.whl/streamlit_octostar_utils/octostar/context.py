class NoContextException(Exception):
    def __init__(self, context_validity, message=None):
        self.message = message
        self.context_validity = context_validity
        super().__init__(self.message)
