from construct import (
    Array,
    Bytes,
    Checksum,
    Computed,
    Const,
    FocusedSeq,
    If,
    IfThenElse,
    Int16sl,
    Int16ul,
    Int32sl,
    Int32ul,
    PaddedString,
    Padding,
    Pointer,
    RepeatUntil,
    RestreamData,
    Seek,
    Struct,
    Tell,
    len_,
    obj_,
    this,
)
from .....private_eye.tools.heidelberg.construct.validators import ChunkPropsValidator


def SignatureString(value: str) -> Const:
    return Const(value, PaddedString(12, "ascii"))


def ConstVersion() -> Const:
    return Const(100, Int32ul)


# fmt: off
IdStruct = Struct(
    "patient" / Int32sl,
    "exam" / Int32sl,
    "series" / Int32sl,
    "image" / Int32sl,
    "index" / Int16sl,
    "mystery" / Int16ul,
)

FileHeaderStruct = Struct(
    "signature" / SignatureString("CMDb"),
    "version" / ConstVersion(),
    "ids" / IdStruct,
)

MainDirectoryStruct = Struct(
    "signature" / SignatureString("MDbMDir"),
    "version" / ConstVersion(),
    "ids" / IdStruct,
    "num_entries" / Int32ul,
    "current" / Int32ul,
    "previous" / Int32ul,
    "mystery" / Int32ul,
)

ChunkHeaderStruct = Struct(
    "header_pos" / Int32ul,
    "start_raw" / Bytes(4),  # Small chunks can hold this data
    "start" / RestreamData(this.start_raw, Int32ul),
    "size" / Int32ul,
    "mystery_1" / Int32ul,
    "ids" / IdStruct,
    "type" / Int32ul,
    "checksum" / Checksum(
        Int32ul,
        lambda data: (
            0x87654321
            + data.header_pos
            + data.start
            + data.size
            + data.mystery_1
            + data.ids.patient
            + data.ids.exam
            + data.ids.series
            + data.ids.image
            + data.ids.index
            + data.type
        ),
        this,
    ),
)

DirectoryStruct = Struct(
    "signature" / SignatureString("MDbDir"),
    "version" / ConstVersion(),
    "ids" / IdStruct,
    "num_entries" / Int32ul,
    "current" / Int32ul,
    "previous" / Int32ul,
    "mystery" / Int32ul,
    "entries" / ChunkHeaderStruct[this.num_entries],
)

ChunkStruct = Struct(
    "signature" / SignatureString("MDbData"),
    "offset" / Tell,
    # Skip this field until we know what the chunk payload is
    "payload_checksum" / Padding(4),
    "header_pos" / Int32ul,
    "pos" / Int32ul,
    "size" / Int32ul,
    "unknown_1" / Int32ul,
    "ids" / IdStruct,
    "type" / Int32ul,
    "checksum" / Checksum(Int32ul, lambda data: 0x8765431C + data, this.header_pos),
    "data" / Bytes(this.size),
    # Go back and populate/verify the payload_checksum
    "payload_checksum" / Pointer(
        this.offset,
        Checksum(Int32ul, lambda data: 0x12435687 + sum(data), this.data)
    )
)

HeidelbergFileStruct = Struct(
    "header" / FileHeaderStruct,
    "main_dir" / MainDirectoryStruct,
    "chunk_headers" / Computed([]),
    # We only care about the chunk headers for the directory tree, so pull those out into a flat list,
    # discarding the directory structures themselves
    Pointer(
        # Start at the main_dir.current
        this.main_dir.current,
        RepeatUntil(
            obj_.previous == 0,
            # All directory instances have 512 entries, not all of which will be populated.
            # Hence, add only the headers which have a size to the headers list.
            FocusedSeq(
                "dir",
                "dir" / DirectoryStruct,
                # Go to the location of the next DirectoryStruct if available
                If(this.dir.previous > 0, Seek(this.dir.previous)),
            ) * (lambda obj, ctx: ctx.chunk_headers.extend(entry for entry in obj.entries if entry.size > 0)),
            discard=True,
        ),
    ),
    "chunk_count" / Computed(len_(this.chunk_headers)),
    "chunks" / Array(
        this.chunk_count,
        FocusedSeq(
            "chunk_data",
            # The header is used to parse the chunk, so temporarily add it to the context
            "header" / Computed(lambda ctx: ctx._.chunk_headers[ctx._index]),
            "chunk_data" / IfThenElse(
                this.header.size <= 4,
                Computed(this.header.start_raw),  # Small segments contain all data in the 'start' variable
                FocusedSeq(
                    "data",
                    Seek(this._.header.start),
                    "chunk" / ChunkPropsValidator(ChunkStruct),
                    "data" / Computed(this.chunk.data),
                ),
            ),
        ),
    ),
)
# fmt: on
