from sqlalchemy import Column, Date, String, BigInteger, Text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, DECIMAL as MYSQL_DECIMAL

from mjdb.model.base.base_model import BaseModel


class DailyStockRiseReasonKeywords(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.filter_type is None:
            self.filter_type = "-"  # Primary Key 에서 None 이 들어가면 안됨.

    __tablename__ = "daily_stock_rise_reason_keywords"
    __table_args__ = {"mysql_charset": "utf8mb4"}

    base_dt = Column(Date, primary_key=True, comment="기준 날짜")
    ticker = Column(String(20), primary_key=True, comment="종목 코드")

    open = Column(INTEGER(11), nullable=False, comment="시가")
    high = Column(INTEGER(11), nullable=False, comment="고가")
    low = Column(INTEGER(11), nullable=False, comment="저가")
    close = Column(INTEGER(11), nullable=False, comment="종가")

    volume = Column(BIGINT(unsigned=True), nullable=False, comment="거래량")
    trading_amount = Column(BIGINT(unsigned=True), nullable=False, comment="거래 대금")

    change = Column(MYSQL_DECIMAL(8, 4), nullable=False, comment="전일 대비 상승률 (%)")
    market = Column(String(20), nullable=False, comment="시장(KOSPI, KOSDAQ 등)")
    market_cap = Column(BIGINT(unsigned=True), nullable=False, comment="시가 총액")
    outstanding_shares = Column(BigInteger, nullable=False, comment="유통 주식 수")

    name = Column(String(100), nullable=False, comment="종목명")
    filter_type = Column(String(50), primary_key=True, nullable=False, comment="필터링 유형")

    industry_kind = Column(String(100), nullable=True, comment="업종(Kind)")
    main_product = Column(String(200), nullable=True, comment="주요 제품")
    industry = Column(String(100), nullable=True, comment="세부 업종")

    keywords = Column(Text, nullable=True, comment="상승 사유 키워드 목록(comma-separated)")

    def __repr__(self):
        return (
            f"<DailyStockRiseReasonKeywords("
            f"base_dt={self.base_dt}, "
            f"ticker='{self.ticker}', "
            f"open={self.open}, "
            f"high={self.high}, "
            f"low={self.low}, "
            f"close={self.close}, "
            f"volume={self.volume}, "
            f"trading_amount={self.trading_amount}, "
            f"change={self.change}, "
            f"market='{self.market}', "
            f"market_cap={self.market_cap}, "
            f"outstanding_shares={self.outstanding_shares}, "
            f"name='{self.name}', "
            f"filter_type='{self.filter_type}', "
            f"industry_kind='{self.industry_kind}', "
            f"main_product='{self.main_product}', "
            f"industry='{self.industry}', "
            f"keywords='{self.keywords}')>"
        )

if __name__ == "__main__":
    from mjdb.model.base.base_model import BaseModel
    objc =DailyStockRiseReasonKeywords(
        base_dt="2023-10-01",
        ticker="000660",
        open=100000,
        high=105000,
        low=95000,
        close=102000,
        volume=5000000,
        trading_amount=510000000000,
        change=2.5,
        market="KOSPI",
        market_cap=6000000000000,
        outstanding_shares=59000000,
        name="Samsung Electronics",
        filter_type="daily_rise",
        industry_kind="Technology",
        main_product="Semiconductors",
        industry="Electronics"
    )

    print(objc)