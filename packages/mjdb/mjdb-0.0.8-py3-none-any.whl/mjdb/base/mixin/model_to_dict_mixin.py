class ModelToDictMixin:
    """
    SQLAlchemy 모델 인스턴스를 딕셔너리로 변환할 수 있는 Mixin 클래스입니다.

    이 Mixin은 `to_dict` 메서드를 제공하여, 모델 인스턴스의 필드를 딕셔너리 형태로 반환합니다.
    """

    def to_dict(self) -> dict:
        """
        SQLAlchemy ORM 객체를 dict로 변환합니다.

        self.__table__.columns 에 정의된 컬럼 이름들을 기준으로 값을 추출합니다.
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}