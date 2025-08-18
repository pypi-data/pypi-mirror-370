from sqlalchemy import Column, Date, String, BigInteger
from mjdb.model.base.base_model import BaseModel

class DailyKorInvestorTradingVolumeSummary(BaseModel):
    """
    일별 종목/투자자 유형/거래 유형별 투자자 매매 요약 테이블 모델 클래스입니다.

    - 투자 주체 별 매수/매도/순매수 거래 내역을 저장합니다.
    - 거래 금액 또는 거래량은 'value' 컬럼에 저장되며, 'transaction_type'에 따라 의미가 달라집니다.

    Composite Primary Key:
        - base_dt: 날짜
        - ticker: 종목 코드
        - investor_type: 투자자 유형
        - transaction_type: 거래 구분 (매수/매도/순매수)
    """

    __tablename__ = "daily_kor_investor_trading_volume_summary"
    __table_args__ = {"mysql_charset": "utf8mb4"}

    base_dt = Column(Date, primary_key=True, comment="기준 날짜")
    ticker = Column(String(20), primary_key=True, comment="종목 코드")
    investor_type = Column(String(50), primary_key=True, comment="투자자 유형 (예: 금융투자, 보험 등)")
    transaction_type = Column(String(10), primary_key=True, comment="매수/매도/순매수 구분")
    value = Column(BigInteger, nullable=False, comment="거래 금액 (원 단위) | 거래량")

    def __repr__(self):
        return (
            f"<DailyKorInvestorTradingVolumeSummary("
            f"base_dt={self.base_dt}, "
            f"ticker='{self.ticker}', "
            f"investor_type='{self.investor_type}', "
            f"transaction_type='{self.transaction_type}', "
            f"value={self.value})>"
        )
