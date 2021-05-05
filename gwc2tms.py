import re
import shutil
from pathlib import Path

import pandas as pd

GWC_TILE_PATTERN = re.compile(
    "EPSG_3031-GIBS_(?P<matrix>\d+)/\d+_\d+/(?P<col>\d+)_(?P<row>\d+).png"
)
ZYX_OUTPUT_PATTERN = "{output_dir}/{matrix}/{row}/{col}.png"


def _build_tile_index(input_dir):
    """Build dataframe with tiles and x, y, z"""
    input_dir = Path(input_dir)
    tiles = []
    for filepath in input_dir.glob("**/*png"):
        if match := GWC_TILE_PATTERN.search(str(filepath)):
            xyz = {k: int(v) for k, v in match.groupdict().items()}
            tiles.append(dict(filepath=filepath, **xyz))

    df = pd.DataFrame(tiles)

    return df


def gwc2zyx(input_dir, output_dir):
    """Conversion script from GeoWebCache tiles (in e.g. GIBS EPSG:3031 grid) to ZYX indexed tiles for use in ipyleaflet

    Keyword arguments:
    input_dir -- source GWC tiles root directory
    output_dir -- output directory for ZYX tiles

    Note: y=0 -> top row  (e.g. `tms=False` for ipyleaflet)
    """
    df = _build_tile_index(input_dir)
    for _, tile in df.iterrows():
        max_row = df[df.matrix == tile.matrix].row.max()
        new_row = max_row - tile.row
        tile.row = new_row
        output_filepath = Path(ZYX_OUTPUT_PATTERN.format(output_dir=output_dir, **tile))
        assert not output_filepath.exists()
        output_filepath.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(tile.filepath, output_filepath)


if __name__ == "__main__":
    input_dir = Path("tiles/itslive_ant_epsg3031_gwc")
    output_dir = Path("tiles/itslive_ant_epsg3031_zyx")
    gwc2zyx(input_dir, output_dir)
