import streamlit as st
import time
import os

QUIZ_FILE = "quiz.txt"
TIME_LIMIT = 10  # 초

# ===============================
# 퀴즈 로드
# ===============================
def load_quiz():
    if not os.path.exists(QUIZ_FILE):
        return []

    quiz = []
    current_song = None

    with open(QUIZ_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # [SONG TITLE]
            if line.startswith("[") and line.endswith("]"):
                current_song = line[1:-1]
                continue

            # question|answer
            if "|" in line and "___" in line and current_song:
                q, a = line.split("|", 1)
                quiz.append({
                    "song": current_song,
                    "question": q,
                    "answer": a.strip(),
                    "full": q.replace("___", a.strip())
                })

    return quiz


# ===============================
# 초기 상태
# ===============================
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.index = 0
    st.session_state.start_time = 0
    st.session_state.quiz = load_quiz()
    st.session_state.results = []


st.set_page_config(page_title="Path of flover", page_icon="🎵")
st.title("🎵 Path of flover")
st.caption("프로미스나인 가사 단어 맞추기 게임")

# ===============================
# 퀴즈 없음 처리
# ===============================
if not st.session_state.quiz:
    st.error("❗ quiz.txt 파일이 없거나 형식이 올바르지 않습니다")
    st.stop()

# ===============================
# 시작 화면
# ===============================
if not st.session_state.started:
    if st.button("▶ 시작"):
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.experimental_rerun()
    st.stop()

# ===============================
# 퀴즈 종료
# ===============================
if st.session_state.index >= len(st.session_state.quiz):
    st.success("🎉 모든 문제를 풀었습니다!")

    last = st.session_state.quiz[-1]
    st.markdown(f"### 🎵 {last['song']}")
    st.markdown(f"**정답 가사:** {last['full']}")

    st.stop()

# ===============================
# 문제 진행
# ===============================
q = st.session_state.quiz[st.session_state.index]
elapsed = int(time.time() - st.session_state.start_time)
remaining = TIME_LIMIT - elapsed

st.markdown(f"### ⏳ 남은 시간: **{remaining}초**")
st.markdown(f"**문제 {st.session_state.index + 1}**")
st.markdown(f"> {q['question']}")

# 시간 초과
if remaining <= 0:
    st.error("❌ 시간 초과")
    st.session_state.results.append(False)
    st.session_state.index += 1
    st.session_state.start_time = time.time()
    st.experimental_rerun()

# 입력
answer = st.text_input("정답 입력", key=f"answer_{st.session_state.index}")

if answer:
    if answer.strip() == q["answer"]:
        st.success("⭕ 정답!")
        st.session_state.results.append(True)
    else:
        st.error("❌ 오답")
        st.session_state.results.append(False)

    st.session_state.index += 1
    st.session_state.start_time = time.time()
    st.experimental_rerun()
