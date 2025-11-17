"""
Dataset Statistics Analyzer

Analyzes crossword puzzle dataset and generates statistics:
- Distribution by day of week
- Answer length patterns
- Grid size distribution
- Publisher/author statistics
- Clue complexity metrics
- Temporal trends
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter, defaultdict
import argparse
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatasetAnalyzer:
    """Analyzes crossword puzzle datasets."""

    def __init__(self, dataset_file: str):
        self.dataset_file = Path(dataset_file)
        self.puzzles = []
        self.stats = {
            'total_puzzles': 0,
            'total_clues': 0,
            'by_day': Counter(),
            'by_size': Counter(),
            'by_source': Counter(),
            'by_publisher': Counter(),
            'by_author': Counter(),
            'by_year': Counter(),
            'answer_lengths': [],
            'clue_lengths': [],
            'grid_sizes': []
        }

    def load_data(self):
        """Load dataset from file."""
        logger.info(f"Loading dataset from: {self.dataset_file}")

        if not self.dataset_file.exists():
            logger.error(f"Dataset file not found: {self.dataset_file}")
            return False

        with open(self.dataset_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    puzzle = json.loads(line.strip())
                    self.puzzles.append(puzzle)
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping invalid JSON line: {e}")

        self.stats['total_puzzles'] = len(self.puzzles)
        logger.info(f"Loaded {len(self.puzzles)} puzzles")
        return True

    def analyze(self):
        """Run all analysis."""
        if not self.puzzles:
            logger.error("No puzzles loaded")
            return

        logger.info("Analyzing dataset...")

        for puzzle in self.puzzles:
            self._analyze_puzzle(puzzle)

        self._print_report()

    def _analyze_puzzle(self, puzzle: Dict[str, Any]):
        """Analyze a single puzzle."""
        # Day of week
        day = puzzle.get('day', 'Unknown')
        self.stats['by_day'][day] += 1

        # Grid size
        size = puzzle.get('size', 'Unknown')
        self.stats['by_size'][size] += 1

        # Source
        source = puzzle.get('source', 'Unknown')
        self.stats['by_source'][source] += 1

        # Publisher
        publisher = puzzle.get('publisher', 'Unknown')
        if publisher and publisher != 'Unknown':
            self.stats['by_publisher'][publisher] += 1

        # Author
        author = puzzle.get('author', 'Unknown')
        if author and author != 'Unknown':
            self.stats['by_author'][author] += 1

        # Year
        date_str = puzzle.get('date', '')
        if date_str:
            try:
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        self.stats['by_year'][dt.year] += 1
                        break
                    except ValueError:
                        continue
            except:
                pass

        # Clues and answers
        clues = puzzle.get('clues', [])
        self.stats['total_clues'] += len(clues)

        for clue in clues:
            if isinstance(clue, dict):
                # Answer length
                answer = clue.get('answer', '')
                if answer:
                    self.stats['answer_lengths'].append(len(answer.replace(' ', '')))

                # Clue length (word count)
                clue_text = clue.get('clue', '')
                if clue_text:
                    word_count = len(clue_text.split())
                    self.stats['clue_lengths'].append(word_count)

        # Grid dimensions
        grid = puzzle.get('grid', [])
        if grid:
            height = len(grid)
            width = len(grid[0]) if grid else 0
            self.stats['grid_sizes'].append((width, height))

    def _print_report(self):
        """Print analysis report."""
        logger.info("\n" + "=" * 70)
        logger.info("DATASET ANALYSIS REPORT")
        logger.info("=" * 70)

        # Overview
        logger.info("\nOVERVIEW:")
        logger.info(f"  Total puzzles: {self.stats['total_puzzles']:,}")
        logger.info(f"  Total clues: {self.stats['total_clues']:,}")
        logger.info(f"  Average clues per puzzle: {self.stats['total_clues'] / self.stats['total_puzzles']:.1f}")

        # By day of week
        logger.info("\nDISTRIBUTION BY DAY OF WEEK:")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Unknown']
        for day in day_order:
            count = self.stats['by_day'].get(day, 0)
            if count > 0:
                pct = 100 * count / self.stats['total_puzzles']
                bar = '█' * int(pct / 2)
                logger.info(f"  {day:12s}: {count:5d} ({pct:5.1f}%) {bar}")

        # By grid size
        logger.info("\nDISTRIBUTION BY GRID SIZE:")
        for size, count in self.stats['by_size'].most_common(10):
            pct = 100 * count / self.stats['total_puzzles']
            bar = '█' * int(pct / 2)
            logger.info(f"  {size:12s}: {count:5d} ({pct:5.1f}%) {bar}")

        # By source
        logger.info("\nDISTRIBUTION BY SOURCE:")
        for source, count in self.stats['by_source'].most_common(10):
            pct = 100 * count / self.stats['total_puzzles']
            logger.info(f"  {source:30s}: {count:5d} ({pct:5.1f}%)")

        # By publisher
        if self.stats['by_publisher']:
            logger.info("\nTOP 10 PUBLISHERS:")
            for publisher, count in self.stats['by_publisher'].most_common(10):
                logger.info(f"  {publisher:40s}: {count:5d}")

        # By author
        if self.stats['by_author']:
            logger.info("\nTOP 10 AUTHORS:")
            for author, count in self.stats['by_author'].most_common(10):
                logger.info(f"  {author:40s}: {count:5d}")

        # By year
        if self.stats['by_year']:
            logger.info("\nDISTRIBUTION BY YEAR:")
            years = sorted(self.stats['by_year'].items())
            for year, count in years[:10]:  # First 10 years
                logger.info(f"  {year}: {count:5d}")
            if len(years) > 20:
                logger.info(f"  ...")
                for year, count in years[-10:]:  # Last 10 years
                    logger.info(f"  {year}: {count:5d}")
            elif len(years) > 10:
                for year, count in years[10:]:
                    logger.info(f"  {year}: {count:5d}")

        # Answer length statistics
        if self.stats['answer_lengths']:
            logger.info("\nANSWER LENGTH STATISTICS:")
            lengths = self.stats['answer_lengths']
            logger.info(f"  Minimum: {min(lengths)}")
            logger.info(f"  Maximum: {max(lengths)}")
            logger.info(f"  Average: {sum(lengths) / len(lengths):.2f}")
            logger.info(f"  Median: {sorted(lengths)[len(lengths) // 2]}")

            # Distribution
            logger.info("\n  Answer Length Distribution:")
            length_dist = Counter(lengths)
            for length in sorted(length_dist.keys())[:20]:  # Top 20 lengths
                count = length_dist[length]
                pct = 100 * count / len(lengths)
                bar = '█' * int(pct / 2)
                logger.info(f"    {length:2d} letters: {count:6d} ({pct:5.1f}%) {bar}")

        # Clue length statistics (word count)
        if self.stats['clue_lengths']:
            logger.info("\nCLUE LENGTH STATISTICS (word count):")
            lengths = self.stats['clue_lengths']
            logger.info(f"  Minimum: {min(lengths)}")
            logger.info(f"  Maximum: {max(lengths)}")
            logger.info(f"  Average: {sum(lengths) / len(lengths):.2f}")
            logger.info(f"  Median: {sorted(lengths)[len(lengths) // 2]}")

        logger.info("\n" + "=" * 70 + "\n")

    def export_stats(self, output_file: str):
        """Export statistics to JSON file."""
        # Convert Counter objects to dicts
        stats_export = {
            'total_puzzles': self.stats['total_puzzles'],
            'total_clues': self.stats['total_clues'],
            'by_day': dict(self.stats['by_day']),
            'by_size': dict(self.stats['by_size']),
            'by_source': dict(self.stats['by_source']),
            'by_publisher': dict(self.stats['by_publisher']),
            'by_author': dict(self.stats['by_author']),
            'by_year': dict(self.stats['by_year']),
            'answer_length_stats': {
                'min': min(self.stats['answer_lengths']) if self.stats['answer_lengths'] else 0,
                'max': max(self.stats['answer_lengths']) if self.stats['answer_lengths'] else 0,
                'avg': sum(self.stats['answer_lengths']) / len(self.stats['answer_lengths']) if self.stats['answer_lengths'] else 0,
                'distribution': dict(Counter(self.stats['answer_lengths']))
            },
            'clue_length_stats': {
                'min': min(self.stats['clue_lengths']) if self.stats['clue_lengths'] else 0,
                'max': max(self.stats['clue_lengths']) if self.stats['clue_lengths'] else 0,
                'avg': sum(self.stats['clue_lengths']) / len(self.stats['clue_lengths']) if self.stats['clue_lengths'] else 0,
                'distribution': dict(Counter(self.stats['clue_lengths']))
            }
        }

        with open(output_file, 'w') as f:
            json.dump(stats_export, f, indent=2)

        logger.info(f"Statistics exported to: {output_file}")

    def get_sample_puzzles(self, n: int = 3) -> List[Dict]:
        """Get sample puzzles from the dataset."""
        import random
        if len(self.puzzles) <= n:
            return self.puzzles
        return random.sample(self.puzzles, n)


def main():
    parser = argparse.ArgumentParser(description='Analyze crossword dataset')
    parser.add_argument('dataset_file', help='Path to JSONL dataset file')
    parser.add_argument('--export', help='Export statistics to JSON file')
    parser.add_argument('--samples', type=int, default=3, help='Number of sample puzzles to show')

    args = parser.parse_args()

    analyzer = DatasetAnalyzer(args.dataset_file)

    if not analyzer.load_data():
        exit(1)

    analyzer.analyze()

    if args.export:
        analyzer.export_stats(args.export)

    # Show sample puzzles
    if args.samples > 0:
        logger.info("\n" + "=" * 70)
        logger.info(f"SAMPLE PUZZLES (showing {args.samples}):")
        logger.info("=" * 70)

        samples = analyzer.get_sample_puzzles(args.samples)
        for i, puzzle in enumerate(samples, 1):
            logger.info(f"\n--- Sample {i} ---")
            logger.info(f"Date: {puzzle.get('date', 'N/A')}")
            logger.info(f"Day: {puzzle.get('day', 'N/A')}")
            logger.info(f"Size: {puzzle.get('size', 'N/A')}")
            logger.info(f"Source: {puzzle.get('source', 'N/A')}")
            logger.info(f"Author: {puzzle.get('author', 'N/A')}")
            logger.info(f"Publisher: {puzzle.get('publisher', 'N/A')}")
            logger.info(f"Theme: {puzzle.get('theme', 'N/A')}")

            clues = puzzle.get('clues', [])
            logger.info(f"Number of clues: {len(clues)}")

            if clues:
                logger.info("\nFirst 3 clues:")
                for j, clue in enumerate(clues[:3], 1):
                    if isinstance(clue, dict):
                        num = clue.get('number', '?')
                        direction = clue.get('direction', '?')
                        text = clue.get('clue', '')
                        answer = clue.get('answer', '')
                        logger.info(f"  {j}. [{num} {direction}] {text}")
                        logger.info(f"     Answer: {answer}")

            grid = puzzle.get('grid', [])
            if grid:
                logger.info("\nGrid:")
                for row in grid[:5]:  # Show first 5 rows
                    logger.info(f"  {row}")
                if len(grid) > 5:
                    logger.info(f"  ... ({len(grid) - 5} more rows)")

        logger.info("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    main()
