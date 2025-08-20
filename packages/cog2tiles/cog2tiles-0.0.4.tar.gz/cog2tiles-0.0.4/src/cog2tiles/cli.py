"""
Command line interface for cog2tiles.

Author: Kshitij Raj Sharma
Copyright: 2025
License: MIT
"""

import argparse
import asyncio
import logging
import os
import sys

try:
    import uvloop
except ImportError:
    uvloop = None

from . import __version__
from .tiler import COGTiler

logger = logging.getLogger(__name__)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure command line argument parser."""
    parser = argparse.ArgumentParser(
        description="COG to tiles converter using modern Python techniques",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cog2tiles input.tif -z 14
  cog2tiles input.tif -z 16 --tile-size 512 --extension webp
  cog2tiles input.tif -z 12 --output-dir custom_tiles/ --workers 64
  cog2tiles input.tif -z 14 --dump-tiles-json
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"cog2tiles {__version__}"
    )
    parser.add_argument("input_cog", help="Input COG file path")
    parser.add_argument(
        "-z", "--zoom", type=int, required=True, help="Zoom level (0-22)"
    )
    parser.add_argument(
        "-o", "--output-dir", default="tiles", help="Output directory (default: tiles)"
    )
    parser.add_argument(
        "--tile-size",
        type=int,
        choices=[256, 512],
        default=256,
        help="Tile size (default: 256)",
    )
    parser.add_argument(
        "--prefix", default="tile", help="Filename prefix (default: tile)"
    )
    parser.add_argument(
        "--extension", default="png", help="File extension (default: png)"
    )
    parser.add_argument(
        "--workers", type=int, help="Max concurrent workers (default: auto)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set the logging level (default: INFO)",
    )
    parser.add_argument(
        "--dump-tiles-json",
        action="store_true",
        help="Generate GeoJSON file with tile status information",
    )

    return parser


async def main():
    """Main application entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level))

    if not 0 <= args.zoom <= 22:
        parser.error("Zoom level must be between 0 and 22")

    if not os.path.exists(args.input_cog):
        parser.error(f"Input file not found: {args.input_cog}")

    try:
        tiler = COGTiler(
            tile_size=args.tile_size,
            max_workers=args.workers,
            prefix=args.prefix,
            extension=args.extension,
            generate_geojson=args.dump_tiles_json,
        )

        await tiler.convert_to_tiles(args.input_cog, args.output_dir, args.zoom)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cli():
    """CLI entry point."""
    if uvloop:
        uvloop.install()
    else:
        logger.warning("uvloop not available, using default asyncio event loop")

    asyncio.run(main())


if __name__ == "__main__":
    cli()
