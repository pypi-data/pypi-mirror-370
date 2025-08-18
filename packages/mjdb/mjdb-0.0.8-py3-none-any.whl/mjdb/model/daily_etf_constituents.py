from sqlalchemy import Column, Date, String, BigInteger, Float, Index
from mjdb.model.base.base_model import BaseModel
from mjdb.model.utiles.df_to_model_instances import df_to_model_instances
from pandas import DataFrame
from typing import List


class DailyETFConstituents(BaseModel):
    """
    ETF 일별 구성 종목 데이터를 저장하는 모델 클래스

    - 'base_dt', 'etf_ticker', 'constituent_ticker'를 복합 기본키로 사용하여
      동일 ETF 구성 종목의 중복 삽입 방지
    - 계약 수량, 총 금액, 포트폴리오 비중 등의 주요 정보를 포함
    """

    __tablename__ = "daily_etf_constituents"
    __table_args__ = (
        Index("idx_base_dt", "base_dt"),
        Index("idx_ticker", "ticker"),
        Index("idx_constituent_ticker", "constituent_ticker"),
        {"mysql_charset": "utf8mb4"},
    )

    base_dt = Column(Date, primary_key=True, comment="기준 일자")
    ticker = Column(String(20), primary_key=True, comment="ETF 종목 코드")
    name = Column(String(100), nullable=False, comment="ETF 종목명")
    constituent_ticker = Column(String(20), primary_key=True, comment="ETF 구성 종목 코드")
    contract_count = Column(Float, nullable=False, comment="보유 계약 수량")
    amount = Column(BigInteger, nullable=False, comment="총 금액")
    weight = Column(Float, nullable=False, comment="포트폴리오 비중(%)")

    def __repr__(self):
        return (
            f"<DailyETFConstituents(base_dt={self.base_dt}, "
            f"etf_ticker='{self.ticker}', etf_name='{self.name}', "
            f"constituent_ticker='{self.constituent_ticker}', "
            f"contract_count={self.contract_count}, amount={self.amount}, "
            f"weight={self.weight})>"
        )

    @classmethod
    def instances_from_dataframe(cls, df: DataFrame) -> List["DailyETFConstituents"]:
        """
        DataFrame에서 모델 인스턴스 리스트로 변환

        Args:
            df (DataFrame): 변환할 데이터프레임

        Returns:
            List[DailyETFConstituents]: 모델 인스턴스 리스트
        """
        return df_to_model_instances(
            df=df,
            model=cls,
            date_fields=["base_dt"],
            required_fields=["ticker", "constituent_ticker", "name"]
        )


if __name__ == "__main__":
    import pandas as pd
    from datetime import datetime

    # 예시 DataFrame 생성
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

    # 모델 인스턴스로 변환
    instances = DailyETFConstituents.instances_from_dataframe(df)
    for inst in instances:
        print(inst)
