def parse_config(gear_context):
    """Parses gear_context config.

    Args:
        gear_context (flywheel_gear_toolkit.GearToolkitContext): context


    Returns:
        (tuple): tuple containing
            - input file path
            - input filename
            - treshold percentile
            - inversion of image
    """

    input_filepath = gear_context.get_input_path("dicom")
    input_filename = gear_context.get_input_filename("dicom_input")

    threshold_percentile = gear_context.config["threshold_percentile"]
    invert_image = gear_context.config["invert_image"]

    return input_filepath, input_filename, threshold_percentile, invert_image
