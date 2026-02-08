import streamlit as st
import random
import time

st.set_page_config(page_title="Path of flover", page_icon="🎵")

st.title("🎵 Path of flover")
st.caption("프로미스나인 가사 단어 맞추기 게임")

TIME_LIMIT = 10  # 문제당 제한 시간 (초)

# =======================
# 퀴즈 파일 로드
# =======================
def load_quiz(file_path="quiz.txt"):
    quizzes = []
    current_song = None

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("[") and line.endswith("]"):
                current_song = line[1:-1]
                continue

            if "|" in line and current_song:
                question, answer = line.split("|", 1)
                quizzes.append({
                    "song": current_song,
                    "question": question,
                    "answer": answer.strip()
                })
    return quizzes


# =======================
# 세션 초기화
# =======================
if "quizzes" not in st.session_state:
    all_quizzes = load_quiz()
    random.shuffle(all_quizzes)

    st.session_state.quizzes = all_quizzes
    st.session_state.index = 0
    st.session_state.results = []
    st.session_state.finished = False
    st.session_state.start_time = time.time()

# start_time 방어 (중요)
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()


# =======================
# 게임 종료 화면
# =======================
if st.session_state.finished:
    st.success("🎉 모든 문제를 완료했습니다!")

    st.markdown("### 📖 정답 공개")
    for q in st.session_state.results:
        revealed = q["question"].replace(
            "___",
            f"**{q['answer']}**"
        )
        st.markdown(f"**🎶 {q['song']}**  \n{revealed}")

    if st.button("다시 시작"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.stop()


# =======================
# 현재 문제
# =======================
quiz = st.session_state.quizzes[st.session_state.index]

elapsed = int(time.time() - st.session_state.start_time)
remaining = TIME_LIMIT - elapsed

st.markdown("### ❓ 문제")
st.write(quiz["question"])

# 타이머 UI
st.progress(max(0, remaining) / TIME_LIMIT)
st.write(f"⏱ 남은 시간: **{max(0, remaining)}초**")

# =======================
# 시간 초과 처리
# =======================
if remaining <= 0:
    st.warning("⏰ 시간 초과! 다음 문제로 넘어갑니다.")
    time.sleep(1)

    st.session_state.index += 1
    st.session_state.start_time = time.time()

    if st.session_state.index >= len(st.session_state.quizzes):
        st.session_state.finished = True

    st.rerun()


# =======================
# 정답 입력
# =======================
user_input = st.text_input(
    "빈칸에 들어갈 단어를 입력하세요",
    key="answer_input"
)

if st.button("제출"):
    # ❌ 오답 → 즉시 종료
    if user_input.strip() != quiz["answer"]:
        st.error("❌ 오답입니다.")
        st.session_state.finished = True
        st.rerun()

    # ✅ 정답
    else:
        st.success("✅ 정답!")
        st.session_state.results.append(quiz)

        st.session_state.index += 1
        st.session_state.start_time = time.time()

        if st.session_state.index >= len(st.session_state.quizzes):
            st.session_state.finished = True

        st.rerun()
