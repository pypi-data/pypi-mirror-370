from mjdb.session.base.base_session import BaseDbSession


class SQLAlchemyDbSession(BaseDbSession):
    """
    SQLAlchemyDbSession

    SQLAlchemy 기반의 데이터베이스 세션 관리 클래스입니다.
    `BaseDbSession`을 상속하여 DB 연결, 세션 생성, 커넥션 풀 설정 등 모든 핵심 기능을 그대로 사용합니다.

    이 클래스는 주로 아래의 용도로 사용됩니다:
        - 도메인 레벨에서 DB 세션을 추상화하고 사용자가 직접 SQLAlchemy 관련 코드를 작성하지 않도록 함
        - 세션 재시도 및 커넥션 안정성을 보장 (BaseDbSession의 retry 전략 상속)
        - SessionContext 객체를 주입받아 커넥션/세션 설정을 모듈화함으로써 확장성과 테스트 용이성 확보

    예시 사용법:
        >>> from mjdb.session.types import SessionContext, EngineConfig, SessionConfig
        >>> ctx = SessionContext(
        ...     db_url="mysql+pymysql://user:pw@localhost:3306/db",
        ...     engine_config=EngineConfig(pool_size=5),
        ...     session_config=SessionConfig(expire_on_commit=False)
        ... )
        >>> db_session = SQLAlchemyDbSession(context=ctx)
        >>> with db_session.get_session_context() as session:
        ...     result = session.execute(text("SELECT 1")).fetchall()

    상속 구성:
        - AbstractDbSession (interface 정의)
        - BaseDbSession (공통 로직 구현)
        - SQLAlchemyDbSession (SQLAlchemy 특화 구현, 필요한 경우 오버라이딩 가능)

    이 클래스는 기본적인 동작을 BaseDbSession에 위임하므로,
    필요 시 다음과 같은 방식으로 기능 확장이 가능합니다:
        - `_create_engine()` 오버라이딩 → 엔진 생성 시 추가 설정 삽입
        - `get_session()` 오버라이딩 → 트랜잭션 전략 변경
        - 로깅 레벨, 연결 확인 쿼리 등을 커스터마이징

    Attributes:
        context (SessionContext): DB URL, EngineConfig, SessionConfig를 포함하는 구성 객체
        logger (logging.Logger): LoggingMixin을 통해 상속된 로깅 인스턴스
    """
