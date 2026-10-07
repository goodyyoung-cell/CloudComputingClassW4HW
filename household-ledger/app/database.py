"""
DB 연결 설정 (워크북 단계 3 ③-③ database.py)

- Engine: 연결 관리
- SessionLocal: DB와의 한 번의 대화(Session) 생성기
- Base: 모든 테이블 모델의 부모

연결 문자열은 .env 또는 Render 환경변수의 DATABASE_URL에서 읽는다.
개념자료의 함정 반영:
  - DATABASE_URL이 없으면 조용히 SQLite 폴백 → 이번엔 '로그를 남겨서' 눈치챌 수 있게 함
  - postgresql:// 는 SQLAlchemy가 기본 드라이버 psycopg2를 찾으므로
    postgresql+psycopg:// 로 자동 정규화한다.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# .env 파일이 있으면 로드 (Render 등 배포 환경에는 .env가 없어도
# 대시보드 환경변수를 os.getenv가 동일하게 읽는다)
load_dotenv()

# 환경변수에서 연결 문자열을 읽는다. 없으면 로컬 테스트용 SQLite로 폴백.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")


def _normalize(url: str) -> str:
    """postgresql:// / postgres:// -> postgresql+psycopg:// 로 드라이버를 명시한다.
    (개념자료: 'psycopg2' 오류는 설치 문제가 아니라 연결 문자열 앞머리 탓)
    """
    if url.startswith("postgresql+"):
        return url  # 이미 드라이버가 명시됨
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = _normalize(DATABASE_URL)

# SQLite일 때만 필요한 옵션
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# 폴백이 조용히 일어나는 것을 막기 위해 어떤 DB에 붙는지 로그로 남긴다.
if DATABASE_URL.startswith("sqlite"):
    print("[database] ⚠️  DATABASE_URL 미설정 → SQLite 로컬 폴백 사용 중")
else:
    # 비밀번호가 노출되지 않도록 호스트 부분만 간단히 표시
    print("[database] ✅  PostgreSQL(Supabase)에 연결합니다.")

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """요청마다 Session을 열고, 끝나면 닫는 FastAPI 의존성."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
