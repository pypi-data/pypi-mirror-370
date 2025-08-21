# AgentLin

通用 Agent 架构，支持多Agent协作和RPC远程调用。

## 主要特性

- 🤖 **多Agent系统**: 基于RabbitMQ的消息队列支持多Agent协作
- 🔗 **RPC远程调用**: 像本地函数一样调用远程Agent方法
- ⏰ **时间同步**: 分布式时间协调机制
- 🛠️ **工具集成**: 丰富的工具生态系统
- 📊 **数据处理**: 内置数据分析和可视化工具
- 🔄 **自动重连**: 健壮的连接管理和故障恢复


## 开始使用

### 1. 安装

```bash
pip install agentlin
```

本地安装

```bash
pip install -e .
# plotly 需要额外下载 chrome 内核用于渲染图表
plotly_get_chrome
```

### 2. 创建 `.env` 文件

复制 `.env.example` 文件为 `.env` 并填写所需的环境变量。

环境变量定义了访问 o3 模型的 API 密钥和其他配置。


### 3. 创建软链接

将公共数据目录 `/mnt/aime/datasets/agent/agent_data` 软链接到你本地项目的 `data` 目录下

```bash
ln -s /mnt/aime/datasets/agent/agent_data data
```

### 4. 运行应用程序

```bash
streamlit run chart_o3_toolcall.py
```

注意：如果你不是在交互式建模的容器里运行的，需要挂一个代理服务将本地请求转发到北美：

```bash
cd tool_server
bash run_aime_proxy_server.sh
```

### 5. 运行 MCP 服务器

```bash
agentlin launch --mcp-server file_system --host localhost --port 9999 --path /file_system_mcp --debug HOME_DIR=<your_home_directory> agentlin launch --mcp-server bash --host localhost --port 9999 --path /bash_mcp --debug
agentlin launch --mcp-server memory --host localhost --port 9999 --path /memory_mcp --debug
agentlin launch --mcp-server web --host localhost --port 9999 --path /web_mcp --debug
TODO_FILE_PATH=<your_todo_file_path> agentlin launch --mcp-server todo --host localhost --port 7780 --path /todo_mcp --debug
```

## 详细文档

参见 [RPC消息队列使用指南](docs/rpc_message_queue_guide.md)


## 目录结构

```sh
agentlin/
├── core/                     # 核心架构组件
│   ├── agent_schema.py       # Agent 模式定义
│   ├── simulator.py          # 仿真器
│   ├── multimodal.py         # 多模态支持
│   └── types.py              # 数据类型定义
├── route/                    # 路由和代理管理
│   ├── client.py             # 客户端
│   ├── mcp_proxy_*.py        # MCP 代理相关
│   ├── session_manager.py    # 会话管理
│   └── *_task_manager.py     # 任务管理器
├── code_interpreter/         # 代码解释器
│   ├── client.py             # 解释器客户端
│   ├── jupyter_*.py          # Jupyter 集成
│   ├── tool_call_display.py  # 工具调用显示
│   └── ...                   # 其他组件
└── tools/                    # 工具集合
    ├── tool_aime.py          # AIME 工具
    ├── tool_code_interpreter.py # 代码解释器工具
    ├── tool_chart.py         # 图表工具
    └── tool_*.py             # 其他工具

chart_agent/                  # 图表 Agent
table_agent/                  # 表格 Agent
tool_server/                  # 工具服务器
docs/                        # 项目文档
assets/                      # 配置文件
data/                        # 数据文件，软链接到 /mnt/aime/datasets/agent/agent_data
```



