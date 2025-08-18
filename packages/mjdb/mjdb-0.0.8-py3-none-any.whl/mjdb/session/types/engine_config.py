from dataclasses import dataclass


@dataclass(frozen=True)
class EngineConfig:
    """
    데이터베이스 연결을 위한 SQLAlchemy 엔진 설정을 정의하는 불변(immutable) 구성 클래스입니다.

    Attributes:
        pool_size (int):
            데이터베이스 커넥션 풀의 기본 연결 수입니다.
            동시에 유지할 수 있는 최소한의 커넥션 개수를 의미하며, 기본값은 10입니다.

        max_overflow (int):
            커넥션 풀 외에 추가로 허용할 수 있는 커넥션 수입니다.
            예를 들어 pool_size가 10이고 max_overflow가 5라면, 최대 15개의 커넥션을 동시에 생성할 수 있습니다.
            기본값은 5입니다.

        pool_recycle (int):
            연결이 재사용되기 전까지의 최대 시간(초 단위)입니다.
            MySQL 등에서 "MySQL server has gone away" 오류를 방지하기 위해 사용됩니다.
            기본값은 1800초 (30분)입니다.

        pool_pre_ping (bool):
            커넥션을 풀에서 꺼내기 전에 ping을 통해 유효성을 검사할지 여부를 결정합니다.
            True일 경우, 비활성화된(dead) 커넥션을 자동으로 감지하고 재연결을 시도합니다.
            기본값은 True입니다.

        echo (bool):
            SQLAlchemy의 SQL 실행 로그를 출력할지 여부를 설정합니다.
            True로 설정하면 디버깅 시 SQL 로그를 확인할 수 있습니다.
            기본값은 False입니다.
    """
    pool_size: int = 10  # 유지할 커넥션 풀의 기본 커넥션 수 (기본값: 10)
    max_overflow: int = 5  # 풀 외에 허용되는 추가 커넥션 수 (기본값: 5)
    pool_recycle: int = 1800  # 커넥션 재활용 주기 (초 단위, 기본값: 1800초 = 30분)
    pool_pre_ping: bool = True  # 커넥션 유효성 검사 여부 (기본값: True)
    echo: bool = False  # SQL 실행 로그 출력 여부 (기본값: False)

if __name__ == "__main__":
    # Example usage
    config = EngineConfig(
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=True
    )
    print(config)