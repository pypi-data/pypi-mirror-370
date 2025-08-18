# CUHKSZ MCP Email Server

一个基于模型上下文协议 (MCP) 的电子邮件收发服务，能够让语言模型安全、可靠地发送邮件及处理附件，用于CUHKSZ的Manus项目。

## 📋 目录

- [项目描述](#-项目描述)
- [可用工具](#-可用工具)
- [安装与部署](#-安装与部署)
- [测试说明](#-测试说明)
- [项目架构](#-项目架构)
- [实现方式与核心逻辑](#-实现方式与核心逻辑)
- [故障排除](#-故障排除)
- [许可证与致谢](#-许可证与致谢)

## ✨ 项目描述

本项目实现了一个基于模型上下文协议 (MCP) 的电子邮件服务。它为语言模型提供了一套标准化的工具，使其能够代表用户执行邮件相关的任务，如撰写和发送邮件、添加附件，以及在指定的目录中搜索文件作为附件。通过将邮件功能封装为安全的 MCP 工具，可以有效避免直接在语言模型中暴露用户的敏感凭证（如邮箱密码或授权码）。

## 🛠️ 可用工具

本服务提供了两个核心工具，用于处理邮件的发送和附件的搜索。

---

### 1. `send_email`
发送一封电子邮件。您可以指定单个或多个收件人、主题、正文，并附上一个或多个附件。

- **参数说明**:
  - `receiver` (`list[str]`): **必须**。收件人的电子邮件地址列表。
  - `subject` (`string`): **必须**。邮件的主题。
  - `body` (`string`): **必须**。邮件的正文内容。
  - `attachments` (`list[str]`): **可选**。要附加的文件名列表。
    - **注意**: 文件必须存在于服务启动时通过 `--dir` 参数指定的附件目录中。

- **返回示例**:
  ```
  Email to recipient@example.com sent successfully from your-email@example.com
  ```

---

### 2. `search_attachments`
在服务配置的附件目录中，根据提供的关键词搜索匹配的文件。

- **参数说明**:
  - `pattern` (`string`): **必须**。用于在文件名中搜索的文本关键词，搜索不区分大小写。

- **返回示例**:
  ```
  Search results for 'test_attachment':
  /app/attachments/test_attachment.txt
  ```

## 🚀 安装与部署

本服务支持 Docker 部署和本地运行两种方式。

### 1. 使用 Docker (推荐)

此方法最简单、最可靠，推荐用于生产和日常使用。

**a. 环境准备**

- 安装 [Docker](https://www.docker.com/get-started/) 和 [Docker Compose](https://docs.docker.com/compose/install/)。
- 克隆本项目。

**b. 配置凭证**

在项目根目录创建一个 `.env` 文件，并填入您的邮箱凭证。

```dotenv
# .env 文件内容
# 发件人的完整邮箱地址
EMAIL_USERNAME=your-email@example.com
# 邮箱的密码或授权码 (强烈推荐使用授权码)
EMAIL_PASSWORD=your_password_or_app_password 
```
**⚠️ 安全提醒**:
- **请勿**将 `.env` 文件提交到任何版本控制系统（如 Git）。
- 对于 QQ 邮箱、Gmail 等服务，您**必须**使用生成的**授权码 (App Password)**，而不是您的账户登录密码。

**c. 构建和启动服务**

在项目根目录下运行以下命令：
```bash
# 构建并以守护进程模式启动容器
docker-compose up --build -d

# 查看实时日志
docker-compose logs -f mcp-email-server

# 停止服务
docker-compose down
```
服务启动后，将在 `http://localhost:3002` 上提供 MCP 接口。

### 2. 本地运行 (用于开发)

**a. 环境准备**

克隆项目后，创建并激活 Python 虚拟环境，然后安装依赖：
```bash
# 创建虚拟环境
python3 -m venv .venv
# 激活虚拟环境 (macOS/Linux)
source .venv/bin/activate
# 激活虚拟环境 (Windows)
# .venv\Scripts\activate

# 安装依赖
pip install -r src/mcp_server_email_cuhksz/requirements.txt
```

**b. 配置凭证**

您可以选择创建 `.env` 文件（推荐）或在启动时使用命令行参数来提供凭证。

**c. 启动服务**

- **使用 `.env` 文件 (推荐)**:
  ```bash
  # 使用 stdio 传输 (用于直接的进程间通信)
  python -m mcp_server_email_cuhksz --dir /path/to/your/attachments

  # 使用 sse 传输 (用于网络访问和测试脚本)
  python -m mcp_server_email_cuhksz --transport sse --dir /path/to/your/attachments
  ```

- **使用命令行参数**:
  ```bash
  python -m mcp_server_email_cuhksz --transport sse --username your-email@example.com --password your_password --dir /path/to/your/attachments
  ```
当使用 `sse` 模式启动后，服务将在 `http://localhost:3002` 上提供 MCP 接口。

## 🧪 测试说明

项目提供了一个测试脚本，用于验证服务是否正常运行。

1.  **启动服务**:
    请确保已通过 `docker-compose up --build` 成功启动了服务。

2.  **安装测试依赖**:
    ```bash
    pip install -r test/requirements.txt
    ```

3.  **运行测试脚本**:
    ```bash
    python -m test.test
    ```
    该脚本会连接到在 Docker 中运行的服务，并尝试发送一封带有附件的测试邮件。

## 🏗️ 项目架构

- **`src/mcp_server_email_cuhksz/`**: 包含所有核心应用代码。
  - **`__main__.py`**: 程序的入口点，负责解析命令行参数、加载环境变量和启动服务。
  - **`mcp_email.py`**: 定义了 `send_email` 和 `search_attachments` 两个 MCP 工具，并包含了实现其功能的后端逻辑。
  - **`email.json`**: 一个关键的配置文件，包含了不同邮件服务提供商 (如 QQ, Gmail, Office 365) 的 SMTP 服务器地址和端口信息。
- **`test/`**:
  - **`test.py`**: 一个客户端测试脚本，用于验证邮件服务的核心功能。
  - **`requirements.txt`**: 运行测试脚本所需的依赖。
- **`attachments/`**: 一个示例目录，用于存放邮件附件。
- **`Dockerfile`**: 用于构建服务 Docker 镜像的配置文件。
- **`docker-compose.yml`**: 用于编排和管理 Docker 容器的配置文件。
- **`.env`**: 用于存放敏感信息（如邮箱用户名和密码/授权码）的环境变量文件。

## 🧠 实现方式与核心逻辑

- **动态 SMTP 配置**: 服务通过 `get_smtp_info` 函数，根据发件人邮箱的域名 (`@qq.com`, `@link.cuhk.edu.cn` 等) 在 `email.json` 中查找对应的 SMTP 服务器和端口。这种设计使其易于扩展，以支持新的邮件服务提供商。
- **异步中的同步处理**: 邮件的发送是使用 Python 内置的、同步的 `smtplib` 库完成的。为了避免这个阻塞操作卡住 `FastMCP` 的异步事件循环，`send_email_logic` 函数被包裹在 `asyncio.to_thread` 中运行，使其在一个独立的线程中执行。
- **优雅的连接关闭**: 考虑到一些邮件服务器（如 QQ 邮箱）在邮件发送成功后可能会立即关闭连接，导致客户端在尝试发送 `QUIT` 命令时出错，程序在 `finally` 块中对 `server.quit()` 进行了特殊的异常处理，**主动忽略**此处的连接错误，从而确保即使服务器“提前挂断”，程序也不会崩溃。

## 🔧 故障排除

- **`ConnectionError: Server disconnected unexpectedly` 或 `TimeoutError`**:
  - 这通常是邮件服务商的安全策略导致的。
  - **检查授权码**: 确认您在 `.env` 中使用的是**授权码 (App Password)** 而不是登录密码。
  - **检查MFA**: 如果您的账户（尤其是 Office 365）开启了多因素认证 (MFA)，您很可能需要生成并使用“应用密码”。
  - **网络问题**: 确认您的服务器或本地机器可以访问外部邮件服务器。

- **`SMTPAuthenticationError`**:
  - 凭证错误。请仔细检查 `.env` 文件中的 `EMAIL_USERNAME` 和 `EMAIL_PASSWORD` 是否完全正确。

- **`ValueError: ... is not a supported email service`**:
  - 您使用的邮箱域名在 `email.json` 中没有对应的配置。请参照该文件中的格式，添加一个新的配置项。

## 📄 许可证与致谢

本项目采用 **MIT 许可证**。

本项目的实现方式，极大地参考了 [mcp-email-client](https://github.com/Shy2593666979/mcp-server-email) 项目。在此向原作者 **Shy2593666979** 表示衷心的感谢，其优秀的设计为本项目提供了宝贵的灵感和参考。
