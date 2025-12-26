#!/usr/bin/env python3
"""
PNG to JPEG Batch Converter CLI Tool

A command-line utility for batch converting PNG images to JPEG format with
configurable quality settings and background color for transparent images.

Usage Examples:
    # Basic conversion with default quality (85)
    python png2jpg.py -i ./input_images -o ./output_images

    # Conversion with custom quality
    python png2jpg.py -i ./input_images -o ./output_images -q 90

    # Recursive conversion including subdirectories
    python png2jpg.py -i ./photos -o ./converted -q 80 -r

    # Conversion with black background for transparent PNGs
    python png2jpg.py -i ./input -o ./output -b 0,0,0

Author: Devin AI
License: MIT
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Tuple, Optional

from PIL import Image


def parse_arguments() -> argparse.Namespace:
    """
    Parse and validate command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments containing:
            - input: Input directory path
            - output: Output directory path
            - quality: JPEG quality (1-100)
            - recursive: Whether to process subdirectories
            - background: RGB background color tuple
    """
    parser = argparse.ArgumentParser(
        description="Batch convert PNG images to JPEG format with configurable quality.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i ./input_images -o ./output_images -q 90
  %(prog)s -i ./photos -o ./converted -q 80 -r
  %(prog)s -i ./input -o ./output -b 0,0,0  # black background
        """
    )

    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="Input directory path containing PNG files (required)"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Output directory path for JPEG files (required, created if doesn't exist)"
    )

    parser.add_argument(
        "-q", "--quality",
        type=int,
        default=85,
        help="JPEG quality 1-100 (optional, default: 85)"
    )

    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Process subdirectories recursively (optional flag)"
    )

    parser.add_argument(
        "-b", "--background",
        type=str,
        default="255,255,255",
        help="RGB background color for transparent PNGs as comma-separated values (optional, default: 255,255,255 white)"
    )

    args = parser.parse_args()

    # Validate input directory exists
    if not os.path.isdir(args.input):
        parser.error(f"Input directory does not exist: {args.input}")

    # Validate quality range
    if not 1 <= args.quality <= 100:
        parser.error(f"Quality must be between 1 and 100, got: {args.quality}")

    # Validate and parse background color
    try:
        bg_parts = args.background.split(",")
        if len(bg_parts) != 3:
            raise ValueError("Background color must have exactly 3 values")
        bg_color = tuple(int(x.strip()) for x in bg_parts)
        for val in bg_color:
            if not 0 <= val <= 255:
                raise ValueError(f"Color value must be between 0 and 255, got: {val}")
        args.background = bg_color
    except ValueError as e:
        parser.error(f"Invalid background color format '{args.background}': {e}. Use format: R,G,B (e.g., 255,255,255)")

    return args


def convert_image(
    input_path: str,
    output_path: str,
    quality: int,
    bg_color: Tuple[int, int, int]
) -> bool:
    """
    Convert a single PNG image to JPEG format.

    Handles images with transparency by compositing them onto a background
    of the specified color. Converts various color modes to RGB for JPEG
    compatibility.

    Args:
        input_path: Path to the input PNG file.
        output_path: Path where the output JPEG file will be saved.
        quality: JPEG quality setting (1-100).
        bg_color: RGB tuple for background color when handling transparency.

    Returns:
        bool: True if conversion was successful, False otherwise.

    Raises:
        No exceptions are raised; errors are caught and reported internally.
    """
    try:
        img = Image.open(input_path)

        # Handle transparency by compositing onto background
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, bg_color)
            if img.mode == 'P':
                img = img.convert('RGBA')
            # Use alpha channel as mask if available
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            elif img.mode == 'LA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save as JPEG with optimization
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        return True

    except Exception as e:
        print(f"Error converting {input_path}: {e}", file=sys.stderr)
        return False


def process_directory(
    input_dir: str,
    output_dir: str,
    quality: int,
    recursive: bool,
    bg_color: Tuple[int, int, int],
    progress_callback: Optional[callable] = None
) -> Tuple[int, int]:
    """
    Process all PNG files in a directory, converting them to JPEG.

    Iterates through the input directory (and subdirectories if recursive
    is True), converting all PNG files to JPEG format while preserving
    the directory structure in the output.

    Args:
        input_dir: Path to the input directory containing PNG files.
        output_dir: Path to the output directory for JPEG files.
        quality: JPEG quality setting (1-100).
        recursive: If True, process subdirectories as well.
        bg_color: RGB tuple for background color when handling transparency.
        progress_callback: Optional callback function for progress updates.
            Called with (message: str, is_error: bool) for each file processed.

    Returns:
        Tuple[int, int]: A tuple containing (converted_count, skipped_count).
    """
    converted_count = 0
    skipped_count = 0

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Get list of files to process
    if recursive:
        files = list(input_path.rglob("*"))
    else:
        files = list(input_path.glob("*"))

    for file_path in files:
        # Skip directories
        if file_path.is_dir():
            continue

        # Check if file is a PNG
        if file_path.suffix.lower() != ".png":
            msg = f"Warning: Skipping non-PNG file: {file_path}"
            if progress_callback:
                progress_callback(msg, False)
            else:
                print(msg)
            skipped_count += 1
            continue

        # Calculate relative path for maintaining directory structure
        relative_path = file_path.relative_to(input_path)
        output_file = output_path / relative_path.with_suffix(".jpg")

        # Display progress
        msg = f"Converting: {file_path.name} -> {output_file.name}"
        if progress_callback:
            progress_callback(msg, False)
        else:
            print(msg)

        # Convert the image
        if convert_image_with_callback(str(file_path), str(output_file), quality, bg_color, progress_callback):
            converted_count += 1
        else:
            skipped_count += 1

    return converted_count, skipped_count


def convert_image_with_callback(
    input_path: str,
    output_path: str,
    quality: int,
    bg_color: Tuple[int, int, int],
    progress_callback: Optional[callable] = None
) -> bool:
    """
    Convert a single PNG image to JPEG format with callback support.

    Same as convert_image but reports errors via callback instead of stderr.

    Args:
        input_path: Path to the input PNG file.
        output_path: Path where the output JPEG file will be saved.
        quality: JPEG quality setting (1-100).
        bg_color: RGB tuple for background color when handling transparency.
        progress_callback: Optional callback for error reporting.

    Returns:
        bool: True if conversion was successful, False otherwise.
    """
    try:
        img = Image.open(input_path)

        # Handle transparency by compositing onto background
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, bg_color)
            if img.mode == 'P':
                img = img.convert('RGBA')
            # Use alpha channel as mask if available
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            elif img.mode == 'LA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save as JPEG with optimization
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        return True

    except Exception as e:
        error_msg = f"Error: {os.path.basename(input_path)} - {e}"
        if progress_callback:
            progress_callback(error_msg, True)
        else:
            print(error_msg, file=sys.stderr)
        return False


def get_png_files(input_dir: str, recursive: bool = False) -> list:
    """
    Get a list of PNG files in a directory.

    Args:
        input_dir: Path to the directory to search.
        recursive: If True, search subdirectories as well.

    Returns:
        list: List of Path objects for PNG files found.
    """
    input_path = Path(input_dir)
    if recursive:
        files = list(input_path.rglob("*.png"))
    else:
        files = list(input_path.glob("*.png"))
    return [f for f in files if f.is_file()]


def main() -> int:
    """
    Main entry point for the PNG to JPEG converter.

    Parses command-line arguments, processes the input directory,
    and displays a summary of the conversion results.

    Returns:
        int: Exit code (0 for success, 1 for errors).
    """
    args = parse_arguments()

    print(f"Starting PNG to JPEG conversion...")
    print(f"Input directory: {args.input}")
    print(f"Output directory: {args.output}")
    print(f"Quality: {args.quality}")
    print(f"Recursive: {args.recursive}")
    print(f"Background color: RGB{args.background}")
    print("-" * 50)

    converted, skipped = process_directory(
        input_dir=args.input,
        output_dir=args.output,
        quality=args.quality,
        recursive=args.recursive,
        bg_color=args.background
    )

    print("-" * 50)
    print(f"Converted {converted} files. {skipped} files skipped.")

    return 0 if converted > 0 or skipped == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
