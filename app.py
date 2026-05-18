import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json

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

# ── Google Sheets 연결 ─────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]
SPREADSHEET_ID = "15aOqBxjaMyGHTJzhTNpHgT6-YcC-TRxHh4UEiMiMHUM"

@st.cache_data(ttl=300)  # 5분마다 자동 갱신
def load_data():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        sh = client.open_by_key(SPREADSHEET_ID)

        # ── Sheet1: 브랜드 현황 ──
        ws1 = sh.get_worksheet(0)
        rows1 = ws1.get_all_values()

        # ── BRAND 탭: 계약 상세 ──
        try:
            ws_brand = sh.worksheet("BRAND")
            rows_brand = ws_brand.get_all_values()
        except:
            rows_brand = []

        # ── TikTok Shop 탭 ──
        try:
            ws_tts = sh.worksheet("TikTok Shop")
            rows_tts = ws_tts.get_all_values()
        except:
            rows_tts = []

        # ── Shopify 탭 ──
        try:
            ws_shp = sh.worksheet("Shopify")
            rows_shp = ws_shp.get_all_values()
        except:
            rows_shp = []

        return rows1, rows_brand, rows_tts, rows_shp

    except Exception as e:
        st.error(f"Google Sheets 연결 오류: {e}")
        return [], [], [], []

# ── 데이터 로드 ────────────────────────────────────────
with st.spinner("데이터 불러오는 중..."):
    rows1, rows_brand, rows_tts, rows_shp = load_data()

if not rows1:
    st.error("데이터를 불러올 수 없습니다. Secrets 설정을 확인해주세요.")
    st.stop()

# ── 데이터 파싱 ────────────────────────────────────────
def parse_sheet(rows, skip_rows=1):
    if len(rows) <= skip_rows:
        return pd.DataFrame()
    headers = rows[skip_rows - 1] if skip_rows > 0 else rows[0]
    data = rows[skip_rows:]
    # 헤더 길이에 맞게 각 행 패딩
    max_col = len(headers)
    padded = [r + [""] * (max_col - len(r)) for r in data]
    return pd.DataFrame(padded, columns=headers)

df_main   = parse_sheet(rows1, skip_rows=1)
df_brand  = parse_sheet(rows_brand, skip_rows=1)
df_tts    = parse_sheet(rows_tts, skip_rows=1)
df_shp    = parse_sheet(rows_shp, skip_rows=1)

# 컬럼명 정리 (공백 제거)
for df in [df_main, df_brand, df_tts, df_shp]:
    df.columns = [str(c).strip() for c in df.columns]

STATUS_ICON = {"Running": "🟢", "End": "⚫", "Planned to end": "🟡", "Suspended": "🔴"}
SETTLE_META = {
    "A": {"label": "A. 이공이공 핑퐁 계정",        "cls": "sb-a", "color": "#0B6645"},
    "B": {"label": "B. 고객사→이공이공 transfer",   "cls": "sb-b", "color": "#1050A0"},
    "C": {"label": "C. 별도 정산",                 "cls": "sb-c", "color": "#7A4A0A"},
    "D": {"label": "기타/미정",                     "cls": "sb-d", "color": "#555"},
}
SETTLE_ICON = {"A": "🟢", "B": "🔵", "C": "🟠", "D": "⚫"}

def get_col(df, *names):
    """여러 가능한 컬럼명 중 존재하는 것 반환"""
    for n in names:
        if n in df.columns:
            return n
    return None

def cell(df, row_idx, *col_names):
    col = get_col(df, *col_names)
    if col is None or row_idx >= len(df):
        return ""
    return str(df.iloc[row_idx][col]).strip()

# ── Sidebar ────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏪 EOEO Dashboard")
    st.caption("브랜드 계약 현황 관리")
    st.divider()

    st.markdown("**Marketplace**")
    tab = st.radio(
        "탭",
        ["전체", "Amazon", "TikTok Shop", "Shopify"],
        label_visibility="collapsed"
    )
    st.divider()

    st.markdown("**필터**")
    search = st.text_input("브랜드명 / 담당자 검색", placeholder="검색어 입력...")

    # 담당자 목록 동적 생성
    pic_col = get_col(df_main, "Main PIC", "PIC", "담당자")
    if pic_col:
        pics = sorted(set(
            str(v).split("/")[1].strip() if "/" in str(v) else str(v)
            for v in df_main[pic_col].dropna()
            if str(v).strip() and str(v).strip() != "NO PIC"
        ))
    else:
        pics = []
    pic_filter = st.selectbox("담당자", ["전체"] + pics)

    status_col = get_col(df_main, "Status", "상태", "계약상태")
    if status_col:
        statuses = ["전체"] + [s for s in ["Running", "Planned to end", "End"] if s in df_main[status_col].values]
    else:
        statuses = ["전체", "Running", "Planned to end", "End"]
    status_filter = st.selectbox("계약 상태", statuses)

    st.divider()
    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()
    st.caption("5분마다 자동 갱신")

# ── 필터링 ─────────────────────────────────────────────
amz_col    = get_col(df_main, "Amazon", "AMZ", "아마존")
tts_col    = get_col(df_main, "TikTok Shop", "TTS", "틱톡")
shp_col    = get_col(df_main, "Shopify", "쇼피파이")
brand_col  = get_col(df_main, "Brand", "브랜드", "Brand Name", "영문명")

def row_matches(row):
    status = str(row.get(status_col, "")).strip() if status_col else ""
    amz    = str(row.get(amz_col, "")).strip()    if amz_col    else ""
    tts    = str(row.get(tts_col, "")).strip()    if tts_col    else ""
    shp    = str(row.get(shp_col, "")).strip()    if shp_col    else ""
    pic    = str(row.get(pic_col, "")).strip()    if pic_col    else ""
    brand  = str(row.get(brand_col, "")).strip()  if brand_col  else ""

    if tab == "Amazon"      and amz not in ("Running", "End"): return False
    if tab == "TikTok Shop" and tts not in ("Running", "End"): return False
    if tab == "Shopify"     and not shp: return False
    if status_filter != "전체" and status != status_filter: return False
    if pic_filter != "전체":
        pic_short = pic.split("/")[1].strip() if "/" in pic else pic
        if pic_filter != pic_short: return False
    if search:
        q = search.lower()
        if q not in brand.lower() and q not in pic.lower(): return False
    return True

filtered = df_main[df_main.apply(row_matches, axis=1)].reset_index(drop=True)

# ── 요약 지표 ──────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("표시 중", len(filtered))
if status_col:
    c2.metric("🟢 Running",    len(filtered[filtered[status_col]=="Running"]))
    c3.metric("🟡 종료 예정",  len(filtered[filtered[status_col]=="Planned to end"]))
    c4.metric("⚫ 계약 종료",  len(filtered[filtered[status_col]=="End"]))

# ── 정산 범례 ──────────────────────────────────────────
st.markdown(
    '<div style="background:#F7F6F2;border-radius:8px;padding:8px 14px;margin-bottom:14px;font-size:12px;color:#888">'
    '정산 방식 &nbsp;&nbsp;'
    '🟢 A. 이공이공 핑퐁 계정 &nbsp;&nbsp;'
    '🔵 B. 고객사→이공이공 transfer &nbsp;&nbsp;'
    '🟠 C. 별도 정산 &nbsp;&nbsp;'
    '⚫ 기타/미정'
    '</div>',
    unsafe_allow_html=True
)

# ── 카드 그리드 ────────────────────────────────────────
if filtered.empty:
    st.info("검색 결과가 없습니다.")
    st.stop()

if "selected" not in st.session_state:
    st.session_state.selected = None

settle_col  = get_col(df_main, "정산방식", "정산 방식", "Settle", "Settlement")
ko_col      = get_col(df_main, "한글명", "Korean", "브랜드(한글)", "회사명")
expire_col  = get_col(df_main, "계약만료일", "Expire", "계약 만료일", "만료일")
ct_col      = get_col(df_main, "계약유형", "Contract Type", "유형")

grid_col, detail_col = (st.columns([3, 2])
                        if st.session_state.selected is not None
                        else (st.columns(1)[0], None))

with (grid_col if detail_col else st.container()):
    cols = st.columns(3)
    for idx, (_, row) in enumerate(filtered.iterrows()):
        brand  = str(row.get(brand_col, "")).strip() if brand_col else f"브랜드 {idx+1}"
        ko     = str(row.get(ko_col, "")).strip()    if ko_col    else ""
        status = str(row.get(status_col, "")).strip() if status_col else ""
        pic    = str(row.get(pic_col, "")).strip()   if pic_col   else ""
        amz    = str(row.get(amz_col, "")).strip()   if amz_col   else ""
        tts    = str(row.get(tts_col, "")).strip()   if tts_col   else ""
        shp    = str(row.get(shp_col, "")).strip()   if shp_col   else ""
        settle = str(row.get(settle_col, "")).strip()[:1].upper() if settle_col else "D"
        expire = str(row.get(expire_col, "")).strip() if expire_col else ""
        ct     = str(row.get(ct_col, "")).strip()    if ct_col    else ""

        sm = SETTLE_META.get(settle, SETTLE_META["D"])
        si = SETTLE_ICON.get(settle, "⚫")
        status_icon = STATUS_ICON.get(status, "")
        pic_short = pic.split("/")[1].strip() if "/" in pic else pic
        selected = st.session_state.selected == brand

        plat_tags = " ".join(filter(None, [
            "`AMZ`"     if amz == "Running" else "",
            "`TTS`"     if tts == "Running" else "",
            "`Shopify`" if shp             else "",
            "`PB`"      if ct  == "PB"     else "",
        ]))

        with cols[idx % 3]:
            border = "2px solid #1A1917" if selected else "1px solid #e8e7e2"
            st.markdown(f"""
            <div style="background:white;border:{border};border-radius:10px;padding:13px 14px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <div>
                        <div style="font-size:13px;font-weight:500">{brand}</div>
                        <div style="font-size:11px;color:#aaa">{ko}</div>
                    </div>
                    <span style="font-size:11px;white-space:nowrap">{status_icon} {status}</span>
                </div>
                <div style="font-size:11px;color:#888;margin-top:4px">{si} {sm['label']}</div>
                <div style="font-size:11px;color:#aaa;margin-top:3px">
                    👤 {pic_short}{(' · ' + expire[:7]) if expire and expire != 'nan' else ''}
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
    sel_rows = df_main[df_main[brand_col] == st.session_state.selected] if brand_col else pd.DataFrame()
    if sel_rows.empty:
        st.session_state.selected = None
        st.rerun()

    row = sel_rows.iloc[0]
    brand  = str(row.get(brand_col, "")).strip() if brand_col else ""
    ko     = str(row.get(ko_col, "")).strip()    if ko_col    else ""
    status = str(row.get(status_col, "")).strip() if status_col else ""
    pic    = str(row.get(pic_col, "")).strip()   if pic_col   else ""
    amz    = str(row.get(amz_col, "")).strip()   if amz_col   else ""
    tts    = str(row.get(tts_col, "")).strip()   if tts_col   else ""
    shp    = str(row.get(shp_col, "")).strip()   if shp_col   else ""
    settle = str(row.get(settle_col, "")).strip()[:1].upper() if settle_col else "D"
    expire = str(row.get(expire_col, "")).strip() if expire_col else ""
    ct     = str(row.get(ct_col, "")).strip()    if ct_col    else ""
    sm     = SETTLE_META.get(settle, SETTLE_META["D"])

    # BRAND 탭에서 추가 정보 매칭
    brand_extra = {}
    if not df_brand.empty and brand_col:
        bc = get_col(df_brand, "Brand", "브랜드", "Brand Name", "영문명")
        if bc:
            match = df_brand[df_brand[bc] == brand]
            if not match.empty:
                brand_extra = match.iloc[0].to_dict()

    # TTS 탭에서 매칭
    tts_extra = {}
    if not df_tts.empty and brand_col:
        tc = get_col(df_tts, "Brand", "브랜드", "스토어명", "Store")
        if tc:
            match = df_tts[df_tts[tc].str.contains(brand, case=False, na=False)]
            if not match.empty:
                tts_extra = match.iloc[0].to_dict()

    # Shopify 탭에서 매칭
    shp_extra = {}
    if not df_shp.empty and brand_col:
        sc = get_col(df_shp, "Brand", "브랜드", "스토어명", "Store")
        if sc:
            match = df_shp[df_shp[sc].str.contains(brand, case=False, na=False)]
            if not match.empty:
                shp_extra = match.iloc[0].to_dict()

    with detail_col:
        st.markdown(f"### {brand}")
        if ko and ko != "nan":
            st.caption(ko)

        badges = " ".join(filter(None, [
            f"`{status}`",
            "`PB`"      if ct  == "PB"              else "",
            "`운영대행`" if ct  == "Operation Agency" else "",
            "`Amazon`"  if amz == "Running"          else "",
            "`TikTok`"  if tts == "Running"          else "",
            "`Shopify`" if shp                       else "",
        ]))
        st.markdown(badges)
        st.divider()

        # 계약 정보
        st.markdown("**📄 계약 정보**")
        acct_col   = get_col(df_main, "Account", "계정명", "아마존계정")
        access_col = get_col(df_main, "Access", "접속방법", "접속 방법")
        sku_col    = get_col(df_main, "SKU", "SKU범위", "sku")
        sub_col    = get_col(df_main, "Sub PIC", "서브담당자")
        ph_col     = get_col(df_main, "PH", "PH Team", "PH팀")

        c1, c2 = st.columns(2)
        acct   = str(row.get(acct_col, "—")).strip()   if acct_col   else "—"
        access = str(row.get(access_col, "—")).strip() if access_col else "—"
        sku    = str(row.get(sku_col, "—")).strip()    if sku_col    else "—"
        sub    = str(row.get(sub_col, "—")).strip()    if sub_col    else "—"
        ph     = str(row.get(ph_col, "—")).strip()     if ph_col     else "—"

        c1.markdown(f"<div class='dp-key'>계정명</div><div class='dp-val'>{acct}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='dp-key'>접속 방법</div><div class='dp-val'>{access}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='dp-key'>계약 만료일</div><div class='dp-val'>{expire if expire != 'nan' else '—'}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='dp-key'>SKU 범위</div><div class='dp-val'>{sku}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='dp-key'>Main PIC</div><div class='dp-val'>{pic}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='dp-key'>Sub PIC</div><div class='dp-val'>{sub}</div>", unsafe_allow_html=True)
        if ph and ph not in ("—", "nan", ""):
            st.markdown(f"<div class='dp-key'>PH Team</div><div class='dp-val'>{ph}</div>", unsafe_allow_html=True)

        st.divider()

        # 정산 정보 (BRAND 탭 우선, 없으면 main 탭)
        st.markdown("**💰 정산 방식**")
        settle_detail_col = get_col(pd.DataFrame([brand_extra]), "정산방식상세", "정산방식", "정산 방식", "Settle Detail") if brand_extra else None
        settle_detail = str(brand_extra.get(settle_detail_col, "")).strip() if settle_detail_col and brand_extra else ""
        card_col      = get_col(pd.DataFrame([brand_extra]), "카드종류", "Card", "카드 종류") if brand_extra else None
        card_no_col   = get_col(pd.DataFrame([brand_extra]), "카드번호", "Card No", "카드 번호") if brand_extra else None
        card_type = str(brand_extra.get(card_col, "")).strip()    if card_col    and brand_extra else ""
        card_no   = str(brand_extra.get(card_no_col, "")).strip() if card_no_col and brand_extra else ""

        st.markdown(
            f'<div class="settle-block {sm["cls"]}">'
            f'<div style="font-size:10px;font-weight:500;color:{sm["color"]};margin-bottom:3px">{sm["label"]}</div>'
            f'<div style="font-size:13px;font-weight:500;color:{sm["color"]}">{settle_detail or sm["label"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        if card_type and card_type not in ("nan", ""):
            c1, c2 = st.columns(2)
            c1.markdown(f"<div class='dp-key'>카드 종류</div><div class='dp-val'>{card_type}</div>", unsafe_allow_html=True)
            if card_no and card_no not in ("nan", ""):
                c2.markdown(f"<div class='dp-key'>카드 번호</div><div class='dp-val' style='font-family:monospace;font-size:11px'>{card_no}</div>", unsafe_allow_html=True)

        # TikTok Shop 정보
        if tts_extra:
            st.divider()
            st.markdown("**🎵 TikTok Shop**")
            store_name = str(tts_extra.get(get_col(pd.DataFrame([tts_extra]), "스토어명", "Store", "Brand") or "", "")).strip()
            settle_ent = str(tts_extra.get(get_col(pd.DataFrame([tts_extra]), "정산법인", "정산 법인", "Settle") or "", "")).strip()
            bank       = str(tts_extra.get(get_col(pd.DataFrame([tts_extra]), "정산은행", "Bank", "은행") or "", "")).strip()
            acct_no    = str(tts_extra.get(get_col(pd.DataFrame([tts_extra]), "계좌번호", "Account No", "계좌") or "", "")).strip()
            link       = str(tts_extra.get(get_col(pd.DataFrame([tts_extra]), "Link", "링크", "URL") or "", "")).strip()

            if store_name and store_name != "nan": st.markdown(f"**{store_name}**")
            if settle_ent and settle_ent != "nan": st.caption(f"정산: {settle_ent}")
            if bank and bank != "nan":             st.caption(f"은행: {bank} {acct_no}")
            if link and link.startswith("http"):   st.markdown(f"[↗ 스토어 링크]({link})")

        # Shopify 정보
        if shp_extra:
            st.divider()
            st.markdown("**🛍️ Shopify**")
            store_name = str(shp_extra.get(get_col(pd.DataFrame([shp_extra]), "스토어명", "Store", "Brand") or "", "")).strip()
            tpl        = str(shp_extra.get(get_col(pd.DataFrame([shp_extra]), "3PL", "TPL", "물류") or "", "")).strip()
            note       = str(shp_extra.get(get_col(pd.DataFrame([shp_extra]), "비고", "Note", "메모") or "", "")).strip()
            link       = str(shp_extra.get(get_col(pd.DataFrame([shp_extra]), "Link", "링크", "URL", "Admin URL") or "", "")).strip()

            if store_name and store_name != "nan": st.markdown(f"**{store_name}**")
            if tpl  and tpl  != "nan":             st.caption(f"3PL: {tpl}")
            if note and note != "nan":             st.caption(note)
            if link and link.startswith("http"):   st.markdown(f"[↗ Shopify Admin]({link})")
