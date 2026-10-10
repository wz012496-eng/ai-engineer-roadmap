# MCP 学习笔记

## 当前 Agent 的工具调用

- `main.py` 是应用入口，调用 `ask_llm_with_tools`。
- `llm.py` 把工具定义发给模型，处理模型返回的 `tool_calls`，再把工具结果交回模型。
- `tools.py` 定义当前模型使用的工具描述，并通过 `TOOL_HANDLERS` 找到 Python 处理函数。
- 处理函数调用 `TaskManager` 执行任务业务操作。

## 接入 MCP 后的职责

- Host：继续承载应用入口、Agent 循环和模型调用。
- MCP Client：发现 MCP Server 提供的工具，并向 Server 发起调用。
- MCP Server：注册和执行任务工具，调用 `TaskManager` 完成业务操作。
- MCP Server 使用 MCP 工具描述；Host 将发现的工具转换成模型 API 所需的工具格式。

## 调用链

用户请求
→ Host 调用模型
→ 模型返回工具调用
→ MCP Client 调用 MCP Server
→ MCP Server 调用任务处理函数和 TaskManager
→ 工具结果返回 Host
→ Host 把结果交给模型生成最终回答

## MCP 解决的问题

MCP 为 AI 应用连接外部工具和上下文能力提供统一接口，让 Host 能发现并调用不同 Server 提供的能力。

## MCP 与直接 Function Calling

- 直接 Function Calling：应用把工具 schema 发给模型，再由应用代码解析模型返回的工具调用并执行。
- MCP：通过标准协议让 Host 发现并调用 Server 提供的工具；Host 仍可把这些工具转成模型 API 所需的 schema。
- 两者关系：Function Calling 负责模型与应用之间的工具调用表达；MCP 负责 Host 与外部工具服务之间的标准化连接。MCP 补充这条链路，不取代 Function Calling。
