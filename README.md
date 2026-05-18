# EOEO Brand Dashboard

EOEO 브랜드 계약 현황 통합 대시보드입니다.  
Google Sheets에서 실시간으로 데이터를 불러옵니다.

## 기능
- Amazon / TikTok Shop / Shopify 플랫폼별 브랜드 현황
- 브랜드 클릭 시 계약 정보 · 정산 방식 · 담당자 상세 확인
- 담당자 · 상태별 필터 및 검색
- 5분마다 Google Sheets 자동 갱신

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

로컬 실행 시 프로젝트 루트에 `.streamlit/secrets.toml` 파일 생성 후 아래 내용 입력:

```toml
[gcp_service_account]
type = "service_account"
project_id = "eoeo-dashboard"
private_key_id = "..."
private_key = "..."
client_email = "eoeo-sheets-reader@eoeo-dashboard.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

## Streamlit Cloud 배포

1. 이 저장소를 GitHub에 push
2. [share.streamlit.io](https://share.streamlit.io) → **New app**
3. 저장소 선택 → Main file path: `app.py` → **Deploy**
4. 배포 후 **Settings → Secrets** 에 위 toml 내용 입력

## 파일 구조

```
eoeo-dashboard/
├── app.py            # 메인 앱 (Google Sheets 연동)
├── requirements.txt  # 패키지 목록
└── README.md
```

## 데이터 수정 방법

Google Sheets 원본 시트를 직접 수정하면 5분 후 앱에 자동 반영됩니다.  
앱에서 **🔄 데이터 새로고침** 버튼을 누르면 즉시 반영됩니다.

## 보안

- 민감 데이터(카드번호, 계좌번호 등)는 Google Sheets에만 저장
- 인증 키는 Streamlit Secrets에만 저장 (코드에 포함되지 않음)
- 저장소는 Public이어도 데이터 노출 없음
