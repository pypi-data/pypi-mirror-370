from dataclasses import dataclass, field
from mjdb.session.types.session_config import SessionConfig
from mjdb.session.types.engine_config import EngineConfig


@dataclass(frozen=True)
class SessionContext:
    """
    데이터베이스 연결과 세션 생성을 위한 구성 정보를 담고 있는 컨텍스트 클래스입니다.

    이 클래스는 SQLAlchemy를 사용하여 데이터베이스에 접근할 때 필요한 설정 값을 하나로 묶어서
    관리하기 위한 목적이며, 주로 엔진 설정과 세션 동작 방식을 함께 정의합니다.

    Attributes:
        db_url (str):
            데이터베이스 연결 문자열(URL)입니다.
            예: "sqlite:///example.db", "mysql+pymysql://user:pass@host/dbname" 등

        engine_config (EngineConfig):
            SQLAlchemy의 Engine 생성 시 사용될 엔진 구성 정보입니다.
            커넥션 풀 크기, 재사용 주기, 로그 출력 등 엔진 레벨의 세부 옵션을 포함합니다.
            기본값은 `EngineConfig()`이며, 인스턴스를 명시적으로 전달하지 않으면 기본 설정으로 사용됩니다.

        session_config (SessionConfig):
            SQLAlchemy 세션(Session)의 동작 방식에 대한 구성입니다.
            자동 커밋 여부, 자동 flush 여부, 커밋 후 객체 만료 여부 등 세션 관련 동작을 정의합니다.
            기본값은 `SessionConfig()`이며, 인스턴스를 명시적으로 전달하지 않으면 기본 설정으로 사용됩니다.
    """

    db_url: str  # 데이터베이스 연결 문자열 (예: sqlite, mysql 등)

    engine_config: EngineConfig = field(default_factory=EngineConfig)
    # 엔진 설정: 커넥션 풀, 재활용 시간, ping 여부 등 설정 포함
    # default_factory를 사용하여 EngineConfig의 기본 인스턴스를 생성

    session_config: SessionConfig = field(default_factory=SessionConfig)
    # 세션 설정: autocommit, autoflush, expire_on_commit 등의 세션 동작 방식 설정
    # default_factory를 사용하여 SessionConfig의 기본 인스턴스를 생성


if __name__ == "__main__":
    # Example usage
    context = SessionContext(
        db_url="sqlite:///example.db",  # SQLite 파일 기반 DB 사용
        engine_config=EngineConfig(pool_size=5, max_overflow=10),  # 커넥션 풀 설정 커스터마이징
        session_config=SessionConfig(autocommit=True, autoflush=False)  # 세션 동작 설정
    )
    print(context)
