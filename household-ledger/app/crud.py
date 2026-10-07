"""
CRUD 로직 — SQLAlchemy Session을 받아 생성·조회·수정·삭제를 수행한다.
라우트(main.py)와 DB 접근을 분리해 두면 코드가 읽기 쉽다.
"""
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models, schemas


# ---------- Category ----------
def create_category(db: Session, data: schemas.CategoryCreate) -> models.Category:
    obj = models.Category(name=data.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_categories(db: Session) -> List[models.Category]:
    return db.query(models.Category).order_by(models.Category.id).all()


# ---------- Account ----------
def create_account(db: Session, data: schemas.AccountCreate) -> models.Account:
    obj = models.Account(name=data.name, balance=data.balance)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_accounts(db: Session) -> List[models.Account]:
    return db.query(models.Account).order_by(models.Account.id).all()


def get_account(db: Session, account_id: int) -> Optional[models.Account]:
    return db.query(models.Account).filter(models.Account.id == account_id).first()


# ---------- Transaction ----------
def create_transaction(
    db: Session, data: schemas.TransactionCreate
) -> models.Transaction:
    """거래를 추가하고, 트랜잭션(원자성)으로 계좌 잔액도 함께 반영한다.
    둘 중 하나라도 실패하면 rollback 되어 '어중간한 상태'가 남지 않는다.
    """
    account = get_account(db, data.account_id)
    if account is None:
        raise ValueError("account_not_found")

    obj = models.Transaction(
        amount=data.amount,
        memo=data.memo,
        account_id=data.account_id,
        category_id=data.category_id,
    )
    try:
        db.add(obj)
        # 잔액 갱신 (수입이면 +, 지출이면 - 는 amount 부호로 처리)
        account.balance = Decimal(account.balance) + Decimal(data.amount)
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(obj)
    return obj


def list_transactions(db: Session) -> List[models.Transaction]:
    return (
        db.query(models.Transaction)
        .order_by(models.Transaction.id.desc())
        .all()
    )


def delete_transaction(db: Session, tx_id: int) -> bool:
    obj = db.query(models.Transaction).filter(models.Transaction.id == tx_id).first()
    if obj is None:
        return False
    account = get_account(db, obj.account_id)
    try:
        if account is not None:
            account.balance = Decimal(account.balance) - Decimal(obj.amount)
        db.delete(obj)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True


# ---------- 집계 (JOIN + GROUP BY) ----------
def stats_by_category(db: Session) -> List[schemas.CategoryStat]:
    """카테고리별 합계·건수. 대상 거래가 하나도 없으면 빈 리스트([])를 돌려준다.
    (개념자료: 빈 결과는 계산이 틀린 게 아니라 대상 거래가 없다는 뜻)
    """
    rows = (
        db.query(
            models.Transaction.category_id,
            models.Category.name,
            func.coalesce(func.sum(models.Transaction.amount), 0).label("total"),
            func.count(models.Transaction.id).label("count"),
        )
        .outerjoin(models.Category, models.Transaction.category_id == models.Category.id)
        .group_by(models.Transaction.category_id, models.Category.name)
        .all()
    )
    return [
        schemas.CategoryStat(
            category_id=r[0],
            category_name=r[1],
            total=r[2],
            count=r[3],
        )
        for r in rows
    ]
