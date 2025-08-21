from contextlib import ExitStack, contextmanager
from pathlib import Path, PurePath
from typing import BinaryIO, Generator, List, Optional, Sequence, Type, Union, cast

from ..private_eye import ParserOptions
from ..private_eye.common.image_parser import ImageParser
from ..private_eye.consts import InputFile, InputFileHandle, RequiresFiles, SectionName
from ..private_eye.data import ParserResults
from ..private_eye.external.external_pb2 import ExternalData
from ..private_eye.utils.binary import peek
from ..private_eye.utils.external import protobuf_proxy, read_data_from_file
from ..private_eye.utils.modules import load_from_module

# DICOM files may legally start with 128 bytes of zeros
ZERO_BYTE_CHECK_LENGTH = 256

_InputType = Union[InputFile, PurePath, str]

parsers = {
    "topcon": "bitfount._vendor.private_eye.topcon.parser.TopconParser",
    "heidelberg": "bitfount._vendor.private_eye.heidelberg.HeidelbergParser",
    "heidelberg-e2e": "bitfount._vendor.private_eye.heidelberg.HeidelbergE2EParser",
    "optos": "bitfount._vendor.private_eye.optos.OptosParser",
    "zeiss": "bitfount._vendor.private_eye.zeiss.parser.ZeissParser",
    "imagenet2000": "bitfount._vendor.private_eye.imagenet2000.imagenet2k_parser.TopconImagenet2000Parser",
    "custom": "bitfount._vendor.private_eye.custom.custom_parser.CustomParser",
}


@contextmanager
def parse(
    parser_name: str,
    input_files: Sequence[_InputType],
    options: ParserOptions = ParserOptions(),
    external_data: ExternalData = ExternalData(),
) -> Generator[ImageParser, None, None]:
    """Given a file path, returns a parser object which can be used to
    extract some or all of the data about a given image file.

    As the given images files are likely to be quite large, we have the option
    of doing a full or partial scan using the `full_parse` parameter.

    * If `True`, all of the file will be scanned, regardless of the requested sections. This is useful for debugging.
    * If `False`, only the sections requested by e.g. :attr:`private_eye.common.ImageParser.read_sections()` will be
      scanned.

    :param parser_name: The parser which should be used
    :param input_files: The image files to open. Can be a list of path strings, Path objects or InputFile objects
    :param options: Options controlling how the parser operates
    :param external_data: Any external data required to parse the files
    :return: An instance of a subclass of :class:`private_eye.common.ImageParser`
    :raises RequiresFiles: If more files are required to parse this image.
    :raises NoImageData: If the files are valid, but only contain ancillary data.
    """
    if len(input_files) == 0:
        raise ValueError("Unable to parse empty list of files")

    parser_cls = _get_parser_cls(parser_name)
    input_file_objects: List[InputFile] = [_to_input_file(f) for f in input_files]

    with ExitStack() as exit_stack:
        input_file_handles: List[InputFileHandle] = [
            InputFileHandle(
                file_path=input_file.file_path,
                original_filepath=input_file.original_filepath,
                handle=cast(BinaryIO, exit_stack.enter_context(input_file.file_path.open("rb"))),
            )
            for input_file in input_file_objects
        ]
        _validate_files(parser_cls, input_file_handles, options)
        wrapped_external_data = protobuf_proxy(external_data)
        yield parser_cls(input_file_handles, options=options, external_data=wrapped_external_data)


def get_extra_files(
    parser_name: str, input_file: InputFile, options: ParserOptions = ParserOptions()
) -> List[PurePath]:
    parser_cls = _get_parser_cls(parser_name)
    with input_file.file_path.open("rb") as file:
        input_file_handle = InputFileHandle(
            file_path=input_file.file_path,
            original_filepath=input_file.original_filepath,
            handle=cast(BinaryIO, file),
        )

        return parser_cls.get_extra_files(input_file_handle, options)


def read_all_from_local_file(
    parser: str,
    input_file: _InputType,
    options: ParserOptions = ParserOptions(),
    external_data_path: Optional[Path] = None,
) -> ParserResults:
    external_data = read_data_from_file(external_data_path) if external_data_path else ExternalData()
    try:
        with parse(parser, [input_file], options, external_data) as image:
            return image.read_all_sections()
    except RequiresFiles as err:
        with parse(parser, [input_file] + list(map(Path, err.files)), options, external_data) as image:
            return image.read_all_sections()


def read_sections_from_local_file(
    parser: str,
    input_file: Path,
    section_names: List[SectionName],
    options: ParserOptions = ParserOptions(),
    external_data_path: Optional[Path] = None,
) -> ParserResults:
    external_data = read_data_from_file(external_data_path) if external_data_path else ExternalData()
    try:
        with parse(parser, [input_file], options, external_data) as image:
            return image.read_sections(*section_names)
    except RequiresFiles as err:
        with parse(parser, [input_file] + list(map(Path, err.files)), options, external_data) as image:
            return image.read_sections(*section_names)


def _to_input_file(input_or_path: _InputType) -> InputFile:
    if isinstance(input_or_path, (str, Path)):
        return InputFile.local_file(input_or_path)
    if isinstance(input_or_path, InputFile):
        return input_or_path
    raise ValueError(f"Unknown input type: {input_or_path.__class__}")


def _get_parser_cls(parser_name: str) -> Type[ImageParser]:
    try:
        full_class_path = parsers[parser_name]
    except KeyError as error:
        raise ValueError(f"Unknown parser: {parser_name}") from error
    else:
        module_path, class_name = full_class_path.rsplit(sep=".", maxsplit=1)
        return cast(Type[ImageParser], load_from_module(module_path, class_name))


def _validate_files(parser_cls: Type[ImageParser], input_files: List[InputFileHandle], options: ParserOptions) -> None:
    """
    On rare occasions, Topcon doesn't save files properly and they end up filled with zeroes.
    This has also been observed in Heidelberg .pdb files.
    Flag this as a specific error case.
    """
    for input_file in input_files:
        fs = input_file.handle
        fs.seek(0)
        with peek(fs, ZERO_BYTE_CHECK_LENGTH) as data:
            if data == (b"\x00" * ZERO_BYTE_CHECK_LENGTH):
                raise ValueError(f"File {input_file} starts with {ZERO_BYTE_CHECK_LENGTH} zeroes.")
        if not parser_cls.matches_file(input_file, options):
            raise ValueError(f"File {input_file} is invalid")
