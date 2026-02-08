import streamlit as st
import random

st.set_page_config(page_title="Path of Flover", page_icon="🎵")

st.title("🎵 Path of Flover")
st.caption("프로미스나인 가사 단어 맞추기 게임")

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

            # [곡 제목]
            if line.startswith("[") and line.endswith("]"):
                current_song = line[1:-1]
                continue

            # 문제|정답
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

        st.markdown(
            f"""
**🎶 {q['song']}**  
{revealed}
"""
        )

    if st.button("다시 시작"):
        for key in ["quizzes", "index", "results", "finished"]:
            del st.session_state[key]
        st.rerun()

    st.stop()


# =======================
# 현재 문제
# =======================
quiz = st.session_state.quizzes[st.session_state.index]

st.markdown("### ❓ 문제")
st.write(quiz["question"])

user_input = st.text_input(
    "빈칸에 들어갈 단어를 입력하세요",
    key="answer_input"
)

if st.button("제출"):
    # ❌ 오답 처리 (힌트 없음, 즉시 종료)
    if user_input.strip() != quiz["answer"]:
        st.error("❌ 오답입니다.")
        st.session_state.finished = True
        st.rerun()

    # ✅ 정답 처리
    else:
        st.success("✅ 정답!")
        st.session_state.results.append(quiz)
        st.session_state.index += 1

        if st.session_state.index >= len(st.session_state.quizzes):
            st.session_state.finished = True

        st.rerun()
