import numpy as np
from os.path import exists, join
from .ssrlExport import makeOffsetStr, makeWeightStr


def exportToAthena(
    folder,
    data,
    header,
    namefmt="{sample}_{scan}.dat",
    c1="",
    c2="",
    headerUpdates={},
    strict=False,
    verbose=True,
    increment=False,
):
    """Exports to Graham's ASCII SSRL data format

    :param folder: Export folder (filename will be auto-generated)
    :param data: Numpy array with data of dimensions (npts, ncols)
    :param header: Dictionary with 'scaninfo', 'motors', 'channelinfo' sub-dictionaries
    :param namefmt: Python format string that will be filled with info from 'scaninfo' dictionary
    :param c1: Comment string 1
    :param c2: Comment string 2
    :param headerUpdates: Manual updates for header dictionary (helpful to fill missing info)
    :returns:
    :rtype:

    """

    filename = join(folder, namefmt.format(**header["scaninfo"]))
    if increment:
        base_filename = filename
        i = 1
        while exists(filename):
            filename = base_filename + f"_{i}"

    if verbose:
        print(f"Exporting to {filename}")
    metadata = {}
    metadata.update(header["scaninfo"])
    metadata.update(headerUpdates)
    if strict:
        # Scan can't be list, just pick first value
        if isinstance(metadata["scan"], (list, tuple)):
            metadata["scan"] = metadata["scan"][0]

    motors = {
        "entnslt": 0,
        "exslit": 0,
        "samplex": 0,
        "sampley": 0,
        "samplez": 0,
        "sampler": 0,
    }
    motors.update(header["motors"])
    channelinfo = header["channelinfo"]
    cols = channelinfo.get("cols")
    weights = channelinfo.get("weights", None)
    offsets = channelinfo.get("offsets", None)
    weightStr = makeWeightStr(weights, cols)
    offsetStr = makeOffsetStr(offsets, cols)
    colStr = " ".join(cols)

    metadata["npts"] = data.shape[0]
    metadata["ncols"] = data.shape[1]
    metadata["cols"] = colStr
    metadata["weights"] = weightStr
    metadata["offsets"] = offsetStr
    metadata["rois"] = channelinfo.get("rois", {})
    metadata["c1"] = c1
    metadata["c2"] = c2

    headerstring = """NSLS                                  
{date}
PTS:{npts:11d} COLS: {ncols:11d}
Sample: {sample}   loadid: {loadid}
Command: {command}
Slits: {entnslt:.2f} {exslit:.2f}
Maniplator Position (XYZ): {samplex:.2f} {sampley:.2f} {samplez:.2f} {sampler:.2f}
Scan: {scan}
{c1}
{c2}
Weights:
{weights}
Offsets:
{offsets}
ROIS:
{rois}
-------------------------------------------------------------------------------
{cols}""".format(
        **metadata, **motors
    )
    headerstring = add_comment_to_lines(headerstring, "#")
    with open(filename, "w") as f:
        f.write(headerstring)
        f.write("\n")
        np.savetxt(f, data, fmt=" %8.8e")


def add_comment_to_lines(multiline_string, comment_char="#"):
    """
    Adds a comment character to the beginning of each line in a multiline string.

    Parameters
    ----------
    multiline_string : str
        The input multiline string.

    Returns
    -------
    str
        The multiline string with comment characters added to each line.
    """
    commented_lines = [
        f"{comment_char} " + line for line in multiline_string.split("\n")
    ]
    return "\n".join(commented_lines)
