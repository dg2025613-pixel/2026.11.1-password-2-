import math
import random

import streamlit as st

st.set_page_config(page_title="암호 해독 게임", page_icon="🔐", layout="centered")

# ---------------------------------------------------------------
# 스타일 (약간 어두운 배경)
# ---------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(160deg, #14161d 0%, #1b1f2b 100%); color: #e6e6ea; }
    h1, h2, h3 { color: #f0c36d !important; }
    .cipher-box {
        background: #0f1117; border: 1px solid #3a3f52; border-radius: 12px;
        padding: 18px; text-align: center; font-size: 2.4rem; letter-spacing: 0.6rem;
        color: #7fe0b0; font-family: 'Courier New', monospace; margin: 10px 0 18px 0;
    }
    .info-box {
        background: #1f2331; border-left: 4px solid #f0c36d; border-radius: 8px;
        padding: 12px 16px; margin: 8px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# 데이터 / 암호 함수
# ---------------------------------------------------------------
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
WORDS = [
    "CAT", "DOG", "SUN", "MAP", "KEY", "SKY", "BOX", "CUP", "PEN", "BAG",
    "MOON", "STAR", "BOOK", "FISH", "TREE", "RAIN", "WIND", "FIRE", "GAME",
    "CODE", "LOCK", "SAFE", "WOLF", "BEAR", "CAKE", "SHIP", "ROAD", "GOLD",
]
WORDS4 = [w for w in WORDS if len(w) == 4]
VALID_A = [a for a in range(2, 8) if math.gcd(a, 26) == 1]  # 아핀 암호의 a: 7 이하이면서 26과 서로소 -> 3, 5, 7


def n(ch):
    return ord(ch) - 65


def c(num):
    return ALPHA[num % 26]


def caesar_encrypt(word, shift=3):
    return "".join(c(n(ch) + shift) for ch in word)


def affine_encrypt(word, a, b):
    return "".join(c(a * n(ch) + b) for ch in word)


def hill_encrypt(word, K):
    out = ""
    for i in range(0, len(word), 2):
        p0, p1 = n(word[i]), n(word[i + 1])
        out += c(K[0][0] * p0 + K[0][1] * p1)
        out += c(K[1][0] * p0 + K[1][1] * p1)
    return out


def hill_inverse(K):
    det = (K[0][0] * K[1][1] - K[0][1] * K[1][0]) % 26
    inv_det = pow(det, -1, 26)
    return [
        [(inv_det * K[1][1]) % 26, (-inv_det * K[0][1]) % 26],
        [(-inv_det * K[1][0]) % 26, (inv_det * K[0][0]) % 26],
    ]


def new_problem(stage):
    if stage == 1:
        word = random.choice(WORDS)
        return {"word": word, "cipher": caesar_encrypt(word, 3)}
    if stage == 2:
        a = random.choice(VALID_A)
        b = random.randint(1, 10)  # b도 작은 수로 (1~10)
        word = random.choice(WORDS)
        return {"word": word, "a": a, "b": b, "cipher": affine_encrypt(word, a, b), "inv_ok": False}
    while True:  # 복호화 행렬 K⁻¹을 작은 숫자(1~4)로 먼저 만든다
        Kinv = [[random.randint(1, 4) for _ in range(2)] for _ in range(2)]
        det = (Kinv[0][0] * Kinv[1][1] - Kinv[0][1] * Kinv[1][0]) % 26
        if math.gcd(det, 26) == 1:
            break
    K = hill_inverse(Kinv)  # 암호화에 쓰는 키 행렬
    word = random.choice(WORDS4)  # 2x2 행렬이므로 2글자씩 묶기 위해 4글자 단어 사용
    return {"word": word, "K": K, "Kinv": Kinv, "cipher": hill_encrypt(word, K)}


# ---------------------------------------------------------------
# 상태 초기화
# ---------------------------------------------------------------
ss = st.session_state
if "stage" not in ss:
    ss.stage = 1
    ss.phase = "intro"  # intro -> play
    ss.problem = None
    ss.tries = 0
    ss.total_tries = 0
    ss.pid = 0


def go_play():
    ss.phase = "play"
    ss.problem = new_problem(ss.stage)
    ss.tries = 0
    ss.pid += 1


def next_stage():
    ss.stage += 1
    ss.phase = "intro"
    ss.problem = None


def retry_new():
    ss.problem = new_problem(ss.stage)
    ss.tries = 0
    ss.pid += 1


def restart():
    for k in list(ss.keys()):
        del ss[k]


def affine_calculator(pid):
    st.caption("숫자 세 개만 넣으면 `역원 × (C − b) mod 26` 을 알아서 계산해 줍니다.")
    c1, c2, c3 = st.columns(3)
    inv = int(c1.number_input("역원 a⁻¹", 0, 25, 0, step=1, key=f"ac_inv_{pid}"))
    cn = int(c2.number_input("글자의 숫자 C", 0, 25, 0, step=1, key=f"ac_c_{pid}"))
    bb = int(c3.number_input("b 값", 0, 25, 0, step=1, key=f"ac_b_{pid}"))
    total = inv * (cn - bb)
    res = total % 26
    st.markdown(
        f"<div style='background:#0f1117;border:1px solid #f0c36d;border-radius:10px;padding:12px 16px;margin:6px 0 14px 0'>"
        f"{inv} × ({cn} − {bb}) = {total} → mod 26 = <b style='color:#7fe0b0;font-size:1.4rem'>{res}</b>"
        f" → 알파벳 <b style='color:#7fe0b0;font-size:1.4rem'>{ALPHA[res]}</b></div>",
        unsafe_allow_html=True,
    )


def show_table():
    rows = "| " + " | ".join(ALPHA) + " |\n|" + "---|" * 26 + "\n| " + " | ".join(str(i) for i in range(26)) + " |"
    st.markdown(rows)


# ---------------------------------------------------------------
# 화면
# ---------------------------------------------------------------
st.title("🔐 암호 해독 게임")
if ss.stage <= 3:
    st.progress((ss.stage - 1) / 3, text=f"{ss.stage} / 3 단계")

# ---------- 설명 화면 ----------
INTRO = {
    1: ("1단계 · 시저 암호",
        """
**시저 암호**는 로마의 율리우스 카이사르(시저)가 군사 편지에 사용했다고 전해지는 암호입니다.
알파벳을 **3칸 뒤로 밀어서** 암호화합니다. (A→D, B→E, C→F … X→A, Y→B, Z→C)

**암호화:** 평문 글자를 3칸 뒤로 이동
**복호화(푸는 법):** 암호문 글자를 **3칸 앞으로** 이동

예) `DUH` → D→A, U→R, H→E → `ARE`

알파벳 끝을 넘어가면 처음으로 돌아옵니다. (A보다 앞으로 가면 Z로)
"""),
    2: ("2단계 · 아핀 암호",
        """
**아핀 암호**는 글자를 숫자로 바꾼 뒤 일차식으로 암호화합니다. (A=0, B=1, … Z=25)

**암호화:**  `C = (a·P + b) mod 26`
**복호화:**  `P = a⁻¹ · (C − b) mod 26`

여기서 `a⁻¹`는 **a의 역원**으로, `a · a⁻¹ ≡ 1 (mod 26)`을 만족하는 수입니다.

**이 게임의 진행 방법**
1. 문제에 주어진 `a`의 **역원을 직접 구해서** 입력합니다. (이 단계만 직접 계산!)
2. 역원이 맞으면 **자동 계산기**가 나타납니다.
3. 암호문 글자를 숫자로 바꿔서(표 참고) 계산기에 **역원, 글자의 숫자, b 값**만 넣으면 `a⁻¹ · (C − b) mod 26`을 계산해 알파벳까지 알려줍니다.
4. 글자마다 반복해서 나온 알파벳을 이어 붙여 정답을 입력합니다.

`a`는 3, 5, 7 중 하나이고, `b`는 문제 화면에서 미리 알려줍니다.

💡 역원 구하는 팁: `a · x`를 26으로 나눈 나머지가 1이 되는 x를 찾으면 됩니다. (x는 0~25 사이)
"""),
    3: ("3단계 · 힐 암호",
        """
**힐 암호**는 행렬을 이용한 암호로, 글자를 **2글자씩 묶어서** 암호화합니다. (A=0, B=1, … Z=25)

**암호화:**  `C = K · P (mod 26)`  (K는 2×2 키 행렬, P는 두 글자의 숫자 열벡터)
**복호화:**  `P = K⁻¹ · C (mod 26)`

(역행렬 K⁻¹ 구하는 법: `det = ad − bc` → det의 역원 → `det⁻¹ · [[d, −b], [−c, a]]` mod 26. 이 게임에서는 **K⁻¹을 미리 알려줍니다.**)

**이 게임의 진행 방법**
1. 암호문을 **2글자씩 묶어** 숫자로 바꿉니다. (표 참고)
2. K⁻¹ = [[p, q], [r, s]], 한 묶음이 (x, y)일 때
   - **첫 번째 글자** = `p × x + q × y` (mod 26)
   - **두 번째 글자** = `r × x + s × y` (mod 26)
3. 곱셈 식 칸에 **숫자만 넣으면 계산과 mod 26은 자동**으로 해 줍니다.
4. 나온 숫자 4개를 알파벳으로 바꿔 이어 붙이면 정답입니다.

예) K⁻¹ = [[1, 2], [3, 1]], 묶음 (x, y) = (5, 7) → 첫 글자 = 1×5 + 2×7 = 19, 둘째 글자 = 3×5 + 1×7 = 22
"""),
}

if ss.stage > 3:
    st.balloons()
    st.success("🎉 모든 단계를 클리어했습니다! 당신은 암호 해독의 달인입니다.")
    st.write(f"총 시도 횟수: **{ss.total_tries}회**")
    st.button("처음부터 다시 하기", on_click=restart)
    st.stop()

if ss.phase == "intro":
    title, body = INTRO[ss.stage]
    st.header(title)
    st.markdown(body)
    st.button("문제 풀기 ▶", on_click=go_play, type="primary")
    st.stop()

# ---------- 문제 화면 ----------
p = ss.problem
title, body = INTRO[ss.stage]
st.header(title)
with st.expander("📖 암호 설명 / 푸는 방법 다시 보기"):
    st.markdown(body)

st.subheader("암호문")
st.markdown(f'<div class="cipher-box">{p["cipher"]}</div>', unsafe_allow_html=True)


def check_answer(ans):
    ans = ans.strip().upper()
    ss.tries += 1
    ss.total_tries += 1
    if ans == p["word"]:
        st.success("✅ 정답입니다!")
        return True
    st.error("❌ 틀렸습니다. 다시 시도해 보세요.")
    return False


# ----- 1단계 -----
if ss.stage == 1:
    st.write("**규칙:** 알파벳을 3칸 뒤로 민 암호입니다. 원래 단어(3~4글자)를 맞혀 보세요.")
    show_table()
    with st.form(f"f1_{ss.pid}"):
        ans = st.text_input("평문 입력 (영어)")
        if st.form_submit_button("제출"):
            if check_answer(ans):
                ss.solved_pid = ss.pid

# ----- 2단계 -----
elif ss.stage == 2:
    a, b = p["a"], p["b"]
    st.write(f"**암호화 식:**  `C = ({a}·P + {b}) mod 26`")
    k1, k2 = st.columns(2)
    k1.metric("a 값", a)
    k2.metric("b 값 (미리 알려드려요)", b)
    show_table()

    st.markdown("#### ① 역원 구하기 (직접 계산)")
    st.write(f"`{a} · x ≡ 1 (mod 26)` 을 만족하는 **x = {a}⁻¹** 를 구하세요.")
    if not p["inv_ok"]:
        with st.form(f"f2a_{ss.pid}"):
            x = st.number_input("a의 역원", min_value=0, max_value=25, step=1, value=0)
            if st.form_submit_button("역원 확인"):
                if (a * int(x)) % 26 == 1:
                    p["inv_ok"] = True
                    st.rerun()
                else:
                    st.error("❌ 틀렸습니다. a·x를 26으로 나눈 나머지가 1이 되어야 합니다.")
        with st.expander("힌트"):
            st.write(f"x에 1, 3, 5 … 같은 값을 넣어 `{a}·x mod 26`이 1이 되는 값을 찾아보세요.")
    else:
        st.success(f"✅ 역원 확인 완료! {a}⁻¹ = {pow(a, -1, 26)}")
        st.markdown("#### ② 복호화 (자동 계산기)")
        nums = ", ".join(f"{ch}={n(ch)}" for ch in p["cipher"])
        st.info(f"암호문 숫자: {nums}")
        affine_calculator(ss.pid)
        with st.form(f"f2b_{ss.pid}"):
            ans = st.text_input("평문 입력 (영어)")
            submitted = st.form_submit_button("제출")
        if submitted:
            if check_answer(ans):
                ss.solved_pid = ss.pid

# ----- 3단계 -----
else:
    Kinv = p["Kinv"]
    cp = p["cipher"]
    st.write("**복호화 행렬 K⁻¹ (미리 알려드려요)**")
    st.latex(rf"K^{{-1}}=\begin{{pmatrix}}{Kinv[0][0]} & {Kinv[0][1]}\\ {Kinv[1][0]} & {Kinv[1][1]}\end{{pmatrix}}")
    show_table()

    st.markdown("#### ① 암호문을 2글자씩 묶어 숫자로")
    st.info(
        f"묶음 1: {cp[0]}={n(cp[0])}, {cp[1]}={n(cp[1])}   |   묶음 2: {cp[2]}={n(cp[2])}, {cp[3]}={n(cp[3])}"
    )

    st.markdown("#### ② 곱셈 식에 숫자 넣기 (계산은 자동)")
    st.write("`(K⁻¹의 숫자) × (암호문 숫자) + (K⁻¹의 숫자) × (암호문 숫자)` 자리에 알맞은 숫자를 넣으면 mod 26 결과가 나옵니다.")
    with st.expander("힌트"):
        st.write("K⁻¹ = [[p, q], [r, s]], 묶음 (x, y)일 때 → 첫 글자: p×x + q×y / 둘째 글자: r×x + s×y")

    for g in range(2):
        st.markdown(f"**묶음 {g + 1} : {cp[2 * g]}{cp[2 * g + 1]}**")
        for r in range(2):
            st.caption("첫 번째 글자" if r == 0 else "두 번째 글자")
            cols = st.columns([1, 0.35, 1, 0.35, 1, 0.35, 1, 2.2])
            vals = []
            for i, col in enumerate(cols[:7]):
                if i % 2 == 0:
                    vals.append(col.number_input(
                        f"h{g}{r}{i}", 0, 25, 0, step=1,
                        key=f"h_{ss.pid}_{g}_{r}_{i}", label_visibility="collapsed"))
                else:
                    col.markdown("<div style='padding-top:8px;text-align:center'>" + ("×" if i in (1, 5) else "+") + "</div>",
                                 unsafe_allow_html=True)
            total = vals[0] * vals[1] + vals[2] * vals[3]
            cols[7].markdown(
                f"<div style='padding-top:6px'>= {total} → mod 26 = <b style='color:#7fe0b0;font-size:1.3rem'>{total % 26}</b></div>",
                unsafe_allow_html=True)

    st.markdown("#### ③ 숫자 4개를 알파벳으로 바꿔 정답 입력")
    with st.form(f"f3b_{ss.pid}"):
        ans = st.text_input("평문 입력 (영어 4글자)")
        submitted = st.form_submit_button("제출")
    if submitted:
        if check_answer(ans):
            ss.solved_pid = ss.pid

# ---------- 정답 후 이동 ----------
if ss.get("solved_pid") == ss.pid:
    st.write(f"정답: **{p['word']}** · 이번 문제 시도 횟수: {ss.tries}회")
    st.button("다음 단계 ▶" if ss.stage < 3 else "게임 클리어 🎉", on_click=next_stage, type="primary")
else:
    st.button("🔄 새 문제 받기", on_click=retry_new)
