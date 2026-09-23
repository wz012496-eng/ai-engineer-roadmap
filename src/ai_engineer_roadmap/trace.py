import json


class TraceLogger:
    def __init__(self, trace_id: str):
        self.trace_id = trace_id

    def log(self, message: str, step: int | None = None):
        if step is None:
            print(f"[TRACE] trace_id={self.trace_id} {message}")
        else:
            print(f"[TRACE] trace_id={self.trace_id} step={step} {message}")

    def tool_call(self, name: str, arguments: dict, step: int):
        self.log(f"Tool call: {name}", step=step)
        self.log(
            f"Tool arguments: {json.dumps(arguments, ensure_ascii=False)}",
            step=step,
        )

    def tool_result(self, name: str, result: str, step: int):
        self.log(f"Tool result: {name}", step=step)
        self.log(result, step=step)

    def error(self, message: str):
        self.log(f"ERROR: {message}")
