# ETAK / EHAK → OpenMapTiles Layer Mapping

How Estonian national datasets (ETAK topography + EHAK administration) are transformed into [OpenMapTiles](https://openmaptiles.org/schema/) vector tile layers. Built with [Planetiler](https://github.com/onthegomap/planetiler).

---

## 1. Data Sources

| Source ID | File | Description |
|-----------|------|-------------|
| `etak` | `vector/data/sources/etak-4326.gpkg` | Estonian Topographic Database (ETAK), reprojected to EPSG:4326 |
| `ehak` | `vector/data/sources/ehak-4326.gpkg` | Estonian Administrative and Settlement Division (EHAK), reprojected to EPSG:4326 |

### ETAK download

<https://geoportaal.maaamet.ee/index.php?lang_id=2&plugin_act=otsing&andmetyyp=ETAK&dl=1&f=ETAK_EESTI_GPKG.zip&page_id=618>

### EHAK downloads

| Layer | URL |
|-------|-----|
| maakond (counties) | <https://s3.pilw.io/rp-kemit-kataster/EHAK/maakond_shp.zip> |
| omavalitsus (municipalities) | <https://s3.pilw.io/rp-kemit-kataster/EHAK/omavalitsus_shp.zip> |
| asustusyksus (settlements) | <https://s3.pilw.io/rp-kemit-kataster/EHAK/asustusyksus_shp.zip> |

### Data Preparation

Both sources are downloaded, extracted, and reprojected to **EPSG:4326** using `ogr2ogr`. EHAK shapefiles (maakond, omavalitsus, asustusyksus) are merged into a single GeoPackage. See `local-build/scripts/prepare-etak.sh`.

---

## 2. ETAK Source Layers Used

| ETAK Layer | Description | Geometry |
|------------|-------------|----------|
| `E_201_meri_a` | Sea / ocean | Polygon |
| `E_202_seisuveekogu_a` | Standing water bodies (lakes, ponds) | Polygon |
| `E_203_vooluveekogu_a` | Flowing water bodies (area) | Polygon |
| `E_203_vooluveekogu_j` | Flowing water bodies (line) | Line |
| `E_301_muu_kolvik_a` | Other land cover (parks, green areas) | Polygon |
| `E_301_muu_kolvik_ka` | Other land cover — classified (cemeteries, aerodromes, harbors, quarries, stadiums) | Polygon |
| `E_302_ou_a` | Yards / land use zones (residential, industrial) | Polygon |
| `E_303_haritav_maa_a` | Cultivated land (fields, orchards) | Polygon |
| `E_304_lage_a` | Open land (meadow, sand) | Polygon |
| `E_305_puittaimestik_a` | Tree vegetation (forest, shrubs) | Polygon |
| `E_306_margala_a` | Wetlands | Polygon |
| `E_401_hoone_ka` | Buildings | Polygon |
| `E_501_tee_j` | Roads (line) | Line |
| `E_501_tee_a` | Roads / transport areas (area) | Polygon |
| `E_502_roobastee_j` | Railways | Line |
| `E_503_siht_j` | Forest compartment lines | Line |

### EHAK Source Layers

| EHAK Layer | Description |
|------------|-------------|
| `maakond` | Counties |
| `omavalitsus` | Municipalities |
| `asustusyksus` | Settlements |

#### EHAK Fields

| Field | Description |
|-------|-------------|
| `ANIMI` | Settlement name |
| `AKOOD` | Settlement code |
| `TYYP` | Unit type (see values below) |
| `ONIMI` | Municipality name |
| `OKOOD` | Municipality code |
| `MNIMI` | County name |
| `MKOOD` | County code |

**EHAK TYYP values:** `0` = maakond (county), `1` = vald (rural municipality), `3` = alev (borough), `4` = linn (city), `5` = omavalitsuse sisene linn (city within municipality), `6` = linnaosa (city district), `7` = alevik (small borough), `8` = küla (village)

---

## 3. Layer-by-Layer Mapping

### 3.1 `transportation` — Roads

**Source:** `E_501_tee_j`

| OMT class | ETAK `tyyp` | ETAK meaning | minZoom |
|-----------|-------------|--------------|---------|
| `motorway` | 10 | Põhimaantee (main road) | 2 |
| `trunk` | 20 | Tugimaantee (national road) | 4 |
| `primary` | 30 | Kõrvalmaantee (secondary national road) | 4 |
| `motorway` | 40 | Ramp / ühendustee (ramp / slip road) | 8 |
| `trunk` | 45 | Muu riigimaantee (other state road) | 4 |
| `secondary` | 50 + `tahtsus=10` | Tänav — põhitänav (main street) | 8 |
| `tertiary` | 50 + `tahtsus=20` | Tänav — jaotustänav (distributor street) | 8 |
| `minor` | 50 + `tahtsus=30,40` | Tänav — kõrvaltänav, kvartalisisene (side/local street) | 12 |
| `path` | 50 + `tahtsus=50` | Jalgtänav (pedestrian street) | 14 |
| `minor` | 60 | Muu tee (other road) | 12 |
| `track` | 70 | Rada (track) | 13 |
| `path` | 80 | Kergliiklustee (light traffic path) | 13 |

**Road attributes:**

| OMT Field | ETAK Field | Mapping |
|-----------|------------|---------|
| `surface=paved` | `teekate` | Values `10` (kõvakate) or `30` (sillutis) |
| `surface=unpaved` | `teekate` | Values `20` (kruus) or `40` (pinnas) |
| `brunnel=bridge` | `a_tasand` / `l_tasand` | Values `1`, `2`, `3` |
| `brunnel=tunnel` | `a_tasand` / `l_tasand` | Value `-1` |
| `expressway=1` | `soidutee` | Value `2` on `tyyp` 10 or 20 |
| `level` | `a_tasand` / `l_tasand` | Raw value (excluding `0`, `997`, `998`) |

### 3.2 `transportation` — Railways

**Source:** `E_502_roobastee_j`

| OMT class | OMT subclass | ETAK `tyyp` | ETAK meaning | minZoom |
|-----------|-------------|-------------|--------------|---------|
| `rail` | `rail` | 10 | Laiarööpmeline (broad gauge) | `tahtsus=10` → 8, else 11 |
| `rail` | `narrow_gauge` | 20 | Kitsarööpmeline (narrow gauge) | `tahtsus=10` → 8, else 11 |
| `rail` | `funicular` | 30 | Köistee (cable railway) | `tahtsus=10` → 8, else 11 |
| `rail` | `tram` | 40 | Trammitee (tramway) | `tahtsus=10` → 8, else 11 |
| `rail` | `rail` | 50 | Muu raudtee (other railway) | `tahtsus=10` → 8, else 11 |

### 3.3 `transportation_name`

**Source:** `E_501_tee_j` (populated from the transportation layer processing)

| OMT Field | ETAK Field |
|-----------|------------|
| `name` | `nimetus` → `ads_nimetus` → `karto_nimi` (first non-empty) |
| `ref` | `tee` (road number) |

**Road network classification** (based on `tee` road number):

| OMT `network` | Road Number Range | minZoom |
|----------------|-------------------|---------|
| `ee-motorway` | 1–11 | 7 |
| `ee-primary` | 12–99 | 9 |
| `ee-secondary` | ≥ 100 | 11 |

Named roads without a `ref` appear from zoom 12+.

### 3.4 `water` — Polygons

**Sources:** ETAK water polygon layers

| OMT class | ETAK Layer | Description | minZoom |
|-----------|------------|-------------|---------|
| `ocean` | `E_201_meri_a` | Sea / ocean | 0 |
| `lake` | `E_202_seisuveekogu_a` | Lakes, ponds | 5 |
| `river` | `E_203_vooluveekogu_a` | Rivers (polygon) | 5 |

### 3.5 `waterway` — Lines

**Source:** `E_203_vooluveekogu_j`

**Filter:** `telje_staatus` = `0` or `10` (main axis / põhitelg)

| OMT class | ETAK `tyyp` | ETAK meaning | minZoom |
|-----------|-------------|--------------|---------|
| `river` | 10 | Jõgi (river) | 9 |
| `canal` | 20 | Kanal (canal) | 9 |
| `stream` | 30 (default) | Oja (stream) | 11 |
| `ditch` | 40, 50 | Peakraav / kraav (main ditch / ditch) | 12 |

| OMT Field | ETAK Field |
|-----------|------------|
| `brunnel=tunnel` | `telje_tyyp=20` |
| `name` | `nimetus` |

### 3.6 `water_name`

**Sources:** `E_202_seisuveekogu_a`, `E_201_meri_a`

| OMT class | ETAK Source | Condition | minZoom |
|-----------|-------------|-----------|---------|
| `ocean` | `E_201_meri_a` | Always | 6 |
| `lake` | `E_202_seisuveekogu_a` | Must have `nimetus` | By area (see below) |

**Lake label zoom by area:**

| Area threshold | minZoom |
|----------------|---------|
| ≥ 5,000,000 m² | 11 |
| ≥ 500,000 m² | 13 |
| < 500,000 m² | 14 |

Labels are placed along center lines computed from the polygon geometry.

### 3.7 `landcover`

| OMT class | OMT subclass | ETAK Layer | ETAK `tyyp` | ETAK meaning | minZoom |
|-----------|-------------|------------|-------------|--------------|---------|
| `wood` | `forest` | `E_305_puittaimestik_a` | 10 | Mets (forest) | 5 |
| `wood` | `forest` | `E_305_puittaimestik_a` | 30 | Põõsastik (shrubs) | 10 |
| `grass` | `meadow` | `E_304_lage_a` | 10 | Rohumaa (meadow) | 10 |
| `grass` | `park` | `E_301_muu_kolvik_a` | 10 | Haljasala (green area) | 8 |
| `farmland` | `farmland` | `E_303_haritav_maa_a` | 10 | Põld (field) | 10 |
| `farmland` | `orchard` | `E_303_haritav_maa_a` | 20 | Aianduslik (orchard/garden) | 12 |
| `wetland` | `wetland` | `E_306_margala_a` | all | Märgala (wetland) | 8 |
| `sand` | `sand` | `E_304_lage_a` | 20 | Liivane (sand) | 8 |

### 3.8 `landuse`

| OMT class | ETAK Layer | ETAK `tyyp` | ETAK meaning | minZoom |
|-----------|------------|-------------|--------------|---------|
| `residential` | `E_302_ou_a` | 10 | Eraõu (private yard / residential) | 5 |
| `industrial` | `E_302_ou_a` | 20 | Tootmisõu (industrial yard) | 5 |
| `cemetery` | `E_301_muu_kolvik_ka` | 30 | Kalmistu (cemetery) | 10 |
| `stadium` | `E_301_muu_kolvik_ka` | 60 | Staadion (stadium) | 10 |
| `quarry` | `E_301_muu_kolvik_ka` | 100 | Karjäär (quarry) | 10 |
| `stadium` | `E_501_tee_a` | 50 | Sports area | 10 |

### 3.9 `building`

**Source:** `E_401_hoone_ka`

All building polygons where `tyyp` is `10` or `20`. minZoom **13**.

### 3.10 `aeroway`

| OMT class | ETAK Layer | ETAK `tyyp` | ETAK meaning | minZoom |
|-----------|------------|-------------|--------------|---------|
| `aerodrome` | `E_301_muu_kolvik_ka` | 40 | Lennuväli (airfield area) | 10 |
| `runway` | `E_501_tee_a` | 40 | Lennurada (runway) | 10 |

### 3.11 `aerodrome_label`

**Source:** `E_301_muu_kolvik_ka` where `tyyp=40` and `nimetus` is not empty.

| Airport | IATA | ICAO | Class | minZoom |
|---------|------|------|-------|---------|
| Tallinna lennujaam | TLL | EETN | `international` | 8 |
| Tartu lennujaam | TAY | EETU | `regional` | 10 |
| Pärnu lennujaam | EPU | EEPU | `regional` | 10 |
| Kuressaare lennujaam | URE | EEKU | `regional` | 10 |
| Kärdla lennujaam | — | EEKD | `regional` | 10 |

### 3.12 `boundary`

**Source:** EHAK (polygon boundaries converted to linestrings)

| OMT `admin_level` | EHAK Layer | Name field | minZoom |
|--------------------|------------|------------|---------|
| 4 (county) | `maakond` | `MNIMI` | 5 |
| 6 (municipality) | `omavalitsus` | `ONIMI` | 9 |
| 8 (settlement) | `asustusyksus` | `ANIMI` | 12 |

All boundaries have `disputed=0` and `maritime=0`.

### 3.13 `place`

**Source:** EHAK

| OMT class | EHAK `TYYP` | Source layer | minZoom | rank |
|-----------|-------------|-------------|---------|------|
| `province` | 0 (maakond) | `maakond` | 4 | 10 |
| `city` | 4 (linn) | `asustusyksus` | 6 | 4 (Tallinn: rank=2, capital=2) |
| `city` | 5 (omavalitsuse sisene linn) | `asustusyksus` | 7 | 6 |
| `town` | 3 (alev) | `asustusyksus` | 8 | 7 |
| `town` | 7 (alevik) | `asustusyksus` | 9 | 8 |
| `suburb` | 6 (linnaosa) | `asustusyksus` | 11 | 9 |
| `village` | 8 (küla) | `asustusyksus` | 10 | 12 |

**Capital:** Tallinn is marked with `capital=2`, `rank=2`.

### 3.14 `park`

**Source:** `E_301_muu_kolvik_a` where `tyyp=10` and `nimetus` is not empty.

| OMT class | Condition | minZoom |
|-----------|-----------|---------|
| `public_park` | Named green areas (haljasala) | 9 |

### 3.15 `poi`

**Source:** ETAK polygon layers, point-on-surface geometry. Only features with a non-empty `nimetus`.

| OMT class | ETAK Layer | ETAK `tyyp` | minZoom |
|-----------|------------|-------------|---------|
| `park` | `E_301_muu_kolvik_a` | 10 | 12 |
| `harbor` | `E_301_muu_kolvik_ka` | 50 | 12 |
| `cemetery` | `E_301_muu_kolvik_ka` | 30 | 12 |

### 3.16 `forest_compartment` *(custom, not in OMT schema)*

**Source:** `E_503_siht_j`

Forest compartment boundary lines. minZoom **13**.

---

## 4. Layers Not Implemented

| OMT Layer | Status |
|-----------|--------|
| `mountain_peak` | Not implemented — Estonia is flat, no significant peaks |
| `housenumber` | Not implemented — requires separate ETL flow (ADS / address data) |
| `boundary` (admin_level=2) | State border skipped by design |

---

## 5. OpenMapTiles Schema Reference

Full schema documentation: <https://openmaptiles.org/schema/>

The OMT schema defines 16 standard layers. This project implements 14 of them plus one custom layer (`forest_compartment`). The table below shows the full OMT layer list and implementation status:

| OMT Layer | Implemented | Primary ETAK/EHAK Source |
|-----------|-------------|--------------------------|
| `aerodrome_label` | Yes | `E_301_muu_kolvik_ka` (tyyp=40) |
| `aeroway` | Yes | `E_301_muu_kolvik_ka`, `E_501_tee_a` |
| `boundary` | Yes | EHAK (maakond, omavalitsus, asustusyksus) |
| `building` | Yes | `E_401_hoone_ka` |
| `housenumber` | No | — |
| `landcover` | Yes | `E_305_puittaimestik_a`, `E_304_lage_a`, `E_303_haritav_maa_a`, `E_306_margala_a`, `E_301_muu_kolvik_a` |
| `landuse` | Yes | `E_302_ou_a`, `E_301_muu_kolvik_ka`, `E_501_tee_a` |
| `mountain_peak` | No | — |
| `park` | Yes | `E_301_muu_kolvik_a` |
| `place` | Yes | EHAK (maakond, asustusyksus) |
| `poi` | Yes | `E_301_muu_kolvik_a`, `E_301_muu_kolvik_ka` |
| `transportation` | Yes | `E_501_tee_j`, `E_502_roobastee_j` |
| `transportation_name` | Yes | `E_501_tee_j` |
| `water` | Yes | `E_201_meri_a`, `E_202_seisuveekogu_a`, `E_203_vooluveekogu_a` |
| `water_name` | Yes | `E_202_seisuveekogu_a`, `E_201_meri_a` |
| `waterway` | Yes | `E_203_vooluveekogu_j` |
| `forest_compartment` | Yes *(custom)* | `E_503_siht_j` |
