from typing import List, Literal, Optional
from datetime import datetime

from redis import Redis
from redis_om import JsonModel
from redis_om.model.model import NotFoundError

from .compatibility import Field, get_redis_db_url
from ..persistent.ndarray import PersistentNdArray


XrpdFieldName = Literal["radial", "azimuthal", "intensity"]


class XrpdPlotInfo(JsonModel, frozen=True):
    scan_name: str
    lima_name: str
    radial_label: str
    azim_label: Optional[str]
    hdf5_url: Optional[str]
    timestamp: datetime = Field(default_factory=datetime.now)
    field_names: List[XrpdFieldName]

    @property
    def legend(self) -> str:
        return f"{self.scan_name} ({self.lima_name})"

    def _get_data_key(self, field_name: XrpdFieldName) -> str:
        return f"{self.scan_name}:{self.lima_name}:plot_data:{field_name}"

    def get_data_array(self, field_name: XrpdFieldName):
        if field_name not in self.field_names:
            raise KeyError(f"No field {field_name} in this PlotInfo")
        return PersistentNdArray(self._get_data_key(field_name))

    def delete_data_arrays(self):
        for field_name in self.field_names:
            PersistentNdArray(self._get_data_key(field_name)).remove()

    @classmethod
    def get(cls, pk):
        try:
            return super().get(pk)
        except NotFoundError:
            # Reraise NotFoundError to get more info in the error message
            raise KeyError(f"PlotInfo not found at {pk}@{cls._meta.database}")

    class Meta:
        database = Redis.from_url(get_redis_db_url())
