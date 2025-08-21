class SessionError(ModuleNotFoundError):
    def __init__(self):
        super().__init__("No module named 'bliss'")
