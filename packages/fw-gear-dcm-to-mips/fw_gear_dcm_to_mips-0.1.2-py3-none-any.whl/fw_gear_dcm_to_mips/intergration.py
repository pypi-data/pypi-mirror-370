"""Converter main interface"""

import logging
import os

from fw_gear_dcm2niix.dcm2niix import dcm2niix_run, prepare
from fw_gear_dcm2niix.utils import parse_config
from fw_gear_nifti_to_mips import converter

log = logging.getLogger(__name__)


def run_dcm_2_niix_gear(gear_context):
    # Prepare dcm2niix input, which is a directory of dicom or parrec images
    gear_args = parse_config.generate_prep_args(gear_context)
    dcm2niix_input_dir = prepare.setup(**gear_args)

    # Run dcm2niix
    gear_args = parse_config.generate_dcm2niix_args(gear_context)

    output = dcm2niix_run.convert_directory(
        dcm2niix_input_dir, gear_context.work_dir, **gear_args
    )

    return output


def convert_dcm_to_niix(gear_context):
    """Convert dicom input file to nifti file.

    Args:
        gear_context (flywheel_gear_toolkit.GearToolkitContext): Gear toolkit Context

    Returns:
        list: List of nifti files that are converted from the dicom input file. Return None if there is not converted_files.
    """
    output = run_dcm_2_niix_gear(gear_context)

    # Nipype interface converted_files from dcm2niix can be a string or list (desired)
    try:
        converted_files = output.outputs.converted_files
        if isinstance(converted_files, str):
            converted_files = [converted_files]

    except AttributeError:
        log.info("No outputs were produced from dcm2niix tool.")
        converted_files = None

    else:
        log.info(f"Returning converted file(s)... {converted_files}")

    return converted_files


def run(gear_context, output_dir, threshold_percentile, invert_image):
    """

    Args:
        gear_context (flywheel_gear_toolkit.GearToolkitContext): Gear toolkit Context
        output_dir (GearToolkitContext.output_dir): Output directory for gear outputs
        threshold_percentile (float): The percentile cutoff for maximum values
        invert_image (bool): Invert the colors of image file. Default True.
    """

    # Prep dcm 2 niix
    output_niix = convert_dcm_to_niix(gear_context)

    if output_niix is not None and len(output_niix) > 0:
        for output in output_niix:
            log.info(f"Converted DICOM file into NIfTi as {os.path.basename(output)}")
            log.info("--- Processing nifti-to-mips gear ---")
            converter.run(
                output_dir,
                output,
                os.path.basename(output),
                threshold_percentile,
                invert_image,
            )
    else:
        log.info("No output to process. Exiting...")
        os.sys.exit(1)
