import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
import plotly.express as px

st.set_page_config(page_title="🏠 房子查询系统", layout="wide")

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

st.sidebar.title("🎛️ 筛选条件")
p_min = float(df['单价'].min())
p_max = float(df['单价'].max())
p_range = st.sidebar.slider("💰 价格范围（万/坪）", round(p_min,1), round(p_max,1), (20.0, 55.0))
mrt_max = st.sidebar.slider("🚇 离MRT不超过（米）", 0, int(df['MRT距离'].max()), 1000)
age_max = st.sidebar.slider("🏠 屋龄不超过（年）", 0, int(df['屋龄'].max()), int(df['屋龄'].max()))
store_min = st.sidebar.slider("🏪 至少几家便利店", int(df['便利店数'].min()), int(df['便利店数'].max()), 0)
region_sel = st.sidebar.selectbox("📍 选择区域", ['全部'] + sorted(df['区域'].unique().tolist()))

filtered = df[
    (df['单价']>=p_range[0]) & (df['单价']<=p_range[1]) &
    (df['MRT距离']<=mrt_max) & (df['屋龄']<=age_max) &
    (df['便利店数']>=store_min)
]
if region_sel != '全部':
    filtered = filtered[filtered['区域']==region_sel]

st.title("🏘️ 房地产数据探索系统")
st.markdown("---")

if len(filtered) == 0:
    st.warning("😅 没找到，放宽一点条件试试！")
else:
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("找到房源", f"{len(filtered)} 套")
    c2.metric("平均价格", f"{filtered['单价'].mean():.1f} 万/坪")
    c3.metric("平均MRT", f"{int(filtered['MRT距离'].mean())} 米")
    c4.metric("平均屋龄", f"{filtered['屋龄'].mean():.1f} 年")
    st.markdown("---")

    def draw_house(p, mrt, a, s, r):
        img = Image.new('RGB', (520, 360), '#87CEEB')
        d = ImageDraw.Draw(img)
        d.rectangle([0, 270, 520, 360], fill='#5a8f5e')
        d.rectangle([0, 305, 520, 320], fill='#666666')
        
        hp = p >= df['单价'].quantile(0.75)
        cheap_far = p <= df['单价'].quantile(0.25) and mrt > 1000
        near = mrt < 500
        
        if hp and near and r == '市中心':
            col, roof, fl, name = '#5B8BD9', '#1E3A67', 11, '🏙️ 市中心高层公寓'
        elif hp:
            col, roof, fl, name = '#7AA7E8', '#2E5296', 8, '🏢 市区品质住宅'
        elif cheap_far:
            col, roof, fl, name = '#C8A777', '#7A5A37', 2, '🏡 郊区独栋小屋'
        else:
            col, roof, fl, name = '#D8C8A8', '#8A6D47', 5, '🏘️ 社区普通住宅'
        
        bx, by = 260, 140
        fw, fh = 95, fl * 16
        
        d.polygon([(bx-52,by-fh),(bx,by-fh-24),(bx+52,by-fh)], fill=roof, outline='#222')
        d.rectangle([(bx-47,by-fh),(bx+47,by)], fill=col, outline='#222')
        
        for floor in range(fl):
            y = by - 9 - floor * 16
            for cw in range(3):
                x = bx - 36 + cw * 29
                d.rectangle([x, y, x+11, y+7], fill='#FFF89C')
        
        if near:
            d.ellipse([410, 275, 445, 310], fill='#FF2B2B', outline='#FFF', width=2)
        else:
            d.ellipse([410, 275, 445, 310], fill='#777777', outline='#FFF', width=2)
        
        if s >= 5:
            for i in range(3):
                sx = 55 + i * 44
                d.rectangle([sx, 290, sx+34, 315], fill='#FFD13F', outline='#444')
        
        def tree(x, y, size=1):
            tw, th = int(5*size), int(18*size)
            r = int(14*size)
            d.rectangle([x-tw//2, y-th, x+tw//2, y], fill='#603820')
            d.ellipse([x-r, y-th-r, x+r, y-th+r], fill='#248030')
        
        tree(85, 270, 1.05)
        tree(435, 270, 0.95)
        if not (hp and near and r == '市中心'):
            tree(55, 290, 0.7)
            tree(465, 290, 0.75)
        
        return img, name

    col_left, col_right = st.columns([1,1])
    
    with col_left:
        st.subheader("🎨 房源预览")
        samples = filtered.head(3)
        for idx, row in samples.iterrows():
            img, name = draw_house(row['单价'], row['MRT距离'], row['屋龄'], row['便利店数'], row['区域'])
            with st.expander(f"{name} — {row['单价']:.1f}万/坪", expanded=True):
                st.image(img, use_container_width=True)
                st.write(f"""
                - **📍 区域：** {row['区域']}
                - **💰 价格：** {row['单价']:.1f} 万新台币/坪
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
        fig = px.scatter(filtered, x='MRT距离', y='单价', color='区域',
                        labels={'MRT距离':'到MRT距离(米)','单价':'单价(万新台币/坪)'},
                        title="距离越近，价格通常越高")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("📊 数据源: UCI Machine Learning Repository — Real Estate Valuation Data Set")
