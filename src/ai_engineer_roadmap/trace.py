import json


class TraceLogger:
    def log(self, message: str):
        print(f"[TRACE] {message}")

    def user_message(self, message: str):
        self.log(f"User: {message}")

    def model_response(self, message):
        self.log(f"Model response: {message}")

    def tool_call(self, name: str, arguments: dict):
        self.log(f"Tool call: {name}")
        self.log(f"Tool arguments: {json.dumps(arguments, ensure_ascii=False)}")

    def tool_result(self, name: str, result):
        self.log(f"Tool result: {name}")
        if isinstance(result, str):
            self.log(result)
        else:
            self.log(
                json.dumps(
                    result,
                    ensure_ascii=False,
                    default=str,
                )
            )

    def error(self, message: str):
        self.log(f"ERROR: {message}")
