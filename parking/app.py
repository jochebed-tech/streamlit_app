import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
import folium
import random

# ==========================================
# 1. 페이지 기본 설정 및 디자인
# ==========================================
st.set_page_config(
    page_title="서울시 공영주차장 정보 서비스",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS 스타일링
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2563EB;
        margin-bottom: 10px;
    }
    .recommend-card {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 12px;
        padding: 20px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 데이터 로드 및 전처리
# ==========================================
@st.cache_data
def load_data():
    file_path = '서울시 공영주차장 안내 정보.csv'
    
    # 인코딩 대응 (cp949, euc-kr, utf-8)
    encodings = ['cp949', 'euc-kr', 'utf-8-sig', 'utf-8']
    df = None
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except Exception:
            continue
            
    if df is None:
        st.error("데이터 파일을 읽을 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")
        return pd.DataFrame()

    # 데이터 정리
    # 1. 주소에서 자치구 추출
    df['자치구'] = df['주소'].str.extract(r'([가-힣]+구)')
    df['자치구'] = df['자치구'].fillna('기타/미분류')

    # 2. 위도/경도 결측치 처리 및 수치형 변환
    df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
    df['경도'] = pd.to_numeric(df['경도'], errors='coerce')

    # 3. 요금 및 시간 관련 열 수치형 변환
    num_cols = ['기본 주차 요금', '기본 주차 시간(분 단위)', '추가 단위 요금', '추가 단위 시간(분 단위)', '일 최대 요금', '총 주차면']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 4. 파생변수: 1시간 기준 계산 요금 (비교용)
    def get_hourly_rate(row):
        base_fee = row['기본 주차 요금']
        base_min = row['기본 주차 시간(분 단위)']
        add_fee = row['추가 단위 요금']
        add_min = row['추가 단위 시간(분 단위)']
        
        if row.get('유무료구분명') == '무료' or base_fee == 0:
            return 0
        
        if base_min >= 60:
            return base_fee
        
        remaining = 60 - base_min
        if add_min > 0 and add_fee > 0:
            units = np.ceil(remaining / add_min)
            return base_fee + (units * add_fee)
        elif base_min > 0:
            return (base_fee / base_min) * 60
        return 0

    df['1시간_추정요금'] = df.apply(get_hourly_rate, axis=1)
    
    return df

df_raw = load_data()

if df_raw.empty:
    st.stop()

# ==========================================
# 3. 주차 요금 계산 함수
# ==========================================
def calculate_parking_fee(row, parking_minutes):
    """이용 시간에 따른 예상 주차 요금 산출"""
    if row.get('유무료구분명') == '무료':
        return 0
    
    base_fee = float(row.get('기본 주차 요금', 0))
    base_min = float(row.get('기본 주차 시간(분 단위)', 0))
    add_fee = float(row.get('추가 단위 요금', 0))
    add_min = float(row.get('추가 단위 시간(분 단위)', 0))
    max_fee = float(row.get('일 최대 요금', 0))

    if parking_minutes <= 0:
        return 0

    if base_min > 0 and parking_minutes <= base_min:
        total = base_fee
    elif base_min > 0 and parking_minutes > base_min:
        remaining = parking_minutes - base_min
        if add_min > 0 and add_fee > 0:
            extra_units = np.ceil(remaining / add_min)
            total = base_fee + (extra_units * add_fee)
        else:
            total = base_fee
    else:
        if add_min > 0 and add_fee > 0:
            extra_units = np.ceil(parking_minutes / add_min)
            total = extra_units * add_fee
        else:
            total = 0

    # 일 최대 요금 적용
    if max_fee > 0 and total > max_fee:
        total = max_fee

    return int(total)

# ==========================================
# 4. 사이드바 - 검색 및 필터 옵션
# ==========================================
st.sidebar.header("🔍 검색 및 필터 조건")

# 1. 자치구 선택
gu_list = ['전체'] + sorted([g for g in df_raw['자치구'].unique() if g != '기타/미분류'])
selected_gu = st.sidebar.selectbox("자치구 선택", gu_list)

# 2. 유/무료 구분
fee_options = ['전체'] + list(df_raw['유무료구분명'].dropna().unique())
selected_fee = st.sidebar.radio("유/무료 구분", fee_options, horizontal=True)

# 3. 주차장 종류 (노상/노외 등)
type_options = ['전체'] + list(df_raw['주차장 종류명'].dropna().unique())
selected_type = st.sidebar.multiselect("주차장 종류", type_options, default=['전체'])

# 4. 주차장명 / 주소 키워드 검색
search_keyword = st.sidebar.text_input("주차장명 또는 주소 검색", placeholder="예: 마장동, 여의도")

# 필터링 적용
df_filtered = df_raw.copy()

if selected_gu != '전체':
    df_filtered = df_filtered[df_filtered['자치구'] == selected_gu]

if selected_fee != '전체':
    df_filtered = df_filtered[df_filtered['유무료구분명'] == selected_fee]

if selected_type and '전체' not in selected_type:
    df_filtered = df_filtered[df_filtered['주차장 종류명'].isin(selected_type)]

if search_keyword.strip():
    kw = search_keyword.strip()
    df_filtered = df_filtered[
        df_filtered['주차장명'].str.contains(kw, case=False, na=False) |
        df_filtered['주소'].str.contains(kw, case=False, na=False)
    ]

# ==========================================
# 5. 메인 레이아웃 및 탭 구성
# ==========================================
st.markdown('<div class="main-title">🅿️ 서울시 공영주차장 스마트 안내 서비스</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">서울시 공영주차장 위치, 요금 계산, 맞춤 추천 및 현황 분석을 제공합니다.</div>', unsafe_allow_html=True)

# 주요 핵심 지표 (KPI)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("검색된 주차장", f"{len(df_filtered):,} 개")
with kpi2:
    total_spaces = int(df_filtered['총 주차면'].sum())
    st.metric("총 주차 면수", f"{total_spaces:,} 면")
with kpi3:
    free_count = len(df_filtered[df_filtered['유무료구분명'] == '무료'])
    st.metric("무료 주차장 수", f"{free_count:,} 개")
with kpi4:
    avg_base = df_filtered[df_filtered['기본 주차 요금'] > 0]['기본 주차 요금'].mean()
    st.metric("평균 기본요금", f"{avg_base:.0f} 원" if not np.isnan(avg_base) else "0 원")

st.markdown("---")

# 탭 메뉴 정의
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 주차장 목록 & 검색", 
    "🗺️ 지도 보기", 
    "💰 요금 계산 & 저렴한 주차장", 
    "🎲 랜덤 추천", 
    "📊 통계 분석"
])

# ------------------------------------------
# TAB 1: 주차장 목록 및 CSV 다운로드
# ------------------------------------------
with tab1:
    st.subheader("주차장 상세 목록")
    
    display_cols = [
        '주차장명', '자치구', '주소', '주차장 종류명', '유무료구분명', 
        '총 주차면', '기본 주차 요금', '기본 주차 시간(분 단위)', '추가 단위 요금', '추가 단위 시간(분 단위)', '전화번호'
    ]
    
    # 존재하는 컬럼만 선택
    valid_cols = [c for c in display_cols if c in df_filtered.columns]
    
    st.dataframe(
        df_filtered[valid_cols],
        use_container_width=True,
        hide_index=True
    )
    
    # CSV 다운로드 기능
    csv_data = df_filtered[valid_cols].to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="📥 검색 결과 CSV 다운로드",
        data=csv_data,
        file_name="서울시_공영주차장_검색결과.csv",
        mime="text/csv"
    )

# ------------------------------------------
# TAB 2: 지도 보기 (Folium)
# ------------------------------------------
with tab2:
    st.subheader("📍 공영주차장 위치 지도")
    
    # 좌표 정보가 유효한 데이터만 추출
    map_df = df_filtered.dropna(subset=['위도', '경도'])
    map_df = map_df[(map_df['위도'] > 33) & (map_df['위도'] < 39) & (map_df['경도'] > 124) & (map_df['경도'] < 132)]
    
    if map_df.empty:
        st.warning("선택한 조건에 위치 정보(위도/경도)가 있는 주차장이 없습니다.")
    else:
        st.info(f"총 {len(map_df):,}개 주차장 위치를 지도에 표시합니다.")
        
        # 지도 중심 설정 (데이터의 평균 좌표)
        center_lat = map_df['위도'].mean()
        center_lng = map_df['경도'].mean()
        
        m = folium.Map(location=[center_lat, center_lng], zoom_start=12)
        
        # 마커 추가 (최대 300개 제한 - 성능 최적화)
        display_map_df = map_df.head(300)
        
        for idx, row in display_map_df.iterrows():
            popup_html = f"""
            <div style="width: 220px; font-family: sans-serif;">
                <h4 style="margin:0 0 8px 0; color:#1E3A8A;">{row['주차장명']}</h4>
                <b>주소:</b> {row['주소']}<br>
                <b>유/무료:</b> {row['유무료구분명']}<br>
                <b>총 주차면:</b> {int(row['총 주차면'])}면<br>
                <b>기본요금:</b> {int(row['기본 주차 요금'])}원 / {int(row['기본 주차 시간(분 단위)'])}분<br>
                <b>전화번호:</b> {row.get('전화번호', ' 정보없음')}
            </div>
            """
            
            icon_color = "green" if row['유무료구분명'] == '무료' else "blue"
            
            folium.Marker(
                location=[row['위도'], row['경도']],
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=row['주차장명'],
                icon=folium.Icon(color=icon_color, icon="info-sign")
            ).add_to(m)
            
        st_folium(m, width=None, height=500, use_container_width=True)

# ------------------------------------------
# TAB 3: 요금 계산기 & 저렴한 주차장 추천
# ------------------------------------------
with tab3:
    st.subheader("💰 예상 주차요금 계산 & 최저가 추천")
    
    col_input1, col_input2 = st.columns([1, 2])
    with col_input1:
        parking_hours = st.number_input("이용 예정 시간 (시간)", min_value=0, max_value=24, value=2, step=1)
        parking_mins = st.number_input("이용 예정 시간 (분)", min_value=0, max_value=59, value=0, step=10)
        total_calc_mins = (parking_hours * 60) + parking_mins
        
        top_n = st.slider("추천받을 주차장 수", min_value=3, max_value=20, value=5)
        
    with col_input2:
        st.write(f"⏱️ **총 주차 시간:** `{parking_hours}시간 {parking_mins}분` ({total_calc_mins}분)")
        
        calc_df = df_filtered.copy()
        calc_df['예상_주차요금'] = calc_df.apply(lambda r: calculate_parking_fee(r, total_calc_mins), axis=1)
        
        # 요금 순 정렬
        cheapest_df = calc_df.sort_values(by=['예상_주차요금', '총 주차면'], ascending=[True, False]).head(top_n)
        
        st.markdown(f"### 🏆 {selected_gu} 최저가 주차장 TOP {top_n}")
        
        for idx, r in cheapest_df.reset_index(drop=True).iterrows():
            fee_text = "🆓 무료" if r['예상_주차요금'] == 0 else f"💵 {r['예상_주차요금']:,} 원"
            st.markdown(f"""
            <div class="metric-card">
                <span style="font-size:1.1rem; font-weight:bold;">{idx+1}. {r['주차장명']}</span> 
                <span style="float:right; font-size:1.2rem; font-weight:bold; color:#2563EB;">{fee_text}</span><br>
                <small>📍 {r['주소']} | 🚗 총 {int(r['총 주차면'])}면 | 📞 {r.get('전화번호','-')}</small>
            </div>
            """, unsafe_allow_html=True)

    # 요금 비교 차트
    if not cheapest_df.empty:
        st.markdown("---")
        fig_fee = px.bar(
            cheapest_df,
            x='주차장명',
            y='예상_주차요금',
            text='예상_주차요금',
            title=f"가장 저렴한 주차장 예상 요금 비교 ({total_calc_mins}분 이용 기준)",
            color='예상_주차요금',
            color_continuous_scale='Blues'
        )
        fig_fee.update_traces(texttemplate='%{text:,}원', textposition='outside')
        fig_fee.update_layout(xaxis_tickangle=-30, height=400)
        st.plotly_chart(fig_fee, use_container_width=True)

# ------------------------------------------
# TAB 4: 랜덤 추천 (오늘의 운수 좋은 주차장)
# ------------------------------------------
with tab4:
    st.subheader("🎲 조건 기반 랜덤 주차장 추천")
    st.write("선택한 필터 조건 내에서 주차장을 랜덤으로 선택합니다.")
    
    if st.button("🎲 주차장 뽑기!", type="primary"):
        if df_filtered.empty:
            st.error("선택한 조건에 해당하는 주차장이 없습니다. 사이드바 필터를 변경해 주세요.")
        else:
            random_row = df_filtered.sample(n=1).iloc[0]
            
            st.markdown(f"""
            <div class="recommend-card">
                <h2>🎉 추천 주차장: {random_row['주차장명']}</h2>
                <hr>
                <p><b>📍 주소:</b> {random_row['주소']}</p>
                <p><b>🏛️ 자치구:</b> {random_row['자치구']} | <b>🏢 종류:</b> {random_row['주차장 종류명']}</p>
                <p><b>💰 기본 요금:</b> {int(random_row['기본 주차 요금']):,}원 / {int(random_row['기본 주차 시간(분 단위)'])}분</p>
                <p><b>🚗 총 주차면수:</b> {int(random_row['총 주차면'])}면</p>
                <p><b>📞 전화번호:</b> {random_row.get('전화번호', '정보 없음')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 지도 표시
            if pd.notna(random_row['위도']) and pd.notna(random_row['경도']):
                r_map = folium.Map(location=[random_row['위도'], random_row['경도']], zoom_start=15)
                folium.Marker(
                    location=[random_row['위도'], random_row['경도']],
                    popup=random_row['주차장명'],
                    icon=folium.Icon(color='red', icon='star')
                ).add_to(r_map)
                st_folium(r_map, width=None, height=350, use_container_width=True)

# ------------------------------------------
# TAB 5: 자치구별 통계 & 시각화 그래프
# ------------------------------------------
with tab5:
    st.subheader("📊 서울시 공영주차장 현황 데이터 분석")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # 1. 자치구별 주차장 수
        gu_counts = df_raw['자치구'].value_counts().reset_index()
        gu_counts.columns = ['자치구', '주차장수']
        fig1 = px.bar(
            gu_counts, 
            x='자치구', 
            y='주차장수', 
            title="자치구별 공영주차장 수",
            color='주차장수',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_g2:
        # 2. 유/무료 주차장 비율
        pay_type_counts = df_raw['유무료구분명'].value_counts().reset_index()
        pay_type_counts.columns = ['구분', '수량']
        fig2 = px.pie(
            pay_type_counts, 
            values='수량', 
            names='구분', 
            title="서울시 공영주차장 유/무료 비율",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig2, use_container_width=True)

    col_g3, col_g4 = st.columns(2)
    
    with col_g3:
        # 3. 자치구별 평균 1시간 주차 요금
        avg_fee_gu = df_raw[df_raw['1시간_추정요금'] > 0].groupby('자치구')['1시간_추정요금'].mean().reset_index()
        avg_fee_gu = avg_fee_gu.sort_values(by='1시간_추정요금', ascending=False)
        fig3 = px.bar(
            avg_fee_gu, 
            x='자치구', 
            y='1시간_추정요금', 
            title="자치구별 평균 1시간 주차 요금 (원)",
            color='1시간_추정요금',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_g4:
        # 4. 최대 주차면수 탑 10 주차장
        top_capacity = df_raw.sort_values(by='총 주차면', ascending=False).head(10)
        fig4 = px.bar(
            top_capacity, 
            x='주차장명', 
            y='총 주차면', 
            title="서울시 최대 규모 공영주차장 TOP 10 (주차면수)",
            color='총 주차면',
            color_continuous_scale='Teal'
        )
        fig4.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig4, use_container_width=True)
