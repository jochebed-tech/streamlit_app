import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="말랑말랑 MBTI 육아 대화법",
    page_icon="🧸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 파스텔톤 사랑스러운 커스텀 CSS 적용
st.markdown("""
    <style>
    /* 메인 배경색 및 폰트 설정 */
    .stApp {
        background-color: #FFF9FA;
        font-family: 'Pretendard', sans-serif;
    }
    
    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: #FFF0F5;
        border-right: 1px solid #FFE4E1;
    }
    
    /* 메인 타이틀 박스 */
    .title-box {
        background: linear-gradient(135deg, #FFB6C1 0%, #FFD1DC 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 20px rgba(255, 182, 193, 0.3);
        margin-bottom: 2rem;
    }
    .title-box h1 {
        color: white !important;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    /* 카드 스타일링 */
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        border: 1px solid #FFE4E1;
        margin-bottom: 1rem;
    }
    
    /* 추천 대화 / 금지 대화 박스 */
    .bad-speak {
        background-color: #FFF0F0;
        border-left: 5px solid #FF6B6B;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 0.5rem;
    }
    .good-speak {
        background-color: #F0FDF4;
        border-left: 5px solid #4ADE80;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 0.5rem;
    }
    
    /* 탭 디자인 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        border: 1px solid #FFE4E1;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFB6C1 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 데이터베이스 (MBTI별 특성 및 훈육법)
MBTI_DATA = {
    "NF (진심과 감정이 중요한 아이 - ENFP, ENFJ, INFP, INFJ)": {
        "mbti_list": ["ENFP", "ENFJ", "INFP", "INFJ"],
        "traits": "감수성이 풍부하고 상상력이 뛰어납니다. 비난에 민감하므로 마음을 먼저 읽어주는 것이 중요해요.",
        "tips": [
            "비판보다는 **공감**을 먼저 해주세요.",
            "아이의 **동기와 마음(의도)**에 집중해 주세요.",
            "직접적인 지적보다는 **자연스러운 대화**로 깨닫게 해주세요."
        ],
        "scenarios": {
            "🛒 마트에서 떼쓸 때": {
                "bad": "너 자꾸 떼쓰면 다시는 마트 안 와!",
                "good": "이 장난감이 정말 마음에 들었구나~ 갖고 싶어 하는 마음은 알겠어. 하지만 오늘은 구경하기로 약속했으니까 사진으로 남겨둘까?"
            },
            "📱 스마트폰만 할 때": {
                "bad": "게임 좀 그만해! 눈 나빠지고 공부는 언제 할 거야?",
                "good": "이 게임이 정말 재미있나 보네! 엄마/아빠한테도 보여줄래? 다 하고 나면 같이 맛있는 간식 먹으면서 얘기하자."
            },
            "📝 할 일을 미룰 때": {
                "bad": "너 아직도 안 했어? 빨리 안 해?",
                "good": "지금 시작하기 조금 귀찮고 힘들구나? 그래도 끝내고 나면 마음이 참 편해질 거야. 엄마가 옆에 있어줄까?"
            }
        }
    },
    "NT (이리와 논리가 필요한 아이 - ENTP, ENTJ, INTP, INTJ)": {
        "mbti_list": ["ENTP", "ENTJ", "INTP", "INTJ"],
        "traits": "호기심이 많고 '왜'에 대한 답이 중요합니다. 감정적 호소보다는 논리적인 이유를 설명해야 수긍합니다.",
        "tips": [
            "감정적인 강요 대신 **분명한 이유**를 설명하세요.",
            "아이가 스스로 선택할 수 있도록 **옵션**을 주세요.",
            "아이의 의견을 존중하며 **논리적인 규칙**을 함께 만드세요."
        ],
        "scenarios": {
            "🛒 마트에서 떼쓸 때": {
                "bad": "안 돼! 안 된다면 안 되는 줄 알아!",
                "good": "오늘은 우리가 XX만 사기로 예산을 정하고 왔어. 지금 이걸 사면 예산을 넘어가는데, 다음 용돈 때 사는 건 어떨까?"
            },
            "📱 스마트폰만 할 때": {
                "bad": "스마트폰 압수야! 당장 이리 내!",
                "good": "스마트폰을 너무 오래 하면 뇌가 쉬지 못해서 네가 좋아하는 퀴즈나 블록놀이를 할 때 집중하기 어려워져. 10분 뒤에 끌까, 15분 뒤에 끌까?"
            },
            "📝 할 일을 미룰 때": {
                "bad": "숙제 안 하면 나중에 고생한다!",
                "good": "지금 숙제를 먼저 끝내면 나중에 너한테 2시간의 자유 시간이 완전히 생겨. 어느 쪽이 더 효율적일까?"
            }
        }
    },
    "SF (현실적이고 다정한 아이 - ESFP, ESFJ, ISFP, ISFJ)": {
        "mbti_list": ["ESFP", "ESFJ", "ISFP", "ISFJ"],
        "traits": "칭찬과 인정을 좋아하며 칭찬을 들을 때 가장 잘 움직입니다. 구체적인 행동 가이드를 주는 것이 좋습니다.",
        "tips": [
            "작은 노력도 **아낌없이 칭찬**해 주세요.",
            "구체적이고 **실제적인 행동 방식**을 알려주세요.",
            "주변 사람들과의 관계를 활용해 긍정적 자극을 주세요."
        ],
        "scenarios": {
            "🛒 마트에서 떼쓸 때": {
                "bad": "너 창피하게 왜 이래? 다 쳐다보잖아!",
                "good": "이게 갖고 싶었구나. 하지만 오늘은 사기로 한 날이 아니야. 착하게 잘 참으면 집에 가서 맛있는 과자 먹자!"
            },
            "📱 스마트폰만 할 때": {
                "bad": "폰만 보지 말고 제발 움직여라!",
                "good": "OO이가 좋아하는 요리 놀이 같이할까? 폰 내려놓고 엄마 도와주면 정말 기쁠 것 같아!"
            },
            "📝 할 일을 미룰 때": {
                "bad": "숙제 다 할 때까지 방에서 나오지 마!",
                "good": "숙제 1쪽만 먼저 다 풀면 좋아하는 간식 줄게! 한 쪽만 먼저 해볼까?"
            }
        }
    },
    "ST (규칙과 실행이 중요한 아이 - ESTP, ESTJ, ISTP, ISTJ)": {
        "mbti_list": ["ESTP", "ESTJ", "ISTP", "ISTJ"],
        "traits": "명확한 규칙과 즉각적인 피드백을 선호합니다. 모호한 말보다 구체적인 행동 목표를 정해주는 것이 효과적입니다.",
        "tips": [
            "**명확한 규칙과 한계**를 미리 설정하세요.",
            "감정적 기싸움 대신 **결과와 사실**에 기반해 대화하세요.",
            "지킬 수 있는 **보상과 처벌**을 명확히 하세요."
        ],
        "scenarios": {
            "🛒 마트에서 떼쓸 때": {
                "bad": "나중에 사줄 테니까 그만해!",
                "good": "마트 오기 전에 장난감은 안 사기로 규칙 정했지? 약속은 지켜야 해. 차에 가서 이야기하자."
            },
            "📱 스마트폰만 할 때": {
                "bad": "그만 좀 해라 좀!",
                "good": "알람 울렸다. 약속한 8시가 되었으니 타이머 끄고 폰 제자리에 둬."
            },
            "📝 할 일을 미룰 때": {
                "bad": "알아서 좀 선선히 해라!",
                "good": "8시부터 8시 30분까지 수학 2페이지 풀기. 다 하면 체크리스트에 동그라미 치자."
            }
        }
    }
}

# 4. 헤더 영역
st.markdown("""
    <div class="title-box">
        <h1>🧸 말랑말랑 MBTI 육아 대화법</h1>
        <p>우리 아이의 마음 문을 열어주는 맞춤형 훈육 솔루션</p>
    </div>
""", unsafe_allow_html=True)

# 5. 사이드바 - MBTI 선택
with st.sidebar:
    st.header("🎀 성향 선택하기")
    
    # 아이 그룹 선택
    selected_group_name = st.selectbox(
        "👧👦 아이의 MBTI 유형군을 선택해 주세요:",
        list(MBTI_DATA.keys())
    )
    
    # 부모 MBTI
    parent_mbti = st.selectbox(
        "👩👨 부모님의 MBTI:",
        ["잘 모르겠음", "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", 
         "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
    )
    
    st.divider()
    st.markdown("💡 **Tip**: 아이의 정확한 MBTI를 모른다면, 가장 가깝다고 느껴지는 유형군을 선택해 보세요!")

# 데이터 가져오기
group_info = MBTI_DATA[selected_group_name]

# 6. 메인 콘텐츠 (탭 구성)
tab1, tab2, tab3 = st.tabs(["✨ 맞춤 훈육가이드", "💬 상황별 대화법", "🔍 아이 MBTI 간단진단"])

# TAB 1: 맞춤 훈육 가이드
with tab1:
    st.subheader(f"🌱 {selected_group_name.split('(')[0]} 아이 특징")
    
    st.markdown(f"""
    <div class="card">
        <h4>💡 아이의 성향 특징</h4>
        <p>{group_info['traits']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🎯 이 유형의 아이를 다룰 때 핵심 원칙")
    col1, col2, col3 = st.columns(3)
    for idx, tip in enumerate(group_info['tips']):
        with [col1, col2, col3][idx]:
            st.markdown(f"""
            <div class="card" style="text-align: center; height: 100%;">
                <h3>0{idx+1}</h3>
                <p>{tip}</p>
            </div>
            """, unsafe_allow_scope=True)

    if parent_mbti != "잘 모르겠음":
        st.info(f"💡 **{parent_mbti} 부모님을 위한 조언**: 부모님의 성향과 아이의 성향이 다를 수 있어요. 부모님의 기준을 적용하기보다 아이의 시선에서 한 번 더 생각해 주시면 훈육 효과가 2배가 됩니다!")

# TAB 2: 상황별 대화법
with tab2:
    st.subheader("🗣️ 실전 상황별 대화 카드")
    
    scenario_choice = st.radio(
        "상황을 선택해 주세요:",
        list(group_info['scenarios'].keys()),
        horizontal=True
    )
    
    selected_scenario = group_info['scenarios'][scenario_choice]
    
    col_bad, col_good = st.columns(2)
    
    with col_bad:
        st.markdown(f"""
        <div class="bad-speak">
            <h4>❌ 이렇게 말하면 마음에 문을 닫아요 (금지어)</h4>
            <p style="font-size: 1.1rem; font-weight: bold; color: #D32F2F; margin-top: 10px;">
                "{selected_scenario['bad']}"
            </p>
        </div>
        """, unsafe_allow_scope=True)
        
    with col_good:
        st.markdown(f"""
        <div class="good-speak">
            <h4>⭕ 이렇게 말해보세요 (추천 대화법)</h4>
            <p style="font-size: 1.1rem; font-weight: bold; color: #2E7D32; margin-top: 10px;">
                "{selected_scenario['good']}"
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.success("💖 **훈육 꿀팁**: 아이가 감정적으로 격양되어 있을 때는 대화법보다 '안전한 장소에서 감정이 가라앉을 때까지 기다려주는 것'이 먼저입니다.")

# TAB 3: 아이 MBTI 간단 진단
with tab3:
    st.subheader("🔍 아이 성향 간단 자가진단 (약식)")
    st.write("아이의 평소 행동을 바탕으로 가장 적합한 성향 그룹을 찾아보세요.")
    
    q1 = st.radio("1. 아이가 새로운 친구나 장소에 갈 때 어떤가요?", ["먼저 다가가고 금방 친해진다 (E)", "처음엔 경계하고 시간이 걸린다 (I)"])
    q2 = st.radio("2. 아이가 말을 할 때 어떤 스타일인가요?", ["상상력이 풍부하고 '만약에~' 말을 많이 한다 (N)", "눈에 보이는 사실이나 구체적인 경험을 말한다 (S)"])
    q3 = st.radio("3. 아이가 서운하거나 화가 났을 때 더 중요한 것은?", ["엄마아빠가 내 기분을 공감해 주는 것 (F)", "왜 안 되는지 이유를 논리적으로 알려주는 것 (T)"])
    
    if st.button("결과 확인하기 🎈", type="primary"):
        res = ""
        res += "E" if "E" in q1 else "I"
        res += "N" if "N" in q2 else "S"
        res += "F" if "F" in q3 else "T"
        
        st.balloons()
        st.markdown(f"""
        <div class="card" style="text-align: center; background-color: #FFF0F5;">
            <h3>🎉 우리 아이는 <span style="color: #FF1493;">[{res}]</span> 성향과 가깝습니다!</h3>
            <p>사이드바에서 해당 성향이 포함된 그룹을 선택하여 맞춤 대화법을 확인해 보세요.</p>
        </div>
        """, unsafe_allow_scope=True)

# 푸터
st.divider()
st.caption("💌 본 앱은 아이의 개별 성향을 이해하고 따뜻하게 소통하기 위한 참고용 가이드입니다.")
