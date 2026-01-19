import json
import os

def load_tourism_data(file_name="tourism_data.json"):
    """
    加载本地文旅数据
    """
    # 获取当前脚本所在的目录 (src)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 回退一级找到 data 目录 (.. -> data)
    base_dir = os.path.dirname(current_dir)
    file_path = os.path.join(base_dir, "data", file_name)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 简单的统计打印
            print(f"✅ 成功加载数据：")
            print(f"   - 景点: {len(data.get('scenic_spots', []))} 个")
            print(f"   - 美食: {len(data.get('food', []))} 个")
            print(f"   - 民宿: {len(data.get('homestay', []))} 个")
            return data
    except FileNotFoundError:
        print(f"❌ 错误：找不到文件 {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"❌ 错误：文件格式不是有效的 JSON")
        return {}

# 这是一个测试代码块，只有直接运行这个文件时才会执行
if __name__ == "__main__":
    load_tourism_data()