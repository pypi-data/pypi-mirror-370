from typing import TypeVar, Type, List
from pandas import DataFrame, to_datetime
import pandas as pd

# TModel은 FromDataFrameMixin을 상속받는 클래스 타입으로 제한됩니다.
TModel = TypeVar("TModel", bound="FromDataFrameMixin")


class FromDataFrameMixin:
    """
    pandas DataFrame으로부터 SQLAlchemy 모델 인스턴스를 생성할 수 있도록 도와주는 Mixin 클래스입니다.

    이 Mixin은 클래스 메서드 `from_df`를 제공하며,
    DataFrame의 각 row를 딕셔너리로 변환한 후, 해당 값을 사용하여 SQLAlchemy 모델 인스턴스를 생성합니다.
    """

    @classmethod
    def from_df(cls: Type[TModel], df: DataFrame) -> List[TModel]:
        """
        pandas DataFrame을 SQLAlchemy 모델 인스턴스 리스트로 변환합니다.

        Args:
            df (DataFrame): 변환하고자 하는 pandas DataFrame

        Returns:
            List[TModel]: SQLAlchemy 모델 인스턴스 리스트

        작동 방식:
            1. DataFrame을 record(행) 단위의 dict 리스트로 변환
            2. 각 record를 unpack하여 SQLAlchemy 모델 인스턴스를 생성
            3. 'base_dt' 컬럼이 존재할 경우, 날짜형으로 변환 (datetime.date 객체로 변환됨)

        예시:
            >>> df = pd.DataFrame([...])
            >>> instances = MyModel.from_df(df)
        """
        # DataFrame을 record(딕셔너리 리스트)로 변환
        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient="records")
        instances = []

        for rec in records:
            # base_dt 컬럼이 있을 경우 datetime 형식으로 파싱 후 날짜 객체로 변환
            if "base_dt" in rec:
                rec["base_dt"] = to_datetime(rec["base_dt"]).date()

            # 언팩을 통해 SQLAlchemy 모델 인스턴스를 생성
            instances.append(cls(**rec))

        return instances