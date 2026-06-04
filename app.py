import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import random

# --- 設定 Google AI API ---
# 請在 Google AI Studio 獲取你的 API Key
os_api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=os_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 初始化 Session State (用於記錄學習內容) ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 功能函數 ---
def get_ai_analysis(text, is_manual=True):
    prompt = f"""
    你是一個專業的西班牙語導師。請針對以下西班牙語短句："{text}"
    1. 提供繁體中文翻譯。
    2. 提供英文翻譯。
    3. 從中挑選一個關鍵詞彙，解釋其詞性及用法。
    格式請統一為：
    中文：...
    英文：...
    詞彙分析：...
    """
    response = model.generate_content(prompt)
    return response.text

def speak_spanish(text):
    tts = gTTS(text=text, lang='es')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- UI 介面 ---
st.set_page_config(page_title="Joel 的西班牙語導師", layout="wide")
st.title("🇪🇸 Joel 的西班牙語導師")

tabs = st.tabs(["Part A: 自主輸入學習", "Part B: 課程隨機學習", "小測驗紀錄庫"])

# --- Part A: 自主輸入 ---
with tabs[0]:
    st.header("Part A: 實時短句分析")
    user_input = st.text_input("請輸入西班牙語短句：", placeholder="例如: Hola, ¿cómo estás?")
    
    if st.button("分析並記錄"):
        if user_input:
            with st.spinner('AI 分析中...'):
                result = get_ai_analysis(user_input)
                st.write(result)
                
                # 發音
                audio_fp = speak_spanish(user_input)
                st.audio(audio_fp, format='audio/mp3')
                
                # 記錄
                st.session_state.history.append({"text": user_input, "analysis": result})
                st.success("已加入學習記錄！")

# --- Part B: 隨機課程 ---
with tabs[1]:
    st.header("Part B: 等級課程隨機練習")
    level = st.selectbox("選擇課程等級", ["A1", "A2", "B1", "B2"])
    
    if st.button("生成隨機短句"):
        prompt = f"請隨機生成一個西班牙語 {level} 等級的短句，並只回傳該短句內容。"
        gen_text = model.generate_content(prompt).text.strip()
        
        st.subheader(f"隨機短句 ({level}): {gen_text}")
        
        with st.spinner('分析中...'):
            result = get_ai_analysis(gen_text)
            st.write(result)
            
            audio_fp = speak_spanish(gen_text)
            st.audio(audio_fp, format='audio/mp3')
            
            st.session_state.history.append({"text": gen_text, "analysis": result})

# --- 測驗系統 ---
st.sidebar.header("📝 隨堂測驗")
if len(st.session_state.history) > 0:
    if st.sidebar.button("開始測驗"):
        test_item = random.choice(st.session_state.history)
        st.session_state.current_test = test_item
        st.session_state.test_active = True

if 'test_active' in st.session_state and st.session_state.test_active:
    st.divider()
    st.subheader("❓ 測驗：這句話是什麼意思？")
    st.info(st.session_state.current_test['text'])
    
    answer = st.text_input("輸入你的中文或英文翻譯答案：")
    if st.button("提交答案"):
        # 簡單判斷：利用 AI 來批改答案
        verify_prompt = f"學生對於西班牙語 '{st.session_state.current_test['text']}' 的翻譯是 '{answer}'。請問是否正確？請只回答：正確 或 錯誤。"
        verification = model.generate_content(verify_prompt).text
        
        if "正確" in verification:
            st.balloons()
            st.success("A++++ 完美的回答！繼續加油！")
        else:
            st.error("再試一次！參考分析：")
            st.write(st.session_state.current_test['analysis'])
        st.session_state.test_active = False

# --- 歷史紀錄預覽 ---
with tabs[2]:
    st.header("📚 已學習清單")
    if st.session_state.history:
        for idx, item in enumerate(st.session_state.history):
            st.write(f"{idx+1}. {item['text']}")
    else:
        st.write("目前還沒有紀錄喔。")
