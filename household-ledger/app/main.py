"""
FastAPI 앱 (워크북 단계 4 — 웹 API 계층)
요청 → FastAPI → SQLAlchemy(ORM) → Supabase(PostgreSQL)

실행:  uvicorn app.main:app --reload
문서:  http://localhost:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 테이블이 없으면 생성한다 (학습용. 실무는 마이그레이션/Alembic).
    # import 시점이 아니라 startup에서 호출해, DB가 잠깐 불안정해도
    # 앱 기동 자체가 실패하지 않도록 한다.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="가계부 API (FastAPI + Supabase/PostgreSQL)",
    description="클라우드컴퓨팅실습 W4 — Render + Supabase 연동 실습",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {"message": "가계부 API 동작 중", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Category ----------
@app.post("/categories", response_model=schemas.CategoryRead, status_code=201)
def create_category(data: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db, data)


@app.get("/categories", response_model=list[schemas.CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return crud.list_categories(db)


# ---------- Account ----------
@app.post("/accounts", response_model=schemas.AccountRead, status_code=201)
def create_account(data: schemas.AccountCreate, db: Session = Depends(get_db)):
    return crud.create_account(db, data)


@app.get("/accounts", response_model=list[schemas.AccountRead])
def list_accounts(db: Session = Depends(get_db)):
    return crud.list_accounts(db)


@app.get("/accounts/{account_id}", response_model=schemas.AccountWithTransactions)
def get_account(account_id: int, db: Session = Depends(get_db)):
    """계좌 하나 + 그 계좌의 거래 목록(중첩 응답, relationship 활용)."""
    account = crud.get_account(db, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="계좌를 찾을 수 없습니다.")
    return account


# ---------- Transaction ----------
@app.post("/transactions", response_model=schemas.TransactionRead, status_code=201)
def create_transaction(data: schemas.TransactionCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_transaction(db, data)
    except ValueError:
        raise HTTPException(status_code=400, detail="존재하지 않는 계좌입니다.")


@app.get("/transactions", response_model=list[schemas.TransactionRead])
def list_transactions(db: Session = Depends(get_db)):
    return crud.list_transactions(db)


@app.delete("/transactions/{tx_id}", status_code=204)
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_transaction(db, tx_id)
    if not ok:
        raise HTTPException(status_code=404, detail="거래를 찾을 수 없습니다.")
    return None


# ---------- 집계 ----------
@app.get("/stats/by-category", response_model=list[schemas.CategoryStat])
def stats_by_category(db: Session = Depends(get_db)):
    """카테고리별 지출/수입 합계·건수. 대상 거래가 없으면 [] 반환."""
    return crud.stats_by_category(db)
