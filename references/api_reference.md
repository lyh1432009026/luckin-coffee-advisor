# 瑞幸咖啡官方接口与数据模型规范

## 1. 接口概览

- **请求端点**: `https://www.lkcoffee.com/portalcapi/resource/portal/product/list`
- **请求方式**: `GET`
- **查询参数**:
  - `queryParamsStr`: JSON 字符串经 URL 编码后的对象，例如：
    `%7B%22pageNum%22%3A1%2C%22pageSize%22%3A100%7D`
    对应 JSON：`{"pageNum": 1, "pageSize": 100}`

## 2. 响应报文结构

```json
{
  "busiCode": "BASE000",
  "code": 1,
  "msg": "成功",
  "status": "SUCCESS",
  "content": {
    "total": 29,
    "pageNum": 1,
    "pageSize": 100,
    "categoryList": [
      {
        "id": 0,
        "categoryName": "全部",
        "slug": "",
        "productList": [
          {
            "id": 1,
            "productName": "生椰拿铁",
            "categorySlug": "lattes",
            "mainImageUrl": "https://img.luckincoffeecdn.com/...",
            "attrTags": ["全球卖出20亿杯"],
            "specSummary": ["咖啡因118.4mg", "热量179kcal"],
            "remarkDesc": "瑞幸首创* · 全球累计销量超20亿杯* ... 热量179kcal，咖啡因118.4mg...",
            "slug": "coconut-latte"
          }
        ]
      }
    ]
  }
}
```

## 3. 品类分类映射表 (categorySlug)

| slug | 分类名称 | 典型产品 |
|---|---|---|
| `lattes` | 拿铁类 | 生椰拿铁、茉莉花香拿铁、拿铁、小黄油拿铁、轻椰茉莉拿铁、丝绒拿铁等 |
| `americanos` | 美式类 | 标准美式、加浓美式、橙C美式、小黄油美式、苹果C美式、柚C美式等 |
| `cold-brew-drinks` | 冷萃类 | 瑰夏之梦、瑰夏白冷萃 |
| `light-milk-teas` | 轻乳茶类 | 鲜萃轻轻茉莉 |
| `fruit-vegetable-teas` | 果蔬茶类 | 羽衣轻体果蔬茶 |
| `iced-teas` | 冰茶冰奶类 | 苹果C冰茶、葡萄冰茶、Hello苹果茉莉等 |
| `non-coffee` | 其他非咖啡类 | 生椰杨枝甘露、经典泰奶、咸法酪泰奶等 |

## 4. 营养学与原料解析规则

1. **热量 (Calories)**:
   - 正则表达式: `r'(?:热量|约)\s*([0-9\.]+)\s*(?:k?cal|大卡)'`
   - 单位：大卡 (kcal)
2. **咖啡因 (Caffeine)**:
   - 正则表达式: `r'咖啡因\s*(?:含量)?\s*([0-9\.]+)\s*mg'`
   - 单位：毫克 (mg)
3. **主要原料**:
   - 优先提取 `remarkDesc` 中 `主要原料[：:]` 之后的内容；次选基于浓缩咖啡、鲜牛奶、冷榨生椰、进口黄油、果原汁等关键词提炼。
