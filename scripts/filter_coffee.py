#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
瑞幸咖啡官方接口数据抓取与智能筛选工具
- 接口地址: https://www.lkcoffee.com/portalcapi/resource/portal/product/list?queryParamsStr={"pageNum":1,"pageSize":100}
- 支持热量、咖啡因、分类、原料及关键词多维度筛选
"""

import sys
import json
import re
import argparse
import urllib.request
import urllib.error

API_URL = 'https://www.lkcoffee.com/portalcapi/resource/portal/product/list?queryParamsStr=%7B%22pageNum%22%3A1%2C%22pageSize%22%3A100%7D'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.lkcoffee.com/'
}

CATEGORY_MAP = {
    'lattes': '拿铁类',
    'americanos': '美式类',
    'cold-brew-drinks': '冷萃类',
    'special-drinks': '特调类',
    'light-milk-teas': '轻乳茶类',
    'iced-teas': '冰茶冰奶类',
    'fruit-vegetable-teas': '果蔬茶类',
    'non-coffee': '其他非咖啡类'
}

def fetch_products():
    """请求瑞幸官方接口拉取所有产品"""
    req = urllib.request.Request(API_URL, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8')
            data = json.loads(content)
            if data.get('code') != 1 or not data.get('content'):
                raise RuntimeError(f"接口返回异常: {data.get('msg', '未知错误')}")
            
            categories = data['content'].get('categoryList', [])
            all_products = []
            for cat in categories:
                if cat.get('categoryName') == '全部' and cat.get('productList'):
                    all_products = cat['productList']
                    break
            if not all_products and categories:
                seen_ids = set()
                for cat in categories:
                    for p in cat.get('productList', []):
                        if p.get('id') not in seen_ids:
                            seen_ids.add(p.get('id'))
                            all_products.append(p)
            return all_products
    except Exception as e:
        sys.stderr.write(f"请求接口失败: {e}\n")
        raise

def parse_product_info(raw_p):
    """从产品原始字段中抽取结构化信息（热量、咖啡因、原料、口感等）"""
    name = raw_p.get('productName', '').strip()
    category_slug = raw_p.get('categorySlug', '')
    category_name = CATEGORY_MAP.get(category_slug, category_slug)
    img_url = raw_p.get('mainImageUrl', '')
    tags = raw_p.get('attrTags', []) or []
    specs = raw_p.get('specSummary', []) or []
    remark = raw_p.get('remarkDesc', '') or ''
    full_text = f"{remark} {' '.join(specs)} {' '.join(tags)}"

    # 1. 提取热量 (kcal)
    calories = None
    cal_match = re.search(r'(?:热量|约)\s*([0-9\.]+)\s*(?:k?cal|大卡)', full_text, re.I)
    if cal_match:
        try:
            calories = float(cal_match.group(1))
        except ValueError:
            pass

    # 2. 提取咖啡因 (mg)
    caffeine = None
    caff_match = re.search(r'咖啡因\s*(?:含量)?\s*([0-9\.]+)\s*mg', full_text, re.I)
    if caff_match:
        try:
            caffeine = float(caff_match.group(1))
        except ValueError:
            pass

    # 3. 提取蛋白质 (g)
    protein = None
    protein_match = re.search(r'蛋白质\s*([0-9\.]+)\s*g', full_text, re.I)
    if protein_match:
        try:
            protein = float(protein_match.group(1))
        except ValueError:
            pass

    # 4. 提取主要原料与配方细节
    ingredients = []
    ing_match = re.search(r'主要原料[：:]\s*([^\n;；]+)', remark)
    if ing_match:
        raw_items = re.split(r'[,，、;；]', ing_match.group(1))
        ingredients = [i.strip() for i in raw_items if i.strip()]
    else:
        # 基于常见成分做词法提取
        potential_ingredients = []
        if '生椰' in full_text: potential_ingredients.append('冷榨生椰')
        if '黄油' in full_text: potential_ingredients.append('新西兰进口黄油')
        if '奶酪' in full_text or '干酪' in full_text: potential_ingredients.append('新西兰进口奶酪')
        if '丝绒风味厚奶' in full_text: potential_ingredients.append('丝绒风味厚奶')
        elif '厚奶' in full_text: potential_ingredients.append('风味厚奶')
        if '牛奶' in full_text or '纯牛奶' in full_text or '鲜牛奶' in full_text: potential_ingredients.append('优质纯牛奶')
        if '茉莉' in full_text: potential_ingredients.append('鲜萃茉莉花香茶汤')
        if '泰式红茶' in full_text or '泰茶' in full_text: potential_ingredients.append('泰式风味红茶')
        if '苹果' in full_text: potential_ingredients.append('NFC苹果汁/原汁')
        if '橙' in full_text: potential_ingredients.append('NFC鲜橙汁')
        if '柚' in full_text: potential_ingredients.append('红西柚果粒与原汁')
        if '黑巧克力' in full_text or '黑巧' in full_text: potential_ingredients.append('纯黑巧克力酱')
        if '芒果' in full_text: potential_ingredients.append('百色芒果果肉')
        if '抹茶' in full_text: potential_ingredients.append('千目级纯抹茶')
        if '瑰夏' in full_text: potential_ingredients.append('SCA80+瑰夏咖啡豆')
        
        if '浓缩咖啡' in full_text or '咖啡豆' in full_text or 'Espresso' in full_text or 'IIAC' in full_text or category_slug in ['americanos', 'lattes', 'cold-brew-drinks', 'special-drinks']:
            potential_ingredients.append('IIAC金奖阿拉比卡浓缩咖啡')

        ingredients = potential_ingredients if potential_ingredients else ['阿拉比卡咖啡豆萃取物']

    # 5. 风味与口感提取
    flavor = ""
    flavor_match = re.search(r'风味与口感[：:]\s*([^\n]+)', remark)
    if flavor_match:
        flavor = flavor_match.group(1).strip()
    else:
        # 从 remarkDesc 前两句提取
        sentences = [s.strip() for s in re.split(r'[\n。]', remark) if s.strip()]
        if sentences:
            flavor = sentences[0]

    # 6. 健康考量（控糖、控脂评估）
    health_notes = []
    if any('0脂' in t for t in tags) or (calories is not None and calories < 30):
        health_notes.append("【控脂极佳】0脂肪/极低脂，无油脂负担")
    elif '黄油' in full_text or '奶酪' in full_text or '厚奶' in full_text:
        health_notes.append("【高脂提醒】含黄油/奶酪/厚乳，饱和脂肪相对较高，血脂关注者建议偶饮或减量")
    
    if any(k in full_text for k in ['果汁', '果茶', '杨枝甘露', '苹果', '橙', '柚', '芒果']):
        health_notes.append("【含果糖】含天然果汁果糖，建议选择「不另外加糖」以降低血糖波动")
    elif calories is not None and calories < 50:
        health_notes.append("【控糖极佳】几乎无碳水与糖分，血糖友好")
    else:
        health_notes.append("【建议配置】下单推荐选「不另外加糖/少少甜」，控糖更稳妥")

    return {
        'id': raw_p.get('id'),
        'name': name,
        'category': category_name,
        'category_slug': category_slug,
        'image': img_url,
        'calories': calories,
        'caffeine': caffeine,
        'protein': protein,
        'tags': tags,
        'specs': specs,
        'ingredients': ingredients,
        'flavor': flavor,
        'health_notes': health_notes,
        'remark': remark
    }

def filter_products(products, args):
    """根据条件过滤产品"""
    filtered = []
    for p in products:
        # 1. 关键词筛选 (商品名 / 原料 / 描述 / 标签)
        if args.keyword:
            kw = args.keyword.lower()
            text_pool = f"{p['name']} {p['category']} {' '.join(p['tags'])} {' '.join(p['ingredients'])} {p['remark']}".lower()
            if kw not in text_pool:
                continue

        # 2. 分类筛选
        if args.category:
            cat_filter = args.category.lower()
            if cat_filter not in p['category_slug'].lower() and cat_filter not in p['category'].lower():
                continue

        # 3. 热量范围筛选
        if args.cal_target is not None:
            tol = args.cal_tol if args.cal_tol is not None else 50
            if p['calories'] is None or abs(p['calories'] - args.cal_target) > tol:
                continue
        else:
            if args.cal_min is not None and (p['calories'] is None or p['calories'] < args.cal_min):
                continue
            if args.cal_max is not None and (p['calories'] is None or p['calories'] > args.cal_max):
                continue

        # 4. 咖啡因范围筛选
        if args.caff_min is not None and (p['caffeine'] is None or p['caffeine'] < args.caff_min):
            continue
        if args.caff_max is not None and (p['caffeine'] is None or p['caffeine'] > args.caff_max):
            continue
        if args.high_caff and (p['caffeine'] is None or p['caffeine'] < 130):
            continue
        if args.low_caff and (p['caffeine'] is None or p['caffeine'] > 60):
            continue
        if args.no_caff and p['caffeine'] is not None and p['caffeine'] > 0:
            continue

        # 5. 健身/低糖/低脂标签筛选
        if args.fitness and not any('健身' in t or '0脂' in t for t in p['tags']):
            continue

        # 6. 排除原料/过敏原
        if args.exclude:
            ex_keywords = [k.strip() for k in args.exclude.split(',')]
            text_pool = f"{p['name']} {' '.join(p['ingredients'])} {p['remark']}"
            if any(k in text_pool for k in ex_keywords):
                continue

        filtered.append(p)

    # 排序处理
    if args.sort:
        if args.sort == 'caff_desc':
            filtered.sort(key=lambda x: (x['caffeine'] is not None, x['caffeine'] or 0), reverse=True)
        elif args.sort == 'caff_asc':
            filtered.sort(key=lambda x: (x['caffeine'] is not None, x['caffeine'] or 9999))
        elif args.sort == 'cal_asc':
            filtered.sort(key=lambda x: (x['calories'] is not None, x['calories'] or 9999))
        elif args.sort == 'cal_desc':
            filtered.sort(key=lambda x: (x['calories'] is not None, x['calories'] or 0), reverse=True)
        elif args.sort == 'cal_closest' and args.cal_target is not None:
            filtered.sort(key=lambda x: abs(x['calories'] - args.cal_target) if x['calories'] is not None else 9999)

    if args.limit and args.limit > 0:
        filtered = filtered[:args.limit]

    return filtered

def format_output(products, fmt='markdown'):
    """格式化输出"""
    if fmt == 'json':
        return json.dumps(products, ensure_ascii=False, indent=2)

    if not products:
        return "未找到完全匹配条件的瑞幸咖啡饮品，建议适度放宽热量或咖啡因区间重试。"

    lines = []
    lines.append(f"为您筛选出 **{len(products)}** 款合适的瑞幸饮品：\n")
    for i, p in enumerate(products, 1):
        cal_str = f"{p['calories']} kcal" if p['calories'] is not None else "官方暂未公示标称值"
        caff_str = f"{p['caffeine']} mg" if p['caffeine'] is not None else "未标称/低或无"
        protein_str = f" | 蛋白质: {p['protein']}g" if p['protein'] is not None else ""
        ing_str = "、".join(p['ingredients']) if p['ingredients'] else "阿拉比卡咖啡豆萃取物"
        tags_str = "、".join([f"`{t}`" for t in p['tags']]) if p['tags'] else "现磨咖啡"

        lines.append(f"### {i}. {p['name']}（{p['category']}）")
        if p['image']:
            lines.append(f"![]({p['image']})")
        lines.append(f"* **热量**: **{cal_str}**")
        lines.append(f"* **咖啡因**: **{caff_str}**{protein_str}")
        lines.append(f"* **主要原料**: {ing_str}")
        if p['flavor']:
            lines.append(f"* **风味口感**: {p['flavor']}")
        lines.append(f"* **特色标签**: {tags_str}")
        if p['health_notes']:
            lines.append(f"* **健康建议**: {'；'.join(p['health_notes'])}")
        lines.append("")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description='瑞幸咖啡智能筛选查询工具')
    parser.add_argument('--keyword', '-k', type=str, help='商品名称、风味或原料关键词')
    parser.add_argument('--category', '-c', type=str, help='商品品类(lattes/americanos/iced-teas/cold-brew-drinks等)')
    parser.add_argument('--cal-target', type=float, help='目标热量(例如 200)')
    parser.add_argument('--cal-tol', type=float, default=50, help='目标热量上下容差范围(默认 ±50 kcal)')
    parser.add_argument('--cal-min', type=float, help='最低热量(kcal)')
    parser.add_argument('--cal-max', type=float, help='最高热量(kcal)')
    parser.add_argument('--caff-min', type=float, help='最低咖啡因(mg)')
    parser.add_argument('--caff-max', type=float, help='最高咖啡因(mg)')
    parser.add_argument('--high-caff', action='store_true', help='高咖啡因(>=130mg)')
    parser.add_argument('--low-caff', action='store_true', help='低咖啡因(<=60mg)')
    parser.add_argument('--no-caff', action='store_true', help='无咖啡因')
    parser.add_argument('--fitness', action='store_true', help='仅看健身/低脂友好')
    parser.add_argument('--exclude', type=str, help='排除的原料关键词(英文逗号分隔)')
    parser.add_argument('--sort', type=str, choices=['caff_desc', 'caff_asc', 'cal_asc', 'cal_desc', 'cal_closest'], help='排序方式')
    parser.add_argument('--limit', type=int, default=10, help='最大返回数量')
    parser.add_argument('--format', type=str, default='markdown', choices=['markdown', 'json'], help='输出格式')

    args = parser.parse_args()

    raw_products = fetch_products()
    parsed_products = [parse_product_info(p) for p in raw_products]
    filtered = filter_products(parsed_products, args)
    output = format_output(filtered, args.format)
    print(output)

if __name__ == '__main__':
    main()
