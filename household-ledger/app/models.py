"""
SQLAlchemy 모델 (워크북 단계 3 ③-④ models.py)
= DB에 '어떻게 저장되는가' (테이블 구조)

세 테이블: categories, accounts, transactions
  - 기본키(PK): 각 행을 유일하게 식별 (id)
  - 외래키(FK): transactions가 accounts/categories의 실재 id만 가리키도록 DB가 보장
  - relationship: 외래키로 이어진 표를 파이썬 객체 수준에서 잇는다
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

    # 이 카테고리에 속한 거래 목록 (relationship)
    transactions = relationship("Transaction", back_populates="category")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    balance = Column(Numeric(14, 2), nullable=False, default=0)

    # 이 계좌의 거래 목록 (account.transactions 로 접근)
    transactions = relationship(
        "Transaction", back_populates="account", cascade="all, delete-orphan"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(14, 2), nullable=False)  # +수입 / -지출
    memo = Column(String(200), nullable=True)
    occurred_at = Column(DateTime(timezone=True), server_default=func.now())

    # 외래키: 반드시 실재하는 accounts.id / categories.id 여야 한다
    account_id = Column(
        Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id = Column(
        Integer, ForeignKey("categories.id"), nullable=True, index=True
    )

    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
