import logging
import math
from collections import OrderedDict, defaultdict
from functools import partial
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union, cast

import attr
import numpy as np
from more_itertools import first, last, only
from ....private_eye.consts import ImageModality, ModalityFlag, SectionName
from ....private_eye.data import (
    BScanImageData,
    BscanLocation,
    Circle,
    ContourData,
    ContourLine,
    HeidelbergImageTransforms,
    ImageData,
    ImageOutputParams,
    ImageProcessingOptions,
    ImagesData,
    ImageSourceDataType,
    ImageTransform,
    Line,
    ParserOptions,
    PhotoImageData,
    PointF,
    Size2D,
    Size3D,
)
from ....private_eye.heidelberg.data import DbFiles, HeidelbergFile, PatientExamSeries, SegmentBody
from ....private_eye.heidelberg.heidelberg_consts import ANTERIOR_DEGREES_TO_MM, INTERIOR_DEGREES_TO_MM, BScanType
from ....private_eye.heidelberg.heidelberg_utils import ushort_to_unsigned_half
from ....private_eye.heidelberg.metadata_builder.abstract_data_builder import DataBuilder
from ....private_eye.heidelberg.modality import get_modality_from_exam_type
from ....private_eye.heidelberg.parser import (
    BScanImageInfoSegment,
    BScanImageSegment,
    BScanRegistrationSegment,
    ContourSegment,
    CustomOctSettingsSegment,
    HrExamType,
    ImageInfo05Segment,
    ImageParseException,
    PhotoImageSegment,
    Segment,
    SeriesInfoSegment,
    UnknownImageSegment,
)
from ....private_eye.utils.maths import angle_from_origin, distance
from skimage.exposure import rescale_intensity
from skimage.transform import warp

logger = logging.getLogger(__name__)


@attr.s(auto_attribs=True, frozen=True)
class _ImageGroup:
    photo_segment: Segment[PhotoImageSegment]
    bscan_segments: Sequence[Segment[BScanImageSegment]]


class _ImagesDataBuilder(DataBuilder[ImagesData]):
    name = SectionName.IMAGES
    requires = [
        SeriesInfoSegment,
        PhotoImageSegment,
        ImageInfo05Segment,
        BScanImageSegment,
        UnknownImageSegment,
        BScanImageInfoSegment,
        BScanRegistrationSegment,
        CustomOctSettingsSegment,
        ContourSegment,
    ]

    def build(self, pes: PatientExamSeries, db_files: DbFiles) -> ImagesData:
        """
        Known combinations of fundus and b-scans:
        * Case 1: Single 'series-level' fundus (i.e. no image ID) and many b-scans.
          We return two images: fundus and OCT. Both have group ID of 0
        * Case 2: N fundus images and N b-scans (N > 0), with matching IDs.
          This is N pairs of a fundus image with a single associated b-scan slice
          We return N fundus and N OCT images, with the group set to image ID to tie together the pairs.
        * Case 3: N fundus images, 0 b-scans, series type set to 'Time Sequence'.
          We return a single fundus image object with N contents images.
        * Case 4: N fundus images, 0 b-scans, series type NOT set to 'Time Sequence'.
          We return N fundus image objects, each with a single contents image.
        """
        series_info: Segment[SeriesInfoSegment] = db_files.edb.get_last_segment_for_pes(SeriesInfoSegment, pes)

        # Some photo segments do not have an image ID, e.g. in the case of a reference fundus image for lots of
        # OCT slices. In this case, we can think of the photo as being at 'series level'
        fundus_segments = _get_segments_ordered_by_image_id(db_files.sdb, PhotoImageSegment, pes)
        bscan_segments = _get_segments_ordered_by_image_id(db_files.sdb, BScanImageSegment, pes)
        unknown_image_segments = _get_segments_ordered_by_image_id(db_files.sdb, UnknownImageSegment, pes)

        # These can correlate either to b-scans or to photos.
        # If we have b-scans, there is an identical segment for each b-scan image ID, and sometimes a single segment
        # without an image ID.
        # If we do not have b-scans, there is a segment per photo segment.
        # In both cases, there is one or more info segments with a sub-index of 0 and 0 or more info segments with a
        # sub-index of None (0xFF).
        #
        # For consistency, we shall apply the following logic:
        # * We only use info segments with a sub-index of 0.
        # * If we have b-scans, we select the last info segment with the image ID of the first b-scan per group
        #   corresponding to a fundus image
        # * If we do not have b-scans, we select the last info segment with the image ID of a given photo image.
        #   We take the last one as Heidelberg stores entries in order (as tested by updating EyeDataSegment via Heyex)
        image_info_segments_dict = _get_last_segments_by_image_id(db_files, pes, ImageInfo05Segment, 0)

        bscan_count = len(bscan_segments)
        if bscan_count > 0:
            fundus_count = len(fundus_segments)
            series_photo = only(
                (im for im in fundus_segments if _get_optional_image_id(im) is None),
                None,
                ImageParseException("Only one fundus image may have a null image ID"),
            )

            # When we have b-scans, the second exam type is always OCT
            image_type = series_info.body.exam_type_1
            if series_info.body.exam_type_2 != HrExamType.OCT:
                raise ImageParseException(
                    f"Found b-scans but with unexpected exam type: {series_info.body.exam_type_2}"
                )

            if series_photo:
                # Case 1
                group_dict = {0: _ImageGroup(series_photo, bscan_segments)}
            elif fundus_count == bscan_count:
                # Case 2
                group_dict = OrderedDict()
                # fundus images and bscans already sorted by image id, so can zip
                for fundus_segment, bscan_segment in zip(fundus_segments, bscan_segments):
                    # This cast is valid as we've dealt with the 'series-level' image above
                    fundus_image_id = cast(int, _get_optional_image_id(fundus_segment))
                    if fundus_image_id != _get_optional_image_id(bscan_segment):
                        raise ImageParseException("Image IDs of fundus and bscan segments must match")
                    group_dict[fundus_image_id] = _ImageGroup(fundus_segment, [bscan_segment])
            else:
                raise ImageParseException(
                    f"Fundus count ({fundus_count}) must match b-scan count ({bscan_count}), "
                    "or a series-level image must exist"
                )

            images = _build_images_by_group(
                pes, db_files, group_dict, image_type, image_info_segments_dict, self.options
            )
        else:
            if series_info.body.series_type == "Time Sequence":
                # Case 3
                # Use the first segment as the source of data for the ImageData object
                photo_segment = fundus_segments[0]
                fundus_info_segment = image_info_segments_dict[_get_optional_image_id(photo_segment)]
                image_type = _get_photo_exam_type(photo_segment, series_info)
                fundus_image_contents = [
                    _build_photo_contents(im, image_info_segments_dict[_get_optional_image_id(im)], self.options)
                    for im in fundus_segments
                ]
                images = [
                    _build_single_fundus_image(photo_segment, fundus_info_segment, image_type, 0, fundus_image_contents)
                ]
            else:
                # Case 4
                images = []
                for fundus_segment in fundus_segments:
                    fundus_id: Optional[int] = _get_optional_image_id(fundus_segment)
                    if fundus_id is None:
                        raise ImageParseException("Fundus images without b-scans expected to have an image ID")
                    image_type = _get_photo_exam_type(fundus_segment, series_info)
                    fundus_info_segment = image_info_segments_dict[fundus_id]
                    fundus_image_contents = [_build_photo_contents(fundus_segment, fundus_info_segment, self.options)]
                    image = _build_single_fundus_image(
                        fundus_segment, fundus_info_segment, image_type, fundus_id, fundus_image_contents
                    )
                    images.append(image)

        unknown_images = _process_unknown_image_segments(unknown_image_segments)
        return ImagesData(images=images + unknown_images)


def _get_all_segments_by_image_id(
    db_files: DbFiles, pes: PatientExamSeries, segment_type: Type[SegmentBody], sub_index: Optional[int] = None
) -> Dict[Optional[int], List[Segment]]:
    segments = db_files.edb.get_segments_for_pes(segment_type, pes, allow_empty=True)
    segments_by_image_id: Dict[Optional[int], List[Segment]] = defaultdict(list)
    for segment in segments:
        if sub_index is None or segment.sm.ind == sub_index:
            segments_by_image_id[segment.sm.slice].append(segment)
    return segments_by_image_id


def _get_last_segments_by_image_id(
    db_files: DbFiles, pes: PatientExamSeries, segment_type: Type[SegmentBody], sub_index: int
) -> Dict[Optional[int], Segment]:
    segments = _get_all_segments_by_image_id(db_files, pes, segment_type, sub_index)
    return {key: last(val) for key, val in segments.items()}


def _get_photo_exam_type(
    photo_segment: Segment[PhotoImageSegment], series_segment: Segment[SeriesInfoSegment]
) -> Optional[HrExamType]:
    exam_types = (series_segment.body.exam_type_1, series_segment.body.exam_type_2)
    if exam_types[1] is None or photo_segment.sm.ind is None:
        return exam_types[0]

    try:
        return exam_types[photo_segment.sm.ind]
    except IndexError as error:
        raise ImageParseException(f"Unexpected ind value: {photo_segment.sm.ind}") from error


def _get_oct_contrast(pes: PatientExamSeries, db_files: DbFiles) -> int:
    try:
        segment = db_files.edb.get_last_segment_for_pes(CustomOctSettingsSegment, pes)
    except KeyError:
        # The default Heyex constrast is 12
        return 12
    else:
        return cast(CustomOctSettingsSegment, segment.body).oct_contrast


def _build_images_by_group(
    pes: PatientExamSeries,
    db_files: DbFiles,
    image_groups: Dict[int, _ImageGroup],
    image_type: Optional[HrExamType],
    photo_info_dict: Dict[Optional[int], Segment[ImageInfo05Segment]],
    options: ParserOptions,
) -> List[ImageData]:
    ret = []

    bscan_info_dict = _get_last_segments_by_image_id(db_files, pes, BScanImageInfoSegment, 1)
    contours_dict = _get_all_segments_by_image_id(db_files, pes, ContourSegment)
    bscan_registration_dict = _get_last_segments_by_image_id(db_files, pes, BScanRegistrationSegment, 1)

    oct_contrast = _get_oct_contrast(pes, db_files)

    processing_flags = {
        image_processing_option.identifier(): {
            "heidelberg_processing_flags": {
                "intensity_adjustment": not image_processing_option.heidelberg_skip_intensity_adjust,
                "transform": not image_processing_option.heidelberg_skip_shape_adjust,
            }
        }
        for image_processing_option in options.image_processing_options
    }

    for group_id, images in image_groups.items():
        photo_segment = images.photo_segment
        bscan_segments = images.bscan_segments

        first_bscan_segment = first(bscan_segments)
        bscan_and_info_segments = [(bscan, bscan_info_dict[_get_optional_image_id(bscan)]) for bscan in bscan_segments]

        # As described in the comment above, if we have b-scans we use the ImageInfo05Segment associated with the
        # first b-scan
        fundus_image_info = photo_info_dict[_get_optional_image_id(first_bscan_segment)]
        fundus_image_contents = [_build_photo_contents(photo_segment, fundus_image_info, options)]
        fundus_image = _build_single_fundus_image(
            photo_segment, fundus_image_info, image_type, group_id, fundus_image_contents
        )
        ret.append(fundus_image)

        bscan_contents = []
        bscan_width = first_bscan_segment.body.width
        bscan_height = first_bscan_segment.body.height

        for bscan_index, (bscan_segment, info_segment) in enumerate(bscan_and_info_segments):
            bscan_id = _get_optional_image_id(bscan_segment)
            try:
                reg_segment = bscan_registration_dict[bscan_id]
                inv_reg_matrix: Optional[np.ndarray] = _build_inverse_registration_matrix(
                    bscan_width, bscan_height, reg_segment.body
                )
            except KeyError:
                inv_reg_matrix = None

            contour_segments = contours_dict.get(bscan_id, None)
            contents = _build_bscan_contents_with_contours(
                bscan_segment,
                info_segment,
                inv_reg_matrix,
                oct_contrast,
                fundus_image_info,
                options.image_processing_options,
                contour_segments,
                bscan_index,
            )
            bscan_contents.append(contents)
        oct_image = _build_single_oct_image(
            bscan_and_info_segments,
            group_id,
            bscan_contents,
            processing_flags,
        )
        ret.append(oct_image)

    return ret


def _build_contour_layers(
    contours_segments: List[Segment[ContourSegment]], bscan_height: int, inv_reg_matrix: Optional[np.ndarray]
) -> List[ContourLine]:
    contours_segments = _deduplicate_sort_layer_segments(contours_segments)

    ret = []
    for contours_segment in contours_segments:
        layer_data = contours_segment.body.data
        if inv_reg_matrix is not None:
            # Invert the inverse transformation, as we need the un-inverted transformation to adjust the contours
            reg_matrix = np.linalg.inv(inv_reg_matrix)
            layer_data = _apply_registration_to_contours(layer_data, reg_matrix)

        # Contour coordinates are from the top instead of bottom, so we need to flip them
        layer_data = bscan_height - layer_data
        ret.append(
            ContourLine(
                layer_name=contours_segment.body.layer_name,
                data=layer_data,
            )
        )
    return ret


def _deduplicate_sort_layer_segments(contour_segments: List[Segment[ContourSegment]]) -> List[Segment[ContourSegment]]:
    """
    We have seen instances of multiple segments with the same layer name, where the only differentiator
    is the first value. We shall assume it is a version ID, although this is an educated guess.
    Hence, in cases of conflict we shall try to pick the contour with the highest 'version' (or whatever it is) number
    """
    layers_by_name: Dict[str, List[Segment[ContourSegment]]] = defaultdict(list)
    for segment in contour_segments:
        layers_by_name[segment.body.layer_name].append(segment)

    ret = []
    for segments_for_layer in layers_by_name.values():
        segments_for_layer.sort(key=lambda s: s.body.mystery_1)
        ret.append(segments_for_layer[-1])

    # Ensure contours are in a deterministic order. This is more for the sake of testing than anything else
    ret.sort(key=lambda s: s.body.id)
    return ret


def _build_photo_contents(
    photo_segment: Segment[PhotoImageSegment], info_segment: Segment[ImageInfo05Segment], options: ParserOptions
) -> PhotoImageData:
    return PhotoImageData(
        image=photo_segment.body.data,
        colour_depth=8,
        capture_datetime=info_segment.body.capture_datetime,
        image_output_params=[
            ImageOutputParams(
                image_processing_options=image_processing_option, image_mode="L", image_transform_functions=[]
            )
            for image_processing_option in options.image_processing_options
        ],
        image_byte_format=ImageSourceDataType.UINT8,
        width=photo_segment.body.width,
        height=photo_segment.body.height,
    )


def _build_single_fundus_image(
    photo_segment: Segment[PhotoImageSegment],
    info_segment: Segment[ImageInfo05Segment],
    image_type: Optional[HrExamType],
    group_id: int,
    contents: Sequence[PhotoImageData],
) -> ImageData:
    if image_type is None:
        logger.warning("No Heyex image type exists for image %s, cannot determine modality", photo_segment.sm.pes)
        modality = ImageModality.UNKNOWN
    else:
        modality = get_modality_from_exam_type(image_type, photo_segment.header.type)
    photo = photo_segment.body

    # Heidelberg fundus images are all square
    side_mm = _convert_scan_angle_to_mm(info_segment.body.scan_angle, modality)

    return ImageData(
        modality=modality,
        group_id=group_id,
        size=Size2D(photo.width, photo.height),
        dimensions_mm=Size2D(side_mm, side_mm),
        resolutions_mm=Size2D(side_mm / photo.width, side_mm / photo.height),
        contents=contents,
        source_id=_build_source_id(group_id, modality, photo_segment.body.type),
        field_of_view=info_segment.body.scan_angle,
    )


def _build_bscan_contents_with_contours(
    bscan_segment: Segment[BScanImageSegment],
    info_segment: Segment[BScanImageInfoSegment],
    inv_reg_matrix: Optional[np.ndarray],
    oct_contrast: int,
    fundus_info_segment: Segment[ImageInfo05Segment],
    image_processing_options: Sequence[ImageProcessingOptions],
    contour_segments: Optional[List[Segment[ContourSegment]]],
    bscan_index: int,
) -> BScanImageData:
    image_bytes = bscan_segment.body.data
    width = bscan_segment.body.width
    height = bscan_segment.body.height
    image_output_params = []
    for image_processing_option in image_processing_options:
        transforms: List[ImageTransform] = []
        mode = None
        if contour_segments:
            contour_data: Optional[ContourData] = ContourData(
                bscan_index=bscan_index,
                contour_layers=_build_contour_layers(
                    contour_segments,
                    height,
                    inv_reg_matrix
                    if inv_reg_matrix is not None and not image_processing_option.heidelberg_skip_shape_adjust
                    else None,
                ),
            )
        else:
            contour_data = None
        if image_bytes:
            # The order here is important!!!
            # The affine transform results in some new pixels being added due to the rotation.
            # The intensity scaling should not be applied to these new pixels.
            if not image_processing_option.heidelberg_skip_intensity_adjust:
                transforms.append(
                    partial(
                        _intensity_scaling,
                        info_segment.body,
                        oct_contrast,
                        width,
                        height,
                    )
                )
                mode = "L"
            else:
                transforms.append(partial(_create_raw_image, width, height))
                mode = "I;16"
            if inv_reg_matrix is not None and not image_processing_option.heidelberg_skip_shape_adjust:
                transforms.append(partial(_register_image, inv_reg_matrix))
        image_output_params.append(
            ImageOutputParams(
                image_processing_options=image_processing_option,
                image_mode=mode,
                image_transform_functions=transforms,
                contour=contour_data,
            )
        )
    locations = _get_shape_for_info(info_segment.body, fundus_info_segment.body)
    return BScanImageData(
        quality=info_segment.body.quality,
        photo_locations=[locations],
        image=image_bytes,
        capture_datetime=info_segment.body.scan_datetime,
        art_average=info_segment.body.art_average,
        image_transform_metadata={
            image_processing_option.identifier(): HeidelbergImageTransforms(
                affine_transform=inv_reg_matrix,
                intensity_scaling_exponent=_intensity_exponent(oct_contrast),
                intensity_scaling_multiplier=info_segment.body.intensity_scaling,
            )
            for image_processing_option in image_processing_options
        },
        image_output_params=image_output_params,
        image_byte_format=ImageSourceDataType.UINT16,
        width=width,
        height=height,
    )


def _create_raw_image(width: int, height: int, image_array: np.ndarray) -> np.ndarray:
    # We replace placeholder data with 0 (black), as this is what Heyex does when displaying b-scans
    return cast(np.ndarray, np.where(image_array == 65535, 0, image_array).reshape(height, width))


def _create_ushort_to_half_lookup_table() -> np.ndarray:
    """
    The lookup table of ushort -> unsigned half values.
    No scaling is performed here, as it depends on values in other segments.
    """
    all_shorts = np.arange(2**16, dtype=np.uint16)
    vector_func = np.vectorize(ushort_to_unsigned_half, otypes=[float])
    return cast(np.ndarray, vector_func(all_shorts))


_ushort_to_half_lookup_table = _create_ushort_to_half_lookup_table()


def _create_unsigned_half_image(image_array: np.ndarray, width: int, height: int) -> np.ndarray:
    return cast(np.ndarray, _ushort_to_half_lookup_table[image_array].reshape(height, width))


def _intensity_exponent(oct_contrast: int) -> int:
    # -24, to compensate for the huge values of intensity_scaling
    return oct_contrast - 24


def _intensity_scaling(
    bscan_info: BScanImageInfoSegment, oct_contrast: int, width: int, height: int, image: np.ndarray
) -> np.ndarray:
    # Need to convert to array in this instance.
    image_array = _create_unsigned_half_image(image, width, height)

    # This is the closest we have got so far to reproducing the scaling performed by Heyex.
    #
    # The histogram shape of the image produced by the log transform is identical to the shape for the image
    # that is produced by Heyex. Hence, this is most likely the correct transform to perform.
    #
    # Playing around with the contrast value in Heyex suggests that the contrast value provided by Heyex is not
    # 'contrast' in the traditional sense (i.e. Out = F(In - 128) + 128), but instead is related to the scale factor
    # of the log transform. Some further playing around with it suggests something along the lines of
    #
    # log_factor = a * 2 ^ contrast + b
    #
    # The closest results for a and b so far are:
    # a = intensity_scaling from BScanInfoSegment
    # b = -24, to compensate for the huge values of intensity_scaling
    scaling = math.ldexp(bscan_info.intensity_scaling, _intensity_exponent(oct_contrast))
    ret = np.log2(scaling * image_array + 1)

    # We clip the image very slightly at the top end, as without it images appear too washed out.
    in_min, in_max = np.percentile(ret, (0, 99.9))
    ret = rescale_intensity(ret, in_range=(in_min, in_max), out_range="uint8")

    return cast(np.ndarray, ret.astype(np.uint8))


def _build_inverse_registration_matrix(width: int, height: int, registration: BScanRegistrationSegment) -> np.ndarray:
    shear_factor_y = np.tan(registration.shear_y_angle)
    dx = registration.dx
    dy = registration.dy
    scale_x = registration.scale_x

    # Build an affine transformation matrix using the given parameters, as this is what is required by scikit
    # Notes:
    #     * transforms all seem to be done relative to the centre of the image, so we need matrices to transform the
    #       origin to image centre and back again.
    #     * the parameters provided seem to be for an *inverse* transformation matrix. This is convenient as it is
    #       exactly what is required by the image, but we need to be explicit about this as the contours transform
    #       is done using the non-inverse transformation
    # fmt: off
    change_origin = np.array([
        [1.0, 0.0, -width / 2],
        [0.0, 1.0, -height / 2],
        [0.0, 0.0, 1.0],
    ], dtype=float)
    revert_origin = np.array([
        [1.0, 0.0, width / 2],
        [0.0, 1.0, height / 2],
        [0.0, 0.0, 1.0],
    ], dtype=float)

    shear = np.array([
        [1.0, 0.0, 0.0],
        [shear_factor_y, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ], dtype=float)
    scale = np.array([
        [scale_x, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ], dtype=float)
    translate = np.array([
        [1.0, 0.0, dx],
        [0.0, 1.0, dy],
        [0.0, 0.0, 1.0],
    ], dtype=float)

    transform = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ], dtype=float)
    # fmt: on

    # Note: order is important - shear is applied before scale
    for mat in [change_origin, shear, scale, translate, revert_origin]:
        # Note: Matrix transforms are applied 'right-to-left', so we flip the multiplication order
        np.matmul(mat, transform, out=transform)
    return transform


def _register_image(inv_reg_matrix: np.ndarray, image_array: np.ndarray) -> np.ndarray:
    # We need the inverse transformation matrix in this case
    image_tf = warp(image_array, inverse_map=inv_reg_matrix, preserve_range=True)
    return cast(np.ndarray, image_tf.astype(image_array.dtype))


def _apply_registration_to_contours(contour_line: np.ndarray, reg_matrix: np.ndarray) -> np.ndarray:
    """
    The contour is a 1D array which actually represents a list of (x, y) coordinates,
    where x is the array index and y is the value.
    Hence, in order to transform this on a 2D plane we first convert the line into a list of (x, y) values,
    which we multiply by the transformation matrix. After this we iterate over the result to map it back into a 1D array
    """
    width = len(contour_line)

    # We convert to a 3D contour as the transformation matrix is 3x3. We don't actually care about the 3rd coordinate,
    # so can ignore its return value
    contour_coords = [np.array([index, val, 1]) for index, val in enumerate(contour_line)]

    # Loop over all the transformed coordinates and map back to the 0..width range by using the converted x-coordinates
    # as the array index. Any coordinates which have been mapped to outside the bounds of the image are ignored, and
    # any values not filled are left as NaN in order to be explicit that these are not valid values
    ret = np.empty(width)
    ret[:] = np.NaN
    for coord in contour_coords:
        np.matmul(reg_matrix, coord, out=coord).astype(np.int32)
        # Ignore the coordinates which have been moved to outside the bounds of the image
        if 0 <= coord[0] < width:
            ret[math.floor(coord[0])] = coord[1]

    return ret


def _build_single_oct_image(
    bscan_and_info_segments: List[Tuple[Segment[BScanImageSegment], Segment[BScanImageInfoSegment]]],
    group_id: int,
    contents: Sequence[BScanImageData],
    processing_flags: Dict[str, Dict[str, Any]],
) -> ImageData:
    modality = ImageModality.OCT

    first_bscan, first_info = first(bscan_and_info_segments)
    _, last_info = last(bscan_and_info_segments)

    # Shortcut for the case of a single scan
    scan_count = len(bscan_and_info_segments)

    if first_info.body.scan_type == BScanType.LINE:
        width_x = _convert_scan_angle_to_mm(first_info.body.scan_angle, modality)
        if scan_count == 1:
            angle_z = 0.0
            depth_resolution = 0.0
        else:
            angle_z = distance(first_info.body.line_start, last_info.body.line_start)
            depth_resolution = angle_z / (scan_count - 1)
    else:
        # The scan_angle is the circle diameter in this case, so we need to convert it to the perimeter
        scan_angle = first_info.body.scan_angle * math.pi
        width_x = _convert_scan_angle_to_mm(scan_angle, modality)
        angle_z = 0.0
        depth_resolution = 0.0
        if scan_count > 1:
            logger.warning("Multiple non-linear b-scans found; cannot calculate z-angle")

    size = Size2D(first_bscan.body.width, first_bscan.body.height)
    # Note: The Z coordinate represents the height of a b-scan in Heidelberg
    dimensions_mm = Size3D(
        width=width_x,
        height=first_info.body.scaling_z * size.height,
        depth=_convert_scan_angle_to_mm(angle_z, modality),
    )

    resolutions_mm = Size3D(
        width=width_x / size.width,
        height=first_info.body.scaling_z,
        depth=_convert_scan_angle_to_mm(depth_resolution, modality),  # Distance between b-scans
    )

    return ImageData(
        modality=modality,
        group_id=group_id,
        size=size,
        dimensions_mm=dimensions_mm,
        resolutions_mm=resolutions_mm,
        contents=contents,
        source_id=_build_source_id(group_id, modality),
        field_of_view=first_info.body.scan_angle,
        extras=processing_flags,
    )


def _process_unknown_image_segments(unknown_image_segments: List[Segment[UnknownImageSegment]]) -> List[ImageData]:
    return [
        ImageData(
            modality=ImageModality.UNKNOWN,
            size=None,
            resolutions_mm=None,
            dimensions_mm=None,
            contents=[],
            group_id=None,
            source_id=f"Unknown-{idx}",
            field_of_view=None,
        )
        for idx, segment in enumerate(unknown_image_segments)
    ]


def _get_image_id(segment: Segment) -> int:
    slice_id = segment.sm.slice
    if slice_id is None:
        raise ImageParseException(f"Slice for segment is None: {segment.sm}")
    return slice_id


def _get_optional_image_id(segment: Segment) -> Optional[int]:
    return segment.sm.slice


def _get_segments_ordered_by_image_id(
    hfile: HeidelbergFile, body_type: Type[SegmentBody], pes: PatientExamSeries
) -> List[Segment]:
    segments = hfile.get_segments_for_pes(body_type, pes, allow_empty=True)
    # If the segment is less than 1 long no point sorting.
    # Results in us not erroring on images we expect to not have slices either.
    if len(segments) > 1:
        segments.sort(key=_get_image_id)
    return segments


def _get_shape_for_info(info: BScanImageInfoSegment, fundus_info: ImageInfo05Segment) -> BscanLocation:
    def _angle_to_pixels(point: PointF) -> PointF:
        # Positions are given in angles relative to the vertical. We want to convert these into a fraction of the
        # total fundus scan angle, which we then multiply by the fundus size in order to get the position relative to
        # the fundus image in pixels. We use the following formula:
        #
        # fraction = (0.5 * scan_angle + position) / scan_angle
        #          = 0.5 + position / scan_angle
        #
        # We then multiple the fraction by the fundus size to get the position in pixels

        fraction_x = 0.5 + point.x / fundus_info.scan_angle
        fraction_y = 0.5 + point.y / fundus_info.scan_angle
        return PointF(fundus_info.ir_image_size_x * fraction_x, fundus_info.ir_image_size_y * fraction_y)

    line_start = _angle_to_pixels(info.line_start)
    if info.scan_type == BScanType.LINE:
        line_end = _angle_to_pixels(info.line_end)
        return Line(line_start, line_end)

    centre_pos = _angle_to_pixels(info.centre_pos)
    angle = angle_from_origin(line_start, centre_pos)
    radius = distance(line_start, centre_pos)
    return Circle(centre_pos, radius, angle)


def _build_source_id(group_id: int, modality: ImageModality, _type: Optional[int] = None) -> str:
    type_suffix = f"-{_type}" if _type else ""
    return f"{modality.code}-{group_id or 0}{type_suffix}"


def _convert_scan_angle_to_mm(scan_angle: Union[int, float], modality: ImageModality) -> float:
    if ModalityFlag.IS_ANTERIOR in modality.flags:
        return scan_angle * ANTERIOR_DEGREES_TO_MM
    return scan_angle * INTERIOR_DEGREES_TO_MM
