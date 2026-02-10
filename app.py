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
HOF_TEST_THRESHOLD = 15   # ✅ 실사용 기준


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
    hof = hof[:10]
    save_hof(hof)


def delete_hof_record(index: int):
    hof = load_hof()
    if 0 <= index < len(hof):
        hof.pop(index)
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
    else:
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
# 모드 선택
# ===============================
if not st.session_state.started:
    st.markdown("## 🎮 난이도 선택")

    mode = st.radio("플레이할 모드를 선택하세요", ["Easy", "Hard"])

    if st.button("▶ 시작"):
        config = MODES[mode]
        all_quiz = load_quiz(config["file"])

        if not all_quiz:
            st.error("❗ 문제 파일을 불러올 수 없습니다")
            st.stop()

        st.session_state.mode = mode
        st.session_state.quiz = random.sample(
            all_quiz, min(config["count"], len(all_quiz))
        )
        st.session_state.time_limit = config["time"]
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.session_state.timeout_handled = False
        st.rerun()

    st.stop()

quiz = st.session_state.quiz
mode = st.session_state.mode

# ===============================
# 게임 종료
# ===============================
if st.session_state.index >= len(quiz):
    st.success("🎉 모든 문제를 완료했어요!")

    correct_count = sum(st.session_state.results)
    st.markdown(f"### 🎯 결과: **{correct_count} / {len(quiz)}**")
    st.success(get_result_message(mode, correct_count))

    # ===== HARD MODE 명예의 전당 =====
    if mode == "Hard" and correct_count >= HOF_TEST_THRESHOLD:
        st.markdown("---")
        st.markdown("## 🏆 HARD MODE 명예의 전당")

        if not st.session_state.hof_saved:
            st.info("축하합니다! 명예의 전당에 기록될 닉네임을 작성해주세요")

            name = st.text_input("닉네임 (최대 8자)", max_chars=8)

            if st.button("📌 기록하기"):
                add_hof_record(name.strip() or "ANON", correct_count)
                st.session_state.hof_saved = True
                st.rerun()

        hof = load_hof()

        st.markdown("### 🥇 TOP 10")
        for i in range(10):
            cols = st.columns([6, 2])
            if i < len(hof):
                cols[0].markdown(
                    f"**{i+1}. {hof[i]['name']}** — {hof[i]['score']}"
                )
                if cols[1].button("🗑 삭제", key=f"del_{i}"):
                    delete_hof_record(i)
                    st.rerun()
            else:
                cols[0].markdown(f"**{i+1}.**")

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
remaining = st.session_state.time_limit - int(elapsed)

if remaining <= 0 and not st.session_state.timeout_handled:
    st.session_state.timeout_handled = True
    st.session_state.results.append(False)
    st.session_state.index += 1
    st.session_state.start_time = time.time()
    st.rerun()

st.markdown(f"### [{mode}] 문제 {st.session_state.index + 1} / {len(quiz)}")
st.markdown(f"⏱ 남은 시간: {max(0, remaining)}초")
st.markdown(current["question"])

with st.form(key=f"form_{st.session_state.index}", clear_on_submit=True):
    answer = st.text_input("정답 입력")
    if st.form_submit_button("제출"):
        st.session_state.results.append(
            is_correct(answer, current["answer"])
        )
        st.session_state.index += 1
        st.session_state.start_time = time.time()
        st.rerun()
