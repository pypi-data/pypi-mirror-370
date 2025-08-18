import argparse
import asyncio
import logging
from .converter import Converter

def main():
    """Command-line interface entry point."""
    parser = argparse.ArgumentParser(
        description="Convert an HTML file with SVG content into an editable PowerPoint (.pptx) file."
    )
    parser.add_argument(
        "input_file",
        help="Path to the input HTML file."
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_file",
        help="Path to the output .pptx file. If not provided, it will be the same as the input file with a .pptx extension."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging for debugging."
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    output_file = args.output_file
    if not output_file:
        output_file = args.input_file.rsplit('.', 1)[0] + ".pptx"

    async def run_conversion():
        converter = Converter(input_file=args.input_file, output_file=output_file)
        await converter.convert()
        logging.info(f"Successfully converted {args.input_file} to {output_file}")

    try:
        asyncio.run(run_conversion())
    except Exception as e:
        logging.error(f"An error occurred during conversion: {e}")
        exit(1)

if __name__ == "__main__":
    main()
