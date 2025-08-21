import os
from glob import glob
from datetime import datetime
from typing import Dict, NamedTuple, Optional, Union, List
from silx.io.h5py_utils import File

_DATA = {
    "/1.1/instrument/positioners_start/streamline_translation": [
        ("Hole", lambda dset: int(dset[()] + 0.5)),
    ],
    "/1.1/instrument/positioners_start/cncx": [
        ("Distance", lambda dset: f"{int(dset[()]/10 + 0.5)} cm"),
    ],
}

_SAMPLES = {
    "ee9b726c-d74e-11ec-8304-58a02398531d": "Empty clip with foil",
    "ee9b726b-d74e-11ec-81e1-58a02398531d": "SiO2 (SRM640c)",
    "ee9b726a-d74e-11ec-a8e1-58a02398531d": "LaB6 (SRM660c)",
    "ee9be771-d74e-11ec-8ca9-58a02398531d": "?",
    "ee9be773-d74e-11ec-86c2-58a02398531d": "CeO2",
    "ee9be78f-d74e-11ec-87bf-58a02398531d": "ZnO",
    "ee9be790-d74e-11ec-8e70-58a02398531d": "TiO2",
    "ee9be791-d74e-11ec-aa39-58a02398531d": "?",
    "ee9bc09b-d74e-11ec-9d7b-58a02398531d": "?",
    "ee9bc09c-d74e-11ec-b4f6-58a02398531d": "?",
}


def get_labels() -> List[str]:
    return ["Time", "Sample", "QR-code", "Dataset"] + [
        s for lst in _DATA.values() for s, _ in lst
    ]


class Dataset(NamedTuple):
    full_name: str
    file_time: str
    data: Dict[str, Union[str, float, int]]

    @property
    def hole(self) -> Optional[int]:
        return self.data["Hole"]

    @property
    def qrcode(self) -> str:
        return self.full_name.rpartition("_")[0]

    @property
    def sample(self) -> str:
        return _SAMPLES.get(self.qrcode, "")

    @property
    def ncols(self) -> int:
        return len(self.data) + 2

    def export(self, ncols: int) -> List[str]:
        row = [self.file_time, self.sample, self.qrcode, self.full_name]
        row += list(map(str, self.data.values()))
        row += [""] * max(ncols - len(row), 0)
        return row


def get_timerecord(raw_pattern: str) -> Dict[str, tuple]:
    files = glob(raw_pattern)
    trecord = dict()

    for filename in files:
        with File(filename, "r") as f:
            file_time = f.attrs.get("file_time")
            if not file_time:
                continue
            data = dict()
            for name, lst in _DATA.items():
                try:
                    dset = f[name]
                except KeyError:
                    continue
                for dest, func in lst:
                    data[dest] = func(dset)
            if len(data) != len(_DATA):
                continue
            skey = datetime.fromisoformat(file_time)
            dataset = Dataset(
                full_name=os.path.basename(os.path.dirname(filename)),
                file_time=file_time,
                data=data,
            )
            print(dataset)
            trecord[skey] = dataset
    return trecord


def save_timerecord(
    trecord: Dict[str, tuple], filename: str = "time_record.csv", sep: str = ","
) -> None:
    with open(filename, "w") as f:
        prev_hole = None
        ncols = max(dataset.ncols for dataset in trecord.values())
        print(sep.join(get_labels()), file=f)
        for _, dataset in sorted(trecord.items()):
            if prev_hole is None:
                prev_hole = dataset.hole
            if (dataset.hole - prev_hole) < 0:
                print(sep.join([" "] * ncols), file=f)
            print(sep.join(dataset.export(ncols)), file=f)
            prev_hole = dataset.hole


def make_timerecord(proposal: str, session: str, filename: str = "time_record.csv"):
    raw_pattern = f"/data/visitor/{proposal}/id31/{session}/raw/*/*/*.h5"
    trecord = get_timerecord(raw_pattern)
    if not trecord:
        raise RuntimeError("No streamline dataset found")
    save_timerecord(trecord, filename=filename)


if __name__ == "__main__":
    make_timerecord("im21", "20230227")
