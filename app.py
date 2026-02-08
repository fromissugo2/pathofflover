import streamlit as st
import time
import random

# ===============================
# 설정
# ===============================
TIME_LIMIT = 10  # 문제당 제한 시간 (초)

st.set_page_config(
    page_title="Path of flover",
    page_icon="🎵",
)

st.title("🎵 Path of flover")
st.caption("프로미스나인 가사 단어 맞추기 팬메이드 퀴즈")

# ===============================
# 문제 로드
# ===============================
def load_quiz(file_path="quiz.txt"):
    quizzes = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            block = {}
            for line in f:
                line = line.strip()
                if not line:
                    if block:
                        quizzes.append(block)
                        block = {}
                    continue

                if line.startswith("Q:"):
                    block["question"] = line[2:].strip()
                elif line.startswith("A:"):
                    block["answer"] = line[2:].strip()
                elif line.startswith("SONG:"):
                    block["song"] = line[5:].strip()
                elif line.startswith("FULL:"):
                    block["full"] = line[5:].strip()

            if block:
                quizzes.append(block)
    except FileNotFoundError:
        pass

    return quizzes


# ===============================
# 세션 상태 초기화
# ===============================
if "quiz" not in st.session_state:
    st.session_state.quiz = load_quiz()
    random.shuffle(st.session_state.quiz)

if not st.session_state.quiz:
    st.error("❗ quiz.txt 파일이 없거나 문제 형식이 올바르지 않습니다.")
    st.stop()

if "started" not in st.session_state:
    st.session_state.started = False

if "index" not in st.session_state:
    st.session_state.index = 0

if "start_time" not in st.session_state:
    st.session_state.start_time = None


# ===============================
# 시작 화면
# ===============================
if not st.session_state.started:
    st.info("Start 버튼을 누르면 게임이 시작됩니다")
    if st.button("▶️ Start"):
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.rerun()
    st.stop()


# ===============================
# 종료 처리
# ===============================
if st.session_state.index >= len(st.session_state.quiz):
    st.success("🎉 모든 문제를 맞혔어요!")

    last = st.session_state.quiz[-1]
    st.markdown("### 🎶 마지막 문제 정보")

    if "song" in last:
        st.write(f"**곡명:** {last['song']}")
    if "full" in last:
        st.write(f"**정답 가사:** {last['full']}")

    st.caption("팬메이드 퀴즈 | Path of flover")
    st.stop()


# ===============================
# 현재 문제
# ===============================
q = st.session_state.quiz[st.session_state.index]

elapsed = int(time.time() - st.session_state.start_time)
remaining = TIME_LIMIT - elapsed


# ===============================
# 시간 초과 처리
# ===============================
if remaining <= 0:
    st.error("❌ 시간 초과!")
    st.session_state.index += 1
    st.session_state.start_time = time.time()
    time.sleep(1)
    st.rerun()


# ===============================
# 문제 표시
# ===============================
st.markdown(f"### 문제 {st.session_state.index + 1}")
st.markdown(f"**{q['question']}**")

timer_placeholder = st.empty()
timer_placeholder.markdown(f"⏱ **남은 시간: {remaining}초**")

answer = st.text_input(
    "정답 입력",
    key=f"input_{st.session_state.index}"
)

if st.button("제출"):
    if answer.strip() == q["answer"]:
        st.success("⭕ 정답!")
    else:
        st.error("❌ 오답!")

    st.session_state.index += 1
    st.session_state.start_time = time.time()
    time.sleep(1)
    st.rerun()


# ===============================
# 실시간 타이머
# ===============================
time.sleep(1)
st.rerun()
