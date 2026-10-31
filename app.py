import math
import random

import streamlit as st
import streamlit.components.v1 as components

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
    while True:
        K = [[random.randint(0, 25) for _ in range(2)] for _ in range(2)]
        det = (K[0][0] * K[1][1] - K[0][1] * K[1][0]) % 26
        if math.gcd(det, 26) == 1:
            break
    word = random.choice(WORDS4)  # 2x2 행렬이므로 2글자씩 묶기 위해 4글자 단어 사용
    return {"word": word, "K": K, "cipher": hill_encrypt(word, K), "inv_ok": False}


CALC_HTML = """
<style>
  body { margin:0; font-family: 'Segoe UI', sans-serif; }
  .calc { background:#2a2f40; border:1px solid #4a5070; border-radius:12px; padding:12px; max-width:340px; margin:auto; }
  #disp { width:100%; box-sizing:border-box; background:#ffffff; color:#000000; caret-color:#000000;
          font-size:26px; font-weight:600; text-align:right; padding:10px 12px; border:none; border-radius:8px;
          font-family:'Courier New', monospace; }
  #res { color:#f0c36d; text-align:right; min-height:22px; margin:6px 4px 8px 0; font-size:15px; font-family:'Courier New', monospace; }
  .grid { display:grid; grid-template-columns:repeat(5, 1fr); gap:6px; }
  button { background:#3b4260; color:#ffffff; border:none; border-radius:8px; padding:11px 0; font-size:17px; cursor:pointer; }
  button:hover { background:#4c5580; }
  button.op { background:#5b4a1f; } button.op:hover { background:#7a6228; }
  button.eq { background:#2e7d5b; } button.eq:hover { background:#3a9a70; }
  button.clr { background:#7d2e3a; } button.clr:hover { background:#9a3a49; }
</style>
<div class="calc">
  <input id="disp" type="text" inputmode="none" placeholder="0" autocomplete="off">
  <div id="res"></div>
  <div class="grid">
    <button onclick="add('7')">7</button><button onclick="add('8')">8</button><button onclick="add('9')">9</button>
    <button class="op" onclick="add('÷')">÷</button><button class="clr" onclick="clr()">C</button>
    <button onclick="add('4')">4</button><button onclick="add('5')">5</button><button onclick="add('6')">6</button>
    <button class="op" onclick="add('×')">×</button><button class="clr" onclick="back()">⌫</button>
    <button onclick="add('1')">1</button><button onclick="add('2')">2</button><button onclick="add('3')">3</button>
    <button class="op" onclick="add('-')">−</button><button class="op" onclick="add('(')">(</button>
    <button onclick="add('0')">0</button><button class="op" onclick="add(' mod ')">mod</button><button class="op" onclick="add('.')">.</button>
    <button class="op" onclick="add('+')">+</button><button class="op" onclick="add(')')">)</button>
    <button class="eq" style="grid-column: 1 / -1" onclick="calc()">=</button>
  </div>
</div>
<script>
  const d = document.getElementById('disp'), r = document.getElementById('res');
  function add(t){ d.value += t; d.focus(); }
  function clr(){ d.value=''; r.textContent=''; }
  function back(){ d.value = d.value.endsWith(' mod ') ? d.value.slice(0,-5) : d.value.slice(0,-1); }
  function ev(e){
    e = e.replace(/×/g,'*').replace(/÷/g,'/').replace(/−/g,'-').trim();
    if(!/^[0-9+\\-*/().\\s]+$/.test(e)) throw 'x';
    return Function('"use strict"; return (' + e + ')')();
  }
  function calc(){
    try{
      let t = d.value; let v;
      if(t.includes('mod')){
        const i = t.lastIndexOf('mod');
        const m = ev(t.slice(i+3)); const l = ev(t.slice(0,i));
        v = ((l % m) + m) % m;
      } else { v = ev(t); }
      r.textContent = '= ' + (Number.isInteger(v) ? v : Math.round(v*1e6)/1e6);
    } catch(e){ r.textContent = '식을 확인하세요'; }
  }
  d.addEventListener('keydown', e => { if(e.key==='Enter'){ e.preventDefault(); calc(); } });
</script>
"""


def show_calculator():
    st.markdown("**🧮 계산기** (mod 버튼: 예) `9 × (7 − 3) mod 26` 입력 후 `=`)")
    components.html(CALC_HTML, height=330)


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
2. 역원이 맞으면 다음 단계로 넘어갑니다.
3. 문제 화면에 있는 **계산기**로 암호문의 알파벳을 숫자로 바꾼 뒤 `a⁻¹ · (C − b) mod 26`을 계산하고, 숫자를 다시 알파벳으로 바꿔 정답을 입력합니다.

`a`는 3, 5, 7 중 하나이고, `b`는 문제 화면에서 미리 알려줍니다.

💡 역원 구하는 팁: `a · x`를 26으로 나눈 나머지가 1이 되는 x를 찾으면 됩니다. (x는 0~25 사이)
"""),
    3: ("3단계 · 힐 암호",
        """
**힐 암호**는 행렬을 이용한 암호로, 글자를 **2글자씩 묶어서** 암호화합니다. (A=0, B=1, … Z=25)

**암호화:**  `C = K · P (mod 26)`  (K는 2×2 키 행렬, P는 두 글자의 숫자 열벡터)
**복호화:**  `P = K⁻¹ · C (mod 26)`

**역행렬 구하는 법** (K = [[a, b], [c, d]])
1. 행렬식 `det = ad − bc`를 구하고 mod 26 합니다.
2. `det`의 역원 `det⁻¹` (mod 26)을 구합니다.
3. `K⁻¹ = det⁻¹ · [[d, −b], [−c, a]]  (mod 26)` (음수는 +26을 해서 0~25로 만듭니다.)

**진행 방법**
1. 주어진 키 행렬 K의 **역행렬 K⁻¹을 직접 구해** 입력합니다.
2. 맞으면 암호문을 2글자씩 나눠 `K⁻¹ · C (mod 26)`을 계산해 정답을 입력합니다.
   (이 단계의 암호문은 2글자씩 2묶음, 총 4글자입니다.)
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
    show_calculator()

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
        st.markdown("#### ② 복호화 (계산기 사용)")
        st.write("암호문을 숫자로 바꾼 뒤 `P = a⁻¹ · (C − b) mod 26` 을 계산해 알파벳으로 바꿔 보세요.")
        nums = ", ".join(f"{ch}={n(ch)}" for ch in p["cipher"])
        st.info(f"암호문 숫자: {nums}")
        with st.form(f"f2b_{ss.pid}"):
            ans = st.text_input("평문 입력 (영어)")
            submitted = st.form_submit_button("제출")
        if submitted:
            if check_answer(ans):
                ss.solved_pid = ss.pid

# ----- 3단계 -----
else:
    K = p["K"]
    st.write("**키 행렬 K**")
    st.latex(rf"K=\begin{{pmatrix}}{K[0][0]} & {K[0][1]}\\ {K[1][0]} & {K[1][1]}\end{{pmatrix}}")
    show_table()
    st.markdown("#### ① 역행렬 K⁻¹ 구하기 (직접 계산, mod 26)")
    Kinv = hill_inverse(K)
    if not p["inv_ok"]:
        with st.form(f"f3a_{ss.pid}"):
            c1, c2 = st.columns(2)
            v00 = c1.number_input("K⁻¹ 1행 1열", 0, 25, 0, key=f"v00_{ss.pid}")
            v01 = c2.number_input("K⁻¹ 1행 2열", 0, 25, 0, key=f"v01_{ss.pid}")
            v10 = c1.number_input("K⁻¹ 2행 1열", 0, 25, 0, key=f"v10_{ss.pid}")
            v11 = c2.number_input("K⁻¹ 2행 2열", 0, 25, 0, key=f"v11_{ss.pid}")
            if st.form_submit_button("역행렬 확인"):
                if [[v00, v01], [v10, v11]] == Kinv:
                    p["inv_ok"] = True
                    st.rerun()
                else:
                    st.error("❌ 틀렸습니다. det, det의 역원, 여인자 행렬 순서로 다시 계산해 보세요.")
        with st.expander("힌트"):
            st.write("det = ad − bc (mod 26) → det의 역원 구하기 → det⁻¹ · [[d, −b], [−c, a]] (mod 26)")
    else:
        st.success("✅ 역행렬 확인 완료!")
        st.latex(rf"K^{{-1}}=\begin{{pmatrix}}{Kinv[0][0]} & {Kinv[0][1]}\\ {Kinv[1][0]} & {Kinv[1][1]}\end{{pmatrix}}")
        st.markdown("#### ② 복호화")
        st.write("암호문을 2글자씩 나눠 숫자 열벡터로 만든 뒤 `K⁻¹ · C (mod 26)`을 계산하세요.")
        cp = p["cipher"]
        st.info(f"묶음 1: {cp[0]}={n(cp[0])}, {cp[1]}={n(cp[1])}   |   묶음 2: {cp[2]}={n(cp[2])}, {cp[3]}={n(cp[3])}")
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
