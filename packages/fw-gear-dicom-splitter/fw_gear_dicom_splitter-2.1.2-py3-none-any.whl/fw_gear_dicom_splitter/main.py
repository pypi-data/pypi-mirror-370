"""Module to run gear."""

import logging
import typing as t
import zipfile
from pathlib import Path

import pandas as pd
from fw_file.dicom import DICOMCollection
from fw_file.dicom.utils import is_dcm, sniff_dcm

from .dicom_splitter.base import SingleSplitter, SplitterError
from .metadata import SeriesName, add_contributing_equipment, update_localizer_frames
from .parser import GearArgs
from .splitters import (
    EuclideanSplitter,
    JensenShannonDICOMSplitter,
    UniqueTagMultiSplitter,
    UniqueTagSingleSplitter,
    split_by_geometry,
)
from .utils import collection_from_df, collection_to_df

# Override dicom validation logging level
validation_log = logging.getLogger("fw_file.dicom.validation")
validation_log.setLevel(logging.INFO)
log = logging.getLogger(__name__)

SCORE_THRESH = 0.5


def run_individual_split(
    splitter: SingleSplitter, dataframe: pd.DataFrame, **kwargs: t.Any
) -> None:
    """Helper function to run one splitter algorithm.

    Args:
        splitter: Initialized SingleSplitter object
        dataframe: DataFrame representing `splitter.files`
    """
    try:
        split = splitter.split(dataframe, **kwargs)
    except SplitterError as e:
        log.error(e.args[0])
        if log.parent.level > logging.DEBUG:  # type: ignore
            log.error("Enable debug to see full stack")
        log.info(
            "Note: JensenShannon splitter is not necessary, but this "
            "failure indicates there is probably something wrong with your "
            "DICOM's PixelData or PixelData attributes."
        )
        log.debug(repr(e), exc_info=True)
        return
    frames_found = split[split["decision"] > 0]
    log.debug(
        "%s found %d localizer frames",
        splitter.__class__.__name__,
        frames_found.shape[0],
    )
    dataframe.loc[dataframe["path"] == split["path"], "score"] += split["decision"]  # type: ignore


def gen_split_score(dcm: DICOMCollection) -> pd.DataFrame:
    """Generate 'voting' score for each frame in DICOM.

    Voting score comes from multiple splitting algorithms and tries to
    find a concensus among these different methods.

    Methods so far:
        1. Split on change in neighboring frames 'ImageOrientationPatient'.
        2. Split on change in neighboring frames 'ImagePositionPatient'.
        3. Split on change in neighboring frames pixel intensity distribution.
        4. Split on unique combo of 'Rows', 'Columns' tags across archive.
        5. Split on unique value of 'ImageType' across archive.

    Args:
        dcm: DICOM archive

    Returns:
        pd.DataFrame: DataFrame representation of DICOM collection and splits
    """
    total: int = 0
    # Need ordering for pairwise splitters
    if all(dcm.bulk_get("InstanceNumber")):
        dcm.sort(key=lambda x: x.InstanceNumber)
        dataframe = collection_to_df(dcm)
        dataframe["score"] = 0

        if all(dcm.bulk_get("ImageOrientationPatient")):
            log.debug(
                "ImageOrientationPatient tag present, attempting localizer split.."
            )
            iop_splitter = EuclideanSplitter(
                dcm, decision_val=30, tag="ImageOrientationPatient"
            )
            run_individual_split(iop_splitter, dataframe)
            total += iop_splitter.decision_val
        else:
            log.debug("ImageOrientationPatient tags not all present.")

        if all(dcm.bulk_get("ImagePositionPatient")):
            log.debug("ImagePositionPatient tag present, attempting localizer split..")
            ipp_splitter = EuclideanSplitter(
                dcm, decision_val=30, tag="ImagePositionPatient"
            )
            run_individual_split(ipp_splitter, dataframe)
            total += ipp_splitter.decision_val
        else:
            log.debug("ImagePositionPatient tags not all present.")

        log.debug("Attempting Jensen-Shannon localizer splitter")
        js_splitter = JensenShannonDICOMSplitter(dcm, decision_val=20)
        try:
            run_individual_split(js_splitter, dataframe)
            total += js_splitter.decision_val
        except RuntimeError:
            log.warning("JensenShannon fit didn't converge. Moving on...")
        except AttributeError:
            log.warning("PixelData not present on one or more slices.  Moving on...")
    else:
        dataframe = collection_to_df(dcm)
        dataframe["score"] = 0
    # Try splitting by rows and columns
    if all(dcm.bulk_get("Rows")) and all(dcm.bulk_get("Columns")):
        log.debug("Row and Column tags present, attempting localizer split...")
        row_col_splitter = UniqueTagSingleSplitter(
            dcm, decision_val=30, tags=["Rows", "Columns"]
        )
        run_individual_split(row_col_splitter, dataframe)
        total += row_col_splitter.decision_val
    else:
        log.debug("Row and Column tags not all present.")

    # Try splitting by image type
    # TODO: Leave out for now, refine heuristic looking specificall for
    # 'LOCALIZER' or other manufacturer specific codewords for Localizer
    # frames.
    #    if all(dcm.bulk_get("ImageType")):
    #        log.debug("ImageType tag present, attempting localizer split..")
    #        image_type_splitter = UniqueTagSingleSplitter(
    #            dcm, tags=["ImageType"]
    #        )
    #        run_individual_split(image_type_splitter, dataframe)
    #        total += image_type_splitter.decision_val
    #    else:
    #        log.debug("Row and Column tags not all present.")

    dataframe["score"] /= total
    return dataframe


def run_split_localizer(
    dcm: DICOMCollection,
) -> t.Tuple[DICOMCollection, ...]:
    """Split localizer from DICOM archive.

    Args:
        dcm (DICOMCollection): DICOM Archive

    Returns:
        t.Tuple[DICOMCollection, ...]: Tuple of DICOM collections,
            first is the main archive, second is the localizer if any.
    """
    if len(dcm) < 2:
        log.warning(
            "Refusing to extract localizer from archive with less than 2 frames."
        )
        return (dcm, DICOMCollection())
    log.debug("Generating splitting score")
    score_dataframe = gen_split_score(dcm)

    dicom_dataframe = score_dataframe[score_dataframe["score"] < SCORE_THRESH]
    localizer_dataframe = score_dataframe[score_dataframe["score"] >= SCORE_THRESH]
    log.debug("Found %d localizer frames", localizer_dataframe.shape[0])

    if localizer_dataframe.shape[0] >= dicom_dataframe.shape[0] * 0.5:
        log.error("Splitting localizer may have failed...")

    dicom_coll = collection_from_df(dcm, dicom_dataframe)
    localizer_coll = collection_from_df(dcm, localizer_dataframe)
    return (dicom_coll, localizer_coll)


def add_phases_to_output(
    outputs: dict,
    collection: DICOMCollection,
    phase_count: int,
    phase_indexes: list[int],
) -> dict:
    """
    Add child collections to output_list derived from phases of the parent collection.

    Args:
        outputs: Dictionary with output filenames as keys and DICOMCollection as values
        collection (DICOMCollection): Parent collection
        phase_count (bool): Number of phases
        phase_indexes (int): Array that maps index to phase

    Returns:
        outputs: Updated outputs dictionary
    """
    secondary = []
    for k in range(phase_count):
        secondary.append(DICOMCollection())
    for image_index in range(len(collection)):
        phase_index = phase_indexes[image_index]
        secondary[phase_index].append(collection[image_index])
    for k in range(phase_count):
        sn = k + 1
        coll = secondary[k]
        name = SeriesName.gen_name(coll, series_number=str(sn))
        outputs[name] = coll
    return outputs


def split_dicom(  # noqa: PLR0912, PLR0915
    dcm: DICOMCollection,
    group_by: t.Optional[t.List[str]],
    split_localizer: bool,
    max_geom_splits: int = -1,
) -> t.Optional[t.Dict[SeriesName, DICOMCollection]]:
    """Split the DICOM archive by tags or localizer.

    Args:
        dcm (DICOMCollection): DICOM archive
        group_by (t.Optional[t.List[str]]): List of tags to split by.
        split_localizer (bool): Whether to split localizer.
        max_geom_splits (int): Maximum number of splits by geometry

    Returns:
        t.Dict[SeriesName, DICOMCollection]: Dictionary with output filenames as
            keys and DICOM collections as values.
    """
    outputs = {}

    if group_by:
        log.info("Attempting group_by split...")
        dataframe = collection_to_df(dcm)
        dataframe["score"] = 0
        tag_splitter = UniqueTagMultiSplitter(dcm, 10, tags=group_by)
        out_dfs = list(tag_splitter.split(dataframe))
        # Sort by number of frames
        out_dfs.sort(key=lambda out_df: out_df.shape[0], reverse=True)
        # GEAR-896, name outputs of group-by consistently with:
        #   {SeriesNumber}-{Modality}-{SeriesDescription}.dicom.zip
        #   and appending a `_{count}` if duplicate name is found
        primary = collection_from_df(dcm, out_dfs[0])
        series = None
        try:
            series = primary.get("SeriesNumber")
        except ValueError:
            # As of 2.0.3, logs a warning and continues instead of returning None
            log.warning("Multiple SeriesNumbers found on primary split.")
        name = SeriesName.gen_name(primary, series_number=series, group_by=group_by)
        log.info("Naming primary collection: %s", str(name))
        outputs[name] = primary
        if len(out_dfs) > 1:
            for i, out_df in enumerate(out_dfs[1:]):
                secondary = collection_from_df(dcm, out_df)
                series = None
                try:
                    series = secondary.get("SeriesNumber")
                except ValueError:
                    # As of 2.0.3, logs a warning and continues instead of returning None
                    log.warning("Multiple SeriesNumbers found on secondary split.")
                name = SeriesName.gen_name(
                    secondary,
                    series_number=(series if series else str(i + 1000)),
                    group_by=group_by,
                )
                counter = 1
                while name in outputs:
                    name.number = counter
                    counter += 1
                log.info("Added secondary collection named: %s", str(name))
                outputs[name] = secondary

    geometric_split = False
    if max_geom_splits > 0 and not outputs:
        # Geometric split is only attempted if configured and no group_by splits
        log.info("Attempting geometric split...")
        phase_count, indexes = split_by_geometry(dcm, max_split_count=max_geom_splits)
        if phase_count is not None and phase_count > 1:
            add_phases_to_output(outputs, dcm, phase_count, indexes)
            geometric_split = True
            log.info("Split by geometry completed.")
        if not phase_count:
            log.warning(
                "One or more slices does not have ImagePositionPatient and/or "
                "ImageOrientationPatient data. Cannot split by geometry."
            )

    if len(outputs) == 0:
        # Add input to outputs dict to have localizer split
        series = None
        try:
            series = dcm.get("SeriesNumber")
        except ValueError:
            # As of 2.0.3, logs a warning and continues instead of returning None
            log.warning("Multiple SeriesNumbers found.")
        name = SeriesName.gen_name(
            dcm, series_number=series if series else None, group_by=group_by
        )
        outputs[name] = dcm

    if len(outputs) > 1:
        # Generating unique attributes for the new grouped series
        # Don't generate new SeriesInstanceUID if groupby contains SeriesInstanceUID
        for name, collection in outputs.items():
            orig_series_uid = collection.get("SeriesInstanceUID")
            orig_series_num = name.series_number
            keep_suid = "SeriesInstanceUID" in group_by
            update_localizer_frames(
                collection, orig_series_uid, orig_series_num, keep_suid
            )

    if split_localizer and not geometric_split:
        log.info("Attempting to extract localizers...")
        # <dcm>.get() will raise ValueError if there are multiple unique values.
        #   let it raise here.
        localizer_outputs = {}
        for name, archive in outputs.items():
            # split_localizer only available for MR or CT modalities
            if archive.get("Modality") not in ["MR", "CT"]:
                log.info(
                    "Split localizer option is only applicable for MR or CT DICOMs. "
                    "%s DICOM modality is %s.",
                    name,
                    archive.get("Modality"),
                )
            else:
                log.info("Splitting collection %s", name)
                dicom, localizer = run_split_localizer(archive)
                localizer_outputs[name] = dicom
                if localizer and len(localizer) > 0:
                    log.info("Found %s localizer frame(s)", str(len(localizer)))
                    orig_series_uid = dicom.get("SeriesInstanceUID")
                    orig_series_num = name.series_number
                    new_series_num = update_localizer_frames(
                        localizer, orig_series_uid, orig_series_num, False
                    )
                    new_name = SeriesName.from_name(name)
                    new_name.series_number = new_series_num
                    new_name.localizer = True
                    localizer_outputs[new_name] = localizer
        outputs.update(localizer_outputs)

    return outputs


# Most of this function is already tested in fw_file
def run(gear_args: GearArgs) -> t.Tuple[t.Tuple[Path, ...], bool]:  # pragma: no cover
    """Main function of module.

    Args:
        GearArgs: dataclass of argument values to be used by the gear

    Returns:
        t.Tuple[Path]: Tuple of saved output paths.
        bool: Whether or not splitter completed successfully
    """
    if sniff_dcm(gear_args.dicom_path):
        log.info("Input is a single DICOM, nothing to split. Exiting")
        return tuple(), True
    if not zipfile.is_zipfile(gear_args.dicom_path):
        log.info("Not a zip file, nothing to split. Exiting")
        return tuple(), True
    with DICOMCollection.from_zip(
        gear_args.dicom_path, force=True, stop_when=None
    ) as dcm:
        filtered = False
        original_filecount = len(dcm)
        if gear_args.filter_archive:
            dcm.filter(is_dcm)
            if len(dcm) != original_filecount:
                filtered = True
                log.warning(
                    f"{(original_filecount - len(dcm))} invalid DICOM files found "
                    "in archive. These files will not be included in output."
                )
        suffix = ".dicom.zip"
        # Don't try to split if there is only one slice.
        if len(dcm) == 1:
            log.info("Only one slice present in archive.")
            return tuple(), True

        collections = split_dicom(
            dcm,
            gear_args.group_by,
            gear_args.extract_localizer,
            gear_args.max_geom_splits,
        )
        # If collections = None, splitter encountered an error (see log)
        if not collections:
            log.info("Archive was not split due to an error.")
            return tuple(), False
        # If nothing was split out
        elif len(collections.items()) in (0, 1) and not filtered:
            log.info("Archive was not split; nothing to split was found.")
            # Return an empty tuple
            return tuple(), True
        # Otherwise populate output dir and return saved paths.
        save_paths = []
        for name, collection in collections.items():
            log.info(
                "Adding contributing equipment to collection: %s",
                str(name),
            )
            add_contributing_equipment(collection)

            if len(collection) > 1 or gear_args.zip_single:
                # save and name
                save_path = gear_args.output_dir / (str(name) + suffix)
                log.info(f"Saving {name} to {save_path}")
                save_paths.append(save_path)
                collection.to_zip(save_path)
            else:
                # remove .zip when only one slice in DICOMCollection
                suffix = suffix.replace(".zip", "")
                save_path = gear_args.output_dir / (str(name) + suffix)
                log.info(f"Saving {name} to {save_path}")
                save_paths.append(save_path)
                collection[0].save(save_path)

        return tuple(save_paths), True
