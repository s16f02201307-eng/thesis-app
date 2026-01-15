import streamlit as st
from PIL import Image
import os
import requests

# ==========================================
# ★ Googleフォーム設定（抽出したIDを反映済み） ★
# ==========================================
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd5N7c-TevI37lnUok95swdvbBsckYJqiQKgqtVslbSjEXU3g/formResponse"

# 抽出した8つのIDを各問に割り当て
ENTRY_IDS = {
    "ex1": "entry.570602587",   # 問1: 四聖堂(標準レンズ)-軒ぞり
    "ex2": "entry.430214277",   # 問2: 四聖堂(標準レンズ)-美しさ
    "ex3": "entry.1985209908",  # 問3: 四聖堂(広角レンズ)-軒ぞり
    "ex4": "entry.1184762339",  # 問4: 四聖堂(広角レンズ)-美しさ
    "ex5": "entry.912116220",   # 問5: 南泉寺(標準レンズ)-軒ぞり
    "ex6": "entry.1339626492",  # 問6: 南泉寺(標準レンズ)-美しさ
    "ex7": "entry.1474939900",  # 問7: 南泉寺(広角レンズ)-軒ぞり
    "ex8": "entry.854426154",   # 問8: 南泉寺(広角レンズ)-美しさ
}

# 画像フォルダと評価タスクの定義
experiments = {
    "ex1": {"name": "四聖堂 (標準)", "folder": "四聖堂1500 35mm", "task": "【軒ぞり】を最も強く感じるポイント"},
    "ex2": {"name": "四聖堂 (標準)", "folder": "四聖堂1500 35mm", "task": "あなたが【最も美しい】と思うポイント"},
    "ex3": {"name": "四聖堂 (広角)", "folder": "四聖堂1500 10mm", "task": "【軒ぞり】を最も強く感じるポイント"},
    "ex4": {"name": "四聖堂 (広角)", "folder": "四聖堂1500 10mm", "task": "あなたが【最も美しい】と思うポイント"},
    "ex5": {"name": "南泉寺 (標準)", "folder": "南泉寺 35mm", "task": "【軒ぞり】を最も強く感じるポイント"},
    "ex6": {"name": "南泉寺 (標準)", "folder": "南泉寺 35mm", "task": "あなたが【最も美しい】と思うポイント"},
    "ex7": {"name": "南泉寺 (広角)", "folder": "南泉寺 10mm", "task": "【軒ぞり】を最も強く感じるポイント"},
    "ex8": {"name": "南泉寺 (広角)", "folder": "南泉寺 10mm", "task": "あなたが【最も美しい】と思うポイント"},
}

# 表示順序
display_order = ["ex1", "ex2", "ex3", "ex4", "ex5", "ex6", "ex7", "ex8"]

# ==========================================

base_img_folder = "."

st.set_page_config(page_title="建築の視覚実験", layout="centered")
st.markdown("""<style>.stTabs [data-baseweb="tab-list"] { gap: 10px; } .stTabs [data-baseweb="tab"] { height: 50px; }</style>""", unsafe_allow_html=True)

st.title("建築の視覚実験")
st.write("各タブで画像をスライドさせ、指示された距離を選んでください。")
st.info("①～⑧まで全八問あります。ご協力お願いします")

# セッション状態の初期化
if 'answers' not in st.session_state:
    st.session_state.answers = {}

for key in experiments.keys():
    if key not in st.session_state.answers:
        st.session_state.answers[key] = 0

if 'submitted' not in st.session_state:
    st.session_state.submitted = False

if st.session_state.submitted:
    st.success("✅ 送信完了！ご協力ありがとうございました。")
    st.balloons()
    st.stop()

# タブの作成
tabs = st.tabs([f"問{i+1}" for i in range(len(display_order))])

def show_ex(tab, key, question_num):
    with tab:
        exp = experiments[key]
        path = os.path.join(base_img_folder, exp["folder"])
        
        if not os.path.exists(path):
            st.error(f"エラー: 画像フォルダが見つかりません ({path})")
            return
            
        files = sorted([f for f in os.listdir(path) if f.endswith(".jpg")])
        if not files:
            st.error("画像ファイルが入っていません")
            return
        
        st.subheader(f"{question_num}. {exp['name']}")
        st.warning(f"指示：{exp['task']}")
        
        val = st.slider("距離調整", 0, len(files)-1, st.session_state.answers[key], key=f"s_{key}")
        st.session_state.answers[key] = val
        
        reversed_index = (len(files) - 1) - val
        file_to_show = files[reversed_index]
        st.image(Image.open(os.path.join(path, file_to_show)), caption=f"現在の位置: No.{reversed_index + 1}", use_container_width=True)

# 表示
for i, key in enumerate(display_order):
    show_ex(tabs[i], key, i+1)

st.markdown("---")
if st.button("送信する", type="primary"):
    data = {}
    valid = True
    for k in ENTRY_IDS:
        path = os.path.join(base_img_folder, experiments[k]["folder"])
        if not os.path.exists(path):
             valid = False
             continue
        files = sorted([f for f in os.listdir(path) if f.endswith(".jpg")])
        
        slider_val = st.session_state.answers[k]
        real_no = (len(files) - 1) - slider_val + 1
        data[ENTRY_IDS[k]] = real_no

    if valid:
        try:
            if requests.post(FORM_URL, data=data).status_code == 200:
                st.session_state.submitted = True
                st.rerun()
            else: 
                st.error("送信に失敗しました。繰り返し起きてしまう場合はお手数ですがこちらに数値を入力してください→→→→→　https://forms.gle/XvdWU5KBS9vbGkZe6")
        except: 
            st.error("もう一度押してください")
    else:
        st.error("画像フォルダエラーのため送信できません")
