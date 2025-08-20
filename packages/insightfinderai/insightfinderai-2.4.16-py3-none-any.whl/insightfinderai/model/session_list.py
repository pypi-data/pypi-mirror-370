from . import SessionTokenUsage

class SessionMetadata:
    def __init__(self,name,model_type,model_version,token_usage: SessionTokenUsage):
        self.name = name
        self.model_type = model_type
        self.model_version = model_version
        self.session_token_usage = token_usage

class SessionList:
    def __init__(self):
        self.sessions: list[SessionMetadata] = []

    # print a table for all the llm sessions
    def print(self):
        if not self.sessions:
            return "No LLM sessions available."

        result = "[LLM Sessions]\n"
        result += "-" * 130 + "\n"
        result += "{:<30} {:<15} {:<40} {:<10}\n".format(
            "Session Name", "Model Type", "Version", "Total Input/Output Tokens"
        )
        result += "-" * 120 + "\n"

        for session in self.sessions:
            result += "{:<30} {:<15} {:<40} {:<10}\n".format(
                session.name[:25] + (".." if len(session.name) > 25 else ""),
                session.model_type[:13] + (".." if len(session.model_type) > 13 else ""),
                session.model_version[:35] + (".." if len(session.model_version) > 35 else ""),
                str(session.session_token_usage.input_token) + ' / ' + str(session.session_token_usage.output_token)
            )

        return result

    def __str__(self):
        return self.print()
