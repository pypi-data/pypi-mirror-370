# from src.db.interfaces.base_repository import BaseRepository
import logging

from mjdb.repositories.abstract.abstract_repository import AbstractRepository
# from src.db.session import get_session_context
from sqlalchemy.sql import text
import os
from dotenv import load_dotenv

from typing import Any, List, Optional, Type, TypeVar
from mjdb.session.sql_alchemy_db_session import SQLAlchemyDbSession
from mjdb.session.types.session_context import SessionContext
from mjdb.session.types.session_config import SessionConfig

from typing import Generator, Dict
from tqdm import tqdm
from sqlalchemy.dialects.mysql import insert
import pandas as pd
# from overrides import override
from sqlalchemy.exc import SQLAlchemyError
import math

EntityType = TypeVar("EntityType")
load_dotenv()

os.environ["STOCK_DATABASE_URL"] = "mysql+pymysql://root:root@192.168.1.3:3307/stock"


class BaseSQLAlchemyRepository(AbstractRepository[EntityType]):
    """
     SQLAlchemy 기반의 범용(generic) 저장소 클래스입니다.

     이 클래스는 특정 SQLAlchemy 모델(EntityType)을 받아,
     데이터베이스에 대한 기본적인 CRUD 작업(Create, Read, Update, Delete)과
     Raw SQL 실행 기능을 제공합니다.

     사용 예시:
         >>> repo = BaseSQLAlchemyRepository(DailyStockRiseReasonKeywords)
         >>> all_items = repo.get_all()
         >>> item = repo.get_by_column('2025-05-14', column_name='base_dt')
         >>> repo.add(new_item)
         >>> repo.update(updated_item)
         >>> repo.delete(item)
         >>> result = repo.execute_raw_query("SELECT * FROM table_name")

     주요 메서드:
         - get_by_column: 특정 컬럼 값을 기준으로 단일 엔티티 조회
         - get_all: 전체 엔티티 조회
         - add: 엔티티 추가
         - update: 엔티티 수정
         - delete: 엔티티 삭제
         - execute_raw_query: Raw SQL 쿼리 실행
         - close: 세션 강제 종료 (보통 필요 없음)
     """
    def __init__(
            self,
            model: Type[EntityType],
            context: Optional[SessionContext] = None,
            log_level: int = logging.INFO
    ):
        """
        SQLAlchemyRepository 생성자

        Args:
            model (Type[EntityType]): 다루고자 하는 SQLAlchemy 모델 클래스
            db_url (str): 데이터베이스 접속 URL (기본값은 환경 변수로부터 가져옴)

        작동 방식:
            - get_session_context 함수를 통해 세션 컨텍스트 매니저 생성
            - 전달받은 모델 클래스를 저장소에서 사용할 수 있도록 설정
        """

        ctx = context or SessionContext(
            db_url=os.getenv("DB_URL"),
            session_config=SessionConfig(expire_on_commit=False)
        )

        self.sql_alchemy_db_session = SQLAlchemyDbSession(context=ctx, log_level=log_level)
        self.session_scope = self.sql_alchemy_db_session.get_session_context()
        self.model = model
        super().__init__(log_level=log_level)
        self.print_public_attributes()

    def get_by_column(self, value: Any, column_name: str = "id") -> Optional[EntityType]:
        """
        컬럼명을 유동적으로 설정하여 조회하는 함수.
        :param column_name: 조회할 컬럼명 (예: 'ticker', 'base_dt' 등)
        :param value: 해당 컬럼에서 찾을 값
        :return: 해당 조건을 만족하는 첫 번째 엔티티
        """

        with self.session_scope() as session:
            v = session.query(self.model).filter(getattr(self.model, column_name) == value).first()
            return v

    def get_all_by_filters(self, **filters: Any) -> List[EntityType]:
        """
        여러 컬럼 값을 기준으로 조건에 맞는 모든 레코드를 조회합니다.

        Args:
            **filters: 컬럼명=값 형태의 키워드 인자들

        Example:
            # base_dt와 market이 모두 일치하는 레코드들을 가져옴
            results = repo.get_all_by_filters(base_dt="2025-06-02", market="KOSPI")
            ..
            for row in results:
                print(row.ticker, row.name, row.keywords)

        Returns:
            List[EntityType]: 조건을 만족하는 모든 레코드 리스트
        """
        with self.session_scope() as session:
            query = session.query(self.model)
            for column, value in filters.items():
                query = query.filter(getattr(self.model, column) == value)
            return query.all()

    def get_all(self) -> List[Any]:
        """
        전체 레코드를 조회합니다.
        """
        with self.session_scope() as session:
            return session.query(self.model).all()

    def add(self, entity: Any) -> None:
        """
        하나의 엔티티를 DB에 추가합니다.
        """
        with self.session_scope() as session:
            session.add(entity)

    def update(self, entity: Any) -> None:
        """
        엔티티를 병합(업데이트)합니다.
        """
        with self.session_scope() as session:
            session.merge(entity)

    def delete(self, entity: Any) -> None:
        """
        엔티티를 삭제합니다.
        """
        with self.session_scope() as session:
            session.delete(entity)

    def execute_raw_query(self, query: str) -> Any:
        """
        Raw SQL 쿼리를 실행합니다.
        """
        with self.session_scope() as session:
            return session.execute(text(query)).fetchall()

    def close(self) -> None:
        """
        세션을 종료합니다.
        """
        with self.session_scope() as session:
            session.close()

    def _get_in_chunks(self, chunk_size: int = 1000) -> Generator[List[Any], None, None]:
        """
        데이터 전체를 chunk_size 단위로 나누어 가져옵니다.
        진행 상황을 tqdm으로 표시합니다.
        """
        with self.session_scope() as session:
            total = session.query(self.model).count()
            for offset in tqdm(range(0, total, chunk_size), total=(total // chunk_size) + 1, desc="Fetching in chunks"):
                chunk = (
                    session.query(self.model)
                    .offset(offset)
                    .limit(chunk_size)
                    .all()
                )
                yield chunk  # 제너레이터로 반환 (필요할 때만 메모리에 로드)

    def get_all_in_chunks(self, chunk_size: int = 1000) -> List[Any]:
        """
        전체 데이터를 청크 단위로 가져와서 하나의 리스트로 합칩니다.
        (메모리 사용량 커질 수 있음)
        """
        results = []
        for chunk in self._get_in_chunks(chunk_size):
            results.extend(chunk)
        return results

    def serial_upsert_entities(self, entities: List[EntityType]) -> None:
        """
        여러개의 엔티티를 한 번에 추가 또는 갱신합니다.

        Args:
            entities (List[EntityType]): 추가 또는 업데이트할 ETF OHLCV 데이터 리스트
        """
        if not entities:
            self.logger.info("[add_list] 입력된 데이터가 비어있어 처리를 생략합니다.")
            return

        try:
            with self.session_scope() as session:
                for entity in tqdm(entities, desc="Serial upserting entities", unit="entity"):
                    try:
                        self.update(entity)
                    except Exception as inner_e:
                        self.logger.warning(f"[add_list] 단일 엔티티 처리 실패: {entity} - {inner_e}", exc_info=True)
                session.commit()

        except Exception as e:
            self.logger.exception(f"[add_list] 전체 데이터 처리 중 오류 발생 {e}")
            raise

    def _entity_to_mapping(self, entity: EntityType) -> Dict[str, Any]:
        """
        SQLAlchemy 모델 인스턴스를 DB insert/update용 dict 형태로 변환합니다.

        - SQLAlchemy 모델의 컬럼 이름을 key로 사용
        - 각 컬럼의 값을 entity에서 꺼내 dict에 담음
        - NaN(float), NaT(datetime) 등 Pandas에서 오는 결측값은 None으로 변환

        Args:
            entity (EntityType): SQLAlchemy 모델 인스턴스

        Returns:
            Dict[str, EntityType]: {"컬럼명": 값} 형태의 dict
        """
        mapping: Dict[str, EntityType] = {}

        # 모델이 가진 모든 컬럼 반복
        for column in self.model.__table__.columns:
            column_name: str = column.name

            # entity에서 해당 컬럼 값 가져오기
            value: EntityType = getattr(entity, column_name)

            # Pandas NaN, NaT 같은 결측치는 None으로 치환
            if pd.isna(value):
                value = None

            # dict에 저장
            mapping[column_name] = value

        return mapping

    def _chunk_entities(
        self,
        entities: List[EntityType],
        chunk_size: int
    ) -> Generator[List[EntityType], None, None]:
        """
        엔티티 리스트를 chunk_size 단위로 잘라 제너레이터로 반환합니다.
        """
        for i in range(0, len(entities), chunk_size):
            yield entities[i:i + chunk_size]

    def _build_upsert_stmt(self, chunk: List[EntityType]):
        """
        주어진 엔티티 청크에 대해 MySQL upsert(insert ... on duplicate key update) 구문 생성
        """
        mappings = [self._entity_to_mapping(e) for e in chunk]
        stmt = insert(self.model).values(mappings)
        update_cols = {
            c.name: stmt.inserted[c.name]
            for c in self.model.__table__.columns
            if not c.primary_key
        }
        return stmt.on_duplicate_key_update(**update_cols)

    def add_list(self, entities: List[EntityType], chunk_size: int = 2000) -> None:
        """
        엔티티 리스트를 청크 단위로 잘라 순차적으로 Bulk Upsert 합니다.

        Args:
            entities (List[Any]): 추가/업데이트할 엔티티 리스트
            chunk_size (int): 한 번에 처리할 데이터 크기
        """
        if not entities:
            self.logger.info("[bulk_upsert] 입력된 데이터가 비어있어 처리하지 않습니다.")
            return

        total_chunks = math.ceil(len(entities) / chunk_size)

        try:
            with self.session_scope() as session:
                for chunk in tqdm(
                    self._chunk_entities(entities, chunk_size),
                    total=total_chunks,
                    desc="Bulk upserting", unit="chunk"
                ):
                    stmt = self._build_upsert_stmt(chunk)
                    session.execute(stmt)
                session.commit()

                # 🔹 DB 저장 완료 후 최종 로그
                self.logger.info(
                    f"[bulk_upsert] DB 저장 완료: 총 {len(entities):,}개 엔티티를 "
                    f"{total_chunks:,}개의 청크로 처리했습니다."
                )

        except SQLAlchemyError:
            self.logger.exception("[bulk_upsert] 전체 데이터 처리 중 오류 발생", exc_info=True)
            raise


if __name__ == "__main__":
    from mjdb.model.daily_stock_rise_reason_keywords import DailyStockRiseReasonKeywords
    import pandas as pd
    import uuid
    from dotenv import load_dotenv
    load_dotenv()

    db_url = os.getenv("STOCK_DATABASE_LOCALHOST_URL")

    # Repository 인스턴스 생성 (모델 클래스 주입)
    session_conf = SessionConfig(expire_on_commit=False)
    context = SessionContext(db_url=db_url, session_config=session_conf)
    repo = BaseSQLAlchemyRepository(DailyStockRiseReasonKeywords, context=context)

    # 1. 데이터 추가 (Create)
    ticker = str(uuid.uuid4())[:5]
    new_stock = DailyStockRiseReasonKeywords(
        # base_dt='2025-05-14',  # 예시 날짜
        base_dt=pd.to_datetime("2025-05-14", format="%Y-%m-%d"),
        ticker=ticker,  # 예시 종목 코드
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
    # repo.add(new_stock)
    # print("✅ 추가 완료")
    #
    # # 2. 단일 조회 (Read by ID)
    # stock = repo.get_by_column(column_name="base_dt", value="2025-05-14")
    # print(f"🔍 ID 1 조회 결과: {stock}")
    # print(f"ticker: {ticker}")
    #
    # # 3. 전체 조회 (Read all)
    # stocks = repo.get_all()
    # print(f"📋 전체 종목 리스트: {stocks}")
    #
    # # 4. 데이터 수정 (Update)
    # if stock:
    #     stock.name = "카카오(수정)"
    #     repo.update(stock)
    #     print(f"✏️ 수정 완료: {stock}")
    #
    # # 5. 삭제 (Delete)
    # if stock:
    #     repo.delete(stock)
    #     print(f"🗑️ 삭제 완료: {stock}")
    #
    # # 6. Raw SQL 실행
    # results = repo.execute_raw_query("SELECT * FROM daily_stock_rise_reason_keywords limit 50;")
    # print("🧾 Raw Query 결과:")
    # for row in results:
    #     print(row)

    repo.add_list([new_stock])