from mjdb.repositories.base.base_repository import BaseSQLAlchemyRepository
from mjdb.model.daily_kor_investor_trading_volume_summary import DailyKorInvestorTradingVolumeSummary

import os

from typing import List
import logging
from mjdb.session.types.session_context import SessionContext
from typing import Optional

class InvestorTradingVolumeRepository(BaseSQLAlchemyRepository[DailyKorInvestorTradingVolumeSummary]):
    """
    일별 종목/투자자 유형/거래 유형별 투자자 매매 요약 데이터를 위한 저장소(Repository) 클래스입니다.

    이 클래스는 SQLAlchemyRepository를 상속하여, 일별 투자자 거래 요약 테이블
    (`daily_kor_investor_trading_volume_summary`)에 특화된 데이터 접근 메서드를 제공합니다.

    Args:
        url (str): 데이터베이스 접속 URL. 기본값은 환경 변수 STOCK_DATABASE_URL.
        verbose (bool): SQLAlchemy 세션 로그 출력 여부.
    """

    def __init__(self, context: Optional[SessionContext] = None, log_level: int = logging.INFO):
        """
        InvestorTradingVolumeRepository 생성자

        Args:
            url (str): 데이터베이스 접속 URL
            verbose (bool): 세션에서 SQL 출력 여부
        """
        super().__init__(model=DailyKorInvestorTradingVolumeSummary, context=context, log_level=log_level)

    def serial_upsert_entities(self, entities: List[DailyKorInvestorTradingVolumeSummary]) -> None:
        """
        여러 개의 투자자 거래 요약 데이터를 한 번에 추가하거나 갱신합니다.

        Args:
            entities (List[DailyKorInvestorTradingVolumeSummary]): 추가 또는 업데이트할 데이터 리스트
        """
        if not entities:
            self.logger.info("[add_list] 입력된 데이터가 비어있어 처리를 생략합니다.")
            return

        try:
            with self.session_scope() as session:
                for entity in entities:
                    try:
                        self.update(entity)
                    except Exception as inner_e:
                        self.logger.warning(f"[add_list] 단일 엔티티 처리 실패: {entity} - {inner_e}", exc_info=True)
                session.commit()

        except Exception as e:
            self.logger.exception(f"[add_list] 전체 데이터 처리 중 오류 발생 {e}")
            raise

if __name__ == "__main__":
    from dotenv import load_dotenv
    from src.db.model.df_to_model_instances import df_to_model_instances
    from mjkit.utiles import get_assets_folder_path, load_pickle
    import os

    load_dotenv()

    url = os.getenv("STOCK_DATABASE_LOCALHOST_URL")
    print(url)

    # Repository 인스턴스 생성 (모델 클래스 주입)
    repo = InvestorTradingVolumeRepository(
        url=url,
        verbose=True
    )

    # # 1. 데이터 추가 (Create)
    # new_record = DailyKorInvestorTradingVolumeSummary(
    #     base_dt=pd.to_datetime("2025-05-14", format="%Y-%m-%d"),
    #     ticker=str(uuid.uuid4())[:5],  # 예시 종목 코드
    #     # ticker="652f3",  # 예시 종목 코드
    #     investor_type="개인",
    #     transaction_type="매수",
    #     value=1000,
    #     # trading_amount=1000000,
    #     # market="KOSPI"
    # )
    #
    # records = []
    # for _ in range(10):
    #     new_record = DailyKorInvestorTradingVolumeSummary(
    #         base_dt=pd.to_datetime("2025-05-14", format="%Y-%m-%d"),
    #         # ticker=str(uuid.uuid4())[:5],  # 예시 종목 코드
    #         ticker = "a4810",
    #         investor_type="개인",
    #         transaction_type="매수",
    #         value=1000,
    #     )
    #     records.append(new_record)

    path = os.path.join(get_assets_folder_path(), "data", "investor_trading_value_df_005930_20250702.pkl")
    df = load_pickle(path)
    df = df.reset_index(drop=False)

    model = df_to_model_instances(df, DailyKorInvestorTradingVolumeSummary)
    print(model)

    for m in model:
        print(m)
        print()


    # repo.add_list(records)

    print("데이터 추가 완료")