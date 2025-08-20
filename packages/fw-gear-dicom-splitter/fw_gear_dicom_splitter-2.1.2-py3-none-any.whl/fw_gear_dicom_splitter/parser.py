"""Parser module to parse gear config.json."""

import typing as t
from dataclasses import dataclass
from pathlib import Path

import flywheel
from flywheel_gear_toolkit import GearToolkitContext


@dataclass
class GearArgs:
    """Arguments to be used for dicom-splitter processing.

    dicom_path: Path of DICOM input file
    output_dir: Path to output directory
    extract_localizer: Whether to split out localizers
    group_by: List of unique tags to split archive on
    max_geom_splits: Max # of geometric splits
    zip_single: Whether to zip single dicoms
    delete_input: Whether to delete input after successful split
    filter_archive: Whether to filter out invalid DICOMs in archive
    delete_reason: Reason for deleting input file (for validated instances)
    """

    dicom_path: Path
    output_dir: Path
    extract_localizer: bool
    group_by: t.List[str]
    max_geom_splits: int
    zip_single: bool
    delete_input: bool
    filter_archive: bool
    delete_reason: flywheel.ContainerDeleteReason


def parse_config(
    gear_context: GearToolkitContext,
) -> GearArgs:
    """Parses gear_context config.json file.

    Returns:
        GearArgs: dataclass of argument values to be used by the gear
    """

    zip_single_raw = gear_context.config.get("zip-single-dicom", "match")
    # Zip single is set to True on "match", False otherwise ("no")
    zip_single = zip_single_raw == "match"

    if gear_context.config.get("group_by", ""):
        group_by = gear_context.config.get("group_by").split(",")
    else:
        group_by = []

    # Validate delete reason early to fail fast on invalid values
    delete_reason_str = gear_context.config.get("delete-reason")
    try:
        delete_reason = flywheel.ContainerDeleteReason(delete_reason_str)
    except ValueError as e:
        valid_reasons = [reason.value for reason in flywheel.ContainerDeleteReason]
        raise ValueError(
            f"Invalid delete reason '{delete_reason_str}'. "
            f"Valid options are: {valid_reasons}"
        ) from e

    gear_args = GearArgs(
        dicom_path=Path(gear_context.get_input_path("dicom")),
        output_dir=gear_context.output_dir,
        extract_localizer=gear_context.config.get("extract_localizer"),
        zip_single=zip_single,
        group_by=group_by,
        max_geom_splits=gear_context.config.get("max_geometric_splits"),
        delete_input=gear_context.config.get("delete_input"),
        filter_archive=gear_context.config.get("filter_archive"),
        delete_reason=delete_reason,
    )

    return gear_args
