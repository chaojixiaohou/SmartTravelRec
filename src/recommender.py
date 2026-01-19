def calculate_match_score(item, intent):
    """
    计算单条数据的匹配分（满分 10 分）
    """
    score = 0
    
    # 1. 地域匹配 (3分)
    # 如果 AI 没解析出地区，或者地区一致，都得分
    if not intent["region"] or intent["region"] in item["region"]:
        score += 3
        
    # 2. 价格匹配 (2分)
    price = item["price"]
    user_price = intent["price"]
    
    if user_price == "免费" and price == 0:
        score += 2
    elif user_price == "性价比高" and 0 < price <= 100:
        score += 2
    elif user_price == "高价" and price > 200:
        score += 2
    elif user_price == "不限":
        score += 1
        
    # 3. 标签匹配 (5分)
    # 计算用户想要的标签和景点标签的交集个数
    user_tags = set(intent["tags"])
    item_tags = set(item["tags"])
    matched_tags = user_tags & item_tags
    
    # 每个匹配的标签得 1.5 分，最高 5 分
    score += min(len(matched_tags) * 1.5, 5)
    
    return score

def personalized_recommend(data, intent, top_n=5):
    """
    推荐入口函数
    """
    category = intent.get("type", "scenic_spots")
    
    # 兜底防止分类不存在
    if category not in data:
        category = "scenic_spots"
        
    items = data.get(category, [])
    
    # 判断用户是否提出了具体要求（如果全空，说明用户只是随便看看，就不用过滤）
    has_constraints = any([intent["region"], intent["price"], intent["tags"]])
    
    results = []
    for item in items:
        match_score = calculate_match_score(item, intent)
        
        # --- 【核心修复点】 ---
        # 如果用户有具体要求，且匹配分为 0，直接跳过，绝不推荐
        if has_constraints and match_score == 0:
            continue
        # --------------------

        final_score = match_score * 0.7 + item["score"] * 0.3
        
        item["match_score"] = round(match_score, 1)
        item["final_score"] = round(final_score, 1)
        results.append(item)
        
    # 按综合得分降序排列
    results.sort(key=lambda x: x["final_score"], reverse=True)
    
    return results[:top_n]