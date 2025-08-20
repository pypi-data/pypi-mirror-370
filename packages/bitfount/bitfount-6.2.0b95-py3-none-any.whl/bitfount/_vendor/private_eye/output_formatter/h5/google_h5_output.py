import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from itertools import groupby
from operator import attrgetter
from pathlib import Path
from typing import Dict, List, Optional, cast

from more_itertools import one, only
from ....private_eye import BScanImageData, ImageData, PhotoImageData
from ....private_eye.consts import ImageModality
from ....private_eye.data import EntireFileOutputRequest, SeriesResult, Size2D, Size3D
from ....private_eye.output_formatter.h5.common import H5Content, write_files
from ....private_eye.output_formatter.output_formatter import EntireFileOutputWriter
from ....private_eye.utils.optional import get_optional

logger = logging.getLogger(__name__)


class _OutputGoogleH5(EntireFileOutputWriter, ABC):
    """ "
    Combines all OCT slices into a single H5.  If there is a colour fundus then that is also chosen, if there is no
    colour fundus fall back to an infrared fundus, and then to nothing.

    Tf there is more than one group of OCTs then only the first group will be chosed and any other groups will be
    dropped with a warning.
    """

    def output(self, result: SeriesResult, request: EntireFileOutputRequest) -> List[Path]:
        try:
            images_data = get_optional(result.images)
        except ValueError as e:
            raise ValueError("Unable to export to H5 without IMAGES section") from e

        images_by_modality: Dict[ImageModality, List[ImageData]] = defaultdict(list)
        for image in images_data.images:
            images_by_modality[image.modality].append(image)

        h5_content = self.extract_h5_content(images_by_modality)
        logger.debug("h5_content: %s", h5_content)

        output_path = request.output_path_prefix.with_name(request.output_path_prefix.name + ".h5")

        logger.debug("Writing to output_path: %s", output_path)
        write_files(output_path, h5_content)
        return [output_path]

    @staticmethod
    @abstractmethod
    def extract_h5_content(images_data: Dict[ImageModality, List[ImageData]]) -> H5Content:
        raise NotImplementedError()


class OutputFaGoogleH5(_OutputGoogleH5):
    """ "Combines all FA images into a single H5.  All other modalities are dropped."""

    @staticmethod
    def extract_h5_content(images_by_modality: Dict[ImageModality, List[ImageData]]) -> H5Content:
        return _combine_all_fundus_images(images_by_modality, ImageModality.FLUORESCEIN_ANGIOGRAPHY)


class OutputIcgaGoogleH5(_OutputGoogleH5):
    """ "Combines all ICGA images into a single H5.  All other modalities are dropped."""

    @staticmethod
    def extract_h5_content(images_by_modality: Dict[ImageModality, List[ImageData]]) -> H5Content:
        return _combine_all_fundus_images(images_by_modality, ImageModality.INDOCYANINE_GREEN_ANGIOGRAPHY)


class OutputOctGoogleH5(_OutputGoogleH5):
    @staticmethod
    def extract_h5_content(images_by_modality: Dict[ImageModality, List[ImageData]]) -> H5Content:
        # We only support a single OCT image (probably with multiple slices)
        oct_images = _pick_first_group(images_by_modality, ImageModality.OCT)
        oct_image = one(
            oct_images,
            too_short=ValueError("No OCT images found"),
            too_long=ValueError("Multiple OCT images in a single group are not supported"),
        )

        fundus_images: List[ImageData] = _pick_matching(
            images_by_modality, ImageModality.COLOUR_PHOTO, oct_image.group_id
        )
        if len(fundus_images) == 0:
            logger.debug("No matching colour fundus, looking for an IR fundus")
            fundus_images = _pick_matching(images_by_modality, ImageModality.SLO_INFRARED, oct_image.group_id)
            logger.debug("Fundus: %s", fundus_images)

        # We only support a single fundus image
        fundus = only(fundus_images, too_long=ValueError("Multiple fundus images in a single group are not supported"))

        return H5Content(
            oct_resolutions=cast(Optional[Size3D], oct_image.resolutions_mm),
            fundus_resolutions=cast(Optional[Size2D], fundus.resolutions_mm) if fundus else None,
            oct=cast(List[BScanImageData], oct_image.contents),
            fundus=cast(List[PhotoImageData], fundus.contents) if fundus else [],
        )


def _pick_first_group(
    images_by_modality: Dict[ImageModality, List[ImageData]], modality: ImageModality
) -> List[ImageData]:
    try:
        unsorted_images = images_by_modality[modality]
    except KeyError as e:
        raise ValueError(f"No image with modality: {images_by_modality}") from e

    grouped_by_group = _group_by_group(unsorted_images)

    group_id: Optional[int]
    if len(grouped_by_group) > 1:
        group_id = None if None in grouped_by_group else min(cast(List[int], grouped_by_group.keys()))
        logger.warning("Multiple %s groups in image - picking first group (%s)", modality, group_id)
    else:
        group_id = one(grouped_by_group)

    return cast(List[ImageData], grouped_by_group[group_id])


def _pick_matching(
    images_by_modality: Dict[ImageModality, List[ImageData]],
    modality: ImageModality,
    group: Optional[int],
) -> List[ImageData]:
    try:
        unsorted_images = images_by_modality[modality]
    except KeyError:
        logger.debug("No %s images available", modality)
        return []

    sorted_by_group = _group_by_group(unsorted_images)
    try:
        return cast(List[ImageData], sorted_by_group[group])
    except KeyError:
        logger.debug("No images of modality %s found with group %s", modality, group)
        return []


def _group_by_group(images: List[ImageData]) -> Dict[Optional[int], List[ImageData]]:
    return dict(
        (k, list(v)) for k, v in groupby(sorted(images, key=attrgetter("group_id")), key=attrgetter("group_id"))
    )


def _combine_all_fundus_images(
    images_by_modality: Dict[ImageModality, List[ImageData]], modality: ImageModality
) -> H5Content:
    def extract_fundus_content(fundus: ImageData) -> PhotoImageData:
        content = one(fundus.contents)
        assert isinstance(content, PhotoImageData)
        return cast(PhotoImageData, content)

    matching_images: List[ImageData] = _pick_all(images_by_modality, modality)
    logger.debug("_combine_all: modalitiy=%s, maching images=%s", modality, matching_images)
    try:
        combined_content = [extract_fundus_content(fundus) for fundus in matching_images]
    except ValueError as e:
        raise ValueError("Exporting multiple slices in a single fundus image is not supported") from e

    number_of_resolutions = len(
        set(None if image.resolutions_mm is None else image.resolutions_mm.to_tuple() for image in matching_images)
    )

    if number_of_resolutions > 1:
        raise ValueError("Combining multiple images with differing resolution data is not supported")

    return H5Content(None, None, oct=[], fundus=combined_content)


def _pick_all(images_by_modality: Dict[ImageModality, List[ImageData]], modality: ImageModality) -> List[ImageData]:
    unsorted_images = images_by_modality[modality]
    if not unsorted_images:
        raise ValueError(f"No images with modality {modality} found")

    return sorted(unsorted_images, key=attrgetter("group_id"))
