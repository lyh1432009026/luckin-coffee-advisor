# 瑞幸咖啡智能选咖助手 (Luckin Coffee Advisor)

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/lyh1432009026/luckin-coffee-advisor)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个专为 AI Agent（WorkBuddy / Claude 等）打造的瑞幸咖啡全品类饮品查询与智能选咖技能（Skill）。

通过实时请求瑞幸咖啡官方开放接口，深度解析全量在售饮品的热量（kcal）、咖啡因（mg）、主要原料、风味口感及特色标签，并根据用户的健康与口味需求输出高保真图文推荐卡片。

---

## 🌟 核心特性

- **官方实时数据**：直连官方数据接口，自动拉取拿铁、美式、冷萃、轻乳茶、果蔬茶等全部在售品类。
- **多维度精准筛选**：
  - **热量区间**：支持目标大卡及容差筛选（如 `200 大卡左右`、`100 大卡以内低卡`）。
  - **咖啡因梯度**：支持高咖啡因（提神）、中低咖啡因或无咖啡因筛选。
  - **健康与慢病考量**：集成血糖与血脂友好评估逻辑，提示饱和脂肪风险与建议选糖等级（如「不另外加糖」）。
  - **成分与过敏原**：支持按原料（生椰/燕麦/纯牛奶）或过敏原进行包含/排除过滤。
- **富媒体输出**：提供高清商品图、标称营养指标、原料清单、口感风味与健康建议的完整卡片展示。

---

## 📂 项目结构

```text
luckin-coffee-advisor/
├── SKILL.md                  # 技能定义与元数据配置（含版本号、双语说明、触发流转）
├── scripts/
│   └── filter_coffee.py      # 核心自动化拉取、正则解析与智能过滤脚本
├── references/
│   └── api_reference.md      # 官方接口逆向契约与数据模型说明文档
├── .gitignore
└── README.md
```

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

### 常用参数说明

| 参数 | 类型 | 默认值 | 作用说明 |
|---|---|---|---|
| `--cal-target` | float | - | 目标热量（大卡） |
| `--cal-tol` | float | 50 | 目标热量容差范围（± kcal） |
| `--cal-min` / `--cal-max` | float | - | 热量下限 / 上限 |
| `--caff-min` / `--caff-max`| float | - | 咖啡因下限 / 上限（mg） |
| `--high-caff` | flag | - | 高咖啡因（≥130mg） |
| `--low-caff` | flag | - | 低咖啡因（≤60mg） |
| `--keyword` | str | - | 原料、风味或商品名关键词 |
| `--category` | str | - | 品类标识（lattes/americanos/iced-teas 等） |
| `--fitness` | flag | - | 仅看含「健身友好」或「0脂」标签 |
| `--exclude` | str | - | 排除原料/过敏原（逗号分隔） |
| `--format` | str | markdown | 输出格式（`markdown` 或 `json`） |

---

## 🤖 在 AI Agent (WorkBuddy) 中使用

将本技能目录放置在 `~/.workbuddy/skills/luckin-coffee-advisor/`，即可在会话中直接通过自然语言触发：

- *“调用技能帮我看看 200 大卡左右的高咖啡因咖啡”*
- *“帮我挑一杯 100 大卡以内、适合健身后喝的提神咖啡”*
- *“看下瑞幸有哪些低糖低脂的果咖”*
- *“我不耐受乳糖，推荐几款高咖啡因的美式或植物基饮品”*

---

## 📄 开源许可

本项目遵循 [MIT](LICENSE) 协议开源。
