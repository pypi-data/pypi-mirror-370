"""Utility functions for federated protocols."""

import logging
from typing import Any

from bitfount.data.datasources.base_source import FileSystemIterableSource
from bitfount.data.datasources.dicom_source import DICOMSource
from bitfount.data.datasources.ophthalmology.ophthalmology_base_source import (
    _OphthalmologySource,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import PATIENT_ID_COL

logger = logging.getLogger(__name__)


def add_patient_metadata_columns(
    row_dict: dict[str, Any], datasource: FileSystemIterableSource, file_path: str
) -> None:
    """Add patient metadata columns to row dict for medical datasources only.

    Specifically, add the patient ID column if available in the datasource's cache.
    This function is used to add the metadata to the error report for failed
    batches/individual files, and should be called at the end of a task. We only
    allow retrieving from cache since at the end of the task all files should have
    been processed and cached. If a specific file is not found then it would indicate
    an issue with the respective file.

    Args:
        row_dict: The dictionary to add columns to
        datasource: The datasource instance
        file_path: File path to extract metadata for
    """
    # Only proceed for datasources that would have this metadata
    if not isinstance(datasource, (DICOMSource, _OphthalmologySource)):
        return

    # Only proceed if datasource has cache
    if not hasattr(datasource, "data_cache") or not datasource.data_cache:
        return

    try:
        # Get cached data for this file
        cached_data = datasource.data_cache.get(file_path)
        if cached_data is None:
            return

        # Always add columns (even if empty) for consistent CSV structure
        patient_id_series = cached_data.get(PATIENT_ID_COL, None)
        row_dict[PATIENT_ID_COL] = (
            str(patient_id_series.iloc[0])
            if patient_id_series is not None and len(patient_id_series) > 0
            else None
        )
    except Exception as e:
        logger.debug(f"Could not extract patient metadata for {file_path}: {e}")
