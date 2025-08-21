import logging
from itertools import groupby
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union, cast, no_type_check

from more_itertools import flatten
from ..private_eye.consts import EntireFileOutputFormat, IndividualImageOutputFormat, OutputFormat
from ..private_eye.exceptions import InvalidPepperLenError, InvalidPepperType
from ..private_eye.output_formatter.dicom.dicom_output import OutputDICOM
from ..private_eye.output_formatter.h5.google_h5_output import OutputFaGoogleH5, OutputIcgaGoogleH5, OutputOctGoogleH5
from ..private_eye.output_formatter.h5.standard_h5_output import OutputStandardH5
from ..private_eye.output_formatter.metadata_output import OutputMetadataConsole, OutputMetadataJSON
from ..private_eye.output_formatter.none_output import OutputNone
from ..private_eye.output_formatter.output_formatter import EntireFileOutputWriter, IndividualImageOutputWriter
from ..private_eye.output_formatter.raw_output import OutputDebugImages, OutputRawFiles, OutputRawImages

from .consts import SectionName
from .data import (
    EntireFileOutputRequest,
    ImageData,
    ImageProcessingOptions,
    ImagesData,
    IndividualImageOutputRequest,
    OutputRequest,
    SeriesResult,
)

logger = logging.getLogger(__name__)

_individual_image_writers: Dict[IndividualImageOutputFormat, Type[IndividualImageOutputWriter]] = {
    IndividualImageOutputFormat.DICOM: OutputDICOM,
    IndividualImageOutputFormat.RAW_IMAGES: OutputRawImages,
    IndividualImageOutputFormat.H5: OutputStandardH5,
}

_entire_file_writers: Dict[EntireFileOutputFormat, Type[EntireFileOutputWriter]] = {
    EntireFileOutputFormat.H5_GOOGLE_OCT: OutputOctGoogleH5,
    EntireFileOutputFormat.H5_GOOGLE_FA: OutputFaGoogleH5,
    EntireFileOutputFormat.H5_GOOGLE_ICGA: OutputIcgaGoogleH5,
    EntireFileOutputFormat.METADATA_JSON: OutputMetadataJSON,
    EntireFileOutputFormat.METADATA_CONSOLE: OutputMetadataConsole,
    EntireFileOutputFormat.RAW_FILES: OutputRawFiles,
    EntireFileOutputFormat.DEBUG_IMAGES: OutputDebugImages,
    EntireFileOutputFormat.NONE: OutputNone,
}


def validate_pepper(_: Any, __: Any, value: Any) -> Optional[str]:
    if not isinstance(value, str) and not isinstance(value, type(None)):
        raise InvalidPepperType(type(value))
    if value and len(value) < 32:
        # We limit here to at least 32 characters.
        # This gives over 2^200 different valid inputs at 32 characters and increasing for longer strings.
        # This assumes each character is encoded as askii and that there are 96 visible ascii characters.
        # 96 options requires roughtly 6.5 bits to encode. 6.5*32 = 208.
        # Worst case means 208 bits of information are encoded in a 32 character long string.
        # This is 4.1*10^62 unique values.
        # At 10 trillion hashes a second this would take 6.5*10^44 years to crack on average.
        # This is a sufficiently large space to make brute forcing the secret implausible.
        raise InvalidPepperLenError(len(value))
    return value


def output_all_data(
    output_formats: Set[OutputFormat],
    output_directory: Path,
    filename_prefix: str,
    result: SeriesResult,
    output_sensitive_data: bool,
    pepper: Optional[str],
    save_to_file: bool = True,
) ->  Any:    # Previous typing was not accurate here.
    logger.debug("Output formats %s", output_formats)
    requests: List[OutputRequest] = []

    for output_format in output_formats:
        if output_format in EntireFileOutputFormat:
            output_format = cast(EntireFileOutputFormat, output_format)
            requests.append(
                EntireFileOutputRequest(
                    output_path_prefix=output_directory / filename_prefix,
                    output_format=output_format,
                    output_sensitive_data=output_sensitive_data,
                    pepper=validate_pepper(None, None, pepper),
                )
            )
        else:
            output_format = cast(IndividualImageOutputFormat, output_format)
            try:
                images_data = cast(ImagesData, result.get(SectionName.IMAGES))
            except KeyError as error:
                raise ValueError(f"Output format {output_format} requires image data") from error

            # Try to give each of the output files a sensible name
            for _, images_by_group in groupby(images_data.images, lambda img: img.group_id):
                for _, images_by_modality in groupby(images_by_group, lambda img: img.modality):
                    for index, image_data in enumerate(images_by_modality):
                        if save_to_file is False:
                            image_modality_code = image_data.modality.code
                        else:
                            image_modality_code=None
                        requests.append(
                            IndividualImageOutputRequest(
                                source_id=image_data.source_id,
                                output_path_prefix=construct_standard_output_file_prefix(
                                    output_directory, filename_prefix, image_data, index
                                ),
                                output_format=output_format,
                                output_sensitive_data=output_sensitive_data,
                                pepper=pepper,
                                save_to_file=save_to_file,
                                image_modality_code=image_modality_code,
                            )
                        )
    return list(flatten(output(requests, result)))



# Type checks are tricky because EntireFileOutputWriter expects EntireFileOutputRequest and IndividualImageOutputWriter
# expects IndividualImageOutputRequest
@no_type_check
def output(
    requests: List[OutputRequest], parser_result: SeriesResult
) -> List[List[Union[Dict[ImageProcessingOptions, Path], Dict[str, np.ndarray]]]]:
    logger.debug("Requests %s", requests)

    def get_writer(
        output_format: OutputFormat,
    ) -> Union[Type[IndividualImageOutputWriter], Type[EntireFileOutputWriter]]:
        if output_format in EntireFileOutputFormat:
            return _entire_file_writers[output_format]
        return _individual_image_writers[output_format]

    return [get_writer(request.output_format)().output(parser_result, request) for request in requests]


def construct_standard_output_file_prefix(
    output_directory: Path, file_name_prefix: str, image_data: ImageData, image_index: int
) -> Path:
    image_group_or_zero = int(image_data.group_id or 0)
    file_name = "-".join(map(str, [file_name_prefix, image_group_or_zero, image_index, image_data.modality.code]))
    return output_directory / file_name
