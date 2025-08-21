import re
from enum import Enum, unique
from typing import Any, Callable, TypeVar

from ....private_eye.data import (
    GoldmannStimulus,
    ParserOptions,
    VisualFieldData,
    VisualFieldReliabilityIndex,
    VisualFieldStorageType,
)
from pydicom.dataset import FileDataset


# This seems to be all the data that can be extracted from this type of DICOM file
# Note that the embedded PDF contains significantly more data, but it is not present in the DICOM tags
#
# Be warned: the data in these files doesn't always exactly match the corresponding OPV/RAW files
# e.g. different names for the same protocol/strategy/fixation monitor. No effort has been made to ensure that
# the same names are used for the same strategies between file types.
@unique
class VFTag(Enum):
    protocol = 0x77171001
    strategy = 0x77171002
    glaucoma_hemifield_test = 0x77171023
    visual_field_index = 0x77171034
    fixation_loss_denominator = 0x77171008
    fixation_loss_numerator = 0x77171009
    false_positive_percentage = 0x77171010
    false_negative_percentage = 0x77171013
    mean_deviation = 0x77171016
    mean_deviation_significance = 0x77171017
    standard_deviation = 0x77171018
    standard_deviation_significance = 0x77171019
    fixation_monitor = 0x77171024
    stimulus_size = 0x77171003
    stimulus_colour = 0x77171004


def parse_zeiss_encapsulated_pdf(ds: FileDataset, options: ParserOptions) -> VisualFieldData:
    return VisualFieldData(
        storage_type=VisualFieldStorageType.PDF,
        modality=None,
        source_id=ds.SOPInstanceUID,
        protocol=_read_tag(ds, VFTag.protocol, str),
        strategy=_read_tag(ds, VFTag.strategy, str),
        left_eye_patient_clinical_information=None,
        right_eye_patient_clinical_information=None,
        fixation_loss=VisualFieldReliabilityIndex(
            _read_tag(ds, VFTag.fixation_loss_numerator, int), _read_tag(ds, VFTag.fixation_loss_denominator, int)
        ),
        # False positives and false negatives are reported as percentages rather than fractions, so invent a fraction
        false_positive_errors=VisualFieldReliabilityIndex(_read_tag(ds, VFTag.false_positive_percentage, int), 100),
        false_negative_errors=VisualFieldReliabilityIndex(_read_tag(ds, VFTag.false_negative_percentage, int), 100),
        visual_field_index=_read_tag(ds, VFTag.visual_field_index, int),
        glaucoma_hemifield_test=_read_tag(ds, VFTag.glaucoma_hemifield_test, str),
        mean_deviation=_read_tag(ds, VFTag.mean_deviation, float),
        mean_deviation_significance=_read_tag(ds, VFTag.mean_deviation_significance, _parse_significance),
        pattern_standard_deviation=_read_tag(ds, VFTag.standard_deviation, float),
        pattern_standard_deviation_significance=_read_tag(
            ds, VFTag.standard_deviation_significance, _parse_significance
        ),
        test_duration=None,
        fixation_monitors=[_read_tag(ds, VFTag.fixation_monitor, str)],
        stimulus_size=_read_tag(ds, VFTag.stimulus_size, GoldmannStimulus),
        stimulus_colour=_read_tag(ds, VFTag.stimulus_colour, str),
        background_luminance=None,
        foveal_sensitivity=None,
        visual_field_data=[],
    )


T = TypeVar("T")


def _read_tag(ds: FileDataset, tag: VFTag, parse_tag: Callable[[Any], T]) -> T:
    return parse_tag(ds[tag.value].value)


def _parse_significance(significance: str) -> float:
    if significance == "Not Significant":
        # It's possible that the other parsers encode this as 0, but we haven't spent long investigating this, see also
        # comment on VisualFieldData.
        return -1

    # We've seen both lowercase and uppercase P used for the significance
    result = re.search("P < (.*)%", significance, re.IGNORECASE)

    if not result:
        raise ValueError(f"Could not parse significance from string: {significance}")

    return float(result.group(1))
