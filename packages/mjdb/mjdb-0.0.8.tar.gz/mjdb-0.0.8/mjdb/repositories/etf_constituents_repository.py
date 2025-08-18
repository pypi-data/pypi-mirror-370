from mjdb.repositories.base.base_repository import BaseSQLAlchemyRepository
from mjdb.model.daily_etf_constituents import DailyETFConstituents
from mjdb.session.types.session_context import SessionContext
from mjdb.session.types.session_config import SessionConfig
import os
import logging


class ETFConstituentsRepository(BaseSQLAlchemyRepository[DailyETFConstituents]):
    """
    ETF 구성 종목 일별 데이터 전용 Repository

    - DailyETFConstituents 모델을 기반으로 MySQL에 데이터 CRUD 지원
    - 단일 엔티티 또는 리스트 단위로 추가/갱신 가능
    """

    def __init__(self, db_url: str = None, log_level: int = logging.INFO):
        """
        Repository 초기화

        Args:
            db_url (str, optional): 데이터베이스 연결 URL. 환경변수 STOCK_DATABASE_LOCALHOST_URL로 대체 가능
            log_level (int): 로깅 레벨
        """
        ctx = SessionContext(
            db_url=db_url or os.getenv("STOCK_DATABASE_LOCALHOST_URL"),
            session_config=SessionConfig(expire_on_commit=False)
        )
        super().__init__(model=DailyETFConstituents, context=ctx, log_level=log_level)

if __name__ == "__main__":
    """
    테스트용 실행 예시
    """
    from datetime import datetime
    import pandas as pd
    from dotenv import load_dotenv

    load_dotenv()
    DB_URL = os.getenv("STOCK_DATABASE_LOCALHOST_URL")

    # Repository 생성
    repo = ETFConstituentsRepository(db_url=DB_URL, log_level=logging.DEBUG)

    # 샘플 DataFrame 생성
    data = {
        "base_dt": [datetime(2025, 8, 14), datetime(2025, 8, 14)],
        "etf_ticker": ["ETF001", "ETF001"],
        "etf_name": ["Sample ETF", "Sample ETF"],
        "constituent_ticker": ["STK001", "STK002"],
        "contract_count": [100, 200],
        "amount": [5000000, 8000000],
        "weight": [25.5, 40.3],
    }
    df = pd.DataFrame(data)

    # DataFrame → 모델 인스턴스 리스트 변환
    instances = DailyETFConstituents.instances_from_dataframe(df)

    # DB에 저장
    repo.serial_upsert_entities(instances)
    print("ETF 구성 종목 데이터 저장 완료")
