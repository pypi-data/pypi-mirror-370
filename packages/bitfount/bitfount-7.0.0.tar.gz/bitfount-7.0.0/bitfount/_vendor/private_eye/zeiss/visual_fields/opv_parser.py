import logging
from math import isclose, pi
from typing import Any, Callable, List, Optional, TypeVar, cast

from more_itertools import one, only
from ....private_eye import Laterality, ParserOptions
from ....private_eye.data import (
    GoldmannStimulus,
    VisualFieldData,
    VisualFieldPatientClinicalInformation,
    VisualFieldReliabilityIndex,
    VisualFieldStorageType,
    VisualFieldTestPoint,
    VisualFieldTestPointNormals,
)
from pydicom import Dataset

logger = logging.getLogger(__name__)


def parse_opv_data(ds: Dataset, _: ParserOptions) -> VisualFieldData:
    normals_elem = one(ds.ResultsNormalsSequence)

    return VisualFieldData(
        storage_type=VisualFieldStorageType.OPV,
        source_id=str(ds.SOPInstanceUID),
        modality="Static",  # DICOM does not support kinetic perimetry
        left_eye_patient_clinical_information=_patient_clinical_information(ds, Laterality.LEFT),
        right_eye_patient_clinical_information=_patient_clinical_information(ds, Laterality.RIGHT),
        protocol=_protocol(ds),
        strategy=_strategy(ds),
        fixation_loss=_fixation_loss(ds),
        false_positive_errors=_false_positives(ds),
        false_negative_errors=_false_negatives(ds),
        visual_field_index=_visual_field_index(ds),
        glaucoma_hemifield_test=_glaucoma_hemifield_test(ds),
        mean_deviation=normals_elem.GlobalDeviationFromNormal,
        mean_deviation_significance=one(normals_elem.GlobalDeviationProbabilitySequence).GlobalDeviationProbability,
        pattern_standard_deviation=normals_elem.LocalizedDeviationFromNormal,
        pattern_standard_deviation_significance=one(
            normals_elem.LocalizedDeviationProbabilitySequence
        ).LocalizedDeviationProbability,
        test_duration=ds.VisualFieldTestDuration,
        fixation_monitors=_fixation_monitors(ds),
        stimulus_size=_stimulus_size(ds),
        stimulus_colour=_stimulus_colour(ds),
        background_luminance=_background_luminance(ds),
        foveal_sensitivity=_foveal_sensitivity(ds),
        visual_field_data=[_visual_field_test_point(ds, p) for p in ds.VisualFieldTestPointSequence],
    )


def _patient_clinical_information(
    ds: Dataset, laterality: Laterality
) -> Optional[VisualFieldPatientClinicalInformation]:

    if laterality == Laterality.RIGHT:
        ophthalmic_information = _get_optional_attribute(ds, "OphthalmicPatientClinicalInformationRightEyeSequence")
        ophthalmic_information = one(ophthalmic_information) if ophthalmic_information else None
    elif laterality == Laterality.LEFT:
        ophthalmic_information = _get_optional_attribute(ds, "OphthalmicPatientClinicalInformationLeftEyeSequence")
        ophthalmic_information = one(ophthalmic_information) if ophthalmic_information else None
    else:
        return None

    if not ophthalmic_information:
        return None
    refractive_information = only(ophthalmic_information.RefractiveParametersUsedOnPatientSequence)

    return VisualFieldPatientClinicalInformation(
        rx_ds=refractive_information.SphericalLensPower if refractive_information else None,
        rx_dc=refractive_information.CylinderLensPower if refractive_information else None,
        rx_axis=refractive_information.CylinderAxis if refractive_information else None,
        pupil_diameter=ophthalmic_information.PupilSize,
    )


def _protocol(ds: Dataset) -> Optional[str]:
    # Per the spec, the word 'Pattern' will always be present in a VF protocol
    return only(x.CodeMeaning for x in ds.PerformedProtocolCodeSequence if "Pattern" in x.CodeMeaning)


def _strategy(ds: Dataset) -> Optional[str]:
    # Per the spec, the word 'Strategy' will always be present in a VF strategy
    return only(x.CodeMeaning for x in ds.PerformedProtocolCodeSequence if "Strategy" in x.CodeMeaning)


def _fixation_loss(ds: Dataset) -> VisualFieldReliabilityIndex:
    fixation_elem = one(ds.FixationSequence)
    return VisualFieldReliabilityIndex(
        numerator=fixation_elem.PatientNotProperlyFixatedQuantity, denominator=fixation_elem.FixationCheckedQuantity
    )


def _false_positives(ds: Dataset) -> VisualFieldReliabilityIndex:
    catch_trial_elem = one(ds.VisualFieldCatchTrialSequence)
    return VisualFieldReliabilityIndex(numerator=round(catch_trial_elem.FalsePositivesEstimate), denominator=100)


def _false_negatives(ds: Dataset) -> VisualFieldReliabilityIndex:
    catch_trial_elem = one(ds.VisualFieldCatchTrialSequence)
    return VisualFieldReliabilityIndex(numerator=round(catch_trial_elem.FalseNegativesEstimate), denominator=100)


def _concept_name(row: Any) -> str:
    data_observation = one(row.DataObservationSequence)
    concept_name = one(data_observation.ConceptNameCodeSequence)
    return cast(str, concept_name.CodeMeaning)


def _visual_field_index(ds: Dataset) -> Optional[int]:
    if "VisualFieldGlobalResultsIndexSequence" not in ds:
        return None

    return only(
        [
            int(one(row.DataObservationSequence).NumericValue)
            for row in ds.VisualFieldGlobalResultsIndexSequence
            if _concept_name(row) == "Visual Field Index"
        ]
    )


def _glaucoma_hemifield_test(ds: Dataset) -> Optional[str]:
    if "VisualFieldGlobalResultsIndexSequence" not in ds:
        return None

    return only(
        [
            one(one(row.DataObservationSequence).ConceptCodeSequence).CodeMeaning
            for row in ds.VisualFieldGlobalResultsIndexSequence
            if _concept_name(row) == "Glaucoma Hemifield Test Analysis"
        ]
    )


# See http://webeye.ophth.uiowa.edu/ips/GEN-INFO/standards/IPS90.HTM
_goldmann_stimuli = {
    0.25: GoldmannStimulus.I,
    1.0: GoldmannStimulus.II,
    4.0: GoldmannStimulus.III,
    16.0: GoldmannStimulus.IV,
    64.0: GoldmannStimulus.V,
}


def _stimulus_size(ds: Dataset) -> GoldmannStimulus:
    # In DICOM files, the stimulus area is measured in square degrees. The stimulus is 300mm from the eye.
    # We want to convert to standard Goldmann stimuli, which are defined in mm^2

    area = (300**2) * ds.StimulusArea * (pi / 180) ** 2

    try:
        # Accept anything within 5% of a standard size
        return one(label for size, label in _goldmann_stimuli.items() if isclose(area, size, rel_tol=0.05))

    except ValueError:
        logger.warning("Unable to map stimulus area to Goldmann stimulus size")
        return GoldmannStimulus.UNKNOWN


def _stimulus_colour(ds: Dataset) -> Optional[str]:
    return only(color.CodeMeaning for color in ds.StimulusColorCodeSequence)


def _background_luminance(ds: Dataset) -> float:
    # DICOM sensibly stores luminance in SI units (cd m^-2). We want to output values in apostlib (asb)
    # To convert, multiply by pi
    return cast(float, ds.BackgroundLuminance * pi)


def _foveal_sensitivity(ds: Dataset) -> Optional[float]:
    if ds.FovealSensitivityMeasured == "YES":
        return cast(float, ds.FovealSensitivity)
    return None


def _fixation_monitors(ds: Dataset) -> List[str]:
    monitoring_code_sequence = one(ds.FixationSequence).FixationMonitoringCodeSequence
    return [monitoring_code.CodeMeaning for monitoring_code in monitoring_code_sequence]


def _visual_field_test_point(ds: Dataset, point: Dataset) -> VisualFieldTestPoint:
    return VisualFieldTestPoint(
        x_coord=float(point.VisualFieldTestPointXCoordinate),
        y_coord=float(point.VisualFieldTestPointYCoordinate),
        stimulus_results=point.StimulusResults,
        sensitivity=float(point.SensitivityValue),
        retest_stimulus_seen=point.get("RetestStimulusSeen", None),
        retest_sensitivity=point.get("RetestSensitivityValue", None),
        normals=_build_normals(point),
    )


def _build_normals(point: Dataset) -> Optional[VisualFieldTestPointNormals]:
    if point.VisualFieldTestPointNormalsSequence is None:
        return None

    normals_sequence = one(point.VisualFieldTestPointNormalsSequence)

    return VisualFieldTestPointNormals(
        age_corrected_sensitivity_deviation=float(normals_sequence.AgeCorrectedSensitivityDeviationValue),
        age_corrected_sensitivity_deviation_probability=float(
            normals_sequence.AgeCorrectedSensitivityDeviationProbabilityValue
        ),
        generalized_defect_corrected_sensitivity_deviation=_get_optional_value(
            normals_sequence, "GeneralizedDefectCorrectedSensitivityDeviationValue", float
        ),
        generalized_defect_corrected_sensitivity_deviation_probability=_get_optional_value(
            normals_sequence, "GeneralizedDefectCorrectedSensitivityDeviationProbabilityValue", float
        ),
    )


def _get_optional_attribute(dataset: Dataset, attribute: str) -> Optional[Any]:
    try:
        return dataset[attribute]
    except KeyError:
        return None


TIn = TypeVar("TIn")
TOut = TypeVar("TOut")


def _get_optional_value(dataset: Dataset, attribute: str, type_converter: Callable[[TIn], TOut]) -> Optional[TOut]:
    try:
        raw_value = dataset[attribute]
    except KeyError:
        return None

    return type_converter(raw_value.value)
