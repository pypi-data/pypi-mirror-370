# from src.db.repositories.base import SQLAlchemyRepository
import logging

from mjdb.repositories.base.base_repository import BaseSQLAlchemyRepository
# from src.db.model.daily_stock_rise_reason_keywords import DailyStockRiseReasonKeywords
from mjdb.model.daily_stock_rise_reason_keywords import DailyStockRiseReasonKeywords
import os

from typing import Optional, List, Dict
from dotenv import load_dotenv
from mjkit.utiles import validate_date_format
from datetime import datetime
from sqlalchemy import func

from mjdb.session.types.session_context import SessionContext

load_dotenv()

class StockRiseReasonKeywordsRepository(BaseSQLAlchemyRepository[DailyStockRiseReasonKeywords]):
    """
    주식 상승 이유 키워드 데이터를 위한 저장소(Repository) 클래스입니다.

    이 클래스는 SQLAlchemyRepository를 상속하여, 일별 주식 상승 이유 키워드 테이블
    (`daily_stock_rise_reason_keywords`)에 특화된 데이터 접근 메서드를 제공합니다.

    Args:
        url (str): 데이터베이스 접속 URL. 기본값은 환경 변수 STOCK_DATABASE_URL.
        verbose (bool): SQLAlchemy 세션 로그 출력 여부.

    사용 예시:
        >>> repo = StockRiseReasonKeywordsRepository()
        >>> result = repo.find_by_ticker("005930")
        >>> keywords = repo.find_by_base_dt("2025-06-02")
    """

    def __init__(self, context: Optional[SessionContext] = None, log_level: int = logging.INFO):
        """
        StockRiseReasonKeywordsRepository 생성자

        Args:
            url (str): 데이터베이스 접속 URL
            verbose (bool): 세션에서 SQL 출력 여부
        """
        super().__init__(model=DailyStockRiseReasonKeywords, context=context, log_level=log_level)

    def find_by_ticker(self, ticker: str) -> Optional[DailyStockRiseReasonKeywords]:
        """
        특정 종목 티커(ticker)를 기준으로 해당 종목의 키워드 정보를 단건 조회합니다.

        Args:
            ticker (str): 조회할 종목 코드 (예: '005930')

        Returns:
            Optional[DailyStockRiseReasonKeywords]: 해당 종목의 키워드 정보 객체. 없으면 None.
        """
        with self.session_scope as session:
            return (
                session.query(self.model)
                .filter_by(ticker=ticker)
                .first()
            )

    def find_by_base_dt(self, base_dt: str) -> List[Dict]:
        """
        기준일(base_dt)을 기준으로 해당 날짜의 모든 종목 키워드 정보를 조회합니다.

        Args:
            base_dt (str): 기준 날짜 (YYYY-MM-DD 형식)

        Example:
            repo = StockRiseReasonKeywordsRepository(url=db_url)
            print(repo.get_max_base_dt())
            >> 2025-06-02

        Returns:
            List[DailyStockRiseReasonKeywords]: 기준일에 해당하는 모든 종목 키워드 레코드 리스트
        """
        validate_date_format(base_dt, sep="-")  # 날짜 포맷 유효성 검증
        orms = self.get_all_by_filters(base_dt=base_dt)
        return list(map(lambda m: m.to_dict(), orms))

    def get_max_base_dt(self) -> Optional[datetime.date]:
        """
        테이블에서 가장 최신의 base_dt 값을 조회합니다.

        Returns:
            Optional[datetime.date]: 가장 최신의 기준일. 데이터가 없으면 None.
        """
        with self.session_scope() as session:
            max_date = session.query(func.max(self.model.base_dt)).scalar()
            return max_date

    # ... 어떤 메소드가 필요하다면 추가 필요.


if __name__ == "__main__":
    import pandas as pd
    import uuid
    # Repository 인스턴스 생성 (모델 클래스 주입)
    # repo = SQLAlchemyRepository(DailyStockRiseReasonKeywords)
    db_url = os.getenv("DB_URL")
    print("db_url: ", print)

    # context = SessionContext(db_url=db_url, session_config=SessionConfig(expire_on_commit=False))
    # repo = StockRiseReasonKeywordsRepository(context=context)
    repo = StockRiseReasonKeywordsRepository()

    # print(repo.get_max_base_dt().strftime("%Y-%m-%d"))

    print(repo.find_by_base_dt(base_dt="2025-06-02"))

    # 1. 데이터 추가 (Create)
    new_stock = DailyStockRiseReasonKeywords(
        # base_dt='2025-05-14',  # 예시 날짜
        base_dt=pd.to_datetime("2025-05-14", format="%Y-%m-%d"),
        ticker=str(uuid.uuid4())[:5],  # 예시 종목 코드
        open=1000,
        high=1050,
        low=950,
        close=1020,
        volume=100000,
        trading_amount=102000000,
        change=2.0,
        market="KOSPI",
        market_cap=5000000000,
        outstanding_shares=100000000,
        name="Example Corp",
        filter_type="Type A",
        industry_kind="Technology",
        main_product="Software",
        industry="Software",
        keywords="growth, innovation, technology"
    )
    repo.add(new_stock)
    print("✅ 추가 완료")
    #
    # 2. 단일 조회 (Read by ID)
    stock = repo.get_by_column(column_name="base_dt", value="2025-05-14")
    print(f"🔍 ID 1 조회 결과: {stock}")

    # 3. 전체 조회 (Read all)
    stocks = repo.get_all()
    print(f"📋 전체 종목 리스트: {stocks}")

    # 4. 데이터 수정 (Update)
    if stock:
        stock.name = "카카오(수정)"
        repo.update(stock)
        print(f"✏️ 수정 완료: {stock}")

    # 5. 삭제 (Delete)
    if stock:
        repo.delete(stock)
        print(f"🗑️ 삭제 완료: {stock}")

    # 6. Raw SQL 실행
    results = repo.execute_raw_query("SELECT * FROM daily_stock_rise_reason_keywords")
    print("🧾 Raw Query 결과:")
    for row in results:
        print(row)