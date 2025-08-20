"""Algorithms for Electronic Health Records (EHR) data.

This package contains implementations of algorithms specifically designed for working
with Electronic Health Records (EHR) data.
"""

from bitfount.federated.algorithms.ehr.ehr_patient_query_algorithm import (
    EHRPatientQueryAlgorithm,
    PatientDetails,
    PatientQueryResults,
)

__all__ = [
    "EHRPatientQueryAlgorithm",
    "PatientDetails",
    "PatientQueryResults",
]
