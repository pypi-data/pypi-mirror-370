try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

_thumb_dir = files("photonforge").joinpath("thumbnails")

thumbnails: dict[bytes, str] = {
    b"bend": _thumb_dir.joinpath("bend.svg").read_text(),
    b"bondpad": _thumb_dir.joinpath("bondpad.svg").read_text(),
    b"crossing": _thumb_dir.joinpath("crossing.svg").read_text(),
    b"dc": _thumb_dir.joinpath("dc.svg").read_text(),
    b"edge-coupler": _thumb_dir.joinpath("edge-coupler.svg").read_text(),
    b"electrical-termination": _thumb_dir.joinpath("electrical-termination.svg").read_text(),
    b"eo-ps": _thumb_dir.joinpath("eo-ps.svg").read_text(),
    b"grating-coupler": _thumb_dir.joinpath("grating-coupler.svg").read_text(),
    b"mmi": _thumb_dir.joinpath("mmi.svg").read_text(),
    b"mmr": _thumb_dir.joinpath("mmr.svg").read_text(),
    b"mzm": _thumb_dir.joinpath("mzm.svg").read_text(),
    b"photodiode": _thumb_dir.joinpath("photodiode.svg").read_text(),
    b"psgc": _thumb_dir.joinpath("psgc.svg").read_text(),
    b"psr": _thumb_dir.joinpath("psr.svg").read_text(),
    b"ring-filter": _thumb_dir.joinpath("ring-filter.svg").read_text(),
    b"s-bend": _thumb_dir.joinpath("s-bend.svg").read_text(),
    b"taper": _thumb_dir.joinpath("taper.svg").read_text(),
    b"termination": _thumb_dir.joinpath("termination.svg").read_text(),
    b"to-ps": _thumb_dir.joinpath("to-ps.svg").read_text(),
    b"transition": _thumb_dir.joinpath("transition.svg").read_text(),
    b"wdm": _thumb_dir.joinpath("wdm.svg").read_text(),
    b"wg": _thumb_dir.joinpath("wg.svg").read_text(),
    b"y-splitter": _thumb_dir.joinpath("y-splitter.svg").read_text(),
}
