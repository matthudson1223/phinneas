"""
Crossword Puzzle Dataset Builder

This script collects crossword puzzles from legal sources and builds a dataset
suitable for LLM fine-tuning. For educational/personal use only.

Data sources (in order of preference):
1. xd.saul.pw - Free crossword data in .xd format (pre-1965 NYT puzzles public domain)
2. CrosswordQA from Hugging Face - 6M+ clue-answer pairs
3. Other legally accessible sources

Output format: JSONL (one puzzle per line)
"""

import os
import json
import time
import requests
import zipfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from tqdm import tqdm
import argparse

from xd_parser import XDParser, parse_xd_simple


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crossword_builder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CrosswordDatasetBuilder:
    """Main class for building crossword puzzle datasets from legal sources."""

    def __init__(self, output_dir: str = 'crossword_data'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.raw_data_dir = self.output_dir / 'raw'
        self.raw_data_dir.mkdir(exist_ok=True)

        self.processed_dir = self.output_dir / 'processed'
        self.processed_dir.mkdir(exist_ok=True)

        self.state_file = self.output_dir / 'builder_state.json'
        self.output_file = self.processed_dir / 'puzzles.jsonl'
        self.csv_file = self.processed_dir / 'puzzles_summary.csv'
        self.failed_log = self.output_dir / 'failed_puzzles.log'

        self.state = self._load_state()
        self.parser = XDParser()

        # Statistics
        self.stats = {
            'total_processed': 0,
            'total_failed': 0,
            'by_source': {},
            'by_day': {}
        }

    def _load_state(self) -> Dict:
        """Load saved state for resume capability."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load state file: {e}")
        return {
            'downloaded_sources': [],
            'processed_files': [],
            'last_update': None
        }

    def _save_state(self):
        """Save current state."""
        self.state['last_update'] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def download_xd_data(self, force: bool = False) -> bool:
        """
        Download crossword data from xd.saul.pw

        Note: This method shows how to download. Users should visit
        https://xd.saul.pw/data and download the data manually, then
        place it in the raw_data directory.
        """
        source_name = 'xd.saul.pw'

        if not force and source_name in self.state['downloaded_sources']:
            logger.info(f"Data from {source_name} already downloaded. Use force=True to re-download.")
            return True

        logger.info("=" * 60)
        logger.info("MANUAL DOWNLOAD REQUIRED")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Please download crossword data manually from:")
        logger.info("  https://xd.saul.pw/data")
        logger.info("")
        logger.info("Download options:")
        logger.info("  1. xd-clues.zip - Millions of clue/answer pairs")
        logger.info("  2. Individual puzzle collections")
        logger.info("")
        logger.info(f"Place downloaded files in: {self.raw_data_dir.absolute()}")
        logger.info("")
        logger.info("=" * 60)

        # Check if user has already downloaded files
        xd_files = list(self.raw_data_dir.glob('*.xd'))
        zip_files = list(self.raw_data_dir.glob('*.zip'))

        if xd_files or zip_files:
            logger.info(f"Found {len(xd_files)} .xd files and {len(zip_files)} .zip files")
            self.state['downloaded_sources'].append(source_name)
            self._save_state()
            return True

        return False

    def extract_zip_files(self):
        """Extract any zip files in the raw data directory."""
        zip_files = list(self.raw_data_dir.glob('*.zip'))

        for zip_path in zip_files:
            extract_dir = self.raw_data_dir / zip_path.stem
            if extract_dir.exists():
                logger.info(f"Already extracted: {zip_path.name}")
                continue

            logger.info(f"Extracting {zip_path.name}...")
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                logger.info(f"Extracted to: {extract_dir}")
            except Exception as e:
                logger.error(f"Failed to extract {zip_path.name}: {e}")

    def parse_xd_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """Parse a single .xd file and return structured data."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Try the simple parser first
            result = parse_xd_simple(content)

            # Validate we got something useful
            if not result.get('clues') and not result.get('grid'):
                logger.warning(f"No clues or grid found in {filepath.name}")
                return None

            # Add source information
            result['source_file'] = str(filepath.name)
            result['source'] = 'xd.saul.pw'

            return result

        except Exception as e:
            logger.error(f"Error parsing {filepath}: {e}")
            with open(self.failed_log, 'a') as f:
                f.write(f"{filepath}: {e}\n")
            return None

    def process_xd_files(self, limit: Optional[int] = None):
        """Process all .xd files in the raw data directory."""
        logger.info("Searching for .xd files...")

        # Find all .xd files recursively
        xd_files = list(self.raw_data_dir.rglob('*.xd'))
        logger.info(f"Found {len(xd_files)} .xd files")

        if limit:
            xd_files = xd_files[:limit]
            logger.info(f"Processing first {limit} files")

        # Open output file in append mode
        processed_count = 0
        failed_count = 0

        with open(self.output_file, 'a', encoding='utf-8') as out_f:
            for filepath in tqdm(xd_files, desc="Processing .xd files"):
                # Skip if already processed
                if str(filepath) in self.state['processed_files']:
                    continue

                # Parse the file
                puzzle = self.parse_xd_file(filepath)

                if puzzle:
                    # Write to JSONL
                    out_f.write(json.dumps(puzzle) + '\n')

                    # Update statistics
                    processed_count += 1
                    day = puzzle.get('day', 'Unknown')
                    self.stats['by_day'][day] = self.stats['by_day'].get(day, 0) + 1

                    # Mark as processed
                    self.state['processed_files'].append(str(filepath))

                    # Save state periodically (every 100 files)
                    if processed_count % 100 == 0:
                        self._save_state()
                        logger.info(f"Progress: {processed_count} processed, {failed_count} failed")

                else:
                    failed_count += 1

                # Polite delay
                time.sleep(0.01)

        self.stats['total_processed'] = processed_count
        self.stats['total_failed'] = failed_count
        self._save_state()

        logger.info(f"Processing complete: {processed_count} puzzles processed, {failed_count} failed")

    def download_huggingface_dataset(self):
        """
        Download CrosswordQA dataset from Hugging Face.

        Requires: pip install datasets
        """
        try:
            from datasets import load_dataset

            logger.info("Downloading CrosswordQA dataset from Hugging Face...")
            dataset = load_dataset("albertxu/CrosswordQA")

            logger.info(f"Dataset loaded: {dataset}")

            # Convert to our format
            output_file = self.processed_dir / 'crosswordqa.jsonl'
            count = 0

            with open(output_file, 'w', encoding='utf-8') as f:
                for split in dataset.keys():
                    for item in tqdm(dataset[split], desc=f"Processing {split}"):
                        # CrosswordQA format: clue, answer pairs
                        entry = {
                            'source': 'CrosswordQA',
                            'clue': item.get('clue', ''),
                            'answer': item.get('answer', ''),
                            'split': split
                        }
                        f.write(json.dumps(entry) + '\n')
                        count += 1

            logger.info(f"CrosswordQA: {count} clue-answer pairs saved to {output_file}")
            return True

        except ImportError:
            logger.warning("datasets library not installed. Run: pip install datasets")
            return False
        except Exception as e:
            logger.error(f"Error downloading CrosswordQA: {e}")
            return False

    def generate_csv_summary(self):
        """Generate a CSV summary of all puzzles."""
        import csv

        logger.info("Generating CSV summary...")

        if not self.output_file.exists():
            logger.warning("No puzzles file found")
            return

        with open(self.output_file, 'r', encoding='utf-8') as f_in, \
             open(self.csv_file, 'w', newline='', encoding='utf-8') as f_out:

            writer = csv.writer(f_out)
            writer.writerow([
                'date', 'day', 'size', 'num_clues', 'avg_answer_length',
                'author', 'publisher', 'has_theme', 'source'
            ])

            for line in f_in:
                try:
                    puzzle = json.loads(line)

                    clues = puzzle.get('clues', [])
                    answers = [c['answer'] for c in clues if 'answer' in c]
                    avg_length = sum(len(a) for a in answers) / len(answers) if answers else 0

                    writer.writerow([
                        puzzle.get('date', ''),
                        puzzle.get('day', ''),
                        puzzle.get('size', ''),
                        len(clues),
                        round(avg_length, 2),
                        puzzle.get('author', ''),
                        puzzle.get('publisher', ''),
                        'yes' if puzzle.get('theme') else 'no',
                        puzzle.get('source', '')
                    ])
                except Exception as e:
                    logger.error(f"Error processing line for CSV: {e}")

        logger.info(f"CSV summary saved to: {self.csv_file}")

    def print_statistics(self):
        """Print collection statistics."""
        logger.info("\n" + "=" * 60)
        logger.info("DATASET STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Total puzzles processed: {self.stats['total_processed']}")
        logger.info(f"Total failed: {self.stats['total_failed']}")
        logger.info("\nBy day of week:")
        for day, count in sorted(self.stats['by_day'].items()):
            logger.info(f"  {day:12s}: {count:5d}")
        logger.info("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Build crossword puzzle dataset')
    parser.add_argument('--output-dir', default='crossword_data', help='Output directory')
    parser.add_argument('--limit', type=int, help='Limit number of puzzles to process')
    parser.add_argument('--download-hf', action='store_true', help='Download CrosswordQA from HuggingFace')
    parser.add_argument('--force-download', action='store_true', help='Force re-download')

    args = parser.parse_args()

    builder = CrosswordDatasetBuilder(output_dir=args.output_dir)

    # Step 1: Check for xd.saul.pw data
    builder.download_xd_data(force=args.force_download)

    # Step 2: Extract any zip files
    builder.extract_zip_files()

    # Step 3: Process .xd files
    builder.process_xd_files(limit=args.limit)

    # Step 4: Download HuggingFace dataset if requested
    if args.download_hf:
        builder.download_huggingface_dataset()

    # Step 5: Generate CSV summary
    builder.generate_csv_summary()

    # Step 6: Print statistics
    builder.print_statistics()

    logger.info(f"\nDataset saved to: {builder.output_file}")
    logger.info(f"CSV summary: {builder.csv_file}")
    logger.info("\nTo resume: Run the same command again (state is saved)")


if __name__ == '__main__':
    main()
