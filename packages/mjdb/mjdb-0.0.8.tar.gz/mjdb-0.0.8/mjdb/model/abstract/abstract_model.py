from mjdb.base.mixin.from_dataframe_mixin import FromDataFrameMixin
from mjdb.base.mixin.model_to_dict_mixin import ModelToDictMixin
from mjkit.mixin import LoggingMixin, AttributePrinterMixin

import logging


class AbstractModel(
    FromDataFrameMixin,
    ModelToDictMixin,
    LoggingMixin,
    AttributePrinterMixin
):
    """
    AbstractModel

    SQLAlchemy 모델을 위한 공통 기능들을 모아 제공하는 추상 기반 클래스입니다.
    이 클래스는 아래와 같은 mixin 기반 기능을 상속하여 제공합니다:

    1. FromDataFrameMixin
        - pandas DataFrame → SQLAlchemy 모델 인스턴스로 변환하는 기능 제공
        - ex) `MyModel.from_dataframe(df)` 호출 가능

    2. ModelToDictMixin
        - SQLAlchemy 모델 인스턴스를 dict로 변환 (serialize 가능)
        - ex) `my_model.to_dict()` 호출 가능

    3. LoggingMixin
        - 클래스 내부에서 self.logger를 사용한 로깅 기능 지원
        - 로깅 레벨(logging.INFO 등)을 지정 가능

    4. AttributePrinterMixin
        - 인스턴스 속성을 보기 쉽게 문자열로 출력할 수 있는 기능 제공
        - __repr__ 또는 print 시 디버깅용으로 유용

    이 추상 클래스는 도메인 모델에서 상속받아 공통 기능을 재사용하기 위한 목적입니다.
    DB에 실제 매핑되는 SQLAlchemy Declarative 모델에서 이 클래스를 상속하여 사용하세요.

    Example:
        >>> class MyStockModel(AbstractModel, Base):
        ...     __tablename__ = "stock"
        ...     id = Column(Integer, primary_key=True)
        ...     ticker = Column(String(10))
        ...
        >>> instance = MyStockModel()
        >>> print(instance.to_dict())
        >>> print(instance)

    Attributes:
        logger (logging.Logger): 내부 로깅용 logger 객체
    """

    def __init__(self, log_level: int = logging.INFO):
        """
        AbstractModel 초기화 메서드

        Args:
            log_level (int, optional): 로깅 레벨 설정 (default: logging.INFO)

        내부적으로 LoggingMixin과 AttributePrinterMixin의 초기화를 담당합니다.
        로거는 self.logger로 접근할 수 있으며, mixin이 자동으로 이름 기반 로거를 생성합니다.
        """
        super().__init__(level=log_level)
