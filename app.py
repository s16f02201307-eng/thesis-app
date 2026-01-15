import streamlit as st
from PIL import Image
import os
import requests

# ==========================================
# ★ここに、履歴から救出した「正しいID」を戻してください！★
# ==========================================
# フォームIDとエントリーIDを履歴のURLから復元しました
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd5N7c-TevI37lnUok95swdvbBsckYJqiQKgqtVslbSjEXU3g/formResponse"

ENTRY_IDS = {
    "ex1": "entry.570602587",   # 四聖堂 標準
    "ex2": "entry.430214277",   # 四聖堂 広角
    "ex3": "entry.1985209908",  # 南泉寺 標準
    "ex4": "entry.1184762339"   # 南泉寺 広角
}
# ==========================================

# 画像フォルダ設定
base_img_folder = "."

# ... (以下、元のコードと同じ)
experiments = {
    "ex1": {"name": "四聖堂 (標準)", "folder": "四聖堂1500 35mm"},
    "ex2": {"name": "四聖堂 (広角)", "folder": "四聖堂1500 10mm"},
    "ex3": {"name": "南泉寺 (標準)", "folder": "南泉寺 35mm"},
    "ex4": {"name": "南泉寺 (広角)", "folder": "南泉寺 10mm"},
}

st.set_page_config(page_title="建築の視覚実験", layout="centered")
st.markdown("""<style>.stTabs [data-baseweb="tab-list"] { gap: 10px; } .stTabs [data-baseweb="tab"] { height: 50px; }</style>""", unsafe_allow_html=True)

st.title("建築の視覚実験")
st.write("各タブで画像をスライドさせ、最も好ましい距離を選んでください。")
st.info("※スライダーを左（初期位置）にすると「手前」、右に動かすと「一番奥」に移動します。")

if 'answers' not in st.session_state:
    st.session_state.answers = {"ex1": 0, "ex2": 0, "ex3": 0, "ex4": 0}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

if st.session_state.submitted:
    st.success("✅ 送信完了！ご協力ありがとうございました。")
    st.balloons()
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["① 四聖堂 標準", "② 四聖堂 広角", "③ 南泉寺 標準", "④ 南泉寺 広角"])

def show_ex(tab, key):
    with tab:
        path = os.path.join(base_img_folder, experiments[key]["folder"])
        # エラー処理
        if not os.path.exists(path):
            st.error(f"エラー: 画像フォルダが見つかりません ({path})")
            return
        files = sorted([f for f in os.listdir(path) if f.endswith(".jpg")])
        if not files:
            st.error("画像ファイルが入っていません")
            return
        
        st.subheader(experiments[key]["name"])
        
        # スライダー作成
        val = st.slider("距離調整", 0, len(files)-1, st.session_state.answers[key], key=f"s_{key}")
        st.session_state.answers[key] = val
        
        # ★修正2: 逆転ロジック (左=奥No.Max, 右=手前No.1)
        # files[0]がNo.1(手前)と仮定すると、逆順にするには:
        reversed_index = (len(files) - 1) - val
        
        # 画像表示
        file_to_show = files[reversed_index]
        st.image(Image.open(os.path.join(path, file_to_show)), caption=f"現在の位置: No.{reversed_index + 1}", use_container_width=True)

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
        if not os.path.exists(path):
             valid = False
             continue
        files = sorted([f for f in os.listdir(path) if f.endswith(".jpg")])
        
        # 逆転計算した「本当のNo」を計算
        slider_val = st.session_state.answers[k]
        real_no = (len(files) - 1) - slider_val + 1
        
        data[ENTRY_IDS[k]] = real_no

    if valid:
        try:
            if requests.post(FORM_URL, data=data).status_code == 200:
                st.session_state.submitted = True
                st.rerun()
            else: st.error("送信に失敗しました。繰り返し起きてしまう場合はお手数ですがこちらに数値を入力してください→→→→→　https://forms.gle/XvdWU5KBS9vbGkZe6")
        except: st.error("エラーが発生しました")
    else:
        st.error("画像フォルダエラーのため送信できません")




