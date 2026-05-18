import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(
    page_title="EOEO Brand Dashboard",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Mono&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.settle-block { border-radius: 7px; padding: 10px 13px; margin: 6px 0; }
.sb-a { background:#E0F4EE; } .sb-b { background:#E5F0FB; }
.sb-c { background:#FEF0D8; } .sb-d { background:#EBEBEB; }
.dp-key { font-size: 11px; color: #999; margin-bottom: 2px; }
.dp-val { font-size: 13px; font-weight: 500; color: #1A1917; }
</style>
""", unsafe_allow_html=True)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]
SPREADSHEET_ID = "15aOqBxjaMyGHTJzhTNpHgT6-YcC-TRxHh4UEiMiMHUM"

@st.cache_data(ttl=300)
def load_data():
    try:
        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]), scopes=SCOPES
        )
        client = gspread.authorize(creds)
        sh = client.open_by_key(SPREADSHEET_ID)

        def get_sheet(name):
            try:
                ws = sh.worksheet(name)
                rows = ws.get_all_values()
                if len(rows) < 2:
                    return pd.DataFrame()
                # 헤더가 2행에 있는 경우(BRAND탭) 처리
                return rows
            except:
                return []

        raw_main  = get_sheet("Sheet1")
        raw_brand = get_sheet("BRAND")
        raw_tts   = get_sheet("TikTok Shop")
        raw_shp   = get_sheet("Shopify")
        return raw_main, raw_brand, raw_tts, raw_shp
    except Exception as e:
        st.error(f"Google Sheets 연결 오류: {e}")
        return [], [], [], []

def rows_to_df(rows, header_row=0):
    if not rows or len(rows) <= header_row:
        return pd.DataFrame()
    headers = [str(h).strip() for h in rows[header_row]]
    data = rows[header_row + 1:]
    padded = [r + [""] * (len(headers) - len(r)) for r in data]
    df = pd.DataFrame(padded, columns=headers)
    # 빈 행 제거
    df = df[df.apply(lambda r: any(str(v).strip() for v in r), axis=1)]
    return df.reset_index(drop=True)

with st.spinner("데이터 불러오는 중..."):
    raw_main, raw_brand, raw_tts, raw_shp = load_data()

if not raw_main:
    st.error("데이터를 불러올 수 없습니다. Secrets 설정을 확인해주세요.")
    st.stop()

# ── Sheet1: 헤더가 2행 (1행은 카테고리) ──
df_main = rows_to_df(raw_main, header_row=1)

# ── BRAND: 헤더가 2행 (1행은 그룹명) ──
df_brand = rows_to_df(raw_brand, header_row=1) if raw_brand else pd.DataFrame()

# ── TikTok Shop / Shopify: 헤더 1행 ──
df_tts = rows_to_df(raw_tts, header_row=0) if raw_tts else pd.DataFrame()
df_shp = rows_to_df(raw_shp, header_row=0) if raw_shp else pd.DataFrame()

# ── 컬럼 매핑 (Sheet1 기준) ──
# 영상에서 확인된 실제 컬럼명
COL = {
    "brand":   "Brand",           # Sheet1
    "company": "Company",
    "status":  "Status",
    "amz":     "Amazon Status",
    "tts":     "TikTok Shop Status",
    "pic":     "Main POC",
    "sub":     "Sub POC",
    "account": "Amazon Account",
    "access":  "접속 방법",
    "expire":  "Contract Expiration Date",
    "ct":      "Contract Type",
    "ph":      "PH TEAM POC",
}

# BRAND 탭 컬럼명
BCOL = {
    "brand":        "Brand (영문 기입)",
    "company":      "Company",
    "ct":           "Contract Type",
    "account":      "Amazon Account",
    "access":       "접속 방법",
    "tts_acct":     "Tiktok Shop Account",
    "status":       "Contract Status",
    "amz_us":       "Amazon Status",
    "amz_ca":       "Amazon CA",
    "amz_mx":       "Amazon MX",
    "tts":          "TikTok Shop Status",
    "expire":       "Contract Expiration Date",
    "pic":          "Brand Main PIC",
    "sub":          "Brand Sub PIC",
    "acct_pic":     "Account PIC",
    "ph":           "PH TEAM PIC",
    "settle":       "정산 방식",
    "sku":          "전체/일부 여부",
    "settle_start": "정산 시작일",
    "settle_end":   "정산 종료일",
    "card_type":    "카드 종류",
    "card_no":      "카드번호 (뒷자리3)",
    "remark":       "Remark",
}

# TikTok Shop 탭 컬럼명
TCOL = {
    "no":       "구분",
    "store":    "스토어 (브랜드)",
    "team":     "스토어 담당자/팀",
    "link":     "스토어 링크",
    "op":       "운영 주체",
    "payer":    "운영비 결제 담당자",
    "settle":   "정산 법인(계정 신원)",
    "bank":     "정산 은행",
    "acct":     "정산 계좌",
    "tpl":      "사용 3PL",
    "start":    "정산 시작일",
    "end":      "정산 종료일",
}

# Shopify 탭 컬럼명
SCOL = {
    "no":    "구분",
    "store": "스토어 (브랜드)",
    "team":  "스토어 담당자/팀",
    "link":  "스토어 링크",
    "op":    "운영 주체",
    "payer": "운영비 결제 담당자",
    "bank":  "정산 은행",
    "acct":  "정산 계좌",
    "tpl":   "사용 3PL",
    "note":  "비고",
    "end":   "종료",
}

def safe(df, row, col_key, col_map):
    col = col_map.get(col_key)
    if col is None or col not in df.columns:
        return ""
    val = str(row.get(col, "")).strip()
    return "" if val in ("nan", "None", "N/A") else val

STATUS_ICON = {"Running": "🟢", "End": "⚫", "Planned to end": "🟡",
               "Suspended": "🔴", "Contract negotiation": "🔵"}

# 정산 방식 분류 (BRAND 탭 정산방식 텍스트 기반)
def classify_settle(text):
    t = str(text).upper()
    if "A." in t or "핑퐁" in t:   return "A"
    if "B." in t or "TRANSFER" in t: return "B"
    if "C." in t or "별도" in t:    return "C"
    return "D"

SETTLE_META = {
    "A": {"label": "A. 이공이공 핑퐁 계정",       "cls": "sb-a", "color": "#0B6645"},
    "B": {"label": "B. 고객사→이공이공 transfer",  "cls": "sb-b", "color": "#1050A0"},
    "C": {"label": "C. 별도 정산",                "cls": "sb-c", "color": "#7A4A0A"},
    "D": {"label": "기타/미정",                    "cls": "sb-d", "color": "#555"},
}
SETTLE_ICON = {"A": "🟢", "B": "🔵", "C": "🟠", "D": "⚫"}

# ── Sidebar ────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏪 EOEO Dashboard")
    st.caption("브랜드 계약 현황 관리")
    st.divider()

    st.markdown("**Marketplace**")
    tab = st.radio("탭", ["전체", "Amazon", "TikTok Shop", "Shopify"],
                   label_visibility="collapsed")
    st.divider()

    st.markdown("**필터**")
    search = st.text_input("브랜드명 / 담당자 검색", placeholder="검색어 입력...")

    pic_col = COL["pic"]
    if pic_col in df_main.columns:
        pics = sorted(set(
            str(v).split("/")[0].strip() if "/" in str(v) else str(v).strip()
            for v in df_main[pic_col].dropna()
            if str(v).strip() and str(v).strip() not in ("NO PIC", "nan", "")
        ))
    else:
        pics = []
    pic_filter = st.selectbox("담당자", ["전체"] + pics)

    status_col = COL["status"]
    status_filter = st.selectbox("계약 상태",
        ["전체", "Running", "Planned to end", "End", "Contract negotiation"])

    st.divider()
    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()
    st.caption("5분마다 자동 갱신")

# ── 필터링 ─────────────────────────────────────────────
def row_matches(row):
    brand  = str(row.get(COL["brand"],  "")).strip()
    status = str(row.get(COL["status"], "")).strip()
    amz    = str(row.get(COL["amz"],    "")).strip()
    tts    = str(row.get(COL["tts"],    "")).strip()
    pic    = str(row.get(COL["pic"],    "")).strip()

    # Shopify: BRAND탭에서 해당 브랜드가 Shopify에 있는지 확인
    has_shp = False
    if not df_shp.empty and SCOL["store"] in df_shp.columns:
        has_shp = df_shp[SCOL["store"]].str.contains(brand, case=False, na=False).any()

    if tab == "Amazon"      and amz  not in ("Running", "End", "Suspended"): return False
    if tab == "TikTok Shop" and tts  not in ("Running", "End"):               return False
    if tab == "Shopify"     and not has_shp:                                  return False
    if status_filter != "전체" and status != status_filter: return False

    if pic_filter != "전체":
        pic_short = str(pic).split("/")[0].strip()
        if pic_filter != pic_short: return False

    if search:
        q = search.lower()
        if q not in brand.lower() and q not in pic.lower(): return False
    return True

filtered = df_main[df_main.apply(row_matches, axis=1)].reset_index(drop=True)

# ── 요약 지표 ──────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("표시 중", len(filtered))
if status_col in df_main.columns:
    c2.metric("🟢 Running",   len(filtered[filtered[status_col]=="Running"]))
    c3.metric("🟡 종료 예정", len(filtered[filtered[status_col]=="Planned to end"]))
    c4.metric("⚫ 계약 종료", len(filtered[filtered[status_col]=="End"]))

st.markdown(
    '<div style="background:#F7F6F2;border-radius:8px;padding:8px 14px;'
    'margin-bottom:14px;font-size:12px;color:#888">'
    '정산 방식 &nbsp;&nbsp;'
    '🟢 A. 이공이공 핑퐁 계정 &nbsp;&nbsp;'
    '🔵 B. 고객사→이공이공 transfer &nbsp;&nbsp;'
    '🟠 C. 별도 정산 &nbsp;&nbsp;'
    '⚫ 기타/미정'
    '</div>', unsafe_allow_html=True
)

if filtered.empty:
    st.info("검색 결과가 없습니다.")
    st.stop()

if "selected" not in st.session_state:
    st.session_state.selected = None

grid_col, detail_col = (st.columns([3, 2])
    if st.session_state.selected else (st.columns(1)[0], None))

# ── 카드 그리드 ────────────────────────────────────────
with (grid_col if detail_col else st.container()):
    cols = st.columns(3)
    for idx, (_, row) in enumerate(filtered.iterrows()):
        brand  = str(row.get(COL["brand"],   "")).strip()
        company= str(row.get(COL["company"], "")).strip()
        status = str(row.get(COL["status"],  "")).strip()
        amz    = str(row.get(COL["amz"],     "")).strip()
        tts    = str(row.get(COL["tts"],     "")).strip()
        pic    = str(row.get(COL["pic"],     "")).strip()
        ct     = str(row.get(COL["ct"],      "")).strip()
        expire = str(row.get(COL["expire"],  "")).strip()

        # 정산방식: BRAND 탭에서 매칭
        settle_key = "D"
        settle_text = ""
        if not df_brand.empty and BCOL["brand"] in df_brand.columns:
            bm = df_brand[df_brand[BCOL["brand"]] == brand]
            if not bm.empty and BCOL["settle"] in df_brand.columns:
                settle_text = str(bm.iloc[0][BCOL["settle"]]).strip()
                settle_key = classify_settle(settle_text)

        sm = SETTLE_META[settle_key]
        si = SETTLE_ICON[settle_key]
        status_icon = STATUS_ICON.get(status, "")
        pic_short = pic.split("/")[0].strip() if "/" in pic else pic
        selected = st.session_state.selected == brand

        plat_tags = " ".join(filter(None, [
            "`AMZ`"     if amz in ("Running",) else "",
            "`TTS`"     if tts == "Running"    else "",
            "`PB`"      if ct  == "PB"         else "",
            "`대행`"    if ct  == "Operation Agency" else "",
        ]))

        with cols[idx % 3]:
            border = "2px solid #1A1917" if selected else "1px solid #e8e7e2"
            exp_str = f" · {expire[:7]}" if expire and expire not in ("nan","") else ""
            st.markdown(f"""
            <div style="background:white;border:{border};border-radius:10px;
                        padding:13px 14px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <div>
                        <div style="font-size:13px;font-weight:500">{brand}</div>
                        <div style="font-size:11px;color:#aaa">{company}</div>
                    </div>
                    <span style="font-size:11px;white-space:nowrap">{status_icon} {status}</span>
                </div>
                {"<div style='font-size:11px;margin-bottom:3px'>" + plat_tags + "</div>" if plat_tags else ""}
                <div style="font-size:11px;color:#888;margin-top:3px">{si} {sm['label']}</div>
                <div style="font-size:11px;color:#aaa;margin-top:3px">
                    👤 {pic_short}{exp_str}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(
                "닫기 ✕" if selected else "상세 보기 →",
                key=f"btn_{brand}_{idx}",
                use_container_width=True
            ):
                st.session_state.selected = None if selected else brand
                st.rerun()

# ── 상세 패널 ──────────────────────────────────────────
if st.session_state.selected and detail_col:
    brand_sel = st.session_state.selected
    main_rows = df_main[df_main[COL["brand"]] == brand_sel]
    if main_rows.empty:
        st.session_state.selected = None
        st.rerun()

    row = main_rows.iloc[0]

    # BRAND 탭 매칭
    brand_row = {}
    if not df_brand.empty and BCOL["brand"] in df_brand.columns:
        bm = df_brand[df_brand[BCOL["brand"]] == brand_sel]
        if not bm.empty:
            brand_row = bm.iloc[0].to_dict()

    # TTS 탭 매칭
    tts_row = {}
    if not df_tts.empty and TCOL["store"] in df_tts.columns:
        tm = df_tts[df_tts[TCOL["store"]].str.contains(brand_sel, case=False, na=False)]
        if not tm.empty:
            tts_row = tm.iloc[0].to_dict()

    # Shopify 탭 매칭
    shp_row = {}
    if not df_shp.empty and SCOL["store"] in df_shp.columns:
        sm2 = df_shp[df_shp[SCOL["store"]].str.contains(brand_sel, case=False, na=False)]
        if not sm2.empty:
            shp_row = sm2.iloc[0].to_dict()

    # 기본값
    status = str(row.get(COL["status"],  "")).strip()
    amz    = str(row.get(COL["amz"],     "")).strip()
    tts_s  = str(row.get(COL["tts"],     "")).strip()
    ct     = str(row.get(COL["ct"],      "")).strip()
    pic    = str(row.get(COL["pic"],     "")).strip()
    sub    = str(row.get(COL["sub"],     "")).strip()
    expire = str(row.get(COL["expire"],  "")).strip()
    account= str(row.get(COL["account"],"")).strip()
    access = str(row.get(COL["access"],  "")).strip()
    ph     = str(row.get(COL["ph"],      "")).strip()
    company= str(row.get(COL["company"], "")).strip()

    # 정산 정보 (BRAND 탭 우선)
    settle_text = str(brand_row.get(BCOL["settle"], "")).strip() if brand_row else ""
    settle_key  = classify_settle(settle_text)
    sm          = SETTLE_META[settle_key]
    card_type   = str(brand_row.get(BCOL["card_type"],  "")).strip() if brand_row else ""
    card_no     = str(brand_row.get(BCOL["card_no"],    "")).strip() if brand_row else ""
    sku         = str(brand_row.get(BCOL["sku"],        "")).strip() if brand_row else ""
    remark      = str(brand_row.get(BCOL["remark"],     "")).strip() if brand_row else ""
    s_start     = str(brand_row.get(BCOL["settle_start"],"")).strip() if brand_row else ""
    s_end       = str(brand_row.get(BCOL["settle_end"],  "")).strip() if brand_row else ""

    has_shp = bool(shp_row)

    with detail_col:
        st.markdown(f"### {brand_sel}")
        if company and company not in ("nan",""):
            st.caption(company)

        badges = " ".join(filter(None,[
            f"`{status}`",
            "`PB`"      if ct=="PB"                 else "",
            "`운영대행`" if ct=="Operation Agency"   else "",
            "`Amazon`"  if amz=="Running"            else "",
            "`TikTok`"  if tts_s=="Running"          else "",
            "`Shopify`" if has_shp                   else "",
        ]))
        st.markdown(badges)
        st.divider()

        # 계약 정보
        st.markdown("**📄 계약 정보**")
        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='dp-key'>계정명</div><div class='dp-val'>{account or '—'}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='dp-key'>접속 방법</div><div class='dp-val'>{access or '—'}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='dp-key'>계약 만료일</div><div class='dp-val'>{expire or '—'}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='dp-key'>SKU 범위</div><div class='dp-val'>{sku or '—'}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='dp-key'>Main PIC</div><div class='dp-val'>{pic or '—'}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='dp-key'>Sub PIC</div><div class='dp-val'>{sub or '—'}</div>", unsafe_allow_html=True)
        if ph and ph not in ("nan","","NO PIC"):
            st.markdown(f"<div class='dp-key'>PH Team</div><div class='dp-val'>{ph}</div>", unsafe_allow_html=True)
        if remark and remark not in ("nan",""):
            st.markdown(f"<div class='dp-key'>비고</div><div class='dp-val'>{remark}</div>", unsafe_allow_html=True)

        st.divider()

        # 정산 방식
        st.markdown("**💰 정산 방식**")
        st.markdown(
            f'<div class="settle-block {sm["cls"]}">'
            f'<div style="font-size:10px;font-weight:500;color:{sm["color"]};margin-bottom:3px">{sm["label"]}</div>'
            f'<div style="font-size:13px;font-weight:500;color:{sm["color"]}">{settle_text or sm["label"]}</div>'
            f'</div>', unsafe_allow_html=True
        )
        if s_start or s_end:
            c1, c2 = st.columns(2)
            if s_start and s_start not in ("nan",""):
                c1.markdown(f"<div class='dp-key'>정산 시작일</div><div class='dp-val'>{s_start}</div>", unsafe_allow_html=True)
            if s_end and s_end not in ("nan",""):
                c2.markdown(f"<div class='dp-key'>정산 종료일</div><div class='dp-val'>{s_end}</div>", unsafe_allow_html=True)
        if card_type and card_type not in ("nan",""):
            c1, c2 = st.columns(2)
            c1.markdown(f"<div class='dp-key'>카드 종류</div><div class='dp-val'>{card_type}</div>", unsafe_allow_html=True)
            if card_no and card_no not in ("nan",""):
                c2.markdown(f"<div class='dp-key'>카드 번호 (뒷 3자리)</div><div class='dp-val' style='font-family:monospace'>{card_no}</div>", unsafe_allow_html=True)

        # TikTok Shop
        if tts_row:
            st.divider()
            st.markdown("**🎵 TikTok Shop**")
            t_store  = str(tts_row.get(TCOL["store"],  "")).strip()
            t_team   = str(tts_row.get(TCOL["team"],   "")).strip()
            t_op     = str(tts_row.get(TCOL["op"],     "")).strip()
            t_settle = str(tts_row.get(TCOL["settle"], "")).strip()
            t_bank   = str(tts_row.get(TCOL["bank"],   "")).strip()
            t_acct   = str(tts_row.get(TCOL["acct"],   "")).strip()
            t_link   = str(tts_row.get(TCOL["link"],   "")).strip()
            t_end    = str(tts_row.get(TCOL["end"],    "")).strip()

            if t_store not in ("nan",""):  st.markdown(f"**{t_store}**")
            if t_team  not in ("nan",""):  st.caption(f"담당팀: {t_team}")
            if t_op    not in ("nan",""):  st.caption(f"운영: {t_op}")
            if t_settle not in ("nan",""): st.caption(f"정산 법인: {t_settle}")
            if t_bank  not in ("nan",""):  st.caption(f"은행: {t_bank}  {t_acct}")
            if t_end   not in ("nan",""):  st.caption(f"정산 종료: {t_end}")
            if t_link  and t_link.startswith("http"):
                st.markdown(f"[↗ 스토어 링크]({t_link})")

        # Shopify
        if shp_row:
            st.divider()
            st.markdown("**🛍️ Shopify**")
            s_store = str(shp_row.get(SCOL["store"], "")).strip()
            s_team  = str(shp_row.get(SCOL["team"],  "")).strip()
            s_op    = str(shp_row.get(SCOL["op"],    "")).strip()
            s_tpl   = str(shp_row.get(SCOL["tpl"],   "")).strip()
            s_note  = str(shp_row.get(SCOL["note"],  "")).strip()
            s_link  = str(shp_row.get(SCOL["link"],  "")).strip()
            s_end   = str(shp_row.get(SCOL["end"],   "")).strip()

            if s_store not in ("nan",""):  st.markdown(f"**{s_store}**")
            if s_team  not in ("nan",""):  st.caption(f"담당팀: {s_team}")
            if s_op    not in ("nan",""):  st.caption(f"운영: {s_op}")
            if s_tpl   not in ("nan",""):  st.caption(f"3PL: {s_tpl}")
            if s_note  not in ("nan",""):  st.caption(s_note)
            if s_end   not in ("nan",""):  st.caption(f"종료: {s_end}")
            if s_link  and s_link.startswith("http"):
                st.markdown(f"[↗ Shopify Admin]({s_link})")
