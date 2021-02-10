class InvalidChartError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InvalidConfigError(Exception):
    def __init__(self, message):
        self.message = f'Validation of the environment variables failed: {message}'
        super().__init__(self.message)
