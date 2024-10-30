import streamlit as st
import pytrends
from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime, timedelta
import time
import plotly.express as px

def initialize_pytrends():
    """初始化 Google Trends API"""
    return TrendReq(hl='en-US', tz=360)

def get_trending_searches(pytrends, region):
    """獲取特定區域的熱門搜索關鍵字"""
    try:
        trending_searches = pytrends.trending_searches(pn=region)
        trending_searches.columns = ['關鍵字']
        return trending_searches
    except Exception as e:
        st.error(f"獲取數據時發生錯誤: {str(e)}")
        return pd.DataFrame()

def get_interest_over_time(pytrends, keyword):
    """獲取關鍵字過去24小時的搜索趨勢"""
    try:
        pytrends.build_payload([keyword], timeframe='now 1-d')
        interest_df = pytrends.interest_over_time()
        return interest_df
    except Exception as e:
        st.error(f"獲取趨勢數據時發生錯誤: {str(e)}")
        return pd.DataFrame()

def main():
    # 設置頁面配置
    st.set_page_config(page_title="Google 趨勢監測", layout="wide")
    
    st.title('🔍 Google 趨勢即時監測')
    
    # 初始化 session state
    if 'selected_keyword' not in st.session_state:
        st.session_state.selected_keyword = None
    
    # 側邊欄配置
    st.sidebar.header('設置')
    
    # 地區選擇
    region_mapping = {
        
        '美國': 'united_states',
        '日本': 'japan',
        '台灣': 'taiwan',
        '香港': 'hong_kong',
        '新加坡': 'singapore'
    }
    
    selected_region = st.sidebar.selectbox(
        '選擇區域',
        options=list(region_mapping.keys())
    )
    
    # 更新頻率設置
    update_interval = st.sidebar.slider(
        '更新頻率 (分鐘)',
        min_value=1,
        max_value=60,
        value=5
    )
    
    # 初始化 PyTrends
    try:
        pytrends = initialize_pytrends()
    except Exception as e:
        st.error(f"初始化 PyTrends 時發生錯誤: {str(e)}")
        return
    
    # 主要內容區域
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader(f'📈 {selected_region}熱門關鍵字')
        trending_df = get_trending_searches(pytrends, region_mapping[selected_region])
        
        if not trending_df.empty:
            st.dataframe(trending_df)
            
            # 選擇關鍵字進行深入分析
            st.session_state.selected_keyword = st.selectbox(
                '選擇關鍵字查看詳細趨勢',
                options=trending_df['關鍵字'].tolist(),
                key='keyword_selector'
            )
    
    with col2:
        if st.session_state.selected_keyword:
            st.subheader(f'🔍 "{st.session_state.selected_keyword}" 搜索趨勢')
            interest_df = get_interest_over_time(pytrends, st.session_state.selected_keyword)
            
            if not interest_df.empty:
                # 使用Plotly繪製互動式圖表
                fig = px.line(
                    interest_df,
                    x=interest_df.index,
                    y=st.session_state.selected_keyword,
                    title=f'{st.session_state.selected_keyword} 過去24小時搜索趨勢'
                )
                fig.update_layout(
                    xaxis_title="時間",
                    yaxis_title="搜索趨勢指數",
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info('請在左側選擇一個關鍵字以查看詳細趨勢')
    
    # 自動更新機制
    auto_update = st.sidebar.checkbox('啟用自動更新')
    if auto_update:
        st.sidebar.write(f'每{update_interval}分鐘自動更新一次')
        time.sleep(update_interval * 60)
        st.rerun()

if __name__ == "__main__":
    main()

# requirements.txt 內容：
"""
streamlit==1.27.0
pytrends==4.9.0
pandas==2.0.3
plotly==5.17.0
"""
