import streamlit as st
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

.bcard {
    background: white;
    border: 1px solid #e8e7e2;
    border-radius: 10px;
    padding: 14px 15px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: border-color .15s;
}
.bcard:hover { border-color: #aaa; }
.bcard.selected { border: 2px solid #1A1917; }

.badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 20px;
    margin-right: 3px;
}
.b-run  { background:#E3F2EC; color:#0D6640; }
.b-end  { background:#EBEBEB; color:#555; }
.b-plan { background:#FEF0D8; color:#7A4A0A; }
.b-sus  { background:#FDEAEA; color:#8C2020; }
.b-pb   { background:#EEECFE; color:#3A30A0; }
.b-blue { background:#E5F0FB; color:#1050A0; }
.b-teal { background:#E0F4EE; color:#0B6645; }

.settle-block {
    border-radius: 7px;
    padding: 10px 13px;
    margin: 6px 0;
}
.sb-a { background:#E0F4EE; }
.sb-b { background:#E5F0FB; }
.sb-c { background:#FEF0D8; }
.sb-d { background:#EBEBEB; }

.dp-key { font-size: 11px; color: #999; margin-bottom: 2px; }
.dp-val { font-size: 13px; font-weight: 500; color: #1A1917; }
.sec-title {
    font-size: 10px; font-weight: 500; color: #999;
    text-transform: uppercase; letter-spacing: .06em;
    margin-bottom: 10px; margin-top: 4px;
}
.stat-card {
    background: #F7F6F2;
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
}
.stat-label { font-size: 11px; color: #999; }
.stat-value { font-size: 24px; font-weight: 400; }
</style>
""", unsafe_allow_html=True)

BRANDS = [
    {"en":"My Normal","ko":"마이노멀","ct":"Partnership","status":"Running","amz":"Running","tts":"Running","shp":"","pic":"이유빈 / YB","sub":"방경환 / KH","account":"Mynormal company","access":"원격/본계정","expire":"2026-02-28","settle":"C","settle_detail":"C. 별도 정산 방식","settle_sub":"","card_type":"C. 고객사카드","card_no":"","sku":"전체SKU","ph":"Maria","tts_info":"Picket Play\n정산: EGONGEGONG LLC / WOORI AMERICA BANK 107017857","shp_info":""},
    {"en":"ELROEL","ko":"모노글로트홀딩스","ct":"Partnership","status":"Running","amz":"Running","tts":"Running","shp":"","pic":"원희종 / HJ","sub":"이유빈 / YB","account":"Tangerine stories","access":"원격/본계정","expire":"2026-05-28","settle":"A","settle_detail":"이공이공 구성원 핑퐁/페이오니아계정","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"5525 7642 1368 1725","sku":"이공이공계정","ph":"Maria","tts_info":"ELROEL SHOP\n정산: 모노글로트홀딩스 / 고객사계좌(페이오니아)","shp_info":""},
    {"en":"HAYEJIN","ko":"하예진","ct":"Partnership","status":"Running","amz":"Running","tts":"Running","shp":"","pic":"방경환 / KH","sub":"이유빈 / YB","account":"HAYEJIN.","access":"일반 부계정","expire":"2026-10-10","settle":"B","settle_detail":"B. 고객사 명의 페이오니아 → 이공이공 transfer","settle_sub":"","card_type":"C. 고객사카드","card_no":"4817","sku":"전체SKU","ph":"","tts_info":"","shp_info":""},
    {"en":"rom&nd","ko":"아이패밀리SC","ct":"Partnership","status":"End","amz":"End","tts":"N/A","shp":"","pic":"김석현 / Sukhyun","sub":"이유빈 / YB","account":"Peach tales","access":"원격/본계정","expire":"2027-02-18","settle":"A","settle_detail":"이공이공 구성원 핑퐁/페이오니아계정","settle_sub":"전체SKU","card_type":"A. 이공이공 핑퐁 카드","card_no":"5329 5933 6421 2537","sku":"전체SKU","ph":"MICHELLE","tts_info":"","shp_info":""},
    {"en":"TOCOBO","ko":"주식회사 픽톤","ct":"Partnership","status":"End","amz":"End","tts":"N/A","shp":"","pic":"김석현 / Sukhyun","sub":"이영현 / YH","account":"Fig Daze","access":"원격/본계정","expire":"2026-04-09","settle":"A","settle_detail":"이공이공 구성원 핑퐁/페이오니아계정","settle_sub":"전체SKU","card_type":"E. 이공이공 구성원 카드","card_no":"5137 9200 4986 2273","sku":"전체SKU","ph":"","tts_info":"","shp_info":""},
    {"en":"JungKwanJang","ko":"한국인삼공사","ct":"Partnership","status":"Running","amz":"Running","tts":"Running","shp":"","pic":"원희종 / HJ","sub":"김석현 / Sukhyun","account":"JKJ/CKJ/Panacea Seoul","access":"원격/본계정","expire":"2026-11-25","settle":"C","settle_detail":"C. 별도 정산 방식","settle_sub":"기존 2개 계정, 통합 예정","card_type":"C. 고객사카드","card_no":"US:7627 CA:8968 광고:0569","sku":"전체SKU","ph":"MICHELLE","tts_info":"Jung Kwan Jang\n정산: 정관장(KG) / 고객사계좌","shp_info":""},
    {"en":"MED:ALL","ko":"메디올","ct":"Partnership","status":"Running","amz":"Running","tts":"Running","shp":"","pic":"김석현 / Sukhyun","sub":"","account":"Tangerine Stories","access":"원격/본계정","expire":"2026-06-04","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"5526 7642 1368 1725","sku":"이공이공계정","ph":"Maria","tts_info":"Picket Play\n정산: EGONGEGONG LLC / WOORI AMERICA BANK","shp_info":""},
    {"en":"KAHI","ko":"코리아테크","ct":"Partnership","status":"Running","amz":"Running","tts":"Running","shp":"Y","pic":"김상엽 / SangYub","sub":"원희종 / HJ","account":"KAHI OFFICIAL","access":"원격/본계정/VPN","expire":"","settle":"D","settle_detail":"고객사 계정 정산","settle_sub":"","card_type":"A. 이공이공 핑퐁 카드","card_no":"6723","sku":"전체SKU","ph":"KRIZIA","tts_info":"KAHI US\n정산: EGONGEGONG LLC / WOORI AMERICA BANK 107017857","shp_info":"KAHI (TF)\nhttps://admin.shopify.com/store/kahicosmetics\n3PL: Amazon MCF"},
    {"en":"BRMUD","ko":"비엠코스","ct":"Partnership","status":"Running","amz":"Running","tts":"N/A","shp":"","pic":"방경환 / KH","sub":"이유빈 / YB","account":"Tangerine Stories","access":"원격/본계정","expire":"2026-05-31","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"5527 7642 1368 1725","sku":"이공이공계정","ph":"Maria","tts_info":"","shp_info":""},
    {"en":"Lapcos","ko":"랩코스","ct":"Partnership","status":"Running","amz":"Running","tts":"N/A","shp":"","pic":"양사비 / Lily","sub":"","account":"The Facemask Store","access":"일반 부계정","expire":"2026-06-14","settle":"C","settle_detail":"C. 별도 정산 방식","settle_sub":"","card_type":"","card_no":"","sku":"","ph":"Maria","tts_info":"LAPCOS TTS\n정산: 랩코스 법인 계좌 / 고객사계좌\n~2025-12","shp_info":""},
    {"en":"PyunkangYul","ko":"편강한방피부과학","ct":"Partnership","status":"Planned to end","amz":"N/A","tts":"Running","shp":"","pic":"이영현 / YH","sub":"","account":"틱톡샵","access":"TTS","expire":"2027-03-31","settle":"C","settle_detail":"C. 별도 정산 방식","settle_sub":"틱톡샵 미국 법인 계좌","card_type":"N/A","card_no":"","sku":"N/A","ph":"","tts_info":"PyunkangYul\n정산: EGONGEGONG LLC / WOORI AMERICA BANK 107017857","shp_info":""},
    {"en":"Sinsuru","ko":"(주)뷰에누보","ct":"Partnership","status":"Planned to end","amz":"Running","tts":"N/A","shp":"","pic":"이영현 / YH","sub":"","account":"Tangerine Stories","access":"런칭 전","expire":"2026-07-09","settle":"D","settle_detail":"진행 전","settle_sub":"","card_type":"","card_no":"","sku":"","ph":"","tts_info":"","shp_info":""},
    {"en":"IUNIK","ko":"아이유닉","ct":"Partnership","status":"Planned to end","amz":"N/A","tts":"Running","shp":"","pic":"이영현 / YH","sub":"","account":"","access":"","expire":"2026-04-30","settle":"D","settle_detail":"N/A","settle_sub":"","card_type":"","card_no":"","sku":"","ph":"","tts_info":"Picket Play","shp_info":""},
    {"en":"HyvaaDent","ko":"천광바이오","ct":"Partnership","status":"Planned to end","amz":"Running","tts":"N/A","shp":"","pic":"원희종 / HJ","sub":"","account":"Teotal","access":"일반 부계정","expire":"","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"5339 5912 7208 1226","sku":"이공이공계정","ph":"Sel","tts_info":"","shp_info":""},
    {"en":"GOTbanchan","ko":"구루파트너스","ct":"Partnership","status":"Planned to end","amz":"Running","tts":"N/A","shp":"","pic":"원희종 / HJ","sub":"","account":"Teotal","access":"일반 부계정","expire":"","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"5340 5912 7208 1226","sku":"이공이공계정","ph":"Sel","tts_info":"","shp_info":""},
    {"en":"HairPlus","ko":"헤어플러스","ct":"Partnership","status":"Planned to end","amz":"Running","tts":"Running","shp":"","pic":"이유빈 / YB","sub":"","account":"Teotal","access":"일반 부계정","expire":"","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"5342 5912 7208 1226","sku":"이공이공계정","ph":"Sel","tts_info":"Picket Play\n정산: EGONGEGONG LLC / WOORI AMERICA BANK","shp_info":""},
    {"en":"Lattcare","ko":"한국비노프","ct":"Partnership","status":"Running","amz":"Running","tts":"N/A","shp":"","pic":"NO PIC","sub":"","account":"Tangerine Stories","access":"원격/본계정","expire":"2024-10-13","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"5533 7642 1368 1725","sku":"이공이공계정","ph":"Maria","tts_info":"","shp_info":""},
    {"en":"FARMSKIN","ko":"팜스킨","ct":"Partnership","status":"Running","amz":"Running","tts":"N/A","shp":"Y","pic":"양사비 / Lily","sub":"이유빈 / YB","account":"FARMSKIN INC","access":"일반 본계정","expire":"2026-03-13","settle":"C","settle_detail":"C. 별도 정산 방식","settle_sub":"","card_type":"고객사 카드","card_no":"","sku":"전체SKU","ph":"Sel","tts_info":"","shp_info":"FARMSKIN INC\n정산: EGONGEGONG LLC / WOORI AMERICA BANK 107017857"},
    {"en":"Troubless","ko":"팜스킨","ct":"Partnership","status":"Running","amz":"Running","tts":"N/A","shp":"","pic":"이유빈 / YB","sub":"","account":"FARMSKIN INC","access":"일반 부계정","expire":"2026-03-13","settle":"C","settle_detail":"C. 별도 정산 방식","settle_sub":"","card_type":"","card_no":"","sku":"전체SKU","ph":"Sel","tts_info":"","shp_info":""},
    {"en":"Selfbeauty","ko":"에스비코스메틱","ct":"Partnership","status":"Planned to end","amz":"End","tts":"N/A","shp":"Y","pic":"이유빈 / YB","sub":"이영현 / YH","account":"SELF BEAUTY","access":"일반 부계정","expire":"","settle":"C","settle_detail":"C. 별도 정산 방식","settle_sub":"계약 종료 논의 중","card_type":"","card_no":"","sku":"","ph":"Maria","tts_info":"","shp_info":"SELF BEAUTY\n정산: EGONGEGONG LLC / WOORI AMERICA BANK 107017857"},
    {"en":"DR.PEPTI","ko":"제이앤코슈","ct":"Partnership","status":"End","amz":"Running","tts":"N/A","shp":"","pic":"이유빈 / YB","sub":"","account":"Tangerine Stories","access":"원격/본계정","expire":"","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"","sku":"이공이공계정","ph":"Maria","tts_info":"","shp_info":""},
    {"en":"Peach C","ko":"에스와이씨에스","ct":"Partnership","status":"Running","amz":"Running","tts":"N/A","shp":"","pic":"양사비 / Lily","sub":"","account":"teotal","access":"일반 부계정","expire":"2026-12-07","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"","sku":"이공이공계정","ph":"Alodia","tts_info":"","shp_info":""},
    {"en":"Refa","ko":"코리아테크","ct":"Partnership","status":"Running","amz":"Running","tts":"Running","shp":"","pic":"김상엽 / SangYub","sub":"원희종 / HJ","account":"korea tech","access":"원격/본계정/VPN","expire":"","settle":"A","settle_detail":"이공이공 구성원 핑퐁/페이오니아계정","settle_sub":"","card_type":"A. 이공이공 핑퐁 카드","card_no":"","sku":"","ph":"KRIZIA","tts_info":"REFA TTS\n정산: EGONGEGONG LLC / WOORI AMERICA BANK 107017857","shp_info":""},
    {"en":"Herbloom","ko":"메르시코","ct":"Partnership","status":"Planned to end","amz":"Running","tts":"N/A","shp":"","pic":"이유빈 / YB","sub":"","account":"Tangerine Stories","access":"원격/본계정","expire":"","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"","sku":"이공이공계정","ph":"Maria","tts_info":"","shp_info":""},
    {"en":"smilebloom","ko":"채화","ct":"Partnership","status":"Running","amz":"Running","tts":"N/A","shp":"Y","pic":"이영현 / YH","sub":"","account":"Smilebloom KKOCH","access":"원격/본계정","expire":"2026-01-01","settle":"C","settle_detail":"C. 별도 정산 방식","settle_sub":"","card_type":"고객사 카드","card_no":"","sku":"","ph":"Sel","tts_info":"","shp_info":"smilebloom\n원격/본계정"},
    {"en":"MAXCLINIC","ko":"엔앤비랩","ct":"Partnership","status":"Running","amz":"Running","tts":"N/A","shp":"","pic":"김석현 / Sukhyun","sub":"양사비 / Lily","account":"MAXCLINIC","access":"일반 부계정","expire":"2026-10-12","settle":"C","settle_detail":"C. 별도 정산 방식","settle_sub":"","card_type":"고객사 카드","card_no":"","sku":"","ph":"Maria","tts_info":"","shp_info":""},
    {"en":"MOTOMONT","ko":"와디즈엑스","ct":"Partnership","status":"Running","amz":"Running","tts":"N/A","shp":"","pic":"이유빈 / YB","sub":"","account":"mot_o_mo__nt","access":"원격/본계정","expire":"2026-04-14","settle":"C","settle_detail":"C. 별도 정산 방식","settle_sub":"고객사 페이오니아 계좌","card_type":"C. 고객사카드","card_no":"","sku":"","ph":"Maria","tts_info":"","shp_info":""},
    {"en":"Kineff","ko":"아미코스메틱","ct":"Partnership","status":"Running","amz":"Running","tts":"N/A","shp":"","pic":"양사비 / Lily","sub":"","account":"Tangerine Stories","access":"원격/본계정","expire":"2026-04-27","settle":"D","settle_detail":"진행 전","settle_sub":"","card_type":"","card_no":"","sku":"","ph":"","tts_info":"","shp_info":""},
    {"en":"Easydew","ko":"디엔코스메틱스","ct":"Partnership","status":"Running","amz":"Running","tts":"Running","shp":"","pic":"김석현 / Sukhyun","sub":"이영현 / YH","account":"Easydew official","access":"원격/본계정","expire":"2026-08-31","settle":"B","settle_detail":"B. 고객사 명의 페이오니아 → 이공이공 transfer","settle_sub":"","card_type":"고객사 카드","card_no":"","sku":"","ph":"Maria","tts_info":"Easydew TTS\n운영대행 / 고객사계좌","shp_info":""},
    {"en":"Memebox","ko":"미미박스","ct":"Partnership","status":"Running","amz":"Running","tts":"Running","shp":"","pic":"원희종 / HJ","sub":"이영현 / YH","account":"MBX Corp","access":"원격/본계정","expire":"","settle":"C","settle_detail":"C. 별도 정산 방식","settle_sub":"","card_type":"고객사 카드","card_no":"","sku":"","ph":"Maria","tts_info":"미미박스 TTS\n정산: 고객사계좌","shp_info":""},
    {"en":"anillo","ko":"메디쿼터스","ct":"Partnership","status":"End","amz":"Running","tts":"Running","shp":"","pic":"이영현 / YH","sub":"김석현 / Sukhyun","account":"anillo","access":"원격/본계정","expire":"2027-06-24","settle":"C","settle_detail":"C. 별도 정산 방식","settle_sub":"고객사 계정으로 결제/정산","card_type":"고객사 카드","card_no":"","sku":"","ph":"","tts_info":"Anillo TTS\n정산: 메디쿼터스 / 고객사계좌","shp_info":""},
    {"en":"Mars Made","ko":"이공이공 PB","ct":"PB","status":"Running","amz":"Running","tts":"Running","shp":"Y","pic":"전병규 / BK","sub":"이영현 / YH","account":"Tangerine Stories","access":"원격/본계정","expire":"","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"","sku":"이공이공계정","ph":"Maria","tts_info":"MARS MADE (브랜드기획팀)\nhttps://seller.us.tiktokshopglobalselling.com/\n담당: 전병규 / 계좌: 30000009371337\n정산 시작: 2025-08-03","shp_info":"MARSMADE (브랜드기획)\nhttps://admin.shopify.com/store/ccid5j-kf\n3PL: Cconma (꽃마) / Amazon MCF"},
    {"en":"PicketPlay","ko":"이공이공 PB","ct":"PB","status":"Running","amz":"N/A","tts":"Running","shp":"Y","pic":"전병규 / BK","sub":"","account":"","access":"","expire":"","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"","card_type":"A. 이공이공 핑퐁 카드","card_no":"5525 7642 1244 9215","sku":"","ph":"","tts_info":"PicketPlay Shop (온라인커머스팀)\nhttps://seller-us.tiktok.com/\n정산: EGONGEGONG LLC / WOORI AMERICA BANK 107017857","shp_info":"PicketPlay (TF)\nhttps://admin.shopify.com/store/picketplay1021\n3PL: EPICHUB (에픽허브)\n~2026-02"},
    {"en":"Kiero","ko":"이공이공 PB","ct":"PB","status":"Running","amz":"Running","tts":"Running","shp":"Y","pic":"전병규 / BK","sub":"","account":"The Baron Store","access":"원격/본계정","expire":"","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정 / BBVA (MX)","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"5525 7642 1614 5520","sku":"이공이공계정","ph":"","tts_info":"Kiero TTS (브랜드기획팀)\n정산: EGONGEGONG S DE RL DE CV / BBVA 0125481058","shp_info":"kiero MX (브랜드기획)\n3PL: Melonn (멕시코 현지 3PL)\n매출-매입가를 서비스 매출로 정산"},
    {"en":"Veyka","ko":"이공이공 PB","ct":"PB","status":"Running","amz":"Running","tts":"Running","shp":"","pic":"전병규 / BK","sub":"","account":"The Baron Store","access":"원격/본계정","expire":"","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"","sku":"이공이공계정","ph":"","tts_info":"Veyka TTS (브랜드기획팀)\nhttps://seller.us.tiktokshopglobalselling.com/\n계좌: 30000009371758","shp_info":""},
    {"en":"404lab","ko":"이공이공 PB","ct":"PB","status":"Running","amz":"N/A","tts":"Running","shp":"","pic":"전병규 / BK","sub":"","account":"","access":"","expire":"","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"","sku":"이공이공계정","ph":"","tts_info":"404lab TTS (브랜드기획팀)\nhttps://seller.us.tiktokshopglobalselling.com/\n계좌: 30000009372171","shp_info":""},
    {"en":"Seoulected","ko":"이공이공 PB","ct":"PB","status":"Running","amz":"N/A","tts":"N/A","shp":"Y","pic":"안정현","sub":"","account":"","access":"","expire":"","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"EGONGEGONG LLC","card_type":"A. 이공이공 핑퐁 카드","card_no":"5525 7642 1614 5520","sku":"","ph":"","tts_info":"","shp_info":"Seoulected (해외영업)\nhttps://admin.shopify.com/store/sx9cwu-5i\nB2B 플랫폼 / Plus 계정 / 준비중"},
    {"en":"Code Bro","ko":"이공이공 PB","ct":"PB","status":"Running","amz":"Running","tts":"N/A","shp":"Y","pic":"전병규 / BK","sub":"","account":"The Baron Store","access":"원격/본계정","expire":"","settle":"A","settle_detail":"A. 이공이공 핑퐁 계정","settle_sub":"이공이공계정","card_type":"A. 이공이공 핑퐁 카드","card_no":"5525 7642 1614 5520","sku":"이공이공계정","ph":"","tts_info":"","shp_info":"Code Bro (브랜드기획)\nhttps://admin.shopify.com/store/code-bro\n3PL: Cconma (꽃마) / Amazon MCF\nPlus 계정 / 현재 Wix 운영중"},
]

SETTLE_META = {
    "A": {"label": "A. 이공이공 핑퐁 계정",           "cls": "sb-a", "color": "#0B6645"},
    "B": {"label": "B. 고객사→이공이공 transfer",      "cls": "sb-b", "color": "#1050A0"},
    "C": {"label": "C. 별도 정산",                    "cls": "sb-c", "color": "#7A4A0A"},
    "D": {"label": "기타/미정",                        "cls": "sb-d", "color": "#555"},
}
STATUS_COLOR = {"Running":"🟢","End":"⚫","Planned to end":"🟡","Suspended":"🔴","N/A":"—"}

# ── Sidebar ──────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏪 EOEO Dashboard")
    st.caption("브랜드 계약 현황 관리")
    st.divider()

    st.markdown("**Marketplace**")
    tab = st.radio(
        "탭 선택",
        ["전체", "Amazon", "TikTok Shop", "Shopify"],
        label_visibility="collapsed",
        key="tab"
    )
    st.divider()
    st.markdown("**필터**")
    search = st.text_input("브랜드명 / 담당자 검색", placeholder="검색어 입력...")
    all_pics = sorted(set(
        b["pic"].split("/")[1].strip() if "/" in b["pic"] else b["pic"]
        for b in BRANDS if b["pic"] and b["pic"] != "NO PIC"
    ))
    pic_filter = st.selectbox("담당자", ["전체"] + all_pics)
    status_filter = st.selectbox("계약 상태", ["전체", "Running", "Planned to end", "End"])
    st.divider()
    st.caption("마지막 업데이트: 2026년 5월")

# ── Filter logic ─────────────────────────────────────
def matches(b):
    if tab == "Amazon"     and b["amz"] not in ("Running","End"): return False
    if tab == "TikTok Shop" and b["tts"] not in ("Running","End"): return False
    if tab == "Shopify"    and not b["shp"]: return False
    if status_filter != "전체" and b["status"] != status_filter: return False
    if pic_filter != "전체":
        pic_short = b["pic"].split("/")[1].strip() if "/" in b["pic"] else b["pic"]
        sub_short = b["sub"].split("/")[1].strip() if "/" in b.get("sub","") else b.get("sub","")
        if pic_filter not in (pic_short, sub_short): return False
    if search:
        q = search.lower()
        if q not in b["en"].lower() and q not in b["ko"].lower() and q not in b["pic"].lower():
            return False
    return True

filtered = [b for b in BRANDS if matches(b)]

# ── Summary stats ─────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("표시 중", len(filtered))
c2.metric("🟢 Running",      sum(1 for b in filtered if b["status"]=="Running"))
c3.metric("🟡 종료 예정",     sum(1 for b in filtered if b["status"]=="Planned to end"))
c4.metric("⚫ 계약 종료",     sum(1 for b in filtered if b["status"]=="End"))

# ── Legend ────────────────────────────────────────────
st.markdown(
    '<div style="background:#F7F6F2;border-radius:8px;padding:8px 14px;margin-bottom:12px;font-size:12px;color:#888;display:flex;gap:16px;flex-wrap:wrap">'
    '정산 방식 &nbsp;'
    '<span>🟢 A. 이공이공 핑퐁 계정</span>'
    '<span>🔵 B. 고객사→이공이공 transfer</span>'
    '<span>🟠 C. 별도 정산</span>'
    '<span>⚫ 기타/미정</span>'
    '</div>',
    unsafe_allow_html=True
)

# ── Card grid + detail ────────────────────────────────
if not filtered:
    st.info("검색 결과가 없습니다.")
else:
    if "selected" not in st.session_state:
        st.session_state.selected = None

    grid_col, detail_col = st.columns([3, 2]) if st.session_state.selected is not None else [st.columns([1])[0], None]

    SETTLE_ICON = {"A":"🟢","B":"🔵","C":"🟠","D":"⚫"}
    PLAT_BADGES = lambda b: " ".join(filter(None,[
        "` AMZ `"  if b["amz"]=="Running" else "",
        "` TTS `"  if b["tts"]=="Running" else "",
        "` Shopify `" if b["shp"] else "",
    ]))

    with (grid_col if detail_col else st.container()):
        cols = st.columns(3)
        for idx, b in enumerate(filtered):
            sc = SETTLE_META.get(b["settle"], SETTLE_META["D"])
            status_icon = STATUS_COLOR.get(b["status"], "")
            with cols[idx % 3]:
                selected = st.session_state.selected == b["en"]
                border = "2px solid #1A1917" if selected else "1px solid #e8e7e2"
                with st.container(border=False):
                    st.markdown(f"""
                    <div style="background:white;border:{border};border-radius:10px;padding:13px 14px;margin-bottom:8px;">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:4px;">
                            <div>
                                <div style="font-size:13px;font-weight:500">{b['en']}</div>
                                <div style="font-size:11px;color:#aaa">{b['ko'] if b['ko'] and 'PB' not in b['ko'] else ''}</div>
                            </div>
                            <span style="font-size:11px">{status_icon} {b['status']}</span>
                        </div>
                        <div style="font-size:11px;color:#888;margin-top:5px">
                            {SETTLE_ICON.get(b['settle'],'⚫')} {sc['label'].replace('^[A-D]\\. ','')}
                        </div>
                        <div style="font-size:11px;color:#aaa;margin-top:3px">
                            👤 {b['pic'].split('/')[1].strip() if '/' in b['pic'] else b['pic']}
                            {'· ' + b['expire'][:7] if b['expire'] else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("상세 보기 →" if not selected else "닫기 ✕",
                                 key=f"btn_{b['en']}_{idx}",
                                 use_container_width=True):
                        st.session_state.selected = None if selected else b["en"]
                        st.rerun()

    # ── Detail panel ──────────────────────────────────
    if st.session_state.selected and detail_col:
        b = next((x for x in BRANDS if x["en"] == st.session_state.selected), None)
        if b:
            sc = SETTLE_META.get(b["settle"], SETTLE_META["D"])
            with detail_col:
                st.markdown(f"### {b['en']}")
                if b["ko"] and "PB" not in b["ko"]:
                    st.caption(b["ko"])

                badges = " ".join(filter(None, [
                    f"`{b['status']}`",
                    "`PB`" if b["ct"]=="PB" else "",
                    "`운영대행`" if b["ct"]=="Operation Agency" else "",
                    "`Amazon`" if b["amz"]=="Running" else "",
                    "`TikTok`" if b["tts"]=="Running" else "",
                    "`Shopify`" if b["shp"] else "",
                ]))
                st.markdown(badges)
                st.divider()

                st.markdown("**📄 계약 정보**")
                c1, c2 = st.columns(2)
                c1.markdown(f"<div class='dp-key'>계정명</div><div class='dp-val'>{b['account'] or '—'}</div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='dp-key'>접속 방법</div><div class='dp-val'>{b['access'] or '—'}</div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                c1.markdown(f"<div class='dp-key'>계약 만료일</div><div class='dp-val'>{b['expire'] or '—'}</div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='dp-key'>SKU 범위</div><div class='dp-val'>{b['sku'] or '—'}</div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                c1.markdown(f"<div class='dp-key'>Main PIC</div><div class='dp-val'>{b['pic'] or '—'}</div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='dp-key'>Sub PIC</div><div class='dp-val'>{b['sub'] or '—'}</div>", unsafe_allow_html=True)
                if b["ph"]:
                    st.markdown(f"<div class='dp-key'>PH Team</div><div class='dp-val'>{b['ph']}</div>", unsafe_allow_html=True)

                st.divider()
                st.markdown("**💰 정산 방식**")
                st.markdown(
                    f'<div class="settle-block {sc["cls"]}">'
                    f'<div style="font-size:10px;font-weight:500;color:{sc["color"]};margin-bottom:3px">{sc["label"]}</div>'
                    f'<div style="font-size:13px;font-weight:500;color:{sc["color"]}">{b["settle_detail"]}</div>'
                    f'{"<div style=\\"font-size:11px;color:"+sc["color"]+";margin-top:3px\\">"+b["settle_sub"]+"</div>" if b["settle_sub"] else ""}'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if b["card_type"]:
                    c1, c2 = st.columns(2)
                    c1.markdown(f"<div class='dp-key'>카드 종류</div><div class='dp-val'>{b['card_type']}</div>", unsafe_allow_html=True)
                    if b["card_no"]:
                        c2.markdown(f"<div class='dp-key'>카드 번호</div><div class='dp-val' style='font-family:monospace;font-size:11px'>{b['card_no']}</div>", unsafe_allow_html=True)

                if b["tts_info"]:
                    st.divider()
                    st.markdown("**🎵 TikTok Shop**")
                    lines = b["tts_info"].split("\n")
                    st.markdown(f"**{lines[0]}**")
                    for line in lines[1:]:
                        if line.startswith("http"):
                            st.markdown(f"[↗ 스토어 링크]({line})")
                        else:
                            st.caption(line)

                if b["shp_info"]:
                    st.divider()
                    st.markdown("**🛍️ Shopify**")
                    lines = b["shp_info"].split("\n")
                    st.markdown(f"**{lines[0]}**")
                    for line in lines[1:]:
                        if line.startswith("http"):
                            st.markdown(f"[↗ Shopify Admin]({line})")
                        else:
                            st.caption(line)
