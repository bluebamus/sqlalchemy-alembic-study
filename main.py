from fastapi import FastAPI
from core_app.core.config import settings
from core_app.core.database import engine, Base  
from core_app.models.tables import User, Profile, Product, Inventory, Order, OrderItem
# router에서 import 했으면, 해당 table 정보들은 삭제해야 함
from core_app.test.db_con_test import test_db_router


# 설정값 출력 (테스트)
# [print(f"{key}: {value}") for key, value in settings.model_dump().items()]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="SQLAlchemy와 Alembic을 사용한 FastAPI 프로젝트"
)

# 라우터 추가
app.include_router(test_db_router)

# 데이터베이스 테이블 생성
# result = Base.metadata.create_all(bind=engine)

