import streamlit as st
import time
import os

# ===============================
# 기본 설정
# ===============================
st.set_page_config(
    page_title="Path of flover",
    page_icon="🎵"
)

st.title("🎵 Path of flover")
st.caption("프로미스나인 가사 단어 맞추기 게임")

QUIZ_FILE = "quiz.txt"
TIME_LIMIT = 10  # 초

# ===============================
# 문제 로딩
# ===============================
def load_quiz(file_path):
    if not os.path.exists(file_path):
        return []

    quiz = []
    current_song = None

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("[") and line.endswith("]"):
                current_song = line[1:-1]
            elif "|" in line and "___" in line and current_song:
                q, a = line.split("|", 1)
                quiz.append({
                    "song": current_song,
                    "question": q,
                    "answer": a.strip()
                })

    return quiz


quiz = load_quiz(QUIZ_FILE)

if not quiz:
    st.error("❗ quiz.txt 파일이 없거나 문제 형식이 올바르지 않습니다")
    st.stop()

# ===============================
# 세션 상태 초기화
# ===============================
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.index = 0
    st.session_state.start_time = None
    st.session_state.results = []

# ===============================
# 시작 화면
# ===============================
if not st.session_state.started:
    st.info("▶ 시작 버튼을 누르면 게임이 시작됩니다")
    if st.button("▶ 시작"):
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.rerun()
    st.stop()

# ===============================
# 게임 종료
# ===============================
if st.session_state.index >= len(quiz):
    st.success("🎉 모든 문제를 완료했어요!")

    for q in quiz:
        answer_line = q["question"].replace(
            "___", f"**{q['answer']}**"
        )
        st.markdown(f"- **[{q['song']}]** {answer_line}")

    st.stop()

# ===============================
# 현재 문제
# ===============================
current = quiz[st.session_state.index]

elapsed = time.time() - st.session_state.start_time
remaining = TIME_LIMIT - int(elapsed)

# ===============================
# 시간 초과 처리
# ===============================
if remaining <= 0:
    st.error("❌ 시간 초과!")
    st.session_state.results.append(False)
    st.session_state.index += 1
    st.session_state.start_time = time.time()
    st.rerun()

# ===============================
# 문제 표시
# ===============================
st.markdown(f"### 문제 {st.session_state.index + 1} / {len(quiz)}")
st.markdown(f"**⏱ 남은 시간: {remaining}초**")
st.markdown(f"### {current['question']}")

# 입력
answer = st.text_input("정답 입력", key=f"input_{st.session_state.index}")

# ===============================
# 제출 버튼
# ===============================
if st.button("제출"):
    if answer.strip() == current["answer"]:
        st.success("⭕ 정답!")
        st.session_state.results.append(True)
    else:
        st.error("❌ 오답")
        st.session_state.results.append(False)

    st.session_state.index += 1
    st.session_state.start_time = time.time()
    st.rerun()

# ===============================
# 실시간 타이머 갱신
# ===============================
time.sleep(1)
st.rerun()
