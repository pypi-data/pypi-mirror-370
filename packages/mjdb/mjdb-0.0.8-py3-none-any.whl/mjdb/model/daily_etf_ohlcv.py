from sqlalchemy import Column, Date, String, BigInteger, Float, Index
from mjdb.model.base.base_model import BaseModel
from mjdb.model.utiles.df_to_model_instances import df_to_model_instances
from pandas import DataFrame
from typing import List

class DailyETFOHLCV(BaseModel):
    """
    ETF 일별 OHLCV 및 NAV, 기초지수 데이터를 저장하는 모델 클래스

    - 'base_dt'와 'ticker'를 복합 기본키로 사용하여 중복 데이터 삽입 방지
    - NAV, 기초지수, 거래량, 거래대금 등 주요 정보를 포함
    """

    __tablename__ = "daily_etf_ohlcv"
    __table_args__ = (
        Index("idx_base_dt", "base_dt"),
        Index("idx_ticker", "ticker"),
        {"mysql_charset": "utf8mb4"},
    )

    base_dt = Column(Date, primary_key=True, comment="기준 일자")
    ticker = Column(String(20), primary_key=True, comment="ETF 종목 코드")
    name = Column(String(100), nullable=False, comment="ETF 종목명")
    nav = Column(Float, nullable=False, comment="순자산가치 (NAV)")
    open = Column(BigInteger, nullable=False, comment="시가")
    high = Column(BigInteger, nullable=False, comment="고가")
    low = Column(BigInteger, nullable=False, comment="저가")
    close = Column(BigInteger, nullable=False, comment="종가")
    volume = Column(BigInteger, nullable=False, comment="거래량")
    trading_amount = Column(BigInteger, nullable=False, comment="거래대금")
    underlying_index = Column(Float, nullable=False, comment="기초지수")

    def __repr__(self):
        return (
            f"<DailyETFOHLCV(base_dt={self.base_dt}, ticker='{self.ticker}', "
            f"name='{self.name}', nav={self.nav}, open={self.open}, high={self.high}, "
            f"low={self.low}, close={self.close}, volume={self.volume}, "
            f"trading_amount={self.trading_amount}, underlying_index={self.underlying_index})>"
        )

    @classmethod
    def instances_from_dataframe(cls, df: DataFrame) -> List["DailyETFOHLCV"]:
        """
        DataFrame에서 모델 인스턴스 리스트로 변환

        Args:
            df (DataFrame): 변환할 데이터프레임

        Returns:
            List[DailyETFOHLCV]: 모델 인스턴스 리스트
        """
        return df_to_model_instances(
            df=df,
            model=cls,
            date_fields=["base_dt"],
            required_fields=["ticker", "name"]
        )

if __name__ == "__main__":
    import pandas as pd
    from datetime import datetime

    # 예시 DataFrame 생성
    data = {
        "base_dt": [datetime(2025, 8, 14), datetime(2025, 8, 15)],
        "ticker": ["ETF001", "ETF002"],
        "name": ["Sample ETF 1", "Sample ETF 2"],
        "nav": [10000.5, 10200.7],
        "open": [10000, 10200],
        "high": [10100, 10300],
        "low": [9950, 10150],
        "close": [10050, 10250],
        "volume": [1500, 1800],
        "trading_amount": [15000000, 18000000],
        "underlying_index": [1300.5, 1320.7],
    }
    df = pd.DataFrame(data)

    # 모델 인스턴스로 변환
    instances = DailyETFOHLCV.instances_from_dataframe(df)
    for inst in instances:
        print(inst)