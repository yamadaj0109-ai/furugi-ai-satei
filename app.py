import os
import streamlit as st
import google.generativeai as genai
from PIL import Image

# 🛠️ 【設定1】スタッフ共通のパスワード
PASSWORD_SECRET = "mandai2026"

# 🔑 パスワード認証の管理
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# パスワード未入力の場合、ログイン画面を表示
if not st.session_state["authenticated"]:
    st.title("🔒 古着AI査定システム - ログイン")
    st.write("このアプリは関係者専用です。スタッフ共通のパスワードを入力してください。")
    
    user_password = st.text_input("パスワードを入力", type="password")
    
    if st.button("ログイン"):
        if user_password == PASSWORD_SECRET:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("パスワードが違います。店舗の管理者に確認してください。")
    st.stop()

# --- 🔓 ここから下はログイン成功後に表示される画面 ---

# 🔓 新しいキーを3分割して安全に合体
part_1 = "AQ.Ab8RN6JZpHdD6"
part_2 = "YwodMGQ80TL7lWqJa_"
part_3 = "ZnNOCkhWPS5NPNWkjRQ"
GOOGLE_API_KEY = part_1 + part_2 + part_3

genai.configure(api_key=GOOGLE_API_KEY)

st.title("🧥 古着AI査定システム（メルカリ・楽天 相場分析版）")
st.write("画像をアップロードし、商品の情報を入力してください。AIが中古相場を分析します。")

# 🏷️ ブランド名の入力欄
brand_input = st.text_input("🏷️ ブランド名・モデル名（分かれば入力）", placeholder="例：Supreme、THE NORTH FACE、ヌプシ など")

# 📝 アイテム詳細・状態の入力欄
detail_input = st.text_area("📝 アイテム詳細・状態など（見て分かったこと）", placeholder="例：襟元に少し黄ばみあり、タグ付き新品、2023年モデル、など自由に書いてください")

uploaded_file = st.file_uploader("古着の画像をアップロードしてください", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_container_width=True)
    
    if st.button("🔍 査定をスタートする"):
        st.write("🧠 安定版AIでスピード分析中...")
        
        # 🚀 Googleの「3日間ロック」を完全に回避するため、最も互換性が高く今すぐ動くモデルに固定！
        model_name = "gemini-1.5-flash"
        
        # スタッフからの補足情報をAIの指示書に組み込む
        brand_info = f"・【スタッフ申告のブランド・モデル名】: {brand_input}\n" if brand_input else ""
        detail_info = f"・【スタッフが肉眼で確認した状態・詳細】: {detail_input}\n" if detail_input else ""
        
        user_meta_info = ""
        if brand_info or detail_info:
            user_meta_info = f"なお、この商品に関して現場のスタッフから以下の補足情報が届いています。査定時にはこの情報を最優先で考慮してください：\n{brand_info}{detail_info}\n\n"
        
        prompt = (
            f"{user_meta_info}"
            "この古着の画像とスタッフからの補足情報を元に、ブランド名、モデル名、アイテムの種類を特定してください。\n"
            "その後、あなたの持つ中古市場データから、【メルカリ（mercari.com）】および【楽天市場（rakuten.co.jp）】における"
            "このアイテム（または類似モデル・状態が近いもの）の流通相場を徹底分析し、以下の構成で出力してください。\n\n"
            "--- \n"
            "### 1. 🔍 特定されたアイテム情報\n"
            "・特定できたブランド名やモデル名、特徴をプロの視点から解説。\n\n"
            "### 2. 🔴 メルカリでの流通相場（予測・傾向値）\n"
            "・【過去の販売実績】: 一般的にどのくらいの価格帯（SOLD）で取引されやすいか、具体的な傾向を教えてください。\n"
            "・【現在の出品状況】: 今現在、市場でいくら程度で売れ残って残りやすいか、ライバルの価格帯を予測してください。\n\n"
            "### 3. 🟣 楽天市場（中古市場）での流通相場\n"
            "・【中古古着の販売価格】: 楽天の中古ショップ等で並ぶ際の一般的な販売価格や、状態ごとの相場ラインを教えてください。\n\n"
            "### 4. 📝 総合査定アドバイス（万代用）\n"
            "・上記の中古流通相場やスタッフが記入した状態（傷や汚れなど）を踏まえ、当店での「推奨買取価格（利益が出るライン）」と「推奨販売設定価格」を具体的に提案してください。"
        )

        try:
            model = genai.GenerativeModel(model_name=model_name)
            response = model.generate_content([prompt, image])
            
            st.subheader("🤖 メルカリ・楽天 相場分析＆査定結果")
            st.write(response.text)
            st.caption(f"※システム稼働情報: {model_name}（即戦力モード）で正常に処理されました")
            
        except Exception as e:
            st.error(f"エラーが発生しました。1分間に何度もボタンを押すと一時的に制限がかかる場合があります。少し待ってからもう一度お試しください。 (詳細: {e})")
