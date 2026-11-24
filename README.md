# Ares — Interactive 3D Mars Atlas

**[Launch Ares — Interactive Mars Atlas](https://sigfly.github.io/ares-mars/)**

A standalone, offline WebGL 2 explorer inspired by [Luna](https://github.com/sigfly/luna-moon). Download the `ares-mars-16k` artifact from the [successful GitHub Actions build](https://github.com/sigfly/ares-mars/actions/runs/45408548940), unzip it, and open `index.html` directly in a modern browser. (GitHub requires sign-in to download workflow artifacts.) No server, network connection, runtime packages, or installation required.

## High-resolution maps

| Layer | Source | Embedded size | Equatorial sampling |
|---|---|---:|---:|
| Color | Viking MDIM 2.1 colorized mosaic, NASA/USGS | 16,384 × 8,192 | 1.30 km/pixel |
| Elevation | Mars Global Surveyor MOLA, NASA Mars Trek merged DEM | 8,192 × 4,096 | 2.60 km/pixel |

The source Viking mosaic has approximately 232 m sampling. The native MOLA grid is approximately 463 m; the atlas resamples both to fit the browser and GitHub single-file constraints. Color is JPEG; elevation is losslessly encoded as unsigned little-endian 16-bit metres above the areoid plus 12,000 m, modulo-differenced per row and gzip compressed. The viewer integrates elevation into its geometry and local lighting slopes. Its spherical geometry is illustrative, not a geodetic measurement tool. The color mosaic is colorized/photometrically processed rather than a calibrated true-color image, and direct sunlight is also illustrative.

## Features

- Navigate any longitude, either pole, and up to 16× zoom; use mouse, touch, or keyboard.
- Switch between color, elevation and shaded relief; toggle a 15° coordinate grid.
- Adjust terrain exaggeration and solar angle/shadow fill.
- Locate 28 major features and robotic landing sites, including Olympus Mons, Valles Marineris, Curiosity, Perseverance, Spirit, Opportunity, Viking and Zhurong.
- Auto-rotation, fullscreen and PNG screenshot export.
- Automatically lowers texture size to 4K on touch/low-memory devices and reports the actual loaded map resolution.

## Build

[GitHub Actions](https://github.com/sigfly/ares-mars/actions/workflows/build.yml) builds and packages the full atlas using read-only repository permissions. The downloadable artifact includes `index.html` and both processed data maps.

```sh
python -m pip install numpy pillow
python tools/build.py
```

The builder requests the NASA Mars Trek raster service in bounded tiles, validates tile dimensions and the signed elevation sample range, stores downloads in `.cache/`, and generates one offline `index.html`. Use `--color 8192 --height 4096` for a compact edition. Higher elevation and smaller color variants are also supported. The `src/viewer.html` template is the editable application, not the generated `index.html`.

### Sources and credits

- [NASA Mars Trek](https://trek.nasa.gov/mars/) — raster access.
- [USGS Viking MDIM 2.1 colorized global mosaic](https://astrogeology.usgs.gov/search/map/mars_viking_colorized_global_mosaic_232m) — NASA Ames/USGS; public-domain data.
- [USGS Mars MGS MOLA global DEM](https://astrogeology.usgs.gov/search/map/mars_mgs_mola_dem_463m) — NASA MGS/MOLA team; public-domain data.
- [NASA Mars facts](https://science.nasa.gov/mars/facts/) — planet statistics.

For local high-resolution scientific analysis, visit Mars Trek. The atlas cannot resolve rover hardware or individual rover tracks. Coordinates are east-positive planetocentric latitude, normalized to ±180° longitude for display.
