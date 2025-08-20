class SessionTokenUsage:
    def __init__(self, input_token = 0, output_token = 0):
        self.input_token = input_token
        self.output_token = output_token
        self.total_token = input_token + output_token