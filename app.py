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
    @import url('https://fonts.googleapis.com/css2?family=Jua&family=Noto+Sans+KR:wght@400;500;700&display=swap');
    .stApp, .stApp p, .stApp li, .stApp label, .stApp button, .stApp input, .stApp textarea { font-family: 'Noto Sans KR', sans-serif; }
    h1, h2, h3, .sec { font-family: 'Jua', 'Noto Sans KR', sans-serif !important; }
    .stApp { background: linear-gradient(160deg, #14161d 0%, #1b1f2b 100%); color: #e6e6ea; }
    h1, h2, h3 { color: #f0c36d !important; }
    .cipher-box {
        background: #0f1117; border: 1px solid #3a3f52; border-radius: 12px;
        padding: 18px; text-align: center; font-size: 2.4rem; letter-spacing: 0.6rem;
        color: #7fe0b0; font-family: 'Courier New', monospace; margin: 10px 0 18px 0;
    }
    .sec { color: #f0c36d; font-size: 1.3rem; margin: 26px 0 8px 0; }
    .card { background: #1f2331; border: 1px solid #343a52; border-radius: 14px; padding: 14px 18px; margin: 6px 0 10px 0; line-height: 1.8; }
    .note { color: #aeb3c7; font-size: .92rem; margin: 6px 2px 10px 2px; line-height: 1.6; }
    .tip { background: #2a2616; border: 1px solid #6b5a22; color: #f6e3a8; border-radius: 12px; padding: 10px 14px; margin: 10px 0; line-height: 1.7; }
    .ex { background: #142a22; border: 1px solid #2e6b52; border-radius: 12px; padding: 12px 16px; margin: 10px 0; line-height: 1.9; }
    .ex .k { color: #7fe0b0; font-weight: 700; }
    .step { display: flex; gap: 12px; align-items: flex-start; background: #1a1e2b; border-radius: 12px; padding: 10px 14px; margin: 8px 0; }
    .step-num { flex: 0 0 32px; height: 32px; border-radius: 50%; background: #f0c36d; color: #14161d; font-weight: 700; display: flex; align-items: center; justify-content: center; }
    .step-txt { display: flex; flex-direction: column; line-height: 1.6; }
    .step-txt span { color: #b9bdd0; font-size: .93rem; }
    .flow { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin: 10px 0; }
    .f-box { background: #0f1117; border: 1px solid #3a3f52; border-radius: 10px; padding: 8px 12px; text-align: center; min-width: 64px; }
    .f-box small { display: block; color: #9aa0b8; font-size: .74rem; }
    .f-box b { font-size: 1.15rem; color: #e6e6ea; }
    .f-box.hot { border-color: #7fe0b0; }
    .f-box.hot b { color: #7fe0b0; }
    .f-arrow { color: #f0c36d; font-size: 1.1rem; }
    .agrid { display: grid; grid-template-columns: repeat(13, 1fr); gap: 3px; margin: 4px 0; }
    .agrid div { background: #0f1117; border: 1px solid #2f3448; border-radius: 6px; text-align: center; padding: 3px 0; }
    .agrid b { display: block; color: #7fe0b0; font-size: .95rem; }
    .agrid small { color: #aeb3c7; font-size: .72rem; }
    .crow { display: grid; grid-template-columns: 44px repeat(13, 1fr); gap: 3px; margin: 3px 0; }
    .crow span { color: #9aa0b8; font-size: .74rem; align-self: center; }
    .crow div { background: #0f1117; border: 1px solid #2f3448; border-radius: 6px; text-align: center; padding: 4px 0; color: #e6e6ea; font-weight: 700; }
    .crow.cipher div { color: #f0c36d; border-color: #6b5a22; }
    .cstrip { margin: 6px 0 12px 0; }
    .try { background: #0f1117; border: 1px solid #2f3448; border-radius: 10px; padding: 7px 14px; margin: 5px 0; }
    .try.ok { border-color: #7fe0b0; color: #7fe0b0; font-weight: 700; }
    .mxw { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin: 12px 0; }
    .mx { display: grid; grid-template-columns: repeat(2, 46px); gap: 6px; padding: 6px 10px; border-left: 3px solid #aeb3c7; border-right: 3px solid #aeb3c7; border-radius: 8px; }
    .vec { display: grid; gap: 6px; padding: 6px 10px; border-left: 3px solid #aeb3c7; border-right: 3px solid #aeb3c7; border-radius: 8px; text-align: center; font-weight: 700; }
    .mx span, .vec span { text-align: center; font-size: 1.1rem; font-weight: 700; padding: 4px 8px; border-radius: 6px; }
    .r1 { color: #7fb7ff; background: rgba(127,183,255,.13); }
    .r2 { color: #ffa27f; background: rgba(255,162,127,.13); }
    .mxw .op { font-size: 1.4rem; color: #f0c36d; }
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

# ---------- 설명 화면 (그림 + 예시) ----------
def _h(*parts):
    return "".join(parts)


def sec(title):
    return f'<div class="sec">{title}</div>'


def card(html):
    return f'<div class="card">{html}</div>'


def note(html):
    return f'<div class="note">{html}</div>'


def tip(html):
    return f'<div class="tip">💡 {html}</div>'


def ex(html):
    return f'<div class="ex">{html}</div>'


def step(num, title, body=""):
    return (f'<div class="step"><div class="step-num">{num}</div>'
            f'<div class="step-txt"><b>{title}</b><span>{body}</span></div></div>')


def flow(items):
    out = ""
    for i, (label, value, hot) in enumerate(items):
        if i:
            out += '<div class="f-arrow">➜</div>'
        out += f'<div class="f-box{" hot" if hot else ""}"><small>{label}</small><b>{value}</b></div>'
    return f'<div class="flow">{out}</div>'


def alpha_grid():
    html = ""
    for start in (0, 13):
        cells = "".join(f"<div><b>{ALPHA[i]}</b><small>{i}</small></div>" for i in range(start, start + 13))
        html += f'<div class="agrid">{cells}</div>'
    return html


def caesar_strip():
    html = ""
    for start in (0, 13):
        top = "".join(f"<div>{ALPHA[i]}</div>" for i in range(start, start + 13))
        bot = "".join(f"<div>{ALPHA[(i + 3) % 26]}</div>" for i in range(start, start + 13))
        html += (f'<div class="cstrip"><div class="crow"><span>평문</span>{top}</div>'
                 f'<div class="crow cipher"><span>암호문</span>{bot}</div></div>')
    return html


def try_row(text, ok=False):
    return f'<div class="try{" ok" if ok else ""}">{text}</div>'


MOD_NOTE = note("🕐 <b>mod 26</b>은 시계와 같아요. 결과가 26 이상이면 <b>26을 빼서</b> 0~25로 맞춥니다. 예) 30 → 30 − 26 = <b>4</b>")


def intro_caesar():
    return _h(
        sec("🏛️ 시저 암호란?"),
        card("로마의 장군 <b>율리우스 카이사르(시저)</b>가 비밀 편지에 쓴 암호예요.<br>알파벳을 전부 <b>3칸씩 뒤로 밀어서</b> 글자를 바꿉니다."),
        sec("① 이렇게 바뀌어요"),
        caesar_strip(),
        note("Z 다음에는 다시 A로 돌아와요. (X→A, Y→B, Z→C)"),
        sec("② 푸는 방법은 반대로!"),
        flow([("암호문", "D", False), ("3칸 앞으로", "◀◀◀", False), ("평문", "A", True)]),
        step(1, "암호문 글자를 하나 봅니다", "예) D"),
        step(2, "알파벳에서 3칸 앞으로 갑니다", "D → C → B → A. (A보다 앞이면 Z로 넘어가요)"),
        step(3, "모든 글자를 바꿔 단어를 완성합니다"),
        ex('<b>예시</b> 암호문 <span class="k">DUH</span><br>D → A, U → R, H → E<br>정답: <span class="k">ARE</span>'),
    )


def intro_affine():
    return _h(
        sec("🧩 아핀 암호란?"),
        card("글자를 <b>숫자로 바꾼 뒤</b>, 식 <b>(a × 글자 + b)</b>로 섞어서 다시 글자로 바꾸는 암호예요."),
        sec("① 글자 ↔ 숫자"),
        alpha_grid(),
        sec("② 암호화는 이렇게 (a = 9, b = 2 예시)"),
        flow([("평문", "E", False), ("숫자", "4", False), ("× 9", "36", False),
              ("+ 2", "38", False), ("mod 26", "12", False), ("암호문", "M", True)]),
        sec("③ 풀 때는 거꾸로!"),
        flow([("암호문", "M", False), ("숫자", "12", False), ("− b(2)", "10", False),
              ("× 역원(3)", "30", False), ("mod 26", "4", False), ("평문", "E", True)]),
        tip("풀이 식: <b>역원 × (암호문 숫자 − b)</b> 를 계산하고 mod 26"),
        sec("④ 역원이 뭐예요?"),
        card("a에 곱했을 때 <b>26으로 나눈 나머지가 1</b>이 되는 수예요. 1, 2, 3 … 순서대로 곱해 보면 찾을 수 있어요."),
        note("예) a = 9 의 역원 찾기"),
        try_row("9 × 1 = 9 → 나머지 9 ✕"),
        try_row("9 × 2 = 18 → 나머지 18 ✕"),
        try_row("9 × 3 = 27 → 27 − 26 = 1 → 나머지 1 ✔ 역원은 3!", ok=True),
        MOD_NOTE,
        sec("🎮 게임에서는"),
        step(1, "a의 역원을 직접 구해서 입력", "a는 3, 5, 7 중 하나, b는 화면에 미리 알려줘요"),
        step(2, "자동 계산기에 숫자 3개 입력", "역원, 암호문 글자의 숫자, b 를 넣으면 알파벳까지 계산해 줘요"),
        step(3, "나온 알파벳을 이어서 정답 입력"),
    )


def intro_hill():
    return _h(
        sec("🧩 힐 암호란?"),
        card("글자를 <b>2개씩 묶어서</b> 숫자 2개로 만들고, <b>숫자 표(행렬)</b>와 곱해서 섞는 암호예요."),
        sec("① 이런 흐름이에요"),
        flow([("암호문 2글자", "TC", False), ("숫자로", "19, 2", False), ("행렬 곱하기", "K<sup>-1</sup>", False),
              ("mod 26", "14, 21", False), ("평문 2글자", "OV", True)]),
        sec("② 곱하는 방법"),
        '<div class="mxw"><div class="mx"><span class="r1">p</span><span class="r1">q</span><span class="r2">r</span><span class="r2">s</span></div>'
        '<div class="op">×</div><div class="vec"><span>x</span><span>y</span></div><div class="op">=</div>'
        '<div class="vec"><span class="r1">p·x + q·y</span><span class="r2">r·x + s·y</span></div></div>',
        card('<span class="r1">&nbsp;윗줄(p, q)&nbsp;</span> → <b>첫 번째 글자</b><br><span class="r2">&nbsp;아랫줄(r, s)&nbsp;</span> → <b>두 번째 글자</b>'),
        sec("③ 예시"),
        note("K<sup>-1</sup> = [[2, 1], [1, 1]], 암호문 묶음 TC (T=19, C=2)"),
        '<div class="mxw"><div class="mx"><span class="r1">2</span><span class="r1">1</span><span class="r2">1</span><span class="r2">1</span></div>'
        '<div class="op">×</div><div class="vec"><span>19</span><span>2</span></div><div class="op">=</div>'
        '<div class="vec"><span class="r1">2×19 + 1×2 = 40</span><span class="r2">1×19 + 1×2 = 21</span></div></div>',
        try_row("첫 번째 글자: 40 → 40 − 26 = 14 → <b>O</b>"),
        try_row("두 번째 글자: 21 → <b>V</b>"),
        ex('정답: <span class="k">OV</span>'),
        MOD_NOTE,
        sec("🎮 게임에서는"),
        step(1, "K⁻¹과 묶음 숫자를 확인", "K⁻¹은 문제에서 미리 알려줘요."),
        step(2, "식 칸에 숫자를 넣기", "곱셈과 mod 26은 자동으로 계산해 줘요"),
        step(3, "나온 숫자 4개를 알파벳으로 바꿔 정답 입력", "표를 보고 숫자 → 알파벳"),
    )


INTRO = {
    1: ("1단계 · 시저 암호", intro_caesar),
    2: ("2단계 · 아핀 암호", intro_affine),
    3: ("3단계 · 힐 암호", intro_hill),
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
    st.markdown(body(), unsafe_allow_html=True)
    st.button("문제 풀기 ▶", on_click=go_play, type="primary")
    st.stop()

# ---------- 문제 화면 ----------
p = ss.problem
title, body = INTRO[ss.stage]
st.header(title)
with st.expander("📖 암호 설명 / 푸는 방법 다시 보기"):
    st.markdown(body(), unsafe_allow_html=True)

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
