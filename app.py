import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import requests
import base64

# 画面の初期設定
st.set_page_config(page_title="古着AI査定システム", layout="centered")

st.title("👕 古着AI査定システム")
st.write("商品の写真をアップロードすると、二次流通のトレンドや市場価値を踏まえた高精度な査定を行います。")

# 🔑 あなたの本物の最新特権キー（ここに直接書いておくのが一番確実です！）
api_key = "AQ.Ab8RN6LxmHWS7CNhHAi6V2ofF0kUABnCA9etzpXL85A9-cgUUw"

# 写真のアップロード機能
uploaded_file = st.file_uploader("古着の画像をアップロード（複数枚は不可）", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた商品", use_container_width=True)
    
    if st.button("✨ 査定を開始する", type="primary"):
        with st.spinner("画像を分析中... トレンドや市場価値を計算しています..."):
            try:
                # 査定精度と価格ロジックを強化した指示書
                prompt = """
                あなたは日本国内のセカンドハンド（古着）市場に精通した、経験豊富なシニアバイヤー・査定士です。
                提出された画像からブランド、アイテムの種類、状態、年代（ヴィンテージ等）を的確に見極め、
                現在の日本の若者トレンド（Y2K、ストリート、シティボーイ、テック系など）や二次流通相場を考慮して査定を行ってください。

                特に【価格設定ルール】を厳格に守ってください：
                1. まず、現在の市場価値から「店頭販売想定価格」を算出してください。
                2. 「買取目安価格」は、その店頭販売想定価格の【4割（40%）】を基本ベース（基準）として計算してください。
                3. トレンド性が非常に高いものや、ヴィンテージ等の高付加価値商品である場合のみ、例外として【最大6割（60%）】まで引き上げて構いません。絶対に6割は超えないでください。
                4. ファストファッションやノーブランドの場合は、販売価格を低く設定し、買取価格も数十円〜数百円のリアルな数字（4割基準）にしてください。

                出力は必ず以下の【Markdownフォーマット】に従い、スタッフやお客様が見やすいように整理して出力してください。丁寧かつ落ち着いた口調（〜です、〜ます）でお願いします。

                ---
                ### 🏷️ 1. 商品の特定・特徴
                * **推定ブランド / アイテム名:** * **年代 / スタイル:** （例：90年代、Y2K、現行トレンドなど）
                * **デザインの特徴:** ### 📊 2. 状態（コンディション）分析
                * **想定ランク:** （S, A, B, C, Dのいずれかで評価）
                * **状態の補足:** （画像から見えるシワ、ヨレ、色褪せ、傷などの有無、または予測される注意点）

                ### 📈 3. トレンド・市場価値の評価
                * **中古市場での需要:** （★☆☆☆☆ 〜 ★★★慢で評価）
                * **主なターゲット層:** （例：20代前半のストリート系メンズ、ミニマル好きな30代女性など）
                * **解説:** （現在の流行りや、なぜその価値になるのかのバイヤー目線の解説）

                ### 💰 4. 参考価格アドバイス（売買比率：4割〜6割厳守）
                * **店頭販売想定価格:** `¥[ここに価格]`
                * **買取目安価格:** `¥[ここに価格]` 〜 `¥[ここに価格]`
                * **価格設定の理由・根拠コメント:** （なぜこの販売価格にしたのか、引上げ・据置きの理由、在庫リスクや回転率を交えて解説してください）

                ### 📝 5. 接客・店舗運営アドバイス
                * **お客様へのアプローチ例:** （買取時の納得感を与える一言や、販売時のセールトーク例）
                * **売場展開の提案:** （店内のどのコーナーに置くと映えるか、相性の良いアイテムなど）
                ---
                """
                
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                
                uploaded_file.seek(0)
                img_bytes = uploaded_file.getvalue()
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {
                                "inlineData": {
                                    "mimeType": f"image/{uploaded_file.type.split('/')[-1]}",
                                    "data": base64_image
                                }
                            }
                        ]
                    }]
                }
                
                res = requests.post(url, json=payload)
                res_json = res.json()
                
                if res.status_code == 200:
                    if 'contents' in res_json:
                        result_text = res_json['contents'][0]['parts'][0]['text']
                        st.success("査定が完了しました！")
                        st.markdown(result_text)
                    elif 'candidates' in res_json:
                        result_text = res_json['candidates'][0]['content']['parts'][0]['text']
                        st.success("査定が完了しました！")
                        st.markdown(result_text)
                    else:
                        st.error("AIからのデータの形が想定と異なります。管理画面の設定を確認してください。")
                else:
                    st.error(f"AIからの返答に失敗しました: {res_json.get('error', {}).get('message', '不明なエラー')}")
                    
            except Exception as e:
                st.error(f"査定中にエラーが発生しました: {e}")