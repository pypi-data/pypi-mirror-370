from dataclasses import dataclass

@dataclass(frozen=True)
class SessionConfig:
    """
    SQLAlchemy 세션(Session)의 동작 방식을 정의하는 구성 클래스입니다.
    이 설정은 데이터베이스와의 트랜잭션 처리, 자동 동기화, 커밋 후 상태 관리 등에 영향을 미칩니다.

    Attributes:
        autocommit (bool):
            세션이 자동으로 커밋(commit)할지를 결정합니다.
            - False일 경우, 명시적으로 `commit()`을 호출해야 데이터베이스에 반영됩니다.
            - True는 권장되지 않으며, 최신 SQLAlchemy에서는 deprecated 처리됨.
            기본값은 False입니다.

        autoflush (bool):
            세션에서 데이터베이스로의 자동 flush 여부를 설정합니다.
            - True이면 쿼리를 실행하기 전에 pending 상태의 변경사항이 자동으로 flush됩니다.
            - False이면 수동으로 flush()를 호출하거나 commit() 시 반영됩니다.
            기본값은 False입니다.

        expire_on_commit (bool):
            커밋 이후 세션에 남아 있는 객체의 상태를 만료시킬지를 설정합니다.
            - True이면 커밋 후 객체는 만료(expired)되어 다음 접근 시 자동으로 DB로부터 새로 로드됩니다.
            - False이면 커밋 후에도 객체 상태가 그대로 유지됩니다.
            기본값은 True입니다.
    """

    autocommit: bool = False        # 세션이 자동으로 commit 할지 여부 (기본값: False)
    autoflush: bool = False         # 쿼리 실행 전 자동으로 flush 할지 여부 (기본값: False)
    expire_on_commit: bool = True   # commit 후 객체 상태를 만료시킬지 여부 (기본값: True)
