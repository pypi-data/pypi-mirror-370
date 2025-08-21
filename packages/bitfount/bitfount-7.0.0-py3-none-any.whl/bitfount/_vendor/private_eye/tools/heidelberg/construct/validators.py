from construct import Container, Struct, Validator


class ChunkPropsValidator(Validator):
    """
    Validate that the IDs and type of the chunk match the header.
    Incoming objects should be ChunkStructs and we expect the context to have
    a ChunkHeaderStruct as a 'header' variable
    """

    def _validate(self, chunk: Struct, ctx: Container, path: str) -> bool:
        header = ctx._.header
        ids_attrs = (
            "patient",
            "exam",
            "series",
            "image",
            "index",
        )
        return chunk.type == header.type and all(getattr(chunk.ids, a) == getattr(header.ids, a) for a in ids_attrs)
