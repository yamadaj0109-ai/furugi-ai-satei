import streamlit as st
import google.generativeai as genai
from PIL import Image

# 🛠️ 【設定】スタッフ共通のパスワード
PASSWORD_SECRET = "mandaifurugi"

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

# Gemini APIの設定
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "YOUR_DEFAULT_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

st.title("🧥 古着AI査定システム（メルカリ・楽天 相場特化版）")
st.write("画像をアップロードすると、メルカリや楽天市場から「過去の売値」と「現在の出品価格」をリサーチします。")

uploaded_file = st.file_uploader("古着の画像をアップロードしてください", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_container_width=True)
    
    st.write("🔍 メルカリと楽天市場の最新情報をリアルタイム検索中...")
    
    try:
        # 🌐 Google検索機能をONにしてモデルを起動
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=[{"google_search": {}}]
        )
        
        prompt = (
            "この古着の画像からブランド名、モデル名、アイテムの種類を特定してください。\n"
            "その後、Google検索を駆使して【メルカリ（mercari.com）】および【楽天市場（rakuten.co.jp）】の中古市場から、"
            "このアイテムと同一、または酷似している商品のリサーチを行い、以下の構成で出力してください。\n\n"
            "--- \n"
            "### 1. 🔍 特定されたアイテム情報\n"
            "・特定できたブランド名やモデル名、特徴を簡潔に。\n\n"
            "### 2. 🔴 メルカリでの流通相場\n"
            "・【過去の販売実績】: どのくらい前（○ヶ月前、最近、など）に、いくら（○円）で売り切れている（SOLD）か、具体的な取引例を出してください。\n"
            "・【現在の出品状況】: 今現在、売れ残って出品中の同一商品がいくら（○円程度）で市場に残っているかを調べてください。\n\n"
            "### 3. 🟣 楽天市場（中古市場）での流通相場\n"
            "・【過去・現在の価格】: 楽天に出品されている（または過去にあった）中古古着の販売価格や、現在の最安値・最高値のラインを教えてください。\n\n"
            "### 4. 📝 総合査定アドバイス（万代用）\n"
            "・上記のリサーチ結果を踏まえ、当店での「推奨買取価格（これくらいで買えば利益が出る）」と「推奨販売設定価格」をプロとして提案してください。\n\n"
            "### 🔗 参考にしたページ（情報元）\n"
            "・検索で見つけたメルカリや楽天の具体的な商品ページや検索結果のURLを、クリックできるリンク形式で箇条書きで必ず載せてください。"
        )
        
        response = model.generate_content([prompt, image])
        
        st.subheader("🤖 メルカリ・楽天 リサーチ＆査定結果")
        st.write(response.text)
        
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
