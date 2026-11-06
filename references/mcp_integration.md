# 瑞幸官方 My-Coffee MCP 服务集成规范

## 1. MCP 服务概述

瑞幸官方开放平台（[open.lkcoffee.com](https://open.lkcoffee.com/)）提供了标准 **Model Context Protocol (MCP)** 服务，使 AI Agent 能够通过标准化工具接口执行门店查询、饮品属性定制与代下单操作。

- **官方协议类型**: `streamablehttp` (SSE / 远程 HTTP 模式)
- **端点 URL**: `https://gwmcp.lkcoffee.com/order/user/mcp`
- **鉴权方式**: `Bearer <LUCKIN_MCP_TOKEN>`
- **Token 获取途径**: 前往 [open.lkcoffee.com](https://open.lkcoffee.com/) 登录个人瑞幸账号获取（Token 有效期通常保留 30 天）。

---

## 2. 客户端配置规范 (mcp.json)

在 WorkBuddy 或其他支持 MCP 的客户端配置文件（如 `~/.workbuddy/mcp.json`）中添加如下配置：

```json
{
  "mcpServers": {
    "my-coffee": {
      "type": "streamablehttp",
      "url": "https://gwmcp.lkcoffee.com/order/user/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_LUCKIN_MCP_TOKEN"
      }
    }
  }
}
```

> **注意**：配置保存后，需在客户端连接器管理中确认并启用该 MCP 连接。

---

## 3. 核心工具清单与契约说明

`my-coffee` MCP 提供以下 8 个标准工具：

### 3.1 门店相关

#### `queryShopList`
- **功能**: 查询附近可用的瑞幸自提门店列表。
- **入参**:
  - `longitude` (number, 必填): 经度（如 `116.4074`）
  - `latitude` (number, 必填): 纬度（如 `39.9042`）
  - `deptName` (string, 可选): 门店名称关键词筛选（如 `"海西金谷广场"`）
- **出参**:
  - `deptId` (number): 门店唯一标识 ID
  - `deptName` (string): 门店名称
  - `address` (string): 门店地址
  - `distance` (number): 距离（米）
  - `status` (number): 营业状态（1=营业中）

---

### 3.2 商品与规格定制

#### `searchProductForMcp`
- **功能**: 基于自然语言搜索门店在售商品。
- **入参**:
  - `deptId` (number, 必填): 门店 ID
  - `keyword` (string, 必填): 搜索词（如 `"生椰拿铁"`, `"橙C美式"`）
- **出参**: 匹配的商品列表及初始 SKU 规格。

#### `queryProductDetailInfo`
- **功能**: 获取指定商品的详细定制选项（温度、杯型、甜度、奶基底等）。
- **入参**:
  - `deptId` (number, 必填): 门店 ID
  - `productId` (number, 必填): 商品 ID
- **出参**: 可选规格列表及各选项 code。

#### `switchProduct`
- **功能**: 切换并锁定商品的具体属性（如：大杯、冰、不另外加糖）。
- **入参**:
  - `deptId` (number, 必填): 门店 ID
  - `productId` (number, 必填): 商品 ID
  - `specCodes` (array): 选中的规格代码集合
  - `operation` (number): 操作类型（通常传 `3`）
- **出参**: 锁定后的具体 SKU ID 与单价。

---

### 3.3 订单与支付流程

#### `previewOrder`
- **功能**: 预览订单计算，自动匹配账户可用优惠券与咖啡库券，获取最终待支付价格。
- **入参**:
  - `deptId` (number, 必填): 门店 ID
  - `items` (array, 必填): 包含商品 SKU ID、数量等对象的列表
- **出参**:
  - `originPrice` (number): 原价
  - `discountPrice` (number): 优惠金额
  - `payPrice` (number): 最终实付金额
  - `couponCodeList` (array): 匹配到的优惠券列表

#### `createOrder`
- **功能**: 正式创建待支付订单并生成支付凭证。
- **入参**:
  - `deptId` (number, 必填): 门店 ID
  - `items` (array, 必填): 下单商品项
  - `couponCodeList` (array, 必填): 从 `previewOrder` 继承的优惠券列表
- **出参**:
  - `orderNo` (string): 订单号
  - `payOrderQrCodeUrl` (string): 微信支付二维码 URL
  - `payUrl` (string): 支付跳转链接

#### `queryOrderDetailInfo`
- **功能**: 查询订单支付状态与取餐码。
- **入参**:
  - `orderNo` (string, 必填): 订单编号
- **出参**:
  - `orderStatus` (string): 状态（`WAIT_PAY` 待支付, `MAKING` 制作中, `WAIT_TAKE` 待取餐, `COMPLETE` 已完成）
  - `takeCode` (string): 取餐码（如 `"A108"`，仅在支付完成后返回）
  - `shopName` (string): 门店名
  - `estimatedTime` (string): 预计完成时间

#### `cancelOrder`
- **功能**: 取消未支付或异常订单。
- **入参**:
  - `orderNo` (string, 必填): 订单编号
- **出参**: 取消成功与否状态。

---

## 4. 业务约束与安全防护原则

1. **外送拦截约束**：
   - 瑞幸官方 MCP **仅支持「到店自提」**，暂不支持配送/外卖。
   - 当检测到用户提及“送货”、“外卖”、“配送到家”等意图时，必须礼貌澄清：“瑞幸官方接口目前仅支持到店自取服务，请问是否自提到店取餐？”并征得用户同意。
2. **两阶段明确确认原则（防误扣款）**：
   - **选店确认**：展示附近的门店（名称、距离、营业状态），由用户明确指定后方可保存 `deptId`；
   - **下单前确认**：调用 `previewOrder` 后，必须向用户清晰列出：
     - **自提门店**：门市名称与地址
     - **商品明细**：商品名、定制规格（杯型/温度/甜度/加料）、数量
     - **金额明细**：原价、优惠减免、实付应付金额
     - **支付方式**：微信扫码支付
     - **明确询问**：“确认以此规格为您发起代下单吗？”待用户回复同意后，方可执行 `createOrder`。
3. **敏感凭证防泄漏**：
   - 微信支付链接及二维码必须以安全链接或直接图片形式给出，禁止泄露用户的完整鉴权 Token。
