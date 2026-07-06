# User-editable settings for the Python GDAL pipeline.
#
# This file is regular Python on purpose: it is easy to comment, copy, and edit.
# The pipeline converts LAYERS to GDAL's required JSON CONF file at runtime.

TILE_GRID = {
    "crs": "EPSG:3301",
    "extent": [40500, 5993000, 1064500, 7017000],
    "origin": [40500, 7017000],
    "size": 1024000,
    "tile_size": 256,
}

MVT = {
    "minzoom": 0,
    "maxzoom": 13,
    "extent": 4096,
    "buffer": 64,
    "compress": True,
    "max_size": 750000,
}

MODES = {
    # Default: full-country generation. This is the main product; it takes
    # longer and uses more disk than the Tallinn prototype.
    "estonia": {
        "output": "estonia",
        "bbox": None,
    },
    # Optional fast prototype around Tallinn. Validates the grid and styling
    # without generating all Estonia tiles. Select with `--mode tallinn`
    # (or MODE=tallinn for Docker Compose).
    "tallinn": {
        "output": "tallinn",
        "bbox": [530000, 6570000, 560000, 6600000],
    },
}

# GDAL MVT layer mapping. Keys are layer names inside basemap.gpkg.
# target_name is the layer name exposed in the final vector tiles.
LAYERS = {
    "transportation_z0_4": {"target_name": "transportation", "minzoom": 0, "maxzoom": 4},
    "transportation_z5_8": {"target_name": "transportation", "minzoom": 5, "maxzoom": 8},
    "transportation_z9_13": {"target_name": "transportation", "minzoom": 9, "maxzoom": 13},
    "transportation_area_z9_13": {"target_name": "transportation", "minzoom": 9, "maxzoom": 13},
    "transportation_name_z8_13": {"target_name": "transportation_name", "minzoom": 8, "maxzoom": 13},
    "water_z0_4": {"target_name": "water", "minzoom": 0, "maxzoom": 4},
    "water_z5_8": {"target_name": "water", "minzoom": 5, "maxzoom": 8},
    "water_z9_13": {"target_name": "water", "minzoom": 9, "maxzoom": 13},
    "waterway_z5_13": {"target_name": "waterway", "minzoom": 5, "maxzoom": 13},
    "landcover_z0_4": {"target_name": "landcover", "minzoom": 0, "maxzoom": 4},
    "landcover_z5_8": {"target_name": "landcover", "minzoom": 5, "maxzoom": 8},
    "landcover_z9_13": {"target_name": "landcover", "minzoom": 9, "maxzoom": 13},
    "landuse_z1_13": {"target_name": "landuse", "minzoom": 1, "maxzoom": 13},
    "landuse_detail_z8_13": {"target_name": "landuse", "minzoom": 8, "maxzoom": 13},
    "aeroway_z6_13": {"target_name": "aeroway", "minzoom": 6, "maxzoom": 13},
    "building_z9_13": {"target_name": "building", "minzoom": 9, "maxzoom": 13},
    "boundary_z0_13": {"target_name": "boundary", "minzoom": 0, "maxzoom": 13},
    "place_z0_13": {"target_name": "place", "minzoom": 0, "maxzoom": 13},
    "place_detail_z8_13": {"target_name": "place", "minzoom": 8, "maxzoom": 13},
    "housenumber_z10_13": {"target_name": "housenumber", "minzoom": 10, "maxzoom": 13},
    "park_z5_13": {"target_name": "park", "minzoom": 5, "maxzoom": 13},
    "poi_z8_13": {"target_name": "poi", "minzoom": 8, "maxzoom": 13},
}

