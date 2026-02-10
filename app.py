import streamlit as st
import time
import os
import random
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


if "started" not in st.session_state:
    reset_game()

# ===============================
# === 추가 ===
# 관리자 / 명예의 전당 관리용 세션
# ===============================
if "removed_hof_ranks" not in st.session_state:
    st.session_state.removed_hof_ranks = set()

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "")

# ===============================
# === 추가 ===
# HARD MODE 명예의 전당 계산 로직
# ===============================
def build_hard_hall_of_fame(correct_count: int):
    hof = {}

    # 기본 6위
    hof[6] = ("AAA", 15)

    if correct_count >= 15:
        rank = 21 - correct_count
        hof[rank] = ("YOU", correct_count)

    # 🔥 운영자가 삭제한 순위 제거
    for r in list(hof.keys()):
        if r in st.session_state.removed_hof_ranks:
            del hof[r]

    return hof

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
    if mode == "Hard":
        st.markdown("---")
        st.markdown("## 🏆 HARD MODE 명예의 전당")

        hof = build_hard_hall_of_fame(correct_count)

        for rank in range(1, 7):
            if rank in hof:
                name, score = hof[rank]
                crown = " 👑" if name == "YOU" else ""
                st.markdown(f"**{rank}위. {name}** — {score}{crown}")
            else:
                st.markdown(f"**{rank}위.**")

        # ===============================
        # === 추가 ===
        # 🔐 운영자 전용 관리
        # ===============================
        st.markdown("---")
        st.markdown("### 🔐 운영자 관리")

        admin_input = st.text_input(
            "관리자 비밀번호",
            type="password",
            key="admin_pw"
        )

        if admin_input == ADMIN_PASSWORD and ADMIN_PASSWORD:
            st.success("운영자 권한 확인됨")

            for rank in range(1, 7):
                if st.button(f"❌ {rank}위 닉네임 삭제", key=f"del_rank_{rank}"):
                    st.session_state.removed_hof_ranks.add(rank)
                    st.rerun()

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
