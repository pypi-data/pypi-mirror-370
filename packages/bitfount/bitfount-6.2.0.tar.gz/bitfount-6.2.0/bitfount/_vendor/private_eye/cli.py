import functools
import logging
import os
import shutil
from pathlib import Path, PurePath
from typing import Any, List, Optional, Set

import attr
import click
from ..private_eye import parse
from ..private_eye.common.image_parser import ImageParser
from ..private_eye.consts import (
    EntireFileOutputFormat,
    IndividualImageOutputFormat,
    OutputFormat,
    RequiresFiles,
    SectionName,
)
from ..private_eye.data import ImageProcessingOptions, ParserOptions, ParserResults
from ..private_eye.external.external_pb2 import ExternalData
from ..private_eye.output import output_all_data, validate_pepper
from ..private_eye.parse import parsers
from ..private_eye.utils.external import read_data_from_file
from ..private_eye.version import version

logger = logging.getLogger(__name__)


class PathlibPath(click.Path):
    def convert(self, value: str, param: Optional[click.Parameter], ctx: Optional[click.Context]) -> Any:
        path_str = super().convert(value, param, ctx)
        return Path(path_str)


class ExternalDataType(PathlibPath):
    name = "external data path"

    def __init__(self, **kwargs: Any) -> None:
        kwargs["dir_okay"] = False
        super().__init__(**kwargs)

    def convert(self, value: str, param: Optional[click.Parameter], ctx: Optional[click.Context]) -> Any:
        path = super().convert(value, param, ctx)
        return read_data_from_file(path)


_default_options = [
    click.argument("image_path", type=PathlibPath(exists=True, dir_okay=False)),
    click.option("-v", "--verbose", is_flag=True),
    click.option(
        "-o",
        "--output-folder",
        required=False,
        type=PathlibPath(dir_okay=True, file_okay=False, writable=True),
        help="Path of output folder",
    ),
    click.option(
        "-m",
        "--output-format",
        "output_formats",
        multiple=True,
        type=click.Choice([e.value for it in (EntireFileOutputFormat, IndividualImageOutputFormat) for e in it]),
        default=[EntireFileOutputFormat.METADATA_JSON.value, IndividualImageOutputFormat.RAW_IMAGES.value],
        help="Output format, e.g. DICOM (defaults to JSON metadata and raw images)",
    ),
    click.option(
        "-i",
        "--include",
        "sections",
        multiple=True,
        type=click.Choice([e.value for e in SectionName]),
        help="Sections to include in the output (defaults to all sections)",
        default=[e.value for e in SectionName],
    ),
    click.option("-d", "--delete-folders", is_flag=True, help="Delete output folders before writing to them"),
    # Options from this point on should be added to ParserOptions
    click.option("--all", "full_parse", is_flag=True, help="(Advanced) Read the entire file when parsing"),
    click.option(
        "--skip-image-data",
        is_flag=True,
        help="Do not read any raw image data. Useful when only image metadata is required.",
    ),
    click.option(
        "--on-string-decode-error",
        type=click.Choice(["strict", "ignore", "replace"]),
        default="strict",
        help="(Advanced) Alter behaviour when failing to decode a string. "
        "Be careful with this, you can mask all sorts of problems!",
    ),
    click.option(
        "--output-sensitive-data", is_flag=True, help="(Advanced) Leave sensitive data in output image files."
    ),
    click.option(
        "--pepper",
        help="At least 32 random characters used as part of the anonymisation process for dicom uid's."
        "Should be kept secret.",
        callback=validate_pepper,
    ),
]


_extra_cli_options = {
    "heidelberg": [
        click.option(
            "--external-data-path",
            "external_data",
            type=ExternalDataType(exists=True),
            help="(Advanced) Path to a file containing external data in Protobuf format",
        ),
        click.option(
            "--skip-intensity-adjust",
            "heidelberg_skip_intensity_adjust",
            is_flag=True,
            help="(Advanced) When parsing heidelberg images, don't perform any automatic "
            "intensity scaling on the bscans. In particular this means the returned image will be 16-bit.",
        ),
        click.option(
            "--skip-shape-adjust",
            "heidelberg_skip_shape_adjust",
            is_flag=True,
            help="(Advanced) When parsing heidelberg images, don't perform any transformation on the bscans.",
        ),
        click.option(
            "--skip-pdb",
            "heidelberg_skip_pdb",
            is_flag=True,
            help="(Advanced) When parsing Heidelberg files, do not parse pdb files. "
            "Add this flag when dealing with corrupt .pdb files which consist of all 0s. "
            "Note: This will override requesting the patient metadata section.",
        ),
    ],
    "heidelberg-e2e": [
        click.option(
            "--skip-intensity-adjust",
            "heidelberg_skip_intensity_adjust",
            is_flag=True,
            help="(Advanced) When parsing heidelberg images, don't perform any automatic "
            "intensity scaling on the bscans. In particular this means the returned image will be 16-bit.",
        ),
        click.option(
            "--skip-shape-adjust",
            "heidelberg_skip_shape_adjust",
            is_flag=True,
            help="(Advanced) When parsing heidelberg images, don't perform any transformation on the bscans.",
        ),
    ],
    "topcon": [
        click.option(
            "--no-clip-bscan",
            "topcon_no_clip_bscan",
            is_flag=True,
            help="(Advanced) When parsing topcon images, don't perform any clipping on the bscans",
        ),
        click.option(
            "--encoding", "topcon_encoding", help="(Advanced) Encoding used when parsing Topcon strings", required=False
        ),
    ],
    "optos": [
        click.option(
            "--external-data-path",
            "external_data",
            type=ExternalDataType(exists=True),
            help="(Advanced) Path to a file containing external data in Protobuf format",
        ),
    ],
    "zeiss": [
        click.option(
            "--no-censor-annotations",
            "zeiss_no_censor_annotations",
            is_flag=True,
            help="(Advanced) Do not censor dates on dated images",
        ),
    ],
    "imagenet2000": [
        click.option(
            "--external-data-path",
            "external_data",
            type=ExternalDataType(exists=True),
            help="(Advanced) Path to a file containing external data in Protobuf format",
        ),
    ],
    "custom": [
        click.option(
            "--external-data-path",
            "external_data",
            type=ExternalDataType(exists=True),
            help="(Advanced) Path to a file containing external data in Protobuf format",
        ),
    ],
}


@attr.s(auto_attribs=True, slots=True)
class PrivateEyeContext:
    parser: str
    image_path: PurePath
    sections: List[str]
    output_folder: Optional[Path]
    verbose: bool
    output_sensitive_data: bool
    full_parse: bool
    output_formats: List[str]
    delete_folders: bool
    skip_image_data: bool
    on_string_decode_error: str
    pepper: str
    external_data: Optional[ExternalData] = None
    topcon_no_clip_bscan: bool = False
    topcon_encoding: Optional[str] = None
    heidelberg_skip_shape_adjust: bool = False
    heidelberg_skip_intensity_adjust: bool = False
    heidelberg_skip_pdb: bool = False
    zeiss_no_censor_annotations: bool = False

    def get_parser_options(self) -> ParserOptions:
        return ParserOptions(
            full_parse=self.full_parse,
            skip_image_data=self.skip_image_data,
            on_string_decode_error=self.on_string_decode_error,
            topcon_encoding=self.topcon_encoding or "Cp1252",
            heidelberg_skip_pdb=self.heidelberg_skip_pdb,
            image_processing_options=[
                ImageProcessingOptions(
                    heidelberg_skip_shape_adjust=self.heidelberg_skip_shape_adjust,
                    heidelberg_skip_intensity_adjust=self.heidelberg_skip_intensity_adjust,
                    topcon_no_clip_bscan=self.topcon_no_clip_bscan,
                    zeiss_no_censor_annotations=self.zeiss_no_censor_annotations,
                )
            ],
        )


@click.group("pe-convert")
@click.version_option(version=version)
def main() -> None:
    pass


def _output(parser: str, **kwargs: Any) -> None:
    obj = PrivateEyeContext(parser=parser, **kwargs)

    click.echo(f"Starting parse of {click.format_filename(str(obj.image_path))}")
    data = _get_result(obj)
    click.echo("Parse complete")

    input_file_stem = obj.image_path.stem
    if obj.output_folder:
        output_folder = obj.output_folder.resolve()
    else:
        output_folder = Path(os.getcwd()) / input_file_stem

    output_formats: Set[OutputFormat] = set()
    for format_ in obj.output_formats:
        try:
            output_formats.add(IndividualImageOutputFormat(format_))
        except ValueError:
            output_formats.add(EntireFileOutputFormat(format_))

    requires_output_directory = not output_formats.issubset(
        {EntireFileOutputFormat.METADATA_CONSOLE, EntireFileOutputFormat.NONE}
    )
    if requires_output_directory:
        if output_folder.is_dir():
            if obj.delete_folders:
                click.echo(f"This folder is being deleted: {output_folder}")
                shutil.rmtree(str(output_folder))
            else:
                raise Exception(f"User disallowed folder deletion for folder: {output_folder}")

        output_folder.mkdir(parents=True)

    click.echo("Starting output")
    multiple_files = len(data.results) > 1
    for index, result in enumerate(data.results):
        output_all_data(
            output_formats=output_formats,
            output_directory=output_folder,
            filename_prefix=f"scan_{index}_{input_file_stem}" if multiple_files else input_file_stem,
            result=result,
            output_sensitive_data=obj.output_sensitive_data,
            pepper=obj.pepper,
        )


def _get_result(obj: PrivateEyeContext) -> ParserResults:
    parser_options = obj.get_parser_options()

    external_data = obj.external_data or ExternalData()
    try:
        with parse(obj.parser, [obj.image_path], parser_options, external_data) as image:
            return _read_sections(image, obj.sections)
    except RequiresFiles as e:
        with parse(obj.parser, [obj.image_path] + e.files, parser_options, external_data) as image:
            return _read_sections(image, obj.sections)


def _read_sections(image: ImageParser, requested_sections: List[str]) -> ParserResults:
    sections = [SectionName(s) for s in requested_sections]
    logger.debug("Attempting to parse sections: %s", sections)
    return image.read_sections(*sections)


for parser_ in parsers:
    cli_options = _default_options + _extra_cli_options.get(parser_, [])

    command = functools.partial(_output, parser=parser_)
    functools.update_wrapper(command, _output)
    for cli_option in reversed(cli_options):
        cli_option(command)
    main.command(parser_)(command)
