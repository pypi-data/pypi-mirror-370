import typing
from collections import Counter
from pathlib import Path

from construct import Struct
from ....private_eye.tools.heidelberg.construct.structs import HeidelbergFileStruct


def _id_str(val: int) -> str:
    return str(None if val == -1 else val)


def _file_key(header: Struct) -> str:
    parts = [f"0x{header.type:x}"] + [
        _id_str(i) for i in [header.ids.patient, header.ids.exam, header.ids.series, header.ids.image, header.ids.index]
    ]
    return "-".join(parts)


def deconstruct(file_path: str, output_path: str, series_id: int) -> None:
    print(f"Deconstructing Heidelberg file at {file_path} into segments")
    file_data = HeidelbergFileStruct.parse_file(file_path)

    output_folder = Path(output_path)
    output_folder.mkdir(exist_ok=True)

    key_counter: typing.Counter[str] = Counter()
    total = 0
    for header, chunk_data in zip(file_data.chunk_headers, file_data.chunks):
        if series_id > -1 and series_id != header.ids.series and header.ids.series > -1:
            continue

        key = _file_key(header)
        file_name = f"{key}-{key_counter[key]}.dat"
        output_file = output_folder / file_name

        with output_file.open("wb") as f:
            f.write(chunk_data)

        total += 1
        key_counter[key] += 1
    print(f"File deconstructed. {total}/{file_data.chunk_count} segments saved to {output_path}")
