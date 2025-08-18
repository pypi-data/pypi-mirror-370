from mjdb.session.abstract.abstract_db_session import AbstractDbSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, text
from contextlib import contextmanager
from typing import Callable, ContextManager
import logging

from mjdb.session.types.engine_config import EngineConfig
from mjdb.session.types.session_config import SessionConfig
from mjdb.session.types.session_context import SessionContext
from tenacity import retry, stop_after_attempt, before_sleep_log, wait_exponential, after_log
from mjkit.utiles import get_logger


class BaseDbSession(AbstractDbSession):
    """
    BaseDbSession

    SQLAlchemy 기반 DB 세션 생성을 위한 기본 구현 클래스입니다.
    - 추상 인터페이스(AbstractDbSession)를 구현합니다.
    - 외부에서 주입받은 SessionContext를 통해 구성 정보를 설정합니다.

    책임:
        - SQLAlchemy 엔진 및 세션 팩토리 생성
        - 세션 단일 획득(get_session)
        - 세션 컨텍스트 제공(get_session_context)

    Attributes:
        context (SessionContext): DB 연결 및 세션 설정 정보를 포함하는 구성 객체
        logger (logging.Logger): 로깅 기능 제공 (LoggingMixin 통해 상속됨)
    """

    def __init__(self, context: SessionContext, log_level: int = logging.INFO):
        """
        BaseDbSession 초기화

        Args:
            context (SessionContext): 세션 생성에 필요한 구성 정보 객체
            log_level (int, optional): 로깅 레벨. 기본값은 logging.INFO
        """
        super().__init__(log_level=log_level)
        self.context = context

    def _create_engine(self):
        """
        SQLAlchemy Engine 생성

        Returns:
            sqlalchemy.engine.Engine: 생성된 SQLAlchemy 엔진
        """
        cfg = self.context.engine_config
        return create_engine(
            self.context.db_url,
            pool_size=cfg.pool_size,
            max_overflow=cfg.max_overflow,
            pool_recycle=cfg.pool_recycle,
            pool_pre_ping=cfg.pool_pre_ping,
            echo=cfg.echo
        )

    def _create_session_factory(self):
        """
        SQLAlchemy sessionmaker 생성

        Returns:
            sessionmaker: 세션 팩토리
        """
        engine = self._create_engine()
        scfg = self.context.session_config
        return sessionmaker(
            autocommit=scfg.autocommit,
            autoflush=scfg.autoflush,
            bind=engine,
            expire_on_commit=scfg.expire_on_commit
        )

    def get_session(self) -> Session:
        """
        단일 세션 객체 생성 및 반환

        - 연결 테스트 수행 (SELECT 1)
        - 커밋 후 세션 반환
        - 호출자가 직접 close()해야 함

        Returns:
            Session: SQLAlchemy 세션 객체

        Example:
            >>> from mjdb.session.core.sqlalchemy_session import SQLAlchemyDbSession
            >>> session_mgr = SQLAlchemyDbSession(context)
            >>> session = session_mgr.get_session()
            >>> result = session.execute(text("SELECT * FROM users"))
            >>> session.commit()
            >>> session.close()
        """
        db_url = self.context.db_url
        self.logger.debug(f"DB 연결을 시도 중... DB URL: {db_url}")
        try:
            factory = self._create_session_factory()
            session = factory()

            self.logger.debug("DB 연결 확인 중... SELECT 1 실행")
            session.execute(text("SELECT 1"))
            self.logger.debug("DB 연결 확인 성공")

            session.commit()
            self.logger.info("DB 연결 및 세션 커밋 성공")
            return session
        except Exception as e:
            self.logger.exception(f"DB 연결 오류: {e}")
            if "session" in locals():
                session.rollback()
                self.logger.debug("DB 연결 롤백 완료")
            raise

    def get_session_context(self) -> Callable[[], ContextManager[Session]]:
        """
        세션 컨텍스트 매니저 반환

        - 자동 재시도(최대 3회)
        - 예외 발생 시 롤백 및 종료
        - 커밋 포함
        - 블록 종료 시 자동으로 세션 종료

        Returns:
            Callable: context manager 함수

        Example:
            >>> from mjdb.session.core.sqlalchemy_session import SQLAlchemyDbSession
            >>> session_mgr = SQLAlchemyDbSession(context)
            >>> session_scope = session_mgr.get_session_context()
            >>> with session_scope() as session:
            ...     result = session.execute(text("SELECT * FROM products"))
            ...     for row in result:
            ...         print(row)
        """
        factory = self._create_session_factory()
        local_logger = get_logger(__name__, self.logger.level)

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=2, min=4, max=60),
            before_sleep=before_sleep_log(local_logger, logging.INFO),
            after=after_log(local_logger, logging.DEBUG)
        )
        @contextmanager
        def _session_scope() -> Session:
            """
            세션 컨텍스트 내부 함수

            Yields:
                Session: SQLAlchemy 세션 객체
            """
            session: Session = factory()
            try:
                local_logger.debug("[2단계] DB 연결 테스트 실행 (SELECT 1)")
                session.execute(text("SELECT 1"))
                local_logger.debug("[2단계] DB 연결 확인 성공")

                yield session

                session.commit()
                local_logger.info("[3단계] 세션 커밋 완료")
            except Exception as e:
                session.rollback()
                local_logger.warning("[3단계] 오류 발생 - 세션 롤백 수행")
                local_logger.exception(e)
                raise
            finally:
                session.close()
                local_logger.debug("[4단계] 세션 종료 완료")

        return _session_scope


if __name__ == "__main__":
    # 테스트용 코드
    import os
    from dotenv import load_dotenv
    load_dotenv()

    db_url_ = os.getenv("DB_URL")
    print(db_url_)


    ec = EngineConfig()
    sc = SessionConfig()
    sct = SessionContext(
        db_url=db_url_,
        engine_config=ec,
        session_config=sc
    )
    base_db_session = BaseDbSession(context=sct, log_level=logging.INFO)

    print(base_db_session.get_session())

    session = base_db_session.get_session()
    print(">> 1. DB 연결 성공!")
    session.close()

    print("session context 테스트,,")

    session_scope = base_db_session.get_session_context()

    with session_scope() as session:
        print("DB 연결 성공!, ", session)
        print(session.execute(text("SELECT 1")).fetchall())
        # result = session.query(MyModel).all()