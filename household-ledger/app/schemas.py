"""
Pydantic 스키마 (워크북 단계 3 ③-⑤ schemas.py)
= API가 '무엇을 받고 돌려주는가' (입출력 형식·검증)

- Create: 입력용. id·occurred_at 처럼 서버가 만드는 값은 받지 않는다.
- Read:   출력용. 저장 후 생긴 값(id·occurred_at)까지 포함한다.
- from_attributes=True 가 있어야 SQLAlchemy 모델 객체를 그대로 return 해도
  스키마로 변환된다. 없으면 ResponseValidationError 발생.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# ---------- Category ----------
class CategoryCreate(BaseModel):
    name: str


class CategoryRead(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


# ---------- Account ----------
class AccountCreate(BaseModel):
    name: str
    balance: Decimal = Decimal("0")


class AccountRead(BaseModel):
    id: int
    name: str
    balance: Decimal
    model_config = ConfigDict(from_attributes=True)


# ---------- Transaction ----------
class TransactionCreate(BaseModel):
    amount: Decimal          # +수입 / -지출
    memo: Optional[str] = None
    account_id: int
    category_id: Optional[int] = None


class TransactionRead(BaseModel):
    id: int
    amount: Decimal
    memo: Optional[str]
    occurred_at: Optional[datetime]
    account_id: int
    category_id: Optional[int]
    model_config = ConfigDict(from_attributes=True)


# ---------- 중첩 응답 (relationship 활용) ----------
class AccountWithTransactions(AccountRead):
    transactions: List[TransactionRead] = []
    model_config = ConfigDict(from_attributes=True)


# ---------- 집계 응답 ----------
class CategoryStat(BaseModel):
    category_id: Optional[int]
    category_name: Optional[str]
    total: Decimal
    count: int
