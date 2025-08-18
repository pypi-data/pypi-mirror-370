from mjdb.repositories.base.base_repository import BaseSQLAlchemyRepository
from mjdb.model.daily_kor_stock_analysis_summary import DailyKorStockAnalysisSummary
import os
from mjdb.session.types.session_context import SessionContext
import logging

from typing import Optional

class KorStockAnalysisSummaryRepository(BaseSQLAlchemyRepository[DailyKorStockAnalysisSummary]):
    """
    KorStockAnalysisSummaryRepository

    - `DailyKorStockAnalysisSummary` 모델을 다루는 SQLAlchemy 기반의 저장소(Repository) 클래스입니다.
    - BaseSQLAlchemyRepository를 상속하며, 공통 CRUD 기능을 모두 제공받습니다.
    - 필요 시 종목 분석 요약에 특화된 도메인 메서드를 추가할 수 있습니다.

    Attributes:
        model: DailyKorStockAnalysisSummary (SQLAlchemy 모델)
        context: SessionContext (DB 연결 설정)
        logger: 로깅 도구 (LoggingMixin 상속됨)
    """

    def __init__(self, context: Optional[SessionContext] = None, log_level: int = logging.INFO):
        """
        저장소 인스턴스 초기화

        Args:
            context (SessionContext, optional): DB 연결 설정 정보
            log_level (int): 로깅 레벨 (기본: logging.INFO)
        """
        super().__init__(model=DailyKorStockAnalysisSummary, context=context, log_level=log_level)

    def find_by_ticker(self, ticker: str) -> Optional[DailyKorStockAnalysisSummary]:
        """
        특정 티커로 단일 종목 요약 데이터를 조회합니다.

        Args:
            ticker (str): 종목 코드 (예: '005930', 'AAPL')

        Returns:
            Optional[DailyKorStockAnalysisSummary]: 해당 티커에 대한 분석 요약 데이터 (없으면 None)

        Example:
            >>> repo.find_by_ticker("005930")
        """
        with self.session_scope as session:
            return (
                session.query(self.model)
                .filter_by(ticker=ticker)
                .first()
            )


if __name__ == "__main__":
    import pandas as pd
    import uuid
    from dotenv import load_dotenv
    load_dotenv()
    # Repository 인스턴스 생성 (모델 클래스 주입)
    db_url = os.getenv("DB_URL")
    print(db_url)

    repo = KorStockAnalysisSummaryRepository(
        # context =SessionContext(db_url=db_url),
        # log_level=logging.INFO
    )

    # 1. 데이터 추가 (Create)
    new_stock = DailyKorStockAnalysisSummary(
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
    )

    # new_stock = DailyKorStockAnalysisSummary(
    #     # base_dt='2025-05-14',  # 예시 날짜
    #     base_dt=pd.to_datetime("2025-04-09", format="%Y-%m-%d"),
    #     ticker="095570",
    #     open=3600,
    #     high=1050,
    #     low=950,
    #     close=1020,
    #     volume=100000,
    #     trading_amount=102000000,
    #     change=2.0,
    #     market="KOSPI",
    #     market_cap=5000000000,
    #     outstanding_shares=100000000,
    #     name="AJ네트웍스",
    #     # filter_type='-',
    #     industry_kind="Technology",
    #     main_product="Software",
    #     industry="Software",
    # )

    print(new_stock)
    print()
    repo.add(new_stock)
    print("✅ 추가 완료")
    # #
    # # 2. 단일 조회 (Read by ID)
    stock = repo.get_by_column(column_name="base_dt", value="2025-05-14")
    print(f"🔍 ID 1 조회 결과: {stock}")
    #
    # # 3. 전체 조회 (Read all)
    stocks = repo.get_all()
    print(f"📋 전체 종목 리스트: {stocks}")

    # 4. 데이터 수정 (Update)
    if stock:
        stock.name = "카카오(수정)"
        repo.update(stock)
        print(f"✏️ 수정 완료: {stock}")

    repo.update(new_stock)

    # 5. 삭제 (Delete)
    if stock:
        repo.delete(stock)
        print(f"🗑️ 삭제 완료: {stock}")

    # 6. Raw SQL 실행
    results = repo.execute_raw_query("SELECT * FROM daily_stock_rise_reason_keywords")
    print("🧾 Raw Query 결과:")
    for row in results:
        print(row)