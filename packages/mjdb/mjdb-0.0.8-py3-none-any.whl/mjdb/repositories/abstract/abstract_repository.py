from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, List, Optional
from mjkit.mixin import LoggingMixin, AttributePrinterMixin
import logging

# ------------------------------------------------------------------------------
# 타입 변수: EntityType
# ------------------------------------------------------------------------------
# 이 저장소가 다룰 도메인 모델 타입을 제너릭으로 지정
# 예: User, StockPrice, DailyStockRiseReasonKeywords 등
EntityType = TypeVar("EntityType")


class AbstractRepository(
    LoggingMixin,
    AttributePrinterMixin,
    ABC,
    Generic[EntityType],
):
    """
    AbstractRepository

    모든 저장소(Repository)가 반드시 구현해야 하는 공통 인터페이스입니다.

    이 추상 클래스는 다음의 목적을 가집니다:
        - 일관된 저장소 인터페이스 제공 (GenericRepository 패턴)
        - CRUD 작업의 최소 단위 정의
        - 공통된 로깅 및 디버깅 기능 믹스인 제공

    주요 특징:
        - 로깅 지원: LoggingMixin을 상속하여 self.logger 사용 가능
        - 디버깅 지원: AttributePrinterMixin을 상속하여 self.print_attributes() 사용 가능

    Type Parameters:
        EntityType: 저장소에서 다룰 도메인 모델 타입

    예:
        class UserRepository(AbstractRepository[User]):
            ...
    """

    def __init__(self, log_level: int = logging.INFO):
        """
        AbstractRepository 초기화

        Args:
            log_level (int): 로깅 레벨 설정 (기본값: logging.INFO)
        """
        super().__init__(level=log_level)

    @abstractmethod
    def get_by_column(self, column_name: str, value: Any) -> Optional[EntityType]:
        """
        특정 컬럼 값을 기준으로 단일 레코드를 조회합니다.

        Args:
            column_name (str): 조회할 컬럼명 (예: 'id', 'email', 'base_dt')
            value (Any): 검색할 값

        Returns:
            Optional[EntityType]: 조회된 모델 인스턴스 또는 None

        예시:
            >>> user = repo.get_by_column("email", "alice@example.com")
        """
        pass

    @abstractmethod
    def get_all(self) -> List[EntityType]:
        """
        모든 레코드를 조회합니다.

        Returns:
            List[EntityType]: 저장된 전체 엔티티 목록

        예시:
            >>> all_users = repo.get_all()
        """
        pass

    @abstractmethod
    def add(self, entity: EntityType) -> None:
        """
        새 엔티티를 DB에 추가합니다.

        Args:
            entity (EntityType): 추가할 도메인 모델 인스턴스

        예시:
            >>> new_user = User(name="Alice")
            >>> repo.add(new_user)
        """
        pass

    @abstractmethod
    def update(self, entity: EntityType) -> None:
        """
        기존 엔티티를 수정합니다.

        Args:
            entity (EntityType): 수정할 도메인 모델 인스턴스

        예시:
            >>> user.name = "Alice Updated"
            >>> repo.update(user)
        """
        pass

    @abstractmethod
    def delete(self, entity: EntityType) -> None:
        """
        주어진 엔티티를 삭제합니다.

        Args:
            entity (EntityType): 삭제할 도메인 모델 인스턴스

        예시:
            >>> repo.delete(user)
        """
        pass

    @abstractmethod
    def execute_raw_query(self, query: str) -> Any:
        """
        Raw SQL 쿼리를 실행합니다.

        - 복잡한 조인, 집계, 커스텀 쿼리 수행에 사용
        - 반환값은 쿼리 목적에 따라 달라질 수 있음 (row list, scalar, etc)

        Args:
            query (str): 실행할 SQL 문자열

        Returns:
            Any: 쿼리 결과 (보통 list 또는 scalar 값)

        예시:
            >>> result = repo.execute_raw_query("SELECT COUNT(*) FROM users")
        """
        pass
