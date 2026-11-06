# 瑞幸咖啡智能选咖与代下单助手 (Luckin Coffee Advisor & Order Assistant)

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/lyh1432009026/luckin-coffee-advisor)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个专为 AI Agent（WorkBuddy / Claude / Cursor 等）打造的瑞幸咖啡全品类饮品查询、营养筛选、门店定位与到店自提代下单技能（Skill）。

直连官方数据接口，深度解析全量在售饮品的热量（kcal）、咖啡因（mg）、主要原料、风味口感及慢病/健康指标；并联动瑞幸官方提供的 **`my-coffee` MCP 服务**，无缝实现附近门店定位、细分属性规格切换、订单自动核券与安全代下单。

---

## 🌟 核心特性

- **官方实时商品库**：直连官方数据接口，自动拉取拿铁、美式、冷萃、轻乳茶、果蔬茶等全部在售品类。
- **多维度营养智能筛选**：
  - **热量区间**：支持目标大卡及容差筛选（如 `200 大卡左右`、`100 大卡以内低卡`）。
  - **咖啡因梯度**：支持高咖啡因（提神）、中低咖啡因或无咖啡因筛选。
  - **健康与控糖控脂**：集成血糖与血脂友好评估逻辑，提示饱和脂肪风险与建议选糖等级（如「不另外加糖」）。
  - **成分与过敏原**：支持按原料（生椰/燕麦/纯牛奶）或过敏原进行包含/排除过滤。
- **门店查询与定位（依赖 my-coffee MCP）**：
  - 支持按经纬度或地名关键词检索附近的瑞幸门店，展示营业状态、详细地址与距离。
- **自提代下单闭环（依赖 my-coffee MCP）**：
  - 支持按自然语言切换温度、甜度、杯型及奶基底。
  - 下单前自动试算最优优惠券/咖啡库券，明示实付金额并执行二次确认。
  - 生成微信支付二维码，用户支付后自动查询并同步取餐码（如 A108）。
- **安全与业务边界**：
  - **仅限到店自提**：严格拦截外卖配送请求，提供合规提示。
  - **资金安全阻断**：支付环节交由用户微信扫码，绝不私自越权扣款。

---

## 📂 项目结构

```text
luckin-coffee-advisor/
├── SKILL.md                  # 技能定义与元数据配置（含版本号、双语说明、触发流转及约束）
├── scripts/
│   └── filter_coffee.py      # 核心自动化拉取、正则解析与智能过滤脚本
├── references/
│   ├── api_reference.md      # 官方商品接口逆向契约与数据模型说明文档
│   └── mcp_integration.md    # 瑞幸官方 my-coffee MCP 服务集成指南与工具契约
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🔌 瑞幸官方 `my-coffee` MCP 配置指南

若需启用门店定位与代下单功能，请在 WorkBuddy 或支持 MCP 的客户端配置中（例如 `~/.workbuddy/mcp.json`）添加瑞幸官方 MCP 服务端点：

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

> **获取 Token**：访问瑞幸 AI 开放平台官网 [open.lkcoffee.com](https://open.lkcoffee.com/)，使用手机号验证码登录后即可一键获取个人专属 MCP Token（有效期通常保留 30 天）。

---

## 🚀 独立运行与命令行测试

除了在 AI Agent 中直接调用外，核心脚本 `scripts/filter_coffee.py` 也支持独立在终端中运行：

```bash
# 1. 筛选 200 大卡左右的高咖啡因咖啡
python scripts/filter_coffee.py --cal-target 200 --cal-tol 50 --high-caff --sort cal_closest

# 2. 严格低热量 (<=100 kcal) 且高提神 (>=150mg 咖啡因)
python scripts/filter_coffee.py --cal-max 100 --caff-min 150 --sort caff_desc

# 3. 关键词搜索（如：生椰）
python scripts/filter_coffee.py --keyword 生椰

# 4. 排除特定原料（如乳糖不耐受人群排除乳制品）
python scripts/filter_coffee.py --exclude 乳制品,牛奶,厚奶,黄油 --sort caff_desc

# 5. 输出结构化 JSON
python scripts/filter_coffee.py --cal-target 200 --format json
```

---

## 🤖 在 AI Agent (WorkBuddy) 中使用

将本技能目录放置在 `~/.workbuddy/skills/luckin-coffee-advisor/`，即可在会话中直接通过自然语言触发：

- *“调用技能帮我看看 200 大卡左右的高咖啡因咖啡”*
- *“帮我查一下海西金谷广场附近的瑞幸门店”*
- *“在附近最近的门店帮我点一杯生椰拿铁，大杯，冰，不另外加糖”*
- *“帮我下一单加浓美式自提，查下应付多少钱并出付款码”*
- *“查一下我刚才那笔订单的取餐码是多少”*

---

## 📄 开源许可

本项目遵循 [MIT](LICENSE) 协议开源。
