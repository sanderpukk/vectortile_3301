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
    # Fast prototype around Tallinn. This validates the grid and styling
    # without generating all Estonia tiles.
    "tallinn": {
        "output": "tallinn",
        "bbox": [530000, 6570000, 560000, 6600000],
    },
    # Full-country generation. This can take much longer and use more disk.
    "full": {
        "output": "estonia",
        "bbox": None,
    },
}

# GDAL MVT layer mapping. Keys are layer names inside basemap.gpkg.
# target_name is the layer name exposed in the final vector tiles.
LAYERS = {
    "transportation_z0_4": {"target_name": "transportation", "minzoom": 0, "maxzoom": 4},
    "transportation_z5_8": {"target_name": "transportation", "minzoom": 5, "maxzoom": 8},
    "transportation_z9_13": {"target_name": "transportation", "minzoom": 9, "maxzoom": 13},
    "transportation_name_z8_13": {"target_name": "transportation_name", "minzoom": 8, "maxzoom": 13},
    "water_z0_4": {"target_name": "water", "minzoom": 0, "maxzoom": 4},
    "water_z5_8": {"target_name": "water", "minzoom": 5, "maxzoom": 8},
    "water_z9_13": {"target_name": "water", "minzoom": 9, "maxzoom": 13},
    "waterway_z5_13": {"target_name": "waterway", "minzoom": 5, "maxzoom": 13},
    "landcover_z0_4": {"target_name": "landcover", "minzoom": 0, "maxzoom": 4},
    "landcover_z5_8": {"target_name": "landcover", "minzoom": 5, "maxzoom": 8},
    "landcover_z9_13": {"target_name": "landcover", "minzoom": 9, "maxzoom": 13},
    "landuse_z1_13": {"target_name": "landuse", "minzoom": 1, "maxzoom": 13},
    "building_z9_13": {"target_name": "building", "minzoom": 9, "maxzoom": 13},
    "boundary_z0_13": {"target_name": "boundary", "minzoom": 0, "maxzoom": 13},
    "place_z0_13": {"target_name": "place", "minzoom": 0, "maxzoom": 13},
    "poi_z8_13": {"target_name": "poi", "minzoom": 8, "maxzoom": 13},
}

