---
name: luckin-coffee-advisor
version: 1.0.0
display_name: 瑞幸咖啡智能选咖助手
display_name_en: Luckin Coffee Advisor
description: 瑞幸咖啡全品类饮品查询与智能选咖助手。当用户询问瑞幸咖啡推荐、按热量（大卡/低卡）、咖啡因（高咖啡因/低咖啡因/提神）、品类（拿铁/美式/果茶/轻乳茶等）、原料（生椰/燕麦/牛乳）或健康控糖控脂诉求筛选饮品时调用。实时请求瑞幸官方接口，输出包含高清图片、热量、咖啡因、主要原料与健康饮用建议的结构化卡片。
description_zh: 瑞幸咖啡全品类饮品查询与智能选咖助手。当用户询问瑞幸咖啡推荐、按热量（大卡/低卡）、咖啡因（高咖啡因/低咖啡因/提神）、品类（拿铁/美式/果茶/轻乳茶等）、原料（生椰/燕麦/牛乳）或健康控糖控脂诉求筛选饮品时调用。实时请求瑞幸官方接口，输出包含高清图片、热量、咖啡因、主要原料与健康饮用建议的结构化卡片。
description_en: An intelligent beverage recommendation assistant for Luckin Coffee. It dynamically fetches official products, filters by calories, caffeine, categories, ingredients, and dietary preferences, and presents structured cards with images, nutrition facts, and recipes.
agent_created: true
---

# 瑞幸咖啡智能选咖助手 (Luckin Coffee Advisor)

## 概述

本技能用于为用户精准筛选、推荐瑞幸咖啡官方在售饮品。通过实时请求瑞幸官方开放接口，深度解析饮品的热量（kcal）、咖啡因含量（mg）、蛋白质、主要原料、风味描述及标签，并输出富媒体图文卡片。

---

## 核心工作流程

```
用户输入筛选需求（如：200大卡左右高咖啡因 / 低卡控脂 / 生椰类 / 提神）
       │
       ▼
执行内置筛选脚本 `scripts/filter_coffee.py`
       │
       ▼
解析官方接口最新 100 条全品类数据（categoryList / productList）
       │
       ▼
结合用户健康与口味偏好做排序与多维度过滤
       │
       ▼
输出结构化图文推荐卡片（图片 + 热量 + 咖啡因 + 原料 + 控糖控脂提示）
```

---

## 脚本调用方式

技能内置了高效的筛选脚本 `scripts/filter_coffee.py`，支持直接通过 Python 命令行调用：

```bash
# 基础示例：筛选 200 大卡左右、高咖啡因的咖啡
python scripts/filter_coffee.py --cal-target 200 --cal-tol 50 --high-caff --sort cal_closest

# 示例 2：严格低卡 (低于 100 kcal) 且提神 (咖啡因 >= 150mg)
python scripts/filter_coffee.py --cal-max 100 --caff-min 150 --sort caff_desc

# 示例 3：果味或果茶关键词筛选
python scripts/filter_coffee.py --keyword 苹果 --sort cal_asc

# 示例 4：排除乳制品/牛奶（乳糖不耐或控脂）
python scripts/filter_coffee.py --exclude 乳制品,牛奶,厚奶,黄油 --sort caff_desc
```

### 常用参数说明

| 参数 | 类型 | 说明 |
|---|---|---|
| `--cal-target` | float | 目标热量（如 `200`） |
| `--cal-tol` | float | 容差范围（默认 `±50 kcal`） |
| `--cal-min` / `--cal-max` | float | 最低 / 最高热量区间 |
| `--caff-min` / `--caff-max`| float | 最低 / 最高咖啡因区间（mg） |
| `--high-caff` | flag | 高咖啡因（`>=130mg`） |
| `--low-caff` | flag | 低咖啡因（`<=60mg`） |
| `--category` | str | 品类（`lattes`, `americanos`, `cold-brew-drinks`, `iced-teas`, `light-milk-teas` 等） |
| `--keyword` | str | 关键词检索（如 `生椰`、`茉莉`、`美式`） |
| `--fitness` | flag | 仅筛选含 `健身友好` 或 `0脂` 标签的饮品 |
| `--exclude` | str | 排除特定成分/过敏原（逗号分隔） |
| `--sort` | str | 排序：`cal_closest`、`caff_desc`、`cal_asc` 等 |
| `--limit` | int | 最大展示数量（默认 10） |

---

## 呈现与输出规范

向用户汇报筛选结果时，必须包含以下核心信息维度，并以 Markdown 渲染：

1. **商品高清缩略图**：使用 `![]({mainImageUrl})` 语法内嵌渲染；
2. **营养关键数值**：
   - **热量**：标称大卡（`xxx kcal`）；
   - **咖啡因**：标称毫克（`xxx mg`）；
3. **配方与口感**：
   - **主要原料**：罗列核心基底（如：冷榨生椰、IIAC金奖浓缩咖啡、鲜萃茉莉花香、新西兰进口黄油等）；
   - **风味口感**：简短口感风味总结；
4. **健康与定制建议**（特别针对控糖、控脂人群）：
   - 标注是否含动物脂肪/饱和脂肪（如黄油、厚乳、奶酪）；
   - 建议下单时的甜度选项（如「推荐选择不另外加糖」）。

---

## 典型场景参考

* **场景 A：200大卡左右的高咖啡因咖啡**
  * 首推：**小黄油美式**（173 kcal，咖啡因 212 mg，黄油坚果香与高提神）；
  * 次推：**小黄油拿铁**（250 kcal，咖啡因 171.9 mg）；
  * 备选：**生椰拿铁**（179 kcal，咖啡因 118.4 mg）；
* **场景 B：减脂健身 / 极低热量高提神**
  * 首推：**加浓美式**（14 kcal，咖啡因 198.9 mg，0糖0脂）；
  * 次推：**标准美式**（11 kcal，咖啡因 164.3 mg，健身首选）；
  * 果咖：**轻椰茉莉拿铁**（120 kcal，咖啡因 179.1 mg，健身友好）。
