from sqlalchemy.orm import declarative_base
from mjdb.model.abstract.abstract_model import AbstractModel


# ------------------------------------------------------------------------------
# BaseModel: SQLAlchemy ORM 모델의 공통 부모 클래스 선언
# ------------------------------------------------------------------------------

# SQLAlchemy의 Declarative 시스템을 통해 모델 클래스를 정의하기 위해 기본이 되는 클래스입니다.
# AbstractModel을 기반으로 하여 다음과 같은 기능이 포함된 ORM 모델을 생성합니다:

# - SQLAlchemy 모델 기능: __tablename__, Column(), PrimaryKey 등 DB 테이블 정의
# - AbstractModel 믹스인 기능:
#     - to_dict(): 모델 인스턴스를 dict로 직렬화
#     - from_dataframe(): DataFrame → 모델 변환 지원
#     - __repr__(): 속성 보기 편한 출력
#     - LoggingMixin: self.logger 지원
#     - AttributePrinterMixin: 디버깅을 위한 속성 출력

# ⚠️ 중요한 포인트:
# BaseModel을 통해 정의된 모든 모델 클래스는 SQLAlchemy ORM 모델이면서 동시에
# AbstractModel에서 제공하는 유틸리티 기능을 **자동으로 상속**받습니다.

# ✅ 사용 예:
#     class User(BaseModel):
#         __tablename__ = "users"
#         id = Column(Integer, primary_key=True)
#         name = Column(String)

BaseModel = declarative_base(cls=AbstractModel)