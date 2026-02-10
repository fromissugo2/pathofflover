import streamlit as st
import time
import os
import random
import json
from streamlit_autorefresh import st_autorefresh

# ===============================
# 기본 설정
# ===============================
st.set_page_config(
    page_title="Path of flover",
    page_icon="🎵"
)

st.title("🎵 Path of flover")
st.caption("프로미스나인 가사 단어 맞추기 게임")

# ===============================
# 모드 설정
# ===============================
MODES = {
    "Easy": {
        "file": "quizeazy.txt",
        "time": 20,
        "count": 10
    },
    "Hard": {
        "file": "quizhard.txt",
        "time": 15,
        "count": 20
    }
}

# ===============================
# 명예의 전당 설정
# ===============================
HOF_FILE = "hard_hall_of_fame.json"
HOF_TEST_THRESHOLD = 1   # 🔥 테스트용 (나중에 15로 변경)


def load_hof():
    if not os.path.exists(HOF_FILE):
        return []
    with open(HOF_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_hof(data):
    with open(HOF_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_hof_record(name: str, score: int):
    hof = load_hof()
    hof.append({"name": name, "score": score})
    hof.sort(key=lambda x: x["score"], reverse=True)
    hof = hof[:10]  # TOP 10 유지
    save_hof(hof)

# ===============================
# 유틸
# ===============================
def normalize(text: str) -> str:
    return text.replace(" ", "").lower()

def is_correct(user_input: str, answer_text: str) -> bool:
    answers = [a.strip() for a in answer_text.split(",")]
    user = normalize(user_input)
    return any(user == normalize(a) for a in answers)

def get_result_message(mode: str, correct: int) -> str:
    if mode == "Easy":
        if correct <= 3:
            return "😅 뉴비시군요"
        elif correct <= 7:
            return "😀 가사를 음미하면서 들어보아요"
        else:
            return "☘️ 훌륭합니다"
    else:  # Hard
        if correct <= 5:
            return "😅 자컨 볼 시간은 있고 가사 볼 시간은 없었나요?"
        elif correct <= 10:
            return "😀 이참에 수록곡 복습!"
        else:
            return "☘️ 당신은 프로미스나인 고인물!"

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

# ===============================
# 세션 초기화
# ===============================
def reset_game():
    st.session_state.started = False
    st.session_state.index = 0
    st.session_state.start_time = None
    st.session_state.results = []
    st.session_state.timeout_handled = False
    st.session_state.quiz = []
    st.session_state.mode = None
    st.session_state.time_limit = 0
    st.session_state.hof_saved = False


if "started" not in st.session_state:
    reset_game()

# ===============================
# 모드 선택 화면
# ===============================
if not st.session_state.started:
    st.markdown("## 🎮 난이도 선택")

    mode = st.radio(
        "플레이할 모드를 선택하세요",
        ["Easy", "Hard"]
    )

    if st.button("▶ 시작"):
        config = MODES[mode]
        all_quiz = load_quiz(config["file"])

        if not all_quiz:
            st.error(f"❗ {config['file']} 파일이 없거나 형식이 올바르지 않습니다")
            st.stop()

        st.session_state.mode = mode
        st.session_state.quiz = random.sample(
            all_quiz,
            min(config["count"], len(all_quiz))
        )
        st.session_state.time_limit = config["time"]
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.session_state.timeout_handled = False
        st.rerun()

    st.stop()

quiz = st.session_state.quiz
TIME_LIMIT = st.session_state.time_limit
mode = st.session_state.mode

# ===============================
# 게임 종료 화면
# ===============================
if st.session_state.index >= len(quiz):
    st.success("🎉 모든 문제를 완료했어요!")

    correct_count = sum(st.session_state.results)
    total = len(st.session_state.results)

    st.markdown(f"### 🎯 결과: **{correct_count} / {total}**")
    st.markdown("### 💬 한 줄 평가")
    st.success(get_result_message(mode, correct_count))

    # ===============================
    # 🏆 HARD MODE 명예의 전당
    # ===============================
    if mode == "Hard" and correct_count >= HOF_TEST_THRESHOLD:
        st.markdown("---")
        st.markdown("## 🏆 HARD MODE 명예의 전당")

        if not st.session_state.hof_saved:
            st.info("축하합니다! 명예의 전당에 기록될 닉네임을 작성해주세요")

            name = st.text_input(
                "닉네임 입력 (최대 8자)",
                max_chars=8
            )

            if st.button("📌 기록하기"):
                final_name = name.strip() or "ANON"
                add_hof_record(final_name, correct_count)
                st.session_state.hof_saved = True
                st.success("✅ 명예의 전당에 기록되었습니다!")
                st.rerun()

        hof = load_hof()

        st.markdown("### 🥇 TOP 10")
        for i in range(10):
            if i < len(hof):
                st.markdown(
                    f"**{i+1}. {hof[i]['name']}** — {hof[i]['score']}"
                )
            else:
                st.markdown(f"**{i+1}.**")

    # ===============================
    # 문제별 결과
    # ===============================
    st.markdown("## 📊 문제별 결과")

    for i, q in enumerate(quiz):
        correct = st.session_state.results[i]
        mark = "⭕" if correct else "❌"

        answer_line = q["question"].replace(
            "___", f"**{q['answer'].split(',')[0]}**"
        )

        st.markdown(
            f"""
**{mark} [{q['song']}]**  
{answer_line}
"""
        )

    if st.button("🔄 다시 하기"):
        reset_game()
        st.rerun()

    st.stop()

# ===============================
# 현재 문제
# ===============================
current = quiz[st.session_state.index]

st_autorefresh(interval=1000, key="timer")

elapsed = time.time() - st.session_state.start_time
remaining = TIME_LIMIT - int(elapsed)

# ===============================
# 시간 초과 처리
# ===============================
if remaining <= 0 and not st.session_state.timeout_handled:
    st.session_state.timeout_handled = True
    st.error("❌ 시간 초과!")
    st.session_state.results.append(False)
    st.session_state.index += 1
    st.session_state.start_time = time.time()
    st.session_state.timeout_handled = False
    st.rerun()

# ===============================
# 문제 표시
# ===============================
st.markdown(f"### [{mode}] 문제 {st.session_state.index + 1} / {len(quiz)}")
st.markdown(f"**⏱ 남은 시간: {max(0, remaining)}초**")
st.markdown(f"### {current['question']}")

# ===============================
# 입력 폼
# ===============================
with st.form(key=f"form_{st.session_state.index}", clear_on_submit=True):
    answer = st.text_input("정답 입력 (엔터로 제출)")
    submitted = st.form_submit_button("제출")

if submitted:
    if is_correct(answer, current["answer"]):
        st.success("⭕ 정답!")
        st.session_state.results.append(True)
    else:
        st.error("❌ 오답")
        st.session_state.results.append(False)

    st.session_state.index += 1
    st.session_state.start_time = time.time()
    st.session_state.timeout_handled = False
    st.rerun()
