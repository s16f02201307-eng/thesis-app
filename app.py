import streamlit as st
from PIL import Image
import os
import requests

# ==========================================
# ★設定エリア（あなたのURLから抽出しました！）★
# ==========================================

# 1. Googleフォームの送信先URL
# (viewform を formResponse に書き換え済みです)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd5N7c-TevI37lnUok95swdvbBsckYJqiQKgqtVslbSjEXU3g/formResponse"

# 2. 質問項目のID
# (いただいたURLの順番通りに割り当てました)
ENTRY_IDS = {
    "ex1": "entry.570602587",   # 四聖堂 35mm
    "ex2": "entry.430214277",   # 四聖堂 10mm
    "ex3": "entry.1985209908",  # 南泉寺 35mm
    "ex4": "entry.1184762339"   # 南泉寺 10mm
}
# ==========================================

base_img_folder = "images"

# 実験の構成
experiments = {
    "ex1": {"name": "四聖堂 (標準 35mm)", "folder": "四聖堂1500 35mm"},
    "ex2": {"name": "四聖堂 (広角 10mm)", "folder": "四聖堂1500 10mm"},
    "ex3": {"name": "南泉寺 (標準 35mm)", "folder": "南泉寺 35mm"},
    "ex4": {"name": "南泉寺 (広角 10mm)", "folder": "南泉寺 10mm"},
}

st.set_page_config(page_title="建築空間の視覚実験", layout="centered")

# --- デザイン調整 ---
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; }
    .stButton button { width: 100%; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("建築空間の視覚実験")
st.write("ご協力ありがとうございます。以下の4つのタブを切り替えて、それぞれの空間で**「最も好ましい」**と感じる距離を選んでください。")

# --- データの保持 ---
if 'answers' not in st.session_state:
    st.session_state.answers = {"ex1": 0, "ex2": 0, "ex3": 0, "ex4": 0}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# --- 送信完了時の画面 ---
if st.session_state.submitted:
    st.success("✅ 送信が完了しました！")
    st.info("ご協力ありがとうございました。ブラウザを閉じて終了してください。")
    st.stop()

# --- タブの作成 ---
tab1, tab2, tab3, tab4 = st.tabs(["① 四聖堂 35mm", "② 四聖堂 10mm", "③ 南泉寺 35mm", "④ 南泉寺 10mm"])

# --- 実験画面を作る関数 ---
def show_experiment(tab, ex_key):
    with tab:
        info = experiments[ex_key]
        folder_path = os.path.join(base_img_folder, info["folder"])
        
        # フォルダチェック
        if not os.path.exists(folder_path):
            st.error(f"エラー: 画像フォルダ '{info['folder']}' が見つかりません。")
            return

        # 画像読み込み
        files = sorted([f for f in os.listdir(folder_path) if f.endswith(".jpg")])
        if not files:
            st.error("エラー: 画像が入っていません。")
            return

        st.subheader(info["name"])
        
        # スライダー
        val = st.slider(
            "スライダーを動かして距離を調整してください", 
            0, len(files)-1, 
            st.session_state.answers[ex_key],
            key=f"slider_{ex_key}"
        )
        st.session_state.answers[ex_key] = val

        # 画像表示
        img_path = os.path.join(folder_path, files[val])
        image = Image.open(img_path)
        st.image(image, caption=f"現在の視点: No. {val + 1}", use_container_width=True)

# 各タブに中身を表示
show_experiment(tab1, "ex1")
show_experiment(tab2, "ex2")
show_experiment(tab3, "ex3")
show_experiment(tab4, "ex4")

st.markdown("---")
st.header("確認と送信")

# 確認表示
col1, col2 = st.columns(2)
with col1:
    st.info(f"**四聖堂 35mm:** No.{st.session_state.answers['ex1'] + 1}")
    st.info(f"**四聖堂 10mm:** No.{st.session_state.answers['ex2'] + 1}")
with col2:
    st.info(f"**南泉寺 35mm:** No.{st.session_state.answers['ex3'] + 1}")
    st.info(f"**南泉寺 10mm:** No.{st.session_state.answers['ex4'] + 1}")

st.write("全ての選択が終わったら、下のボタンを押してください。")

# 送信ボタン
if st.button("この内容で送信する", type="primary"):
    # Googleフォームへ送るデータ
    # (+1 しているのは、プログラムの「0番」を人間の「1番」に直すため)
    form_data = {
        ENTRY_IDS["ex1"]: st.session_state.answers['ex1'] + 1,
        ENTRY_IDS["ex2"]: st.session_state.answers['ex2'] + 1,
        ENTRY_IDS["ex3"]: st.session_state.answers['ex3'] + 1,
        ENTRY_IDS["ex4"]: st.session_state.answers['ex4'] + 1
    }
    
    try:
        # 裏側でひっそり送信
        response = requests.post(FORM_URL, data=form_data)
        
        if response.status_code == 200:
            st.session_state.submitted = True
            st.rerun() # 画面更新して完了メッセージへ
        else:
            st.error("送信に失敗しました。もう一度押してみてください。")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")