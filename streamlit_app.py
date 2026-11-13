
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 页面设置
# ==========================================
st.set_page_config(
    page_title="HOMELY | 房地产探索平台",
    page_icon="🏡",
    layout="wide"
)

# ==========================================
# 2. 自定义 UI 样式
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', 'Noto Sans SC', sans-serif;
}

.stApp {
    background-color: #F5F7F6;
}

[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E8ECE9;
}

[data-testid="stSidebar"] h1 {
    color: #183D35;
    font-size: 23px;
    font-weight: 800;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

.hero {
    background: linear-gradient(120deg, #173F36, #286B58);
    padding: 36px 40px;
    border-radius: 20px;
    color: white;
    margin-bottom: 28px;
}

.hero h1 {
    color: white !important;
    font-size: 34px !important;
    font-weight: 800 !important;
    margin-bottom: 8px;
}

.hero p {
    color: #D6E9DF;
    font-size: 15px;
    margin-bottom: 0;
}

.hero-tag {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    padding: 7px 14px;
    border-radius: 30px;
    font-size: 12px;
    margin-bottom: 14px;
}

.section-title {
    color: #183D35;
    font-size: 21px;
    font-weight: 800;
    margin-top: 22px;
    margin-bottom: 15px;
}

.metric-card {
    background: white;
    border: 1px solid #E8EEEA;
    border-radius: 16px;
    padding: 20px;
    min-height: 125px;
    box-shadow: 0 3px 12px rgba(20,60,40,0.035);
}

.metric-label {
    color: #77857D;
    font-size: 13px;
    margin-bottom: 12px;
}

.metric-value {
    color: #183D35;
    font-size: 27px;
    font-weight: 800;
}

.metric-icon {
    font-size: 22px;
    margin-bottom: 8px;
}

.property-card {
    background: white;
    border: 1px solid #E6ECE8;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
}

.property-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}

.property-type {
    color: #245B49;
    font-size: 14px;
    font-weight: 700;
}

.property-badge {
    background: #EAF5EE;
    color: #28764E;
    border-radius: 20px;
    padding: 5px 11px;
    font-size: 11px;
    font-weight: 700;
}

.property-price {
    color: #183D35;
    font-size: 25px;
    font-weight: 800;
    margin-bottom: 12px;
}

.property-info {
    color: #738078;
    font-size: 13px;
    line-height: 2;
}

.info-box {
    background: #EAF3EE;
    border-left: 4px solid #347A5B;
    padding: 13px 16px;
    border-radius: 8px;
    color: #285C45;
    font-size: 13px;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E8EEEA;
    padding: 17px;
    border-radius: 14px;
}

h2, h3 {
    color: #183D35 !important;
}

.stButton button {
    border-radius: 10px;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. 加载数据
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")

    df.columns = [
        'No', '日期', '屋龄', 'MRT距离',
        '便利店数', '纬度', '经度', '单价'
    ]

    numeric_cols = [
        '日期', '屋龄', 'MRT距离',
        '便利店数', '纬度', '经度', '单价'
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=numeric_cols).copy()

    lat_m = df['纬度'].mean()
    lon_m = df['经度'].mean()
    lat_s = df['纬度'].std()
    lon_s = df['经度'].std()

    def get_region(r):
        la, lo = r['纬度'], r['经度']

        if abs(la-lat_m) < lat_s*0.5 and abs(lo-lon_m) < lon_s*0.5:
            return '市中心'
        if lo > lon_m + lon_s*0.5:
            return '东区'
        if lo < lon_m - lon_s*0.5:
            return '西区'
        if la > lat_m + lat_s*0.5:
            return '北区'
        if la < lat_m - lat_s*0.5:
            return '南区'

        return '郊区'

    df['区域'] = df.apply(get_region, axis=1)

    return df


df = load_data()


# ==========================================
# 4. 顶部 Banner
# ==========================================
st.markdown("""
<div class="hero">
    <div class="hero-tag">🏡 SMART PROPERTY DISCOVERY</div>
    <h1>找到理想中的家。</h1>
    <p>探索房地产数据，比较地段、交通与价格，做出更明智的选择。</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 5. 侧边栏筛选
# ==========================================
st.sidebar.markdown("## 🎛️ 搜索房源")
st.sidebar.caption("根据你的需求调整筛选条件")

st.sidebar.markdown("---")

p_min = float(df['单价'].min())
p_max = float(df['单价'].max())

default_low = max(p_min, float(df['单价'].quantile(0.1)))
default_high = min(p_max, float(df['单价'].quantile(0.9)))

p_range = st.sidebar.slider(
    "💰 价格范围（万新台币/坪）",
    min_value=p_min,
    max_value=p_max,
    value=(default_low, default_high)
)

mrt_max = st.sidebar.slider(
    "🚇 MRT 最大距离（米）",
    0,
    int(df['MRT距离'].max()),
    min(1500, int(df['MRT距离'].max()))
)

age_max = st.sidebar.slider(
    "🏠 最大屋龄（年）",
    0,
    int(df['屋龄'].max()),
    int(df['屋龄'].max())
)

store_min = st.sidebar.slider(
    "🏪 最少便利店数量",
    int(df['便利店数'].min()),
    int(df['便利店数'].max()),
    int(df['便利店数'].min())
)

region_sel = st.sidebar.selectbox(
    "📍 选择区域",
    ['全部'] + sorted(df['区域'].unique().tolist())
)

st.sidebar.markdown("---")
st.sidebar.caption("HOMELY · PROPERTY ANALYTICS")


# ==========================================
# 6. 筛选数据
# ==========================================
filtered = df[
    (df['单价'] >= p_range[0]) &
    (df['单价'] <= p_range[1]) &
    (df['MRT距离'] <= mrt_max) &
    (df['屋龄'] <= age_max) &
    (df['便利店数'] >= store_min)
].copy()

if region_sel != '全部':
    filtered = filtered[filtered['区域'] == region_sel]


# ==========================================
# 7. 数据统计
# ==========================================
st.markdown('<div class="section-title">📊 房地产市场概览</div>',
            unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

total = len(filtered)

if total > 0:
    metrics = [
        ("🏡", "符合条件的房源", f"{total:,}", "套房源"),
        ("💰", "平均单价", f"{filtered['单价'].mean():.1f}", "万新台币 / 坪"),
        ("🚇", "平均 MRT 距离", f"{filtered['MRT距离'].mean():.0f}", "米"),
        ("🏠", "平均屋龄", f"{filtered['屋龄'].mean():.1f}", "年")
    ]

    for col, (icon, label, value, unit) in zip(
        [c1, c2, c3, c4], metrics
    ):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div style="color:#98A49D;font-size:12px;margin-top:4px">
                    {unit}
                </div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.warning("目前没有符合条件的房源，请调整左侧筛选条件。")


# ==========================================
# 8. 房源展示
# ==========================================
if total > 0:

    st.markdown(
        '<div class="section-title">✨ 为你找到的房源</div>',
        unsafe_allow_html=True
    )

    # 以价格从低到高排序
    samples = filtered.sort_values('单价').head(6)

    def get_property_info(row):
        price = row['单价']
        mrt = row['MRT距离']
        region = row['区域']

        if mrt < 500:
            badge = "🚇 交通便利"
        elif price < df['单价'].quantile(0.25):
            badge = "💎 高性价比"
        elif region == '市中心':
            badge = "📍 核心地段"
        else:
            badge = "🏡 宜居选择"

        if price >= df['单价'].quantile(0.75):
            style = "品质住宅"
        elif price <= df['单价'].quantile(0.25):
            style = "经济型住宅"
        else:
            style = "社区住宅"

        return badge, style

    left, right = st.columns([1.15, 1])

    with left:
        st.markdown("### 🏘️ 房源推荐")
        st.caption("根据目前的筛选条件，展示价格较低的 6 套房源")

        for _, row in samples.iterrows():
            badge, style = get_property_info(row)

            st.markdown(f"""
            <div class="property-card">
                <div class="property-top">
                    <div class="property-type">🏠 {style}</div>
                    <div class="property-badge">{badge}</div>
                </div>
                <div class="property-price">
                    NT$ {row['单价']:.1f}
                    <span style="font-size:13px;color:#8A978F;font-weight:400">
                        万 / 坪
                    </span>
                </div>
                <div class="property-info">
                    📍 {row['区域']}　
                    🚇 MRT {row['MRT距离']:.0f} 米<br>
                    🏠 屋龄 {row['屋龄']:.1f} 年　
                    🏪 便利店 {int(row['便利店数'])} 家
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ======================================
    # 9. 数据分析区
    # ======================================
    with right:

        st.markdown("### 📈 价格与交通关系")
        st.caption("观察 MRT 距离与房地产单价之间的关系")

        fig = px.scatter(
            filtered,
            x='MRT距离',
            y='单价',
            color='区域',
            hover_data=['屋龄', '便利店数'],
            labels={
                'MRT距离': '距离 MRT（米）',
                '单价': '单价（万新台币 / 坪）',
                '区域': '区域',
                '屋龄': '屋龄（年）',
                '便利店数': '便利店数量'
            },
            template='plotly_white',
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        fig.update_traces(
            marker=dict(size=9, opacity=0.75)
        )

        fig.update_layout(
            height=390,
            title=None,
            margin=dict(l=15, r=15, t=20, b=15),
            legend_title_text='区域',
            font=dict(family='Arial', color='#40534A'),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        st.plotly_chart(fig, use_container_width=True)

        # ==================================
        # 10. 房源位置地图
        # ==================================
        st.markdown("### 🗺️ 房源地理位置")
        st.caption("查看符合条件的房源在地图上的分布")

        map_df = filtered.copy()

        map_fig = px.scatter_mapbox(
            map_df,
            lat='纬度',
            lon='经度',
            color='区域',
            hover_data={
                '单价': ':.1f',
                '屋龄': ':.1f',
                'MRT距离': ':,.0f',
                '便利店数': True
            },
            zoom=11,
            height=390,
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        map_fig.update_layout(
            mapbox_style="open-street-map",
            margin=dict(l=0, r=0, t=0, b=0),
            legend_title_text='区域'
        )

        st.plotly_chart(map_fig, use_container_width=True)


    # ======================================
    # 11. 完整数据表
    # ======================================
    st.markdown("---")
    st.markdown(
        '<div class="section-title">📋 房源详细资料</div>',
        unsafe_allow_html=True
    )

    display_df = filtered[
        ['No', '区域', '单价', '屋龄', 'MRT距离', '便利店数']
    ].copy()

    display_df.columns = [
        '编号', '区域', '价格（万/坪）',
        '屋龄（年）', 'MRT距离（米）', '便利店数'
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=300
    )

    # 下载功能
    csv = display_df.to_csv(index=False).encode('utf-8-sig')

    st.download_button(
        label="📥 下载筛选后的房源资料",
        data=csv,
        file_name="property_data.csv",
        mime="text/csv"
    )


# ==========================================
# 12. 页脚
# ==========================================
st.markdown("---")

st.markdown("""
<div style="text-align:center;padding:15px;color:#89968E">
    <div style="font-size:18px;font-weight:800;color:#285B48">
        🏡 HOMELY
    </div>
    <div style="font-size:12px;margin-top:6px">
        Smart Property Discovery & Data Analytics
    </div>
    <div style="font-size:11px;margin-top:8px">
        Data Source: UCI Machine Learning Repository
        · Real Estate Valuation Dataset
    </div>
</div>
""", unsafe_allow_html=True)
