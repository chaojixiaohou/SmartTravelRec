import time
from src.data_loader import load_tourism_data
from src.ai_agent import get_user_intent
from src.recommender import personalized_recommend
from src.visualizer import visualize_recommendations

def main():
    print("="*50)
    print("乌兰察布文旅智能推荐系统 (AI驱动版) 启动中...")
    print("="*50)
    
    # 1. 加载数据
    data = load_tourism_data()
    if not data:
        return

    # 2. 交互循环
    while True:
        user_input = input("\n🗣️  请输入你的需求 (输入 'q' 退出): \n>> ").strip()
        
        if user_input.lower() == 'q':
            print("👋 感谢使用，再见！")
            break
        
        if not user_input:
            continue
            
        print(f"\n🧠 正在分析意图: '{user_input}' ...")
        
        # 3. AI 解析
        start_time = time.time()
        intent = get_user_intent(user_input)
        print(f"✅ 解析结果: {intent} (耗时 {time.time()-start_time:.2f}s)")
        
        # 4. 推荐算法
        recommendations = personalized_recommend(data, intent)
        
        if recommendations:
            print(f"\n🎉 为你找到 {len(recommendations)} 个好去处：")
            for idx, item in enumerate(recommendations, 1):
                print(f"   {idx}. {item['name']} | {item['region']} | 评分:{item['score']} | ¥{item['price']}")
                print(f"      标签: {item['tags']}")
            
            # 5. 可视化
            print("\n📈 正在生成分析图表...")
            visualize_recommendations(recommendations)
        else:
            print("😔 抱歉，没有找到匹配的结果，换个说法试试？")

if __name__ == "__main__":
    main()