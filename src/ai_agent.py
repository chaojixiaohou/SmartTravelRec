import requests
import json
import os
import time

def load_config():
    """加载配置文件"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"无法加载 config.json: {e}")
        return {}

def ai_intent_analysis(user_input):
    """
    方案 A：调用阿里云通义千问 (Qwen) 解析意图
    """
    config = load_config()
    api_key = config.get("ali_api", {}).get("api_key")

    if not api_key:
        print("❌ 错误：未配置阿里云 API Key")
        return None

    # 阿里云百炼兼容 OpenAI 协议，用 requests 调用非常简单
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    你是一个文旅需求提取助手。请分析用户输入，提取以下字段并严格按 JSON 格式返回：
    1. region: 具体的旗/县/区名（如"集宁区", "察右后旗"等）。
    2. type: 只能从 ["scenic_spots", "food", "homestay"] 中选一个。
    3. price: 价格偏好（"性价比高", "免费", "高价", "不限"）。
    4. tags: 提取的关键词列表（如 "火山", "草原", "亲子"）。
    
    用户输入："{user_input}"
    
    要求：只返回纯 JSON 字符串，不要Markdown格式，不要解释。
    """

    payload = {
        "model": "qwen-turbo",  # 选用 qwen-turbo，速度快且免费额度高
        "messages": [
            {"role": "system", "content": "你是专业的JSON数据提取助手。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }

    try:
        # 发送请求
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code != 200:
            print(f"⚠️ 阿里云报错: {response.text}")
            return None

        result = response.json()
        # 提取内容
        content = result['choices'][0]['message']['content']
        
        # 清洗数据 (去掉 ```json 等标记)
        if "```" in content:
            content = content.replace("```json", "").replace("```", "")
        
        return json.loads(content)

    except Exception as e:
        print(f"⚠️ AI 调用失败: {e}")
        return None

def manual_intent_analysis(user_input):
    """
    方案 B：降级方案（手动关键词匹配）
    """
    print("🔄 启用降级方案（关键词匹配）...")
    intent = {"region": "", "type": "", "price": "", "tags": []}
    
    # 乌兰察布行政区匹配
    regions = {
        "集宁": "集宁区", "察右后": "察右后旗", "察右中": "察右中旗", 
        "四子王": "四子王旗", "兴和": "兴和县"
    }
    for key, value in regions.items():
        if key in user_input:
            intent["region"] = value
            break
            
    # 类型匹配
    if any(w in user_input for w in ["吃", "饭", "餐", "肉", "面"]):
        intent["type"] = "food"
    elif any(w in user_input for w in ["住", "酒店", "民宿", "房"]):
        intent["type"] = "homestay"
    else:
        intent["type"] = "scenic_spots"

    # 标签与价格
    keywords = ["火山", "草原", "亲子", "拍照", "自驾", "免费", "便宜", "贵"]
    for k in keywords:
        if k in user_input:
            intent["tags"].append(k)
            if k in ["免费", "便宜"]:
                intent["price"] = "免费" if k == "免费" else "性价比高"
            if k == "贵":
                intent["price"] = "高价"
                
    return intent

def get_user_intent(user_input):
    # 优先尝试 AI
    intent = ai_intent_analysis(user_input)
    if intent:
        return intent
    # 失败则降级
    return manual_intent_analysis(user_input)

# 测试代码
if __name__ == "__main__":
    print("正在测试阿里云 API...")
    test_input = "我想去察右后旗看火山，还要住得舒服一点"
    print(f"解析结果: {get_user_intent(test_input)}")