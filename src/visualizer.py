import matplotlib.pyplot as plt

def set_chinese_font():
    """解决 Matplotlib 中文乱码问题"""
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun'] 
    plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题

def visualize_recommendations(recommendations):
    """
    绘制推荐结果的图表
    """
    if not recommendations:
        print("没有推荐结果，跳过绘图")
        return

    set_chinese_font()
    
    # 提取数据
    names = [item["name"] for item in recommendations]
    scores = [item["score"] for item in recommendations]
    prices = [item["price"] for item in recommendations]
    
    # 创建画布 (宽12，高5)
    plt.figure(figsize=(12, 5))
    
    # --- 图1：评分柱状图 ---
    plt.subplot(1, 2, 1)
    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99', '#c2c2f0']
    plt.bar(names, scores, color=colors[:len(names)])
    plt.title("推荐项目评分对比 (5分制)")
    plt.ylabel("评分")
    plt.xticks(rotation=15) # 文字倾斜防止重叠
    plt.ylim(0, 5.5)
    
    # --- 图2：价格分布饼图 ---
    plt.subplot(1, 2, 2)
    # 简单划分价格区间
    price_ranges = {"免费": 0, "100元以下": 0, "100-300元": 0, "300元以上": 0}
    for p in prices:
        if p == 0: price_ranges["免费"] += 1
        elif p <= 100: price_ranges["100元以下"] += 1
        elif p <= 300: price_ranges["100-300元"] += 1
        else: price_ranges["300元以上"] += 1
    
    # 过滤掉数量为0的区间
    data = {k: v for k, v in price_ranges.items() if v > 0}
    
    plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=140)
    plt.title("推荐项目价格区间分布")
    
    # 调整布局并展示
    plt.tight_layout()
    print("📊 图表已生成，请在弹出的窗口中查看...")
    plt.show()