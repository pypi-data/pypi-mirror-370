"""
Main COGTiler class for converting COG files to web map tiles.

Author: Kshitij Raj Sharma
Copyright: 2025
License: MIT
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import mercantile
import numpy as np
import polars as pl
from PIL import Image
from rasterio.crs import CRS
from rasterio.warp import transform_bounds
from rio_tiler.io import Reader
from rio_tiler.models import ImageData
from tqdm.asyncio import tqdm

from .utils import normalize_array, process_bands

logger = logging.getLogger(__name__)


class COGTiler:
    """
    High-performance COG to web map tiles converter.

    This class handles the conversion of Cloud Optimized GeoTIFFs to web map tiles
    with automatic CRS handling, concurrent processing, and multiple output formats.
    """

    def __init__(
        self,
        tile_size: int = 256,
        max_workers: Optional[int] = None,
        prefix: str = "tile",
        extension: str = "png",
        generate_geojson: bool = False,
    ):
        """
        Initialize the COGTiler.

        Args:
            tile_size: Size of output tiles (256 or 512)
            max_workers: Maximum concurrent workers (auto-detected if None)
            prefix: Filename prefix for generated tiles
            extension: Output file extension (png, jpg, webp)
            generate_geojson: Whether to generate GeoJSON with tile status
        """
        self.tile_size = tile_size
        self.max_workers = max_workers or min(128, os.cpu_count() * 8)
        self.prefix = prefix
        self.extension = extension.lower().replace(".", "")
        self.generate_geojson = generate_geojson

        if tile_size not in [256, 512]:
            raise ValueError("Tile size must be 256 or 512")

        self._setup_numba()

    def _setup_numba(self) -> None:
        """Warm up Numba JIT compilation with dummy data."""
        dummy_data = np.random.rand(3, 256, 256).astype(np.float32)
        normalize_array(dummy_data[0])

    async def convert_to_tiles(
        self, input_cog: str, output_dir: str, zoom: int
    ) -> None:
        """
        Convert COG to web map tiles at specified zoom level.

        Args:
            input_cog: Path to input COG file
            output_dir: Output directory for tiles
            zoom: Target zoom level (0-22)
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        bounds = self._get_transformed_bounds(input_cog)
        tiles_df = self._generate_tile_dataframe(bounds, zoom)

        if tiles_df.is_empty():
            logger.warning("No tiles to generate")
            return

        if self.generate_geojson:
            tile_results = await self._process_tiles_concurrently(
                tiles_df, input_cog, output_dir
            )
            await self._generate_tiles_geojson(tiles_df, tile_results, output_dir)
        else:
            await self._process_tiles_concurrently_simple(
                tiles_df, input_cog, output_dir
            )

    def _get_transformed_bounds(
        self, input_cog: str
    ) -> Tuple[float, float, float, float]:
        """Get COG bounds transformed to WGS84 if necessary."""
        with Reader(input_cog) as cog:
            info = cog.info()
            bounds = info.bounds
            crs = info.crs

            if not crs:
                raise ValueError("COG has no CRS information")

            logger.info(f"COG CRS: {crs}")
            logger.info(f"COG bounds: {bounds}")

            if crs != CRS.from_epsg(4326):
                logger.info("Transforming bounds from source CRS to WGS84")
                try:
                    bounds = transform_bounds(crs, CRS.from_epsg(4326), *bounds)
                    logger.info(f"Transformed bounds: {bounds}")
                except Exception as e:
                    raise ValueError(f"Failed to transform bounds to WGS84: {e}")

            self._validate_bounds(bounds)
            return bounds

    def _validate_bounds(self, bounds: Tuple[float, float, float, float]) -> None:
        """Validate that bounds are within valid WGS84 range."""
        west, south, east, north = bounds
        if not (
            -180 <= west <= 180
            and -180 <= east <= 180
            and -90 <= south <= 90
            and -90 <= north <= 90
        ):
            raise ValueError(
                f"Bounds {bounds} are outside valid WGS84 range [-180,-90,180,90]"
            )

    def _generate_tile_dataframe(
        self, bounds: Tuple[float, float, float, float], zoom: int
    ) -> pl.DataFrame:
        """Generate DataFrame of tiles to process."""
        try:
            tiles_generator = mercantile.tiles(*bounds, zoom)
            tiles_df = pl.DataFrame(
                [{"x": t.x, "y": t.y, "z": t.z} for t in tiles_generator]
            )
            return tiles_df
        except Exception as e:
            raise ValueError(
                f"Failed to generate tiles for bounds {bounds} at zoom {zoom}: {e}"
            )

    async def _process_tiles_concurrently_simple(
        self, tiles_df: pl.DataFrame, input_cog: str, output_dir: str
    ) -> None:
        """Process tiles using async concurrency."""
        total_tiles = len(tiles_df)
        logger.info(
            f"Generating {total_tiles} tiles at zoom {tiles_df['z'][0]} using {self.max_workers} workers"
        )

        semaphore = asyncio.Semaphore(self.max_workers)

        async def process_tile_batch(tile_batch):
            async with semaphore:
                return await self._process_tile_batch_simple(
                    tile_batch, input_cog, output_dir
                )

        batch_size = max(1, total_tiles // (self.max_workers * 4))
        logger.info(f"Batch size: {batch_size}")

        batches = [
            tiles_df.slice(i, min(batch_size, total_tiles - i))
            for i in range(0, total_tiles, batch_size)
        ]
        logger.info(f"Number of batches: {len(batches)}")

        tasks = [process_tile_batch(batch) for batch in batches]

        results = []
        for result in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            batch_results = await result
            results.extend(batch_results)

        self._log_processing_results(results, total_tiles)

    async def _process_tiles_concurrently(
        self, tiles_df: pl.DataFrame, input_cog: str, output_dir: str
    ) -> List[Dict[str, Any]]:
        """Process tiles using async concurrency and return detailed results."""
        total_tiles = len(tiles_df)
        logger.info(
            f"Generating {total_tiles} tiles at zoom {tiles_df['z'][0]} using {self.max_workers} workers"
        )

        semaphore = asyncio.Semaphore(self.max_workers)

        async def process_tile_batch(tile_batch):
            async with semaphore:
                return await self._process_tile_batch(tile_batch, input_cog, output_dir)

        batch_size = max(1, total_tiles // (self.max_workers * 4))
        logger.info(f"Batch size: {batch_size}")

        batches = [
            tiles_df.slice(i, min(batch_size, total_tiles - i))
            for i in range(0, total_tiles, batch_size)
        ]
        logger.info(f"Number of batches: {len(batches)}")

        tasks = [process_tile_batch(batch) for batch in batches]

        all_results = []
        for result in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            batch_results = await result
            all_results.extend(batch_results)

        self._log_processing_results([r["success"] for r in all_results], total_tiles)
        return all_results

    def _log_processing_results(self, results: List[bool], total_tiles: int) -> None:
        """Log summary of tile processing results."""
        successful = sum(results)
        failed = len(results) - successful

        logger.info(f"Completed: {successful}/{total_tiles} tiles")

        if failed > 0:
            logger.warning(f"Failed: {failed}/{total_tiles} tiles")
            if failed > successful:
                logger.warning("Most tiles failed - this might indicate:")
                logger.warning("1. Tiles are outside the COG data bounds (normal)")
                logger.warning("2. Data processing issues")
                logger.warning("3. File permission issues")
                logger.warning(
                    "Run with --log-level WARNING to see individual tile failures"
                )

    async def _process_tile_batch_simple(
        self, tile_batch: pl.DataFrame, raster_path: str, output_dir: str
    ) -> List[bool]:
        """Process a batch of tiles in a thread executor."""
        loop = asyncio.get_event_loop()

        def process_batch():
            results = []
            with Reader(raster_path) as cog:
                for row in tile_batch.iter_rows(named=True):
                    result = self._process_single_tile(
                        row["x"], row["y"], row["z"], cog, output_dir
                    )
                    results.append(result)
            return results

        return await loop.run_in_executor(None, process_batch)

    async def _process_tile_batch(
        self, tile_batch: pl.DataFrame, raster_path: str, output_dir: str
    ) -> List[Dict[str, Any]]:
        """Process a batch of tiles in a thread executor."""
        loop = asyncio.get_event_loop()

        def process_batch():
            results = []
            with Reader(raster_path) as cog:
                for row in tile_batch.iter_rows(named=True):
                    success = self._process_single_tile(
                        row["x"], row["y"], row["z"], cog, output_dir
                    )
                    results.append(
                        {
                            "x": row["x"],
                            "y": row["y"],
                            "z": row["z"],
                            "success": success,
                        }
                    )
            return results

        return await loop.run_in_executor(None, process_batch)

    def _process_single_tile(
        self, x: int, y: int, z: int, cog_reader: Reader, output_dir: str
    ) -> bool:
        """Process a single tile."""
        try:
            filename = f"{self.prefix}-{x}-{y}-{z}.{self.extension}"
            output_path = Path(output_dir) / filename

            if output_path.exists():
                return True

            tile_data = cog_reader.tile(
                x, y, z, tilesize=self.tile_size, resampling_method="bilinear"
            )

            if not tile_data.data.any():
                return False

            img_array = self._process_tile_data(tile_data)
            if img_array is None:
                logger.warning(f"Failed to process tile data for {x}-{y}-{z}")
                return False

            img = self._create_pil_image(img_array)
            if img is None:
                logger.warning(f"Failed to create PIL image for {x}-{y}-{z}")
                return False

            self._save_image(img, output_path)
            return True

        except Exception as e:
            logger.warning(f"Error processing tile {x}-{y}-{z}: {e}")
            return False

    def _process_tile_data(self, tile_data: ImageData) -> Optional[np.ndarray]:
        """Process tile data for image creation."""
        try:
            data = tile_data.data

            if data.dtype == np.uint8:
                processed = process_bands(data)
            else:
                if data.dtype in [np.float32, np.float64]:
                    data = np.clip(data * 255, 0, 255)

                processed = process_bands(data)
                if processed.ndim == 2:
                    processed = normalize_array(processed)
                else:
                    shape = processed.shape
                    if len(shape) == 3:
                        normalized = np.empty_like(processed, dtype=np.uint8)
                        for i in range(shape[2]):
                            normalized[:, :, i] = normalize_array(processed[:, :, i])
                        processed = normalized

            return processed

        except Exception:
            return None

    def _create_pil_image(self, img_array: np.ndarray) -> Optional[Image.Image]:
        """Create PIL Image from numpy array."""
        try:
            return Image.fromarray(img_array)
        except Exception:
            return None

    def _save_image(self, img: Image.Image, output_path: Path) -> None:
        """Save PIL Image with format-specific optimizations."""
        save_kwargs = {"optimize": True}

        if self.extension in ["jpg", "jpeg"]:
            if img.mode == "RGBA":
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(
                    img, mask=img.split()[-1] if img.mode == "RGBA" else None
                )
                img = background
            save_kwargs.update({"format": "JPEG", "quality": 90})
        elif self.extension == "webp":
            save_kwargs.update({"format": "WebP", "quality": 90, "method": 6})
        elif self.extension == "png":
            save_kwargs.update({"compress_level": 6})

        img.save(output_path, **save_kwargs)

    async def _generate_tiles_geojson(
        self,
        tiles_df: pl.DataFrame,
        tile_results: List[Dict[str, Any]],
        output_dir: str,
    ) -> None:
        """Generate GeoJSON file with tile bounds and status."""
        output_path = Path(output_dir)
        geojson_path = output_path / "tiles.geojson"

        results_map = {(r["x"], r["y"], r["z"]): r["success"] for r in tile_results}

        features = []

        for row in tiles_df.iter_rows(named=True):
            x, y, z = row["x"], row["y"], row["z"]

            tile_bounds = mercantile.bounds(x, y, z)

            polygon_coords = [
                [
                    [tile_bounds.west, tile_bounds.south],
                    [tile_bounds.east, tile_bounds.south],
                    [tile_bounds.east, tile_bounds.north],
                    [tile_bounds.west, tile_bounds.north],
                    [tile_bounds.west, tile_bounds.south],
                ]
            ]

            success = results_map.get((x, y, z), False)
            status = "downloaded" if success else "failed"

            feature = {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": polygon_coords},
                "properties": {
                    "x": x,
                    "y": y,
                    "z": z,
                    "status": status,
                    "filename": f"{self.prefix}-{x}-{y}-{z}.{self.extension}",
                },
            }

            features.append(feature)

        geojson = {"type": "FeatureCollection", "features": features}

        with open(geojson_path, "w") as f:
            json.dump(geojson, f, indent=2)

        logger.info(
            f"Generated GeoJSON with {len(features)} tile features: {geojson_path}"
        )

        downloaded_count = sum(
            1 for f in features if f["properties"]["status"] == "downloaded"
        )
        failed_count = len(features) - downloaded_count
        logger.info(
            f"Tiles summary: {downloaded_count} downloaded, {failed_count} failed"
        )
