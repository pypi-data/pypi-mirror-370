from typing import Optional

from pydantic import BaseModel, model_validator


class QueryConfig(BaseModel):
    use_exclude: bool = False
    n_records: int = 100
    dt_field: Optional[str] = None
    use_dask: bool = False
    as_dask: bool = False

    @model_validator(mode='after')
    def check_n_records(self):
        if self.n_records < 0:
            raise ValueError('Number of records must be non-negative')
        return self
