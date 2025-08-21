import re
from typing import Callable, List, Tuple

from ...private_eye import ImageModality

Rule = Callable[[str, List[str]], bool]


PROC_NAME_OVERRIDES = {
    "colour_d2xs": ImageModality.UNKNOWN,  # Confirmed to contain face photos as well as fundus images
    "blue_rtc_870955": ImageModality.REFLECTANCE_BLUE,
    "cf12_rtc_870955": ImageModality.COLOUR_PHOTO,
    "fag": ImageModality.FLUORESCEIN_ANGIOGRAPHY,
    "green_cityrd": ImageModality.REFLECTANCE_GREEN,
    "ia_es3200": ImageModality.INDOCYANINE_GREEN_ANGIOGRAPHY,
    "lr_rtc_870955": ImageModality.COLOUR_PHOTO,
    "nw200": ImageModality.COLOUR_PHOTO,
    "nw7_10.0": ImageModality.COLOUR_PHOTO,
    "nw7_fluo10.0": ImageModality.FLUORESCEIN_ANGIOGRAPHY,
    "nw7_icg": ImageModality.INDOCYANINE_GREEN_ANGIOGRAPHY,
    "red": ImageModality.RED,
}


def _any_part_equals(*patterns: str) -> Rule:
    """
    Any of the parts equals one of the given patterns
    """
    return lambda name, parts: any(part in patterns for part in parts)


def _first_part_equals(*patterns: str) -> Rule:
    """
    Specifically the first part equals one of the given patterns
    """
    return lambda name, parts: parts[0] in patterns


def _name_startswith(*patterns: str) -> Rule:
    """
    The full procedure name starts with one of the given patterns
    """
    return lambda name, parts: any(name.startswith(p) for p in patterns)


_rules: List[Tuple[Rule, ImageModality]] = [
    # Imported images in Imagenet2000 can be reports from other scanners instead of the actual images.
    # We do not want these as
    # a) they are useless as images of their given modality and
    # b) they can have identifiable data, which we do NOT want exposed accidentally
    # This rule should always be first
    (_any_part_equals("import", "imported", "montage"), ImageModality.UNKNOWN),
    (_name_startswith("red_free"), ImageModality.RED_FREE),
    (_first_part_equals("cell"), ImageModality.CELL_ANALYSIS),
    (_first_part_equals("slit"), ImageModality.SLIT_LAMP),
    (_first_part_equals("af", "autof", "autofluorescent"), ImageModality.AUTOFLUORESCENCE_GREEN),
    (_first_part_equals("rf", "redfree"), ImageModality.RED_FREE),
    (_first_part_equals("icg"), ImageModality.INDOCYANINE_GREEN_ANGIOGRAPHY),
    (_name_startswith("fluor", "flour", "fluro"), ImageModality.FLUORESCEIN_ANGIOGRAPHY),
    (_first_part_equals("ffa", "fa"), ImageModality.FLUORESCEIN_ANGIOGRAPHY),
    (_first_part_equals("ff", "face"), ImageModality.FACE_PHOTO),
    (_name_startswith("color", "colour"), ImageModality.COLOUR_PHOTO),
    (_any_part_equals("color", "colour", "couleur", "rgb", "photo", "nikon"), ImageModality.COLOUR_PHOTO),
]


def proc_to_modality(proc_name: str) -> ImageModality:
    """
    Procedure names can be quite varied as users are allowed to type in their own.
    However, there are a few patterns that we can match which will catch the majority of entries
    in the MEH Imagenet2000 database.

    The method is as follows:
    1. Make the procedure name lowercase to allow case-insensitive matching
    2. Check the explicit modalities dictionary for any direct matches. These should be reserved for those names
       which do not fit anywhere reasonable.
    3. Standardise the name and split into parts:
        a) Remove and numeric characters and dots. There are many variations on names which simply have a different
           numeric suffix to a common base, e.g. colour_6 and colour_12
        b) Replace any runs of non-letter characters with a standard splitter character, e.g. _
        c) Split into parts using the above character
        d) Remove any parts named 'study'. A few names either start with 'study' or have it in the middle somewhere,
           while having a well-known name elsewhere.
    4. Run the matching rules on the standardised modality name and parts, and return if any matches found
    :param proc_name:
    :return:
    """
    proc_name = proc_name.lower()
    try:
        return PROC_NAME_OVERRIDES[proc_name]
    except KeyError:
        pass

    proc_name = re.sub(r"[\d.]", "", proc_name)
    proc_name = re.sub(r"[^a-z]+", "_", proc_name)
    parts = [p for p in proc_name.split(sep="_") if p and p != "study"]

    for rule, modality in _rules:
        if rule(proc_name, parts):
            return modality

    return ImageModality.UNKNOWN
