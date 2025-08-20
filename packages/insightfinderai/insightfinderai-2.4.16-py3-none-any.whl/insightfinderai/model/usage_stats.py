class UsageStats:
    def __init__(self, input_token_used,output_token_used, total_token_limit):
        self.input_token_used = input_token_used
        self.output_token_used = output_token_used
        self.total_token_limit = total_token_limit
        self.total_token_usage = round((input_token_used + output_token_used) / total_token_limit * 100)

    def print(self):
        output = f"""
Organization consumption status:
- Total token count: {self.input_token_used + self.output_token_used}
- Total token limit: {self.total_token_limit}
- Consumption percentage: {self.total_token_usage}%
"""
        return output

    def __str__(self):
        return self.print()