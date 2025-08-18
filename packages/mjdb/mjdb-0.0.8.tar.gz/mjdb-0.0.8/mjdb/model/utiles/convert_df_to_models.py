from typing import Type, TypeVar, List
import pandas as pd
from sqlalchemy.ext.declarative import DeclarativeMeta

# 모델 타입 변수: SQLAlchemy Declarative 클래스에 바인딩
M = TypeVar("M", bound=DeclarativeMeta)


def convert_df_to_models(
    df: pd.DataFrame,
    model: Type[M]
) -> List[M]:
    """
    주어진 pandas DataFrame을 SQLAlchemy 모델 인스턴스 리스트로 변환합니다.

    이 함수는 각 row를 dict로 변환한 뒤, 해당 딕셔너리를 언패킹하여
    모델 인스턴스를 생성합니다. 주로 DB 저장 전에 모델 변환 시 사용합니다.

    Args:
        df (pd.DataFrame): 변환 대상 DataFrame
        model (Type[M]): SQLAlchemy Declarative 모델 클래스

    Returns:
        List[M]: 모델 인스턴스로 구성된 리스트

    Example:
        >>> df = pd.DataFrame([...])
        >>> instances = convert_df_to_models(df, MyModel)
        >>> for instance in instances:
        ...     session.add(instance)
    """
    # DataFrame → dict 리스트로 변환
    records = df.to_dict(orient="records")

    instances: List[M] = []

    for record in records:
        # 특정 필드 전처리 예시: base_dt가 존재하고 결측치가 아니면 변환
        if "base_dt" in record and not pd.isna(record["base_dt"]):
            record["base_dt"] = pd.to_datetime(record["base_dt"]).date()

        # dict를 모델 인스턴스로 변환
        instance = model(**record)
        instances.append(instance)

    return instances
