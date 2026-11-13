import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
import plotly.express as px

st.set_page_config(page_title="🏠 房地产数据探索系统", layout="wide")

# ========== 加载数据 ==========
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df.columns = ['No','日期','屋龄','MRT距离','便利店数','纬度','经度','单价']
    lat_m, lon_m = df['纬度'].mean(), df['经度'].mean()
    lat_s, lon_s = df['纬度'].std(), df['经度'].std()
    def get_region(r):
        la, lo = r['纬度'], r['经度']
        if abs(la-lat_m)<lat_s*0.5 and abs(lo-lon_m)<lon_s*0.5: return '市中心'
        if lo>lon_m+lon_s*0.5: return '东区'
        if lo<lon_m-lon_s*0.5: return '西区'
        if la>lat_m+lat_s*0.5: return '北区'
        if la<lat_m-lat_s*0.5: return '南区'
        return '郊区'
    df['区域'] = df.apply(get_region, axis=1)
    return df

df = load_data()

# ========== 侧边栏 ==========
st.sidebar.title("🎛️ 筛选条件")

p_min = float(df['单价'].min())
p_max = float(df['单价'].max())
p_range = st.sidebar.slider(
    "💰 价格范围（万新台币/坪）",
    round(p_min,1), round(p_max,1), (25.0, 50.0)
)

mrt_max = st.sidebar.slider(
    "🚇 距MRT距离（米）",
    0, int(df['MRT距离'].max()), 1500
)

age_max = st.sidebar.slider(
    "🏠 屋龄不超过（年）",
    0, int(df['屋龄'].max()), int(df['屋龄'].max())
)

store_min = st.sidebar.slider(
    "🏪 周边便利店至少（家）",
    int(df['便利店数'].min()), int(df['便利店数'].max()), 0
)

region_sel = st.sidebar.selectbox(
    "📍 选择意向区域",
    ['全部'] + sorted(df['区域'].unique().tolist())
)

# ========== 筛选逻辑 ==========
filtered = df[
    (df['单价'] >= p_range[0]) & (df['单价'] <= p_range[1]) &
    (df['MRT距离'] <= mrt_max) & (df['屋龄'] <= age_max) &
    (df['便利店数'] >= store_min)
]
if region_sel != '全部':
    filtered = filtered[filtered['区域'] == region_sel]

# ========== 主页面 ==========
st.title("🏘️ 房地产数据探索系统")
st.markdown("---")

if len(filtered) == 0:
    st.warning("😅 暂时没有找到符合条件的房源，请尝试放宽筛选条件！")
else:
    # 统计卡片
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("找到房源", f"{len(filtered)} 套")
    c2.metric("平均单价", f"{filtered['单价'].mean():.1f} 万/坪")
    c3.metric("平均MRT距离", f"{int(filtered['MRT距离'].mean())} 米")
    c4.metric("平均屋龄", f"{filtered['屋龄'].mean():.1f} 年")
    
    st.markdown("---")

    # ========== 优化版：画房子函数（更好看！）==========
    def draw_house(p, mrt, a, s, r):
        W, H = 560, 400
        img = Image.new('RGB', (W, H), '#E0EFF9')
        d = ImageDraw.Draw(img)
        
        # 天空渐变+太阳
        for y in range(180):
            alpha = int(200 - y)
            color = f'rgb({135+y//3},{206-y//5},{235-y//4})'
            d.rectangle([0, y, W, y+1], fill=color)
        d.ellipse([460, 40, 510, 90], fill='#FFD93D', outline='#F9A825', width=3)
        
        # 远山
        d.polygon([(0, 220), (120, 140), (240, 220)], fill='#90B77D', outline='#6A9F5C')
        d.polygon([(200, 200), (350, 120), (500, 200)], fill='#7FB77E', outline='#5D9F5C')
        d.polygon([(380, 220), (520, 150), (560, 220)], fill='#90B77D', outline='#6A9F5C')
        
        # 草地
        d.rectangle([0, 220, W, H], fill='#A8D892')
        d.rectangle([0, 235, W, 245], fill='#7ABF5A')
        
        # 小路
        d.polygon([(W//2-40, H), (W//2-20, 245), (W//2+20, 245), (W//2+40, H)], fill='#D4B996')
        
        # 判断类型
        hp = p >= df['单价'].quantile(0.75)
        cheap_far = p <= df['单价'].quantile(0.25) and mrt > 1000
        near = mrt < 500
        
        if hp and near and r == '市中心':
            body_color = '#4A90D9'
            roof_color = '#1E4D8C'
            fl = 12
            style = '🏙️ 市中心高层公寓'
            desc = '核心地段 · 交通便利 · 配套完善'
        elif hp:
            body_color = '#74A9E8'
            roof_color = '#2E6BC9'
            fl = 8
            style = '🏢 市区品质住宅'
            desc = '环境优美 · 闹中取静 · 品质优选'
        elif cheap_far:
            body_color = '#E8C896'
            roof_color = '#A67C52'
            fl = 2
            style = '🏡 郊区独栋小屋'
            desc = '价格亲民 · 空间宽敞 · 自然舒适'
        else:
            body_color = '#F0D9B5'
            roof_color = '#B58860'
            fl = 5
            style = '🏘️ 社区普通住宅'
            desc = '性价比高 · 生活便利 · 温馨宜居'
        
        bx, by = W//2, 230
        bw, bh = 130, fl * 20
        
        # 主楼体
        d.rectangle([bx-bw//2, by-bh, bx+bw//2, by], fill=body_color, outline='#333', width=2)
        
        # 屋顶
        roof_h = 35
        d.polygon([
            (bx-bw//2-10, by-bh),
            (bx, by-bh-roof_h),
            (bx+bw//2+10, by-bh)
        ], fill=roof_color, outline='#333', width=2)
        
        # 大门
        dw, dh = 30, 45
        d.rectangle([bx-dw//2, by-dh, bx+dw//2, by], fill='#8B5A2B', outline='#5C3A1D', width=2)
        d.ellipse([bx+dw//2-5, by-dh//2-3, bx+dw//2, by-dh//2+3], fill='#FFD700')
        
        # 窗户
        ww, wh = 18, 24
        gap_x = 35
        gap_y = 28
        for floor in range(fl):
            y_pos = by - bh + 12 + floor * gap_y
            for col in range(-1, 2):
                x_pos = bx + col * gap_x - ww//2
                if not (floor == 0 and col == 0):  # 跳过大门位置
                    d.rectangle([x_pos, y_pos, x_pos+ww, y_pos+wh], fill='#FFF9C4', outline='#CCC', width=1)
                    d.line([(x_pos+ww//2, y_pos), (x_pos+ww//2, y_pos+wh)], fill='#CCC', width=1)
                    d.line([(x_pos, y_pos+wh//2), (x_pos+ww, y_pos+wh//2)], fill='#CCC', width=1)
        
        # MRT 位置指示
        if near:
            d.ellipse([50, 250, 90, 290], fill='#FF4757', outline='#FFF', width=3)
            d.rectangle([62, 265, 78, 275], fill='#FFF')
        else:
            d.ellipse([50, 250, 90, 290], fill='#B0B0B0', outline='#FFF', width=3)
        
        # 便利店图标
        if s >= 5:
            for i in range(3):
                sx = W - 100 + i * 35
                d.rectangle([sx, 260, sx+25, 285], fill='#FFD32B', outline='#E6B800', width=2)
                d.rectangle([sx+8, 268, sx+17, 277], fill='#FFF')
        
        # 树木
        def draw_tree(x, y, size=1):
            tw, th = int(8*size), int(25*size)
            r = int(20*size)
            d.rectangle([x-tw//2, y-th, x+tw//2, y], fill='#6B4226')
            d.ellipse([x-r, y-th-r, x+r, y-th+r], fill='#2E7D32')
            d.ellipse([x-r+5, y-th-r+10, x+r-5, y-th+r-5], fill='#388E3C')
        
        draw_tree(bx - bw//2 - 45, 245, 1.15)
        draw_tree(bx + bw//2 + 45, 245, 1.05)
        if not (hp and near and r == '市中心'):
            draw_tree(30, H-30, 0.9)
            draw_tree(W-30, H-30, 0.85)
        
        return img, style, desc

    # ========== 展示区 ==========
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.subheader("🎨 房源预览")
        samples = filtered.head(3)
        for idx, row in samples.iterrows():
            img, style, desc = draw_house(row['单价'], row['MRT距离'], row['屋龄'], row['便利店数'], row['区域'])
            with st.expander(f"{style} — {row['单价']:.1f} 万/坪", expanded=(idx==samples.index[0])):
                st.image(img, use_container_width=True)
                st.info(f"✨ {desc}")
                st.markdown(f"""
                - **📍 区域：** {row['区域']}
                - **💰 价格：** **{row['单价']:.1f}** 万新台币/坪
                - **🚇 距MRT：** {int(row['MRT距离'])} 米
                - **🏠 屋龄：** {row['屋龄']:.1f} 年
                - **🏪 便利店：** {row['便利店数']} 家
                """)
    
    with col_right:
        st.subheader("📋 详细数据")
        display_df = samples[['区域','单价','屋龄','MRT距离','便利店数']].copy()
        display_df.columns = ['区域','价格(万/坪)','屋龄(年)','MRT距离(米)','便利店数']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.subheader("📊 价格分布图")
        fig = px.scatter(
            filtered, x='MRT距离', y='单价', color='区域',
            labels={'MRT距离':'到MRT距离（米）','单价':'单价（万新台币/坪）'},
            title="距离MRT越近，价格通常越高",
            template='plotly_white',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(
            title_x=0.5,
            xaxis_title="到MRT距离（米）",
            yaxis_title="单价（万新台币/坪）"
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("📊 数据源: UCI Machine Learning Repository — Real Estate Valuation Data Set | 💻 制作: 房地产数据探索系统")
