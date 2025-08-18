from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import ContextManager
from mjkit.mixin import LoggingMixin, AttributePrinterMixin
import logging


class AbstractDbSession(ABC, LoggingMixin, AttributePrinterMixin):
    """
    AbstractDbSession

    데이터베이스 세션 생성 및 컨텍스트 관리 방법을 정의하는 추상 베이스 클래스입니다.
    - LoggingMixin: 로깅 기능 제공
    - AttributePrinterMixin: 인스턴스 속성 출력 기능 제공 (디버깅 지원)

    서브클래스는 get_session() 및 get_session_context() 메서드를 반드시 구현해야 합니다.

    Attributes:
        log_level (int): 로깅 레벨 (예: logging.INFO, logging.DEBUG)
    """

    def __init__(self, log_level: int = logging.INFO):
        """
        AbstractDbSession 초기화

        Args:
            log_level (int, optional): 로그 출력 레벨 지정. 기본값은 logging.INFO

        Example:
            >>> session_mgr = MyDbSessionSubclass(log_level=logging.DEBUG)
            >>> session_mgr.log("로그 메시지")
        """
        super().__init__(level=log_level)

    @abstractmethod
    def get_session(self) -> Session:
        """
        세션 인스턴스를 반환합니다.

        메서드를 호출할 때마다 새로운 SQLAlchemy Session 객체를 생성해야 합니다.
        직접 관리할 필요 없이 간단하게 DB 작업에 사용할 수 있습니다.

        Returns:
            Session: SQLAlchemy 세션 객체

        Example:
            >>> session = session_mgr.get_session()
            >>> result = session.execute(text("SELECT 1"))
        """
        raise NotImplementedError(f"{self.__class__.__name__} 클래스는 get_session() 메서드를 구현해야 합니다.")

    @abstractmethod
    def get_session_context(self) -> ContextManager[Session]:
        """
        컨텍스트 매니저 형태로 세션을 제공합니다.

        with 블록 내부에서 세션을 사용하고, 블록 종료 시 자동으로 commit 또는 rollback 및 close 처리됩니다.

        Returns:
            ContextManager[Session]: SQLAlchemy 세션을 관리하는 컨텍스트 매니저

        Example:
            >>> with session_mgr.get_session_context() as session:
            ...     session.add(obj)
            ...     # 블록 종료 시 자동 커밋
        """
        raise NotImplementedError(f"{self.__class__.__name__} 클래스는 get_session_context() 메서드를 구현해야 합니다.")