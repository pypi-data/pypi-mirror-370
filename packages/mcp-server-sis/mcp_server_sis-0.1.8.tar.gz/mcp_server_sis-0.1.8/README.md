# CUHKSZ SIS MCP 服务器

一个基于模型上下文协议 (MCP) 的香港中文大学（深圳）学生信息系统 (SIS) 接口服务。

## 📋 目录

- [项目描述](#项目描述)
- [可用工具](#可用工具)
- [安装与部署](#安装与部署)
- [测试说明](#测试说明)
- [项目架构](#项目架构)
- [实现方式与核心逻辑](#实现方式与核心逻辑)
- [故障排除](#故障排除)
- [许可证](#许可证)

## ✨ 项目描述

一个基于模型上下文协议 (MCP) 的香港中文大学（深圳）学生信息系统 (SIS) 接口服务，该服务使语言模型能够查询课程表、成绩、课程信息等。

## 🛠️ 可用工具

---

### 1. `sis_get_schedule`
获取您在 SIS 系统中当前学期的个人课程表。

- **参数说明**: 无需参数。

---

### 2. `sis_get_course`
查询指定课程在特定学期的详细开课信息，包括时间、地点、教师和名额。

- **参数说明**:
  - `course_code` (`string`): **必须**。完整的课程代码。
    - **格式**: 由学科前缀和课程编号组成，例如 `"CSC3002"`。
  - `term` (`string`): **必须**。要查询的学期代码。
    - **格式**: 四位数字，前两位代表学年，后两位代表学期。例如:
      - `"2410"`: 2024-25学年的第一学期 (秋季)。
      - `"2420"`: 2024-25学年的第二学期 (春夏)。
      - `"2450"`: 2024-25学年的夏季学期。
  - `open_only` (`bool`): *可选*。是否只显示仍有名额的课程。默认为 `False`。

---

### 3. `sis_get_grades`
查询您在指定学期的所有课程成绩。

- **参数说明**:
  - `term` (`string`): **必须**。要查询的学期名称。
    - **格式**: SIS 系统中的标准学期名称，例如 `"2024-25 Term 1"`。

---

### 4. `sis_get_course_outline`
查询指定课程的官方大纲信息，包括课程描述和先修课程要求。

- **参数说明**:
  - `course_code` (`string`): **必须**。完整的课程代码，例如 `"CSC3002"`。

---

### 5. `sis_get_academic_record`
查询您的完整学术记录，包括所有学期修读过的课程、成绩和学分。

- **参数说明**: 无需参数。

## 🚀 安装与部署

本服务支持 Docker 部署和本地运行两种方式。

### 1. 使用 Docker (推荐)

此方法最简单，推荐用于生产和日常使用。

**a. 环境准备**

- 安装 [Docker](https://www.docker.com/get-started/) 和 [Docker Compose](https://docs.docker.com/compose/install/)。
- 克隆项目:
  ```bash
  git clone https://github.com/BetterAndBetterII/awesome-cuhksz-mcp.git
  cd SIS-MCP
  ```

**b. 配置凭证**

在项目根目录 (`SIS-MCP/`) 创建一个 `.env` 文件，并填入您的 SIS 凭证。

```
# .env 文件内容
SIS_USERNAME=你的学号
SIS_PASSWORD=你的密码
```
**⚠️ 安全提醒**: 请勿将 `.env` 文件提交到版本控制系统。

**c. 构建和启动服务**

```bash
# 构建并以守护进程模式启动容器（首次运行或代码更新后）
docker-compose up --build -d

# 查看实时日志
docker-compose logs -f sis-mcp

# 停止服务
docker-compose down
```
服务启动后，将在 `http://localhost:3000` 上提供 MCP 接口。


### 2. 本地运行 (用于开发)

如果您希望在本地直接运行服务进行开发或测试：

**a. 环境准备**

克隆项目并进入目录：
```bash
git clone https://github.com/BetterAndBetterII/awesome-cuhksz-mcp.git
cd SIS-MCP
```

创建并激活 Python 虚拟环境：
```bash
python3 -m venv .venv
source .venv/bin/activate
```

安装项目依赖。使用 `-e` 标志以可编辑模式安装，这样您的代码更改会立刻生效：
```bash
pip install -e .
```

**b. 配置凭证**

您可以通过以下两种方式提供您的 SIS 凭证（命令行参数优先）：

1.  **（推荐）创建 `.env` 文件**:
    在项目根目录 (`SIS-MCP/`) 下创建一个 `.env` 文件，并填入您的凭证。
    ```
    # .env 文件内容
    SIS_USERNAME=你的学号
    SIS_PASSWORD=你的密码
    ```

2.  **命令行参数**:
    在启动命令中直接提供凭证。

**c. 启动服务**

- 如果您配置了 `.env` 文件：
  ```bash
  # 使用模块名启动 (默认使用 stdio 传输)
  python -m mcp_server_sis

  # 或者，使用安装后生成的可执行脚本 (默认使用 stdio 传输)
  mcp-server-sis
  ```

- 如果您希望使用命令行参数提供凭证 (默认使用 stdio 传输)：
  ```bash
  python -m mcp_server_sis --username 你的学号 --password 你的密码
  ```
  
> **注意**: `stdio` 模式用于直接的进程间通信，不会监听网络端口。如果需要通过网络（如 `http://localhost:3000`）访问服务，或运行 `test/test.py` 脚本，必须在启动时指定 `sse` 传输模式：
> ```bash
> python -m mcp_server_sis --transport sse
> ```

- 如果您希望使用命令行参数提供凭证并使用 SSE 传输：
  ```bash
  python -m mcp_server_sis --transport sse --username 你的学号 --password 你的密码
  ```

当使用 `sse` 模式启动后，服务将在 `http://localhost:3000` 上提供 MCP 接口。

## 🏗️ 项目架构

### 核心模块说明

#### 1. `sis.py` - MCP 服务器层
- **职责**: 定义 MCP 工具接口，处理异步请求，管理缓存和登录状态。
- **核心功能**:
  - 全局登录状态管理（15分钟超时自动重登录）。
  - 结果缓存机制（TTL 可配置，默认1小时）。
  - 异步工具包装（将同步爬虫代码在线程池中执行）。

#### 2. `sis_system.py` - SIS 交互层
- **职责**: 直接与 CUHKSZ SIS 网站交互，处理登录认证和数据抓取。
- **核心功能**:
  - 双阶段 ADFS OAuth2 登录流程。
  - HTML 解析和数据提取。
  - 会话管理和 Cookie 处理。

#### 3. `__main__.py` - 服务入口与凭证管理
- **职责**: 处理服务启动、参数配置和凭证管理。它会验证启动时是否提供了必要的 SIS 用户名和密码，并支持从命令行参数或 `.env` 文件中读取这些凭证。
- **传输协议**: Server-Sent Events (SSE)。
- **默认端口**: 3000。

## 🔧 实现方式与核心逻辑

### 1. 登录认证流程
服务采用双阶段认证，首先向 ADFS 获取授权码，然后使用该码完成 SIS 系统的最终登录，从而建立会话。

### 2. 缓存机制
为提高性能和避免重复请求，所有查询类的工具都默认启用了一小时的缓存。您可以通过 `sis_clear_cache` 工具手动清除缓存。

### 3. 数据抓取
通过模拟浏览器行为，提交表单并解析返回的 HTML 页面来提取所需的数据。核心解析库为 `lxml`。

## 🧪 测试说明

项目提供了完整的自动化测试脚本 `test/test.py`，用于验证所有 MCP 工具的功能。

### 运行测试

```bash
# 确保服务已启动 (无论是通过 Docker 还是本地运行)
# 进入测试目录并运行测试
cd test
python test.py
```
脚本会自动连接服务、发现工具、使用预设参数调用并显示结果。

## 🔧 故障排除

### 常见问题

#### 1. 容器启动失败
- **症状**: `docker-compose up` 命令失败。
- **解决方案**: 检查 `.env` 文件是否存在，并重新构建容器 `docker-compose up --build`。

#### 2. 登录失败
- **症状**: 日志显示 "Failed to login to SIS system" 或 "Username or password incorrect!"。
- **解决方案**: 验证 `.env` 文件中的 `SIS_USERNAME` 和 `SIS_PASSWORD` 是否正确。

#### 3. 启动时报错 "Error: SIS_USERNAME and SIS_PASSWORD must be provided"
- **症状**: 服务无法启动，并显示凭证缺失的错误。
- **解决方案**:
  - **Docker**: 确保项目根目录中存在 `.env` 文件且内容正确。
  - **本地运行**: 确保已创建 `.env` 文件，或在启动时通过 `--username` 和 `--password` 参数提供了凭证。

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---
**⚠️ 免责声明**: 本项目仅供学习和研究使用。请遵守学校的相关政策和服务条款。 