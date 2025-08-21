import logging
from collections import defaultdict
from typing import DefaultDict, List, Optional, Set, Type

import attr
from more_itertools import flatten
from ....private_eye import ParserOptions
from ....private_eye.heidelberg.data import (
    DirectoryHeader,
    HeidelbergFile,
    PatientExamSeries,
    Segment,
    SegmentBody,
    StandardMetadata,
)
from ....private_eye.heidelberg.parser.segment.primitive import parse_small_segment
from ....private_eye.heidelberg.parser.segment_parser import _segment_types_by_target, parse_segment

from ...exceptions import ImageParseException
from .stream_wrapper import HeidelbergStreamWrapper

logger = logging.getLogger(__name__)


def parse(
    fs: HeidelbergStreamWrapper,
    parser_options: ParserOptions,
    required_pes: Optional[PatientExamSeries] = None,
    file_header_metadata: Optional[StandardMetadata] = None,
    required_segments: Optional[Set[Type[SegmentBody]]] = None,
) -> List[HeidelbergFile]:

    pes_not_provided = required_pes is None
    if pes_not_provided:
        # Provide a PES to parse, then refactor result to split by PES later
        required_pes = PatientExamSeries(None, None, None)
    if not file_header_metadata:
        file_header_metadata = fs.read_file_header()

    (main_header_metadata, node_reference) = fs.read_main_header()

    all_segments = []
    current = node_reference.current
    while current != 0:
        fs.seek(current)
        (directory_header_metadata, directory_header) = fs.read_directory_header()

        _check_metadata_is_homogenous(directory_header_metadata, file_header_metadata, main_header_metadata)
        all_segments.extend(directory_header.segments)
        current = directory_header.node_reference.previous

    required_types = _calculate_required_segment_types(required_segments)
    logger.debug("Required types: %s", required_types)

    segments: DefaultDict[Type[SegmentBody], List[Segment]] = defaultdict(list)
    for header_segment in all_segments:
        required = required_types is None or header_segment.type in required_types
        logger.debug("Processing segment:%s required:%s", header_segment.type, required)

        # Filter for segments only relevant to the current patient->exam->series chain
        segment_pes = header_segment.standard_metadata.pes

        if required and segment_pes == required_pes:
            if header_segment.size <= 4:
                segment = parse_small_segment(header_segment)
            else:
                fs.seek(header_segment.start)
                segment = parse_segment(fs, header_segment.type, parser_options)
                _validate_segment_against_directory_header(header_segment, segment)

            segments[type(segment.body)].append(segment)

    parser_result = HeidelbergFile(main_header_metadata, node_reference, segments)

    if pes_not_provided:
        return _separate_result_by_pes(parser_result)
    return [parser_result]


def _separate_result_by_pes(parser_result: HeidelbergFile) -> List[HeidelbergFile]:
    segments_by_pes_then_type: DefaultDict[
        PatientExamSeries, DefaultDict[Type[SegmentBody], List[Segment]]
    ] = defaultdict(lambda: defaultdict(list))

    for segment_type, segment_list in parser_result.segments.items():
        for segment in segment_list:
            pes = PatientExamSeries(segment.sm.patient_id, segment.sm.exam_id, segment.sm.series_id)
            segments_by_pes_then_type[pes][segment_type].append(segment)

    # Extract segments without a series (patient/device, i.e. non-image segments) and add to every other segment list
    non_image_data = {pes: data for pes, data in segments_by_pes_then_type.items() if not pes.is_series()}
    if len(non_image_data) > 2:
        # May have less than 2 if didn't specify Patient/Device in required_segments
        raise ValueError(
            f"E2E file should have exactly 2 non-image segments (1 Patient, 1 Device), found {len(non_image_data)}"
        )

    for pes, segments_dict in list(segments_by_pes_then_type.items()):
        if pes.is_series():
            for segment_type_dict in non_image_data.values():
                segments_dict.update(segment_type_dict)
        else:
            segments_by_pes_then_type.pop(pes)

    return [
        HeidelbergFile(parser_result.standard_metadata, parser_result.node_reference, segments)
        for segments in segments_by_pes_then_type.values()
    ]


def _calculate_required_segment_types(required_segments: Optional[Set[Type[SegmentBody]]]) -> Optional[List[int]]:
    required_types: Optional[List[int]]
    if required_segments is not None:
        required_types = list(flatten(_segment_types_by_target[segment] for segment in required_segments))
    else:
        required_types = None
    return required_types


def _check_metadata_is_homogenous(
    directory_header_metadata: StandardMetadata,
    file_header_metadata: StandardMetadata,
    main_header_metadata: StandardMetadata,
) -> None:
    if attr.evolve(file_header_metadata, mystery_1=0) != attr.evolve(main_header_metadata, mystery_1=0):
        raise ImageParseException(
            "Metadata in file header didn't match that in main header: "
            f"{file_header_metadata} / {main_header_metadata}"
        )
    if attr.evolve(file_header_metadata, mystery_1=0) != attr.evolve(directory_header_metadata, mystery_1=0):
        raise ImageParseException(
            "Metadata in file header didn't match that in directory header: "
            f"{file_header_metadata} / {directory_header_metadata}"
        )


def _validate_segment_against_directory_header(header_segment: DirectoryHeader.Segment, segment: Segment) -> None:
    """
    This could be pulled out into a rule, but it would be a bit messy at the moment because of the layout of the data
    classes.

    Interestingly, this fails if we also compare some of the mystery values (currently excluded from comparison in their
    definitions).
    """
    if segment.header.standard_metadata != header_segment.standard_metadata:
        raise ImageParseException("Metadata in directory header doesn't match that in actual segments")
    for attribute in ["size", "type"]:
        if getattr(segment.header, attribute) != getattr(header_segment, attribute):
            raise ImageParseException(f'Attribute "{attribute}" in segment doesn\'t match directory header')
