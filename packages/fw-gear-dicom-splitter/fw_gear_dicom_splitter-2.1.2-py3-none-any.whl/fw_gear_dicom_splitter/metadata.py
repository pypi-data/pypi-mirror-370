"""Metadata handling."""

import datetime
import logging
import typing as t
from collections import Counter
from pathlib import Path

from flywheel_gear_toolkit import GearToolkitContext
from fw_file.dicom import DICOMCollection
from fw_file.dicom.utils import generate_uid
from fw_meta.imports import load_file_name
from pydicom.dataset import Dataset
from pydicom.sequence import Sequence

from . import __version__, pkg_name

log = logging.getLogger(__name__)

VERSION = __version__.split(".")


class SeriesName:
    def __init__(  # noqa: PLR0913
        self,
        series_number: t.Optional[str],
        modality: t.Optional[str],
        series_description: t.Optional[str],
        number: t.Optional[int],
        localizer: bool = False,
        group_by_str: t.Optional[str] = None,
    ):
        self.series_number = series_number
        self.modality = modality
        self.series_description = series_description
        self.number = number
        self.localizer = localizer
        self.group_by_str = group_by_str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SeriesName):
            return NotImplemented
        return repr(self) == repr(other)

    def __hash__(self) -> int:
        return hash(repr(self))

    @classmethod
    def gen_name(
        cls,
        dcm: DICOMCollection,
        series_number: t.Optional[str] = None,
        number: t.Optional[int] = None,
        group_by: t.Optional[list[str]] = None,
    ) -> "SeriesName":
        """Generate a SeriesName from a collection and optional series number.

        Args:
            dcm (DICOMCollection): DICOM archive
            series_number (t.Optional[str]): Optional series number.

        Returns:
            SeriesName: SeriesName object.
        """
        series_description: t.Optional[str] = Counter(
            dcm.bulk_get("SeriesDescription")
        ).most_common()[0][0]

        modality: t.Optional[str] = Counter(dcm.bulk_get("Modality")).most_common()[0][
            0
        ]
        if not series_number:
            series_number = Counter(dcm.bulk_get("SeriesNumber")).most_common()[0][0]

        group_by_str = group_by_to_str(dcm, group_by)

        return cls(
            series_number, modality, series_description, number, False, group_by_str
        )

    @classmethod
    def from_name(cls, other: "SeriesName"):
        return cls(
            other.series_number,
            other.modality,
            other.series_description,
            other.number,
            other.localizer,
            other.group_by_str,
        )

    def __repr__(self) -> str:
        s_num = "series-1"
        if self.series_number:
            s_num = f"series-{self.series_number}"
        mod = f"_{self.modality}" if self.modality else ""
        descr = f"_{self.series_description}" if self.series_description else ""
        groupby = f"_{self.group_by_str}" if self.group_by_str else ""
        num = f"_{self.number}" if self.number else ""
        name = s_num + mod + descr + groupby + num
        if self.localizer:
            name += "_localizer"
        return load_file_name(name)


def add_contributing_equipment(dcm: DICOMCollection) -> None:
    """Helper function to populate ContributingEquipmentSequence."""
    cont_dat = Dataset()
    cont_dat.Manufacturer = "Flywheel"
    cont_dat.ManufacturerModelName = pkg_name
    cont_dat.SoftwareVersions = ".".join(VERSION)

    for dcm_slice in dcm:
        raw = dcm_slice.dataset.raw
        if not raw.get("ContributingEquipmentSequence"):
            raw.ContributingEquipmentSequence = Sequence()
        raw.ContributingEquipmentSequence.append(cont_dat)


def update_modified_attributes_sequence(
    dcm: DICOMCollection,
    modified: t.Dict[str, t.Any],
    mod_system: str = "fw_gear_dicom_splitter",
    source: t.Optional[str] = None,
    reason: str = "COERCE",
) -> None:
    """Update modified attributes sequence for a collection.

    Args:
        dcm (DICOMCollection): Collection to modify
        modified (t.Dict[str, Any]): key and value pairs to set.
        mod_system (t.Optional[str], optional): System doing modification.
            Defaults to None.
        source (t.Optional[str], optional): Original source of data.
            Defaults to None.
        reason (str, optional): Reason for modifying, either 'COERCE',
            or 'CORRECT' in order to comply with DICOM standard.
                Defaults to 'COERCE'.
    """
    # Modified attributes dataset
    mod_dat = Dataset()
    for key, value in modified.items():
        setattr(mod_dat, key, value)
    # Original attributes dataset
    orig_dat = Dataset()
    # Add Modified attributes dataset as a sequence
    orig_dat.ModifiedAttributesSequence = Sequence([mod_dat])
    if mod_system:
        orig_dat.ModifyingSystem = mod_system
    if source:
        orig_dat.SourceOfPreviousValues = source
    orig_dat.ReasonForTheAttributeModification = reason
    curr_dt = datetime.datetime.now().astimezone()
    curr_dt_str = curr_dt.strftime("%Y%m%d%H%M%S.%f%z")
    orig_dat.AttributeModificationDateTime = curr_dt_str

    for dcm_slice in dcm:
        # Append original attributes sequence dataset for each dicom
        #   in archive
        raw = dcm_slice.dataset.raw

        if not raw.get("OriginalAttributesSequence", None):
            raw.OriginalAttributesSequence = Sequence()
        raw.OriginalAttributesSequence.append(orig_dat)


def gen_series_uid(dcm: DICOMCollection) -> str:
    """Simple helper to generate and set 64-character uid."""
    uid = generate_uid()
    dcm.set("SeriesInstanceUID", uid)
    return uid


def populate_qc(
    context: GearToolkitContext, file_name: str, split: bool, success: bool
) -> None:
    """Utility to populate splitter specific qc info on an output filename.

    Args:
        context: GearToolkitContext of gear run
        file_name: Input DICOM filename as string
        split: Whether DICOM archive was split
        success: Whether processing of input DICOM was successful
    """
    dicom = context.get_input("dicom")
    get_parent_fn = getattr(context.client, f"get_{dicom['hierarchy']['type']}")
    parent = get_parent_fn(dicom["hierarchy"]["id"])
    orig = parent.get_file(dicom["location"]["name"])

    original = {
        "original": {
            "filename": orig.name,
            "file_id": getattr(orig, "file_id", ""),
        }
    }

    context.metadata.add_qc_result(
        file_name,
        "split",
        state=("PASS" if success else "FAIL"),
        data=(original if split else {}),
    )


def populate_tags(
    context: GearToolkitContext,
    output_paths: t.Tuple,
    set_deleted: t.Optional[str] = None,
) -> None:
    """Populate splitter specific tags on output files and input file.

    Args:
        context: GearToolkitContext of gear run
        output_paths: Tuple of paths to created output files
        set_deleted: Whether input file was deleted or retained, None if not split
    """

    tag: str = context.config.get("tag", "")
    tag_single: str = context.config.get("tag-single-output", "")

    if not set_deleted:
        # set_deleted==None occurs when the DICOM was not split.
        # Here, the input file is simply tagged with the configured tag(s)
        context.metadata.add_file_tags(context.get_input("dicom"), [tag])
    else:
        # If set_deleted is not None, the DICOM was split.
        if set_deleted == "retained":
            # Input file is tagged with configured tags as well as "delete",
            # to match gear functioning before gear rules r/w was supported.
            input_tags = [tag]
            input_tags.append("delete")
            context.metadata.add_file_tags(context.get_input("dicom"), input_tags)
        # If set_deleted == "deleted", the input file no longer exists,
        # so there is no input file to tag and we move on.

        # Output files are sorted alphabetically by file name
        paths = sorted(list(output_paths))
        for i, path in enumerate(paths):
            file_ = Path(path).name
            tags = [tag]
            if i == 0 and len(tag_single) > 0:
                tags.append(tag_single)
            context.metadata.add_file_tags(file_, tags)


def update_localizer_frames(
    dcm: DICOMCollection,
    orig_series_uid: t.Optional[str],
    orig_series_num: t.Optional[str],
    keep_series_uid: bool = False,
) -> str:
    """Updates localizer frames modified attributes sequence and sets SeriesNumber.

    Args:
        dcm: DICOM archive
        orig_series_uid: Original SeriesUID
        orig_series_num: Original SeriesNumber
        keep_series_uid: Whether to keep SeriesUID or generate new UID

    Returns:
        str: New SeriesNumber
    """
    log.info(
        "Updating modified attributes sequence with original "
        + f"SeriesInstanceUID: {orig_series_uid}, "
        + f"original SeriesNumber: {orig_series_num}",
    )
    update_modified_attributes_sequence(
        dcm,
        modified={
            "SeriesInstanceUID": orig_series_uid,
            "SeriesNumber": orig_series_num,
        },
    )
    new_series_uid = orig_series_uid if keep_series_uid else gen_series_uid(dcm)
    new_series_num = int(orig_series_num or 1) + 1000
    dcm.set("SeriesNumber", new_series_num)
    log.info(
        f"Adding new SeriesInstanceUID: {new_series_uid}"
        + f", SeriesNumber: {new_series_num}"
    )
    return str(new_series_num)


def group_by_to_str(dcm: DICOMCollection, group_by: t.Optional[t.List[str]]):
    """Create list of group_by tags and values to be appended to output filaname.
    Do not include SeriesInstanceUID/SeriesNumber in this list.
    See GEAR-3401.

    Args:
        dcm (DICOMCollection): DICOMCollection
        group_by (list[str]): List of tags we are splitting on

    Returns:
        str: String describing group_by tags, starts and ends with "_". Meant
            to be included in output filename.
    """
    if not group_by:
        return ""

    to_remove = {"SeriesInstanceUID", "SeriesNumber"}
    group_by = set(group_by) - to_remove

    return "_".join([f"{tag}-{dcm.get(tag)}" for tag in group_by])
