from sqlalchemy import Column, Date, String, BigInteger, Float, Index
from mjdb.model.base.base_model import BaseModel
from mjdb.model.utiles.df_to_model_instances import df_to_model_instances
from pandas import DataFrame
from typing import List

class DailyShareholderOwnership(BaseModel):
    """
    일별 종목별 주요 주주 지분 보유 현황 스냅샷 테이블 모델 클래스입니다.

    - 주주 유형별 보통주 수량, 지분율, 유통주식 수 및 유통 비율 정보를 저장합니다.
    - 'reference_date', 'ticker', 'shareholder_type', 'last_change_date'를 복합 기본키로 사용합니다.
    """

    __tablename__ = "daily_shareholder_ownership"
    __table_args__ = (
        Index("idx_reference_date", "reference_date"),
        Index("idx_ticker", "ticker"),
        Index("idx_shareholder_type", "shareholder_type"),
        Index("idx_last_change_date", "last_change_date"),
        {"mysql_charset": "utf8mb4"},
    )

    reference_date = Column(Date, primary_key=True, comment="기준 일자")
    ticker = Column(String(20), primary_key=True, comment="종목 코드")
    name = Column(String(100), nullable=False, comment="종목명")
    shareholder_type = Column(String(50), primary_key=True, comment="주주 유형 (예: 외국인, 기관 등)")
    common_shares = Column(BigInteger, nullable=False, comment="보통주 보유 수량")
    ownership_ratio = Column(Float, nullable=False, comment="지분율 (%)")
    total_shares_outstanding = Column(BigInteger, nullable=False, comment="총 발행 주식 수")
    floating_shares = Column(BigInteger, nullable=False, comment="유통 주식 수")
    floating_share_ratio = Column(Float, nullable=False, comment="유통 비율 (%)")
    last_change_date = Column(Date, primary_key=True, comment="최근 변경 일자")

    def __repr__(self):
        return (
            f"<DailyShareholderOwnership("
            f"reference_date={self.reference_date}, "
            f"ticker='{self.ticker}', "
            f"name='{self.name}', "
            f"shareholder_type='{self.shareholder_type}', "
            f"common_shares={self.common_shares}, "
            f"ownership_ratio={self.ownership_ratio}, "
            f"total_shares_outstanding={self.total_shares_outstanding}, "
            f"floating_shares={self.floating_shares}, "
            f"floating_share_ratio={self.floating_share_ratio}, "
            f"last_change_date={self.last_change_date})>"
        )

    @classmethod
    def instances_from_dataframe(cls, df: DataFrame) -> List["DailyShareholderOwnership"]:
        """
        DataFrame에서 모델 인스턴스 리스트로 변환합니다.

        Args:
            df (DataFrame): 변환할 데이터프레임

        Returns:
            List[DailyShareholderOwnership]: 모델 인스턴스 리스트
        """

        return df_to_model_instances(
            df=df,
            model=cls,
            date_fields=["reference_date", "last_change_date"],
            required_fields=["ticker", "shareholder_type"]
        )