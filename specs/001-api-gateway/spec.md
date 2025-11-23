# Feature Specification: LLM API Gateway 网关系统

**Feature Branch**: `001-api-gateway`  
**Created**: 2025-11-23  
**Status**: Draft  
**Input**: User description: "实现一个 API Gateway，包括如下功能：代理 openai 风格的 LLM API 调用；有限流功能，但请求超限后，对请求进行排队处理而不是直接拒绝请求。提供一个基础的 Admin Console 来配置 LLM API Server，可以配置每一个 Server 的 URL，API KEY，以及提供的 model 列表，同时还能够配置限流的 rpm 和 tpm。代理的过程需要保持 API 不变，客户端需要在原 API 的 header 上添加一个 App-Name 来表明其身份，不做额外验证，这个身份会用在统计用量上。Admin Console 需要能够展示用量信息，维度包含 API Server + App-Name。限流会以 API Server 为维度。"

## Clarifications

### Session 2025-11-23

- Q: 当队列已满（达到最大队列长度）时，新请求如何处理？ → A: 移除队列中最旧的请求，接受新请求（FIFO 驱逐），确保最新的请求优先得到处理

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 客户端代理 LLM API 调用 (Priority: P1)

客户端应用通过网关调用 LLM API，网关自动路由到配置的后端 LLM 服务器。客户端只需在请求头添加 `App-Name` 标识身份，无需管理不同后端服务器的 URL 和 API Key。

**Why this priority**: 这是网关的核心功能，提供统一的 API 入口，简化客户端集成，是所有其他功能的基础。

**Independent Test**: 可以通过配置一个后端 LLM 服务器，客户端发送 OpenAI 格式的请求（带 App-Name header），验证网关成功转发请求并返回响应。

**Acceptance Scenarios**:

1. **Given** 网关已配置一个 LLM 后端服务器（包含 URL、API Key 和可用模型列表），**When** 客户端发送包含 `App-Name` header 的 OpenAI 格式请求到网关，**Then** 网关将请求转发到后端服务器，并将响应原样返回给客户端
2. **Given** 客户端发送的请求中指定的模型在某个后端服务器的模型列表中，**When** 网关接收到请求，**Then** 网关自动选择该后端服务器进行转发
3. **Given** 客户端发送请求但未包含 `App-Name` header，**When** 网关接收到请求，**Then** 网关拒绝请求并返回错误信息
4. **Given** 后端 LLM 服务器返回错误响应，**When** 网关接收到该响应，**Then** 网关将错误原样返回给客户端

---

### User Story 2 - 管理员配置 LLM 后端服务器 (Priority: P1)

管理员通过 Admin Console 配置后端 LLM 服务器，包括服务器的 URL、API Key、可用模型列表以及限流参数（RPM 和 TPM）。

**Why this priority**: 必须先配置后端服务器，网关才能工作，这是系统运行的前提条件。

**Independent Test**: 可以独立测试 Admin Console 的配置功能，验证能够添加、修改、删除 LLM 服务器配置，并且配置能够持久化保存。

**Acceptance Scenarios**:

1. **Given** 管理员登录 Admin Console，**When** 添加新的 LLM 服务器配置（URL、API Key、模型列表、RPM、TPM），**Then** 配置成功保存，网关可以使用该配置
2. **Given** 已存在的 LLM 服务器配置，**When** 管理员修改其参数（如更新 API Key 或调整限流参数），**Then** 修改生效，网关立即使用新配置
3. **Given** 已存在的 LLM 服务器配置，**When** 管理员删除该配置，**Then** 配置被删除，网关不再将请求路由到该服务器
4. **Given** 管理员输入的 URL 格式不正确，**When** 尝试保存配置，**Then** 系统提示错误并拒绝保存

---

### User Story 3 - 请求超限后排队处理 (Priority: P2)

当某个后端 LLM 服务器的请求速率达到配置的限流阈值（RPM 或 TPM）时，网关将新到达的请求加入队列等待处理，而不是直接拒绝。

**Why this priority**: 这是提升用户体验的关键功能，避免因短时流量突刺导致请求失败，但依赖核心代理功能已实现。

**Independent Test**: 可以通过配置低限流阈值，快速发送大量请求，验证超限请求被排队而非拒绝，并在限流窗口重置后按顺序处理。

**Acceptance Scenarios**:

1. **Given** 后端服务器配置的 RPM 为 10，**When** 客户端在 1 分钟内发送第 11 个请求，**Then** 第 11 个请求进入队列等待，而不是被拒绝
2. **Given** 队列中有等待的请求，**When** 限流窗口重置（下一分钟开始），**Then** 网关从队列中取出请求继续处理
3. **Given** 后端服务器配置的 TPM 为 100,000 tokens，**When** 当前分钟的 token 使用量接近限额，新请求到达，**Then** 网关根据请求预估的 token 数判断是否排队
4. **Given** 队列中的请求等待超过预设超时时间，**When** 超时触发，**Then** 网关返回超时错误给客户端

---

### User Story 4 - 管理员查看用量统计 (Priority: P3)

管理员通过 Admin Console 查看各个后端 LLM 服务器和客户端应用（App-Name）的用量统计，包括请求数、token 使用量等指标。

**Why this priority**: 用量统计帮助管理员监控系统使用情况和成本，但不影响网关的核心功能运行。

**Independent Test**: 可以通过模拟不同 App-Name 发送请求到不同后端服务器，验证 Admin Console 能够按维度（服务器 + App-Name）准确展示统计数据。

**Acceptance Scenarios**:

1. **Given** 客户端 A 通过网关调用后端服务器 1，**When** 管理员查看用量统计，**Then** 可以看到按"服务器 1 + App-A"维度的请求数和 token 使用量
2. **Given** 多个客户端调用多个后端服务器，**When** 管理员查看统计面板，**Then** 可以按时间范围（如今日、本周）筛选查看用量数据
3. **Given** 系统运行一段时间后，**When** 管理员导出用量报表，**Then** 能够获取详细的用量明细数据
4. **Given** 某个 App-Name 的用量异常高，**When** 管理员查看统计，**Then** 可以快速识别该应用的用量趋势

---

### Edge Cases

- 当后端 LLM 服务器不可用（网络故障或服务下线）时，网关如何处理请求？
- 当队列已满（达到最大队列长度）时，网关将移除队列中等待时间最长的请求，为新请求腾出空间（FIFO 驱逐策略）
- 当客户端请求的模型在所有配置的后端服务器中都不存在时，如何响应？
- 当网关重启时，队列中未处理的请求如何处理？
- 当多个后端服务器都支持同一模型时，网关如何选择路由目标？
- 当 Admin Console 配置更新时，正在处理的请求是否受影响？
- 当客户端提供的 `App-Name` 包含特殊字符或非法值时，如何处理？

## Requirements *(mandatory)*

### Functional Requirements

**代理与路由**
- **FR-001**: 网关必须接受 OpenAI 格式的 HTTP 请求，并保持请求和响应格式不变
- **FR-002**: 网关必须要求客户端在请求 header 中包含 `App-Name` 字段，用于标识客户端身份
- **FR-003**: 网关必须根据请求中的模型名称，自动选择配置的后端 LLM 服务器进行转发
- **FR-004**: 网关必须在转发请求时，使用配置的后端服务器 API Key 进行认证
- **FR-005**: 网关必须记录每次请求的 App-Name、目标服务器、请求时间、响应状态和 token 使用量

**限流与排队**
- **FR-006**: 网关必须支持按后端服务器维度配置 RPM（每分钟请求数）限流
- **FR-007**: 网关必须支持按后端服务器维度配置 TPM（每分钟 token 数）限流
- **FR-008**: 网关必须在请求超过 RPM 或 TPM 限额时，将请求加入队列而非直接拒绝
- **FR-009**: 网关必须在限流窗口重置后，按先进先出（FIFO）顺序处理队列中的请求
- **FR-010**: 网关必须为排队请求设置超时机制，超时后返回错误给客户端
- **FR-025**: 每个后端服务器的请求队列必须有最大长度限制，当队列满时采用 FIFO 驱逐策略（移除最旧的请求，接受新请求）

**配置管理（Admin Console）**
- **FR-011**: Admin Console 必须提供界面用于添加新的后端 LLM 服务器配置
- **FR-012**: 每个后端服务器配置必须包含：URL、API Key、可用模型列表、RPM、TPM
- **FR-013**: Admin Console 必须提供界面用于修改已有的后端服务器配置
- **FR-014**: Admin Console 必须提供界面用于删除后端服务器配置
- **FR-015**: Admin Console 必须验证配置输入的有效性（如 URL 格式、RPM/TPM 为正整数）
- **FR-016**: 配置变更必须动态加载，无需重启网关服务即可生效，确保正在处理的请求不受影响

**用量统计（Admin Console）**
- **FR-017**: Admin Console 必须展示按"后端服务器 + App-Name"维度的用量统计
- **FR-018**: 用量统计必须包含请求总数、成功/失败数、token 使用量
- **FR-019**: Admin Console 必须支持按时间范围筛选用量数据（如今日、本周、本月）
- **FR-020**: 用量数据必须持久化存储，网关重启后数据不丢失

**错误处理**
- **FR-021**: 网关必须在客户端请求缺少 `App-Name` header 时返回 400 错误
- **FR-022**: 网关必须在请求的模型不存在于任何后端服务器时返回 404 错误
- **FR-023**: 网关必须在后端服务器不可用时返回 502 错误
- **FR-024**: 网关必须在排队请求超时后返回 504 错误

### Key Entities

- **LLM 后端服务器配置**：表示一个后端 LLM API 服务器，包含 URL、API Key、支持的模型列表、RPM 和 TPM 限流配置
- **请求记录**：表示一次 API 调用，包含 App-Name、目标服务器、请求时间、响应状态、token 使用量等信息
- **队列项**：表示一个被限流而排队的请求，包含原始请求内容、入队时间、App-Name 等信息
- **用量统计**：聚合数据，按"后端服务器 + App-Name"维度统计请求数和 token 使用量

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 客户端通过网关调用 LLM API 的平均响应时间不超过直接调用后端服务器增加 50 毫秒
- **SC-002**: 网关能够支持至少 1000 个并发客户端请求而不出现请求失败
- **SC-003**: 当请求速率超过限流阈值时，95% 的排队请求能够在 30 秒内得到处理
- **SC-004**: Admin Console 配置变更在 5 秒内生效
- **SC-005**: 用量统计数据的准确率达到 99.9%（与实际请求记录对比）
- **SC-006**: 网关系统的可用性达到 99.5%（月度统计）
