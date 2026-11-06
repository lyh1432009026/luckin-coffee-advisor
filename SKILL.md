---
name: luckin-coffee-advisor
version: 1.1.0
display_name: 瑞幸咖啡智能选咖与下单助手
display_name_en: Luckin Coffee Advisor & Order Assistant
description: 瑞幸咖啡全品类饮品查询、智能选咖、附近门店定位与自提代下单助手。支持按热量、咖啡因、原料和健康偏好筛选咖啡，并可联动瑞幸官方 my-coffee MCP 服务实现附近门店查询、规格自提定制、订单预览与代下单。
description_zh: 瑞幸咖啡全品类饮品查询、智能选咖、附近门店定位与自提代下单助手。支持按热量、咖啡因、原料和健康偏好筛选咖啡，并可联动瑞幸官方 my-coffee MCP 服务实现附近门店查询、规格自提定制、订单预览与代下单。
description_en: An intelligent beverage recommendation and ordering assistant for Luckin Coffee. It dynamically fetches official products, filters by nutrition, and integrates with the official my-coffee MCP server for store locator, customized SKU selection, order preview, and in-store pickup ordering.
agent_created: true
---

# 瑞幸咖啡智能选咖与代下单助手 (Luckin Coffee Advisor & Order Assistant)

## 概述

本技能为用户提供从**智能选品**到**门店查询**及**到店自提代下单**的一站式服务：
1. **智能选品引擎**：实时直连官方接口，深度解析饮品热量（kcal）、咖啡因含量（mg）、主要原料及健康控糖控脂考量；
2. **MCP 代下单引擎**：联动瑞幸官方提供的 `my-coffee` MCP 服务（端点 `https://gwmcp.lkcoffee.com/order/user/mcp`），提供附近门店检索、商品规格属性定制、订单预览算价、生成支付二维码及取餐码查询全流程。

---

## 核心工作流与操作契约

```
用户输入需求（如：“帮我查附近的瑞幸并点一杯200大卡左右高咖啡因的咖啡”）
       │
       ▼
【第 1 步：查店与选店】
调用 `queryShopList`（传入经纬度或门店地名）
展示附近门店列表 ──> 等待用户明确指定确认自提门店，锁定 `deptId`
       │
       ▼
【第 2 步：智能选品与规格定制】
结合本地 `filter_coffee.py` 筛选低卡/高咖啡因/原料偏好饮品
调用 `searchProductForMcp` 搜索对应商品
调用 `queryProductDetailInfo` 与 `switchProduct`（operation: 3）切换并锁定温度、杯型、糖度
       │
       ▼
【第 3 步：订单预览与实付核算】
调用 `previewOrder`，传入 `deptId` 与定制商品项
系统自动匹配账户可用优惠券与咖啡库券，获取最终实付 `payPrice`
       │
       ▼
【第 4 步：关键节点二次确认】（强制阻断点，严禁跳步！）
向用户展示清晰的订单确认面板：
• 自提门店：[门店名]（[详细地址]）
• 商品规格：[商品名] [大杯/冰/不另外加糖等] x 数量
• 金额明细：原价 ¥XX，优惠券减免 ¥XX，实际应付：¥XX
询问：“确认以此规格为您生成代下单支付二维码吗？”
       │
       ▼（用户明确同意）
【第 5 步：创建订单与支付】
调用 `createOrder`，原样传递 `previewOrder` 返回的 `couponCodeList`
向用户输出微信支付二维码图片与支付跳转链接
       │
       ▼（用户完成付款）
【第 6 步：取餐码同步】
调用 `queryOrderDetailInfo` 查询订单最新状态，返回取餐码（如 A108）与预计完成时间
```

---

## 严格业务约束与安全防护守则

1. **外送拦截约束**：
   - 瑞幸官方 MCP **仅支持到店自取，不支持外送配送**；
   - 用户提到“送外卖”、“送到家”时，须友好提示：“目前瑞幸官方开放接口仅支持到店自取，请问您同意前往门店自提吗？”
2. **两阶段防误确认**：
   - 选店必须经用户确认，不可擅自指定任意远距离门店；
   - 支付前必须呈现优惠后实付总价与退改规则，获得用户许可后方可触发 `createOrder`；
3. **MCP 服务依赖与降级**：
   - 查店与下单功能需要客户端加载了瑞幸官方的 `my-coffee` MCP 服务；
   - 若当前会话尚未配置 `my-coffee` MCP，引导用户在 `~/.workbuddy/mcp.json` 中配置端点，或前往 [open.lkcoffee.com](https://open.lkcoffee.com/) 获取授权 Token。

---

## 瑞幸官方 `my-coffee` MCP 工具对照表

| 工具名称 | 触发时机 | 核心入参 | 关键产出 |
|---|---|---|---|
| `queryShopList` | 门店定位与检索 | `longitude`, `latitude`, `deptName` | 附近门店列表、`deptId`、营业状态 |
| `searchProductForMcp` | 搜索商品基础信息 | `deptId`, `keyword` | 商品基础 SKU 与 ID |
| `queryProductDetailInfo` | 查看可选温度/杯型/糖度 | `deptId`, `productId` | 可定制属性集合与规格代码 |
| `switchProduct` | 切换锁定具体饮品属性 | `deptId`, `productId`, `specCodes`, `operation: 3` | 锁定后的最终 SKU ID |
| `previewOrder` | 下单前试算价格与优惠 | `deptId`, `items` | 原价、优惠减免、实付应付、优惠券列表 |
| `createOrder` | 正式创建订单 | `deptId`, `items`, `couponCodeList` | 订单号 `orderNo`、支付二维码 `payOrderQrCodeUrl` |
| `queryOrderDetailInfo` | 查询支付状态与取餐码 | `orderNo` | 订单状态、取餐码 `takeCode`、预计自提时间 |
| `cancelOrder` | 用户取消未付款订单 | `orderNo` | 取消成功标志 |

---

## 客户端 MCP 配置指南 (`~/.workbuddy/mcp.json`)

当用户需要在 WorkBuddy 中启用查店与代下单时，可在 `~/.workbuddy/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "my-coffee": {
      "type": "streamablehttp",
      "url": "https://gwmcp.lkcoffee.com/order/user/mcp",
      "headers": {
        "Authorization": "Bearer <YOUR_LUCKIN_MCP_TOKEN>"
      }
    }
  }
}
```

*注：登录凭证可从瑞幸 AI 开放平台官网（[open.lkcoffee.com](https://open.lkcoffee.com/)）登录个人瑞幸账户后一键生成获取。*

---

## 典型场景交互示例

### 场景一：查询附近门店
* **用户**：“帮我查一下海西金谷广场附近的瑞幸门店”
* **AI**：调用 `queryShopList(deptName="海西金谷广场")`，返回匹配的 3-5 家门店，附上地址与距离，并询问用户指定哪一家自提。

### 场景二：智能选咖 + 一句话自提代下单
* **用户**：“我在海西金谷广场店，帮我点一杯 200 大卡左右高提神的咖啡”
* **AI**：
  1. 调用 `filter_coffee.py` 筛选出最适合的「小黄油美式」（173 kcal，咖啡因 212 mg）；
  2. 调用 `searchProductForMcp` 匹配小黄油美式并用 `switchProduct` 设置为大杯、冰、不另外加糖；
  3. 调用 `previewOrder` 得到优惠计算：原价 ¥21.00，匹配 5 元优惠券，实付 ¥16.00；
  4. 向用户输出确认卡片：“海西金谷广场店，小黄油美式（大杯/冰/不另外加糖），原价 ¥21，优惠后实付 ¥16，是否确认下单？”；
  5. 用户回复“确认”后，调用 `createOrder` 展示微信支付二维码；
  6. 用户扫码付款后，调用 `queryOrderDetailInfo` 告知：“支付成功！您的取餐码为 A102，预计 5 分钟后可取。”
