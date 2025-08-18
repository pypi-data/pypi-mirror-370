from typing import Type, TypeVar, List, Optional, Dict, Any
import pandas as pd
from sqlalchemy.ext.declarative import DeclarativeMeta

# 모델 타입 변수: SQLAlchemy Declarative 클래스에 바인딩
M = TypeVar("M", bound=DeclarativeMeta)


def _df_to_dict_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    DataFrame을 dict 레코드 리스트로 변환합니다.

    Args:
        df (pd.DataFrame): 입력 데이터프레임

    Returns:
        List[Dict[str, Any]]: 각 row가 dict인 리스트
    """
    return df.to_dict(orient="records")


def _convert_date_fields(record: Dict[str, Any], date_fields: Optional[List[str]]) -> None:
    """
    지정된 필드를 datetime.date 형식으로 변환합니다.

    Args:
        record (Dict[str, Any]): 변환 대상 딕셔너리
        date_fields (Optional[List[str]]): 변환할 필드 이름 목록

    Notes:
        해당 필드가 존재하고, 결측치가 아니면 변환 수행
    """
    if not date_fields:
        return

    for field in date_fields:
        if field in record and not pd.isna(record[field]):
            record[field] = pd.to_datetime(record[field]).date()


def _validate_required_fields(
    record: Dict[str, Any],
    required_fields: Optional[List[str]],
    model: Type[M]
) -> None:
    """
    record에 필수 필드가 모두 존재하는지 확인합니다.

    Args:
        record (Dict[str, Any]): 필드 존재를 확인할 dict
        required_fields (Optional[List[str]]): 필수 필드 목록
        model (Type[M]): 검증 실패 시 오류 메시지에 사용될 모델명

    Raises:
        ValueError: 필수 필드가 누락된 경우
    """
    if not required_fields:
        return

    missing = [field for field in required_fields if field not in record]
    if missing:
        raise ValueError(f"{model.__name__} 레코드에 누락된 필드: {missing}")


def _create_model_instance(record: Dict[str, Any], model: Type[M]) -> M:
    """
    dict 데이터를 SQLAlchemy 모델 인스턴스로 변환합니다.

    Args:
        record (Dict[str, Any]): 모델 생성에 사용할 데이터
        model (Type[M]): SQLAlchemy 모델 클래스

    Returns:
        M: 생성된 모델 인스턴스
    """
    return model(**record)


def df_to_model_instances(
    df: pd.DataFrame,
    model: Type[M],
    date_fields: Optional[List[str]] = None,
    required_fields: Optional[List[str]] = None
) -> List[M]:
    """
    pandas DataFrame을 SQLAlchemy 모델 인스턴스 리스트로 변환합니다.

    각 row는 dict로 변환된 후, 날짜 필드가 있으면 변환되고,
    필수 필드 누락 여부가 확인된 뒤 모델 인스턴스로 변환됩니다.

    Args:
        df (pd.DataFrame): 변환 대상 DataFrame
        model (Type[M]): SQLAlchemy Declarative 모델 클래스
        date_fields (Optional[List[str]]): datetime.date로 변환할 필드 목록
        required_fields (Optional[List[str]]): 누락 여부를 확인할 필드 목록

    Returns:
        List[M]: 모델 인스턴스 리스트

    Raises:
        ValueError: 필수 필드가 누락된 경우
    """
    records = _df_to_dict_records(df)
    instances = []

    for record in records:
        _convert_date_fields(record, date_fields)
        _validate_required_fields(record, required_fields, model)
        instance = _create_model_instance(record, model)
        instances.append(instance)

    return instances
