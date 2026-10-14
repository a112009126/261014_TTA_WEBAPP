# 261014_TTA_WEBAPP

네이버 검색 결과를 키워드별로 수집해 로컬 웹 대시보드에서 조회하는 Flask 프로젝트입니다.

## 주요 기능

- 키워드별 검색 결과 수집: `KMA`, `날씨`, `기상청`, `태풍`, `폭염`, `강풍`
- 버튼을 눌러 수동으로 데이터 새로고침
- 키워드 필터 및 제목·URL 검색
- 결과를 `my_2nd_crawling.xlsx` 파일로 다운로드
- 초기 화면은 빈 상태로 시작하며 샘플 데이터는 넣지 않았습니다.

## 실행 환경

- Python 3.10 이상 권장
- Microsoft Edge 브라우저
- Selenium Manager가 EdgeDriver를 자동으로 준비하지 못하는 환경에서는 호환되는 `msedgedriver.exe` 경로를 지정하세요.

## 설치 및 실행 (Windows)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

브라우저에서 http://127.0.0.1:5000 을 여세요. **데이터 새로고침**을 누르면 수집이 시작됩니다.

EdgeDriver 경로를 직접 지정하려면 PowerShell에서 다음처럼 실행할 수 있습니다.

```powershell
$env:EDGE_DRIVER_PATH="C:\\path\\to\\msedgedriver.exe"
python app.py
```

## 참고

- 수집은 자동 반복이 아니라 대시보드의 새로고침 버튼을 눌렀을 때 실행됩니다.
- 검색 페이지의 HTML 구조 및 선택자는 변경될 수 있으므로 수집 결과가 없거나 달라지면 `app.py`의 선택자를 점검하세요.
- 네이버 서비스 이용약관 및 접근 정책을 준수하고, 과도한 요청은 피하세요.
- `FLASK_SECRET_KEY` 환경 변수는 로컬 운영 목적에 맞게 변경할 수 있습니다.
