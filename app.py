import streamlit as st
import matplotlib.pyplot as plt
import time

# 引入我们写好的核心模块
from src.data_loader import load_tourism_data
from src.ai_agent import get_user_intent
from src.recommender import personalized_recommend

# 1. 页面配置 (必须是第一行执行的代码)
st.set_page_config(
    page_title="乌兰察布文旅助手",
    page_icon="🌋",
    layout="wide"
)

# 解决中文乱码的字体设置
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

# 2. 加载数据 (使用 @st.cache_data 防止每次点击按钮都重新加载文件)
@st.cache_data
def get_data():
    return load_tourism_data()

data = get_data()

# --- 侧边栏设计 ---
with st.sidebar:
    st.title("🌋 乌兰察布文旅")
    st.markdown("---")
    st.write(f"**已加载数据统计:**")
    st.info(f"📍 景点: {len(data.get('scenic_spots', []))} 个")
    st.success(f"🥘 美食: {len(data.get('food', []))} 家")
    st.warning(f"🏡 民宿: {len(data.get('homestay', []))} 家")
    st.markdown("---")
    st.caption("Powered by LLM & Streamlit")

# --- 主页面设计 ---
st.title("🤖 智能文旅推荐系统")
st.markdown("#### *“告诉我你想去哪、想吃什么，AI 为你规划”*")

# 初始化对话历史 (让它像聊天软件一样)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示之前的对话
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. 获取用户输入
user_input = st.chat_input("请输入你的需求（例如：想去察右后旗看火山，住得舒服点）")

if user_input:
    # 显示用户的话
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # --- AI 核心处理流程 ---
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # A. AI 解析意图
        with st.status("🧠 AI 正在思考...", expanded=True) as status:
            st.write("正在连接大模型 API...")
            intent = get_user_intent(user_input)
            st.write(f"✅ 解析成功: {intent}")
            
            st.write("正在匹配本地数据库...")
            recommendations = personalized_recommend(data, intent)
            status.update(label="✅ 规划完成!", state="complete", expanded=False)

        # B. 展示推荐结果
        if recommendations:
            response_md = f"为您找到 **{len(recommendations)}** 个好去处：\n\n"
            message_placeholder.markdown(response_md)
            
            # 使用 Streamlit 的列布局来展示卡片
            for item in recommendations:
                with st.expander(f"🏆 {item['name']} ({item['score']}分) - ¥{item['price']}", expanded=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**📍 地址**: {item['address']}")
                        st.markdown(f"**🏷️ 标签**: :blue[{', '.join(item['tags'])}]")
                    with c2:
                        st.metric("匹配度", f"{item['match_score']}分")

            # C. 数据可视化 (这里我们重新画图，适配网页版)
            st.markdown("### 📊 数据洞察")
            
            # 准备数据
            names = [item["name"] for item in recommendations]
            scores = [item["score"] for item in recommendations]
            prices = [item["price"] for item in recommendations]

            # 创建图表对象
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # 柱状图
            ax1.bar(names, scores, color='#66b3ff')
            ax1.set_title("评分对比")
            ax1.set_ylim(0, 5.5)
            ax1.tick_params(axis='x', rotation=45)

            # 饼图
            price_ranges = {"免费": 0, "100元以下": 0, "100+": 0}
            for p in prices:
                if p == 0: price_ranges["免费"] += 1
                elif p <= 100: price_ranges["100元以下"] += 1
                else: price_ranges["100+"] += 1
            data_pie = {k: v for k, v in price_ranges.items() if v > 0}
            ax2.pie(data_pie.values(), labels=data_pie.keys(), autopct='%1.1f%%')
            ax2.set_title("价格分布")

            st.pyplot(fig) # 把图表画在网页上

            # 保存对话历史
            st.session_state.messages.append({"role": "assistant", "content": response_md})

        else:
            fail_msg = "抱歉，没有找到匹配的结果，请尝试换个关键词（如：美食、民宿、火山）。"
            message_placeholder.markdown(fail_msg)
            st.session_state.messages.append({"role": "assistant", "content": fail_msg})