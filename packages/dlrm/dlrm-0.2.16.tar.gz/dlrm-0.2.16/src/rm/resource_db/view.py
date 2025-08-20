from dataclasses import dataclass
from functools import cached_property
from typing import Dict, Generic, TypeVar

from .db import ID, NAME, ResourceDB
import pandas as pd

RESOURCE_DB = TypeVar('RESOURCE_DB', bound=ResourceDB)

@dataclass
class DBView(Generic[RESOURCE_DB]):
    db:RESOURCE_DB

    # @cached_property
    @property
    def table(self)->pd.DataFrame:
        id_tokens_dict:Dict[ID, list[NAME]] = {k: v.split("/") for k, v in self.db.dir_db.id_name_dict.items()}
        max_len = max([len(v) for v in id_tokens_dict.values()], default=0)

        for k, v in id_tokens_dict.items():
            for i in range(max_len-len(v)):
                v.append("")
        
        df = pd.DataFrame(id_tokens_dict).T.reset_index()
        df.rename(columns={"index": "id"}, inplace=True)

        return df