# CUHKSZ Booking MCP 服务器

一个基于模型上下文协议 (MCP) 的香港中文大学（深圳）场馆预订系统接口服务。

## 📋 目录

- [项目描述](#项目描述)
- [可用工具](#可用工具)
- [安装与部署](#安装与部署)
- [测试说明](#测试说明)
- [项目架构](#项目架构)
- [实现方式与核心逻辑](#实现方式与核心逻辑)
- [故障排除](#故障排除)
- [许可证与免责声明](#许可证与免z声明)

## ✨ 项目描述

一个基于模型上下文协议 (MCP) 的香港中文大学（深圳）场馆预订系统接口服务，该服务使语言模型能够查询场地信息、检查可用时段并执行在线预订。

## 🛠️ 可用工具

本服务提供了一套结构化的工具，用于查询和预订场地。推荐的调用流程是：
1.  使用 `booking_get_field_info` 获取目标场地类型的总体信息，包括其下的具体场所列表及其 ID。
2.  使用 `booking_get_available_places` 查询在特定时间段内，哪些具体场所是可用的。
3.  使用 `booking_book` 预订一个确切的可用场所。

---

### 1. `booking_get_field_info`
查询指定场地类型在某一天内的基本信息，包括所有具体场所的列表和当天的预订情况。

- **参数说明**:
  - `field` (`Literal["badminton"]`): **必须**。要查询的场地类型。
    - **约束**: 目前仅支持 `"badminton"`。必须使用英文名称。
  - `start_time` (`string`): **必须**。查询范围的开始时间。
    - **格式**: `YYYY-MM-DD HH:MM`。
  - `end_time` (`string`): **必须**。查询范围的结束时间。
    - **格式**: `YYYY-MM-DD HH:MM`。

- **返回示例**:
  ```
  场地信息:
  场地名称: badminton
  场地ID: 1097
  
  可用场所:
    - 羽毛球场1 (ID: 1100)
    - 羽毛球场2 (ID: 1101)
    ...
  
  当前预订 (3 个):
    - Booker: 张三, Start Time: ..., End Time: ..., Reason: ..., PlaceID: 1100
    ...
  ```

---

### 2. `booking_get_available_places`
根据 `booking_get_field_info` 的结果，查询在您指定的时间段内，哪些具体的场所是空闲的。

- **参数说明**:
  - `field` (`Literal["badminton"]`): **必须**。要查询的场地类型。
    - **约束**: 目前仅支持 `"badminton"`。必须使用英文名称。
  - `query_start_time` (`string`) & `query_end_time` (`string`): **必须**。用于获取当天预订信息的查询范围，通常是场地开放的一整天（如 `08:00` 到 `22:00`）。
    - **格式**: `YYYY-MM-DD HH:MM`。
  - `check_start_time` (`string`) & `check_end_time` (`string`): **必须**。您希望预订的**具体**时间段。
    - **格式**: `YYYY-MM-DD HH:MM`。

- **返回示例**:
  ```
  时间段 2025-01-01 17:00 到 2025-01-01 18:00 的可用场地:

    - 羽毛球场2 (ID: 1101)
    - 羽毛球场4 (ID: 1103)

  共 2 个场地可用
  ```

---

### 3. `booking_book`
执行预订操作。您需要提供从前两个工具中获取的 ID。

- **参数说明**:
  - `field_id` (`string`): **必须**。要预订的**场地类型**的 ID，从 `booking_get_field_info` 获取 (例如，羽毛球场地的 ID 是 "1097")。
  - `place_id` (`string`): **必须**。要预订的**具体场所**的 ID，从 `booking_get_available_places` 的返回结果中选取。
  - `start_time` (`string`) & `end_time` (`string`): **必须**。预订的起止时间。
    - **格式**: `YYYY-MM-DD HH:MM`。
  - `telephone` (`string`): **必须**。您的联系电话。
  - `reason` (`string`): **必须**。预订原因或主题 (例如 "🏸" 或 "Badminton Practice")。
  - `details` (`string`): **必须**。预订的详细说明。

## 🚀 安装与部署

本服务支持 Docker 部署和本地运行两种方式。

### 1. 使用 Docker (推荐)

此方法最简单，推荐用于生产和日常使用。

**a. 环境准备**

- 安装 [Docker](https://www.docker.com/get-started/) 和 [Docker Compose](https://docs.docker.com/compose/install/)。
- 克隆项目:
  ```bash
  git clone https://github.com/BetterAndBetterII/awesome-cuhksz-mcp.git
  cd BOOKING-MCP
  ```

**b. 配置凭证**

在项目根目录 (`BOOKING-MCP/`) 创建一个 `.env` 文件，并填入您的凭证。

```
# .env 文件内容
BOOKING_USERNAME=你的学号
BOOKING_PASSWORD=你的密码
```
**⚠️ 安全提醒**: 请勿将 `.env` 文件提交到版本控制系统。

**c. 构建和启动服务**

```bash
# 构建并以守护进程模式启动容器
docker-compose up --build -d

# 查看实时日志
docker-compose logs -f booking-mcp

# 停止服务
docker-compose down
```
服务启动后，将在 `http://localhost:3001` 上提供 MCP 接口。

### 2. 本地运行 (用于开发)

**a. 环境准备**

克隆项目并进入目录：
```bash
git clone https://github.com/BetterAndBetterII/awesome-cuhksz-mcp.git
cd BOOKING-MCP
```

创建并激活 Python 虚拟环境：
```bash
python3 -m venv .venv
source .venv/bin/activate
```

安装项目依赖（以可编辑模式）：
```bash
pip install -e .
```

**b. 配置凭证**

您可以通过以下两种方式提供凭证（命令行参数优先）：

1.  **（推荐）创建 `.env` 文件**:
    在项目根目录 (`BOOKING-MCP/`) 下创建一个 `.env` 文件。
    ```
    # .env 文件内容
    BOOKING_USERNAME=你的学号
    BOOKING_PASSWORD=你的密码
    ```

2.  **命令行参数**:
    在启动命令中直接提供。

**c. 启动服务**

- 如果您配置了 `.env` 文件：
  ```bash
  # 使用模块名启动 (默认使用 stdio 传输)
  python -m mcp_server_booking
  # 或
  mcp-server-booking
  ```

- 如果您希望使用命令行参数 (默认使用 stdio 传输)：
  ```bash
  python -m mcp_server_booking --username 你的学号 --password 你的密码
  ```
  
> **注意**: `stdio` 模式用于直接的进程间通信，不会监听网络端口。如果需要通过网络（如 `http://localhost:3001`）访问服务，或运行 `test/test.py` 脚本，必须在启动时指定 `sse` 传输模式：
> ```bash
> python -m mcp_server_booking --transport sse
> ```

- 如果您希望使用命令行参数提供凭证并使用 SSE 传输：
  ```bash
  python -m mcp_server_booking --transport sse --username 你的学号 --password 你的密码
  ```

当使用 `sse` 模式启动后，服务将在 `http://localhost:3001` 上提供 MCP 接口。

## 📄 项目架构

### 核心模块说明

- **`