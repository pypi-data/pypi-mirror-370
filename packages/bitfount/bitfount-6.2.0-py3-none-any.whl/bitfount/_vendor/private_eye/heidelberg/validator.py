import logging
from typing import Callable, List

from ...private_eye.exceptions import ImageParseException
from ...private_eye.heidelberg.data import DbFiles, Segment
from ...private_eye.heidelberg.parser.segment.image import BScanImageSegment, PhotoImageSegment

_rules = []


logger = logging.getLogger(__name__)


def rule(func: Callable[[DbFiles], List[str]]) -> Callable[[DbFiles], List[str]]:
    _rules.append(func)
    return func


def validate(db_files: DbFiles) -> None:
    errors: List[str] = []
    for _rule in _rules:
        new_errors = _rule(db_files)
        logger.debug("Running rule %s", _rule)
        logger.debug("Found errors %s", new_errors)
        errors.extend(new_errors)

    if len(errors) > 0:
        raise ImageParseException(f"Unable to validate heidelberg files: {errors}")


@rule
def patient_ids_match(db_files: DbFiles) -> List[str]:
    patient_id = db_files.sdb.standard_metadata.patient_id
    errors = []
    if db_files.edb.standard_metadata.patient_id != patient_id:
        errors.append("EDB patient ID doesn't match SDB patient ID")
    if db_files.pdb.standard_metadata.patient_id != patient_id:
        errors.append("PDB patient ID doesn't match SDB patient ID")
    return errors


@rule
def exam_id_matches(db_files: DbFiles) -> List[str]:
    exam_id = db_files.sdb.standard_metadata.exam_id
    if db_files.edb.standard_metadata.exam_id != exam_id:
        return ["EDB exam ID doesn't match that in SDB"]
    return []


@rule
def identical_fundus_details(db_files: DbFiles) -> List[str]:
    segment: Segment[PhotoImageSegment]
    fundus_details = [
        (segment.body.width, segment.body.height) for segment in db_files.sdb.segments.get(PhotoImageSegment, [])
    ]
    if not all(fundus_details[0] == fundus_detail for fundus_detail in fundus_details):
        return ["Not all fundus images have the same details"]
    return []


@rule
def identical_tomogram_details(db_files: DbFiles) -> List[str]:
    segment: Segment[BScanImageSegment]
    tomogram_details = [
        (segment.body.width, segment.body.height) for segment in db_files.sdb.segments.get(BScanImageSegment, [])
    ]
    if not all(tomogram_details[0] == detail for detail in tomogram_details):
        return ["Not all tomogram images have the same details"]
    return []
