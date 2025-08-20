#!/usr/bin/env python
import sys
import os
import argparse
import logging
from prismui_icon_gen.generator import IconGenerator

logging.basicConfig(level=logging.INFO, format=" [ %(levelname)s ] : %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="PrismUI Icon Generator CLI")
    parser.add_argument("--icons_dir", required=True, help="Input icons folder (theme directory)")
    parser.add_argument("--output_dir", default=None, help="Output folder (default: {theme}_icon)")
    parser.add_argument("--clean", action="store_true", help="Remove previous generated files before generating")
    args = parser.parse_args()

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    try:
        gen = IconGenerator(base_dir=base_dir, icons_dir=args.icons_dir, output_dir=args.output_dir)
        gen.generate_all_themes(clean_first=args.clean)
        logger.info("✅ Icon resources generated successfully!")
    except Exception as e:
        logger.error("❌ Error occurred: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
