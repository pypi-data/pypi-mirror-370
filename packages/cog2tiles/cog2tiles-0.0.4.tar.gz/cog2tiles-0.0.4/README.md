# cog2tiles

 Cloud Optimized GeoTIFF (COG) to web map tiles converter built with modern Python.

## Installation

### Using uv (recommended)

```bash
git clone https://github.com/kshitijrajsharma/cog2tiles.git
cd cog2tiles
uv sync
```

### Using pip

```bash
pip install cog2tiles
```

## Usage

### Command Line Interface

Basic usage:
```bash
cog2tiles input.tif -z 19
```

Advanced usage:
```bash
cog2tiles input.tif -z 19 --tile-size 512 --extension png --output-dir tiles/ --workers 64
```

### Options

- `input_cog`: Path to input COG file
- `-z, --zoom`: Target zoom level (0-22)
- `-o, --output-dir`: Output directory (default: tiles)
- `--tile-size`: Tile size in pixels, 256 or 512 (default: 256)
- `--prefix`: Filename prefix for tiles (default: tile)
- `--extension`: Output format - png, jpg, webp (default: png)
- `--workers`: Maximum concurrent workers (default: auto-detected)
- `--log-level`: Logging level - DEBUG, INFO, WARNING, ERROR (default: INFO)

### Python API

```python
import asyncio
from cog2tiles import COGTiler

async def main():
    tiler = COGTiler(
        tile_size=512,
        max_workers=32,
        extension="webp"
    )
    
    await tiler.convert_to_tiles("input.tif", "output/", zoom=19)

asyncio.run(main())
```

## Requirements

- Python 3.11 or higher
- GDAL/rasterio for geospatial operations
- Numba for accelerated processing
- UV for dependency management
- uvloop for the fast asyncio loops (optional)

## Development

### Setup Development Environment

```bash
git clone https://github.com/kshitijrajsharma/cog2tiles.git
cd cog2tiles
uv sync --dev
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black src/
uv run isort src/
```

## Supported Input Formats

- Cloud Optimized GeoTIFF (COG)
- Any rasterio-supported format with proper georeferencing

## Output Formats

- PNG (lossless, supports transparency)
- JPEG (lossy, smaller file sizes)
- WebP (modern format, good compression)

## License

MIT License - see LICENSE file for details.

## Author

Kshitij Raj Sharma (2025)
