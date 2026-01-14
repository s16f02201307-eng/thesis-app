import streamlit as st
from PIL import Image
import os
import requests

# ==========================================
# ★設定完了：あなたのGoogleフォーム情報★
# ==========================================
# 送信先URL
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd5N7c-TevI37lnUok95swdvbBsckYJqiQKgqtVslbSjEXU3g/formResponse"

# 質問ID（URLから解析しました）
# ※作成順序通り: 四聖堂35mm -> 四聖堂10mm -> 南泉寺35mm -> 南泉寺10mm と仮定しています
ENTRY_IDS = {
    "ex1": "entry.570602587",   # 四聖堂 35mm
    "ex2": "entry.430214277",   # 四聖堂 10mm
    "ex3": "entry.1985209908",  # 南泉寺 35mm
    "ex4": "entry.1184762339"   # 南泉寺 10mm
}
# ==========================================

# ★修正1: 画像フォルダの場所を「.（ここ）」に変更
base_img_folder = "."

experiments = {
    "ex1": {"name": "四聖堂 (標準 35mm)", "folder": "四聖堂1500 35mm"},
    "ex2": {"name": "四聖堂 (広角 10mm)", "folder": "四聖堂1500 10mm"},
    "ex3": {"name": "南泉寺 (標準 35mm)", "folder": "南泉寺 35mm"},
    "ex4": {"name": "南泉寺 (広角 10mm)", "folder": "南泉寺 10mm"},
}

st.set_page_config(page_title="建築空間の視覚実験", layout="centered")
st.markdown("""<style>.stTabs [data-baseweb="tab-list"] { gap: 10px; } .stTabs [data-baseweb="tab"] { height: 50px; }</style>""", unsafe_allow_html=True)

st.title("建築空間の視覚実験")
st.write("各タブで画像をスライドさせ、最も好ましい距離を選んでください。")
st.info("※スライダーを左（初期位置）にすると「一番奥」、右に動かすと「手前」に移動します。")

# セッション状態の初期化
if 'answers' not in st.session_state:
    st.session_state.answers = {"ex1": 0, "ex2": 0, "ex3": 0, "ex4": 0}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# 送信完了画面
if st.session_state.submitted:
    st.success("✅ 送信完了！ご協力ありがとうございました。")
    st.balloons()
    st.stop()

# タブ作成
tab1, tab2, tab3, tab4 = st.tabs(["① 四聖堂 35mm", "② 四聖堂 10mm", "③ 南泉寺 35mm", "④ 南泉寺 10mm"])

def show_ex(tab, key):
    with tab:
        path = os.path.join(base_img_folder, experiments[key]["folder"])
        
        # フォルダチェック
        if not os.path.exists(path):
            st.error(f"エラー: 画像フォルダが見つかりません ({path})")
            return
            
        files = sorted([f for f in os.listdir(path) if f.endswith(".jpg")])
        
        # ファイルチェック
        if not files:
            st.error("画像ファイルが入っていません")
            return
        
        st.subheader(experiments[key]["name"])
        
        # スライダー作成 (0 〜 枚数-1)
        val = st.slider("距離調整", 0, len(files)-1, st.session_state.answers[key], key=f"s_{key}")
        st.session_state.answers[key] = val
        
        # ★修正2: 逆転ロジック (左=奥No.Max, 右=手前No.1)
        # スライダー0のとき -> 最後の画像(一番奥)
        # スライダーMaxのとき -> 最初の画像(一番手前)
        reversed_index = (len(files) - 1) - val
        
        # 画像表示
        file_to_show = files[reversed_index]
        st.image(Image.open(os.path.join(path, file_to_show)), caption=f"現在の位置: No.{reversed_index + 1}", use_container_width=True)

# 各タブの中身を表示
show_ex(tab1, "ex1")
show_ex(tab2, "ex2")
show_ex(tab3, "ex3")
show_ex(tab4, "ex4")

st.markdown("---")
if st.button("送信する", type="primary"):
    # データ送信処理
    data = {}
    valid = True
    
    for k in ENTRY_IDS:
        path = os.path.join(base_img_folder, experiments[k]["folder"])
        
        # フォルダが存在するか確認
        if not os.path.exists(path):
             valid = False
             continue
             
        files = sorted([f for f in os.listdir(path) if f.endswith(".jpg")])
        if not files:
            valid = False
            continue

        # 逆転計算した「本当のNo」を計算してセット
        slider_val = st.session_state.answers[k]
        real_no = (len(files) - 1) - slider_val + 1
        
        data[ENTRY_IDS[k]] = real_no

    if valid:
        try:
            # Googleフォームへ送信
            response = requests.post(FORM_URL
