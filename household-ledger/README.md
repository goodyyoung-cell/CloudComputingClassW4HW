# 가계부 API — FastAPI + Supabase(PostgreSQL) + Render

클라우드컴퓨팅실습 W4 과제. FastAPI 백엔드를 SQLAlchemy(ORM)로 Supabase(PostgreSQL)에 연결하고 Render에 배포한다.

## 구조

```
household-ledger/
├─ app/
│  ├─ database.py   # Engine / Session / Base, DATABASE_URL 로딩
│  ├─ models.py     # SQLAlchemy 모델 (테이블 구조, PK/FK/relationship)
│  ├─ schemas.py    # Pydantic 스키마 (입출력, from_attributes)
│  ├─ crud.py       # 생성·조회·수정·삭제 + 집계(JOIN/GROUP BY)
│  └─ main.py       # FastAPI 라우트
├─ requirements.txt
├─ render.yaml      # Render Blueprint (선택)
├─ .env.example     # 연결 문자열 양식 (.env 로 복사해 사용)
└─ .gitignore       # .env, *.db 제외
```

## 데이터 모델

- **categories** — 카테고리 (id, name)
- **accounts** — 계좌 (id, name, balance)
- **transactions** — 거래 (id, amount, memo, occurred_at, account_id→accounts, category_id→categories)

외래키로 "존재하지 않는 계좌의 거래"를 DB가 차단하고, 거래 추가/삭제 시 계좌 잔액을 트랜잭션(원자성)으로 함께 반영한다.

## 주요 엔드포인트

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/` | 상태 확인 |
| GET | `/health` | 헬스체크 |
| POST/GET | `/categories` | 카테고리 생성/목록 |
| POST/GET | `/accounts` | 계좌 생성/목록 |
| GET | `/accounts/{id}` | 계좌 + 거래 목록(중첩 응답) |
| POST/GET | `/transactions` | 거래 생성/목록 |
| DELETE | `/transactions/{id}` | 거래 삭제 |
| GET | `/stats/by-category` | 카테고리별 합계·건수(집계) |

대화형 문서: `/docs`

## 로컬 실행

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # .env 안의 DATABASE_URL 을 Supabase 값으로 수정
uvicorn app.main:app --reload
```

`http://localhost:8000/docs` 접속. `DATABASE_URL`을 설정하지 않으면 로컬 `local.db`(SQLite)로 폴백한다(콘솔에 경고가 찍힘).

## Render 배포 요약

1. 이 저장소를 GitHub에 push
2. Render → New + → **Web Service** → 저장소 선택
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Environment → **DATABASE_URL** 에 Supabase 연결 문자열 추가
6. 배포 후 `https://<앱이름>.onrender.com/docs` 확인

> 자세한 단계는 함께 제공한 배포 가이드(`배포_가이드.md`) 참고.
