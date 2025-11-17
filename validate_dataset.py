"""
Dataset Validation Script

Validates crossword puzzle dataset for completeness and quality.
Checks for:
- Required fields
- Data integrity
- Duplicate entries
- Answer/clue consistency
- Grid validity
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict, Counter
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatasetValidator:
    """Validates crossword puzzle datasets."""

    def __init__(self, dataset_file: str):
        self.dataset_file = Path(dataset_file)
        self.issues = defaultdict(list)
        self.stats = {
            'total_puzzles': 0,
            'valid_puzzles': 0,
            'invalid_puzzles': 0,
            'warnings': 0,
            'errors': 0
        }

    def validate(self) -> Dict[str, Any]:
        """Run all validation checks."""
        logger.info(f"Validating dataset: {self.dataset_file}")

        if not self.dataset_file.exists():
            logger.error(f"Dataset file not found: {self.dataset_file}")
            return {'valid': False, 'error': 'File not found'}

        puzzles = []
        line_num = 0

        # Read and validate each puzzle
        with open(self.dataset_file, 'r', encoding='utf-8') as f:
            for line in f:
                line_num += 1
                try:
                    puzzle = json.loads(line.strip())
                    puzzles.append((line_num, puzzle))
                except json.JSONDecodeError as e:
                    self.issues['json_errors'].append(f"Line {line_num}: {e}")
                    self.stats['errors'] += 1

        self.stats['total_puzzles'] = len(puzzles)
        logger.info(f"Total puzzles to validate: {len(puzzles)}")

        # Run validation checks
        self._check_required_fields(puzzles)
        self._check_data_integrity(puzzles)
        self._check_duplicates(puzzles)
        self._check_grid_validity(puzzles)
        self._check_clue_answer_consistency(puzzles)

        # Calculate valid/invalid counts
        self.stats['invalid_puzzles'] = len(set(
            line_num for issue_list in self.issues.values()
            for line_num in issue_list if isinstance(line_num, int)
        ))
        self.stats['valid_puzzles'] = self.stats['total_puzzles'] - self.stats['invalid_puzzles']

        # Print results
        self._print_report()

        return {
            'valid': self.stats['errors'] == 0,
            'stats': self.stats,
            'issues': dict(self.issues)
        }

    def _check_required_fields(self, puzzles: List[tuple]):
        """Check if all required fields are present."""
        required_fields = ['clues', 'date', 'size']
        recommended_fields = ['day', 'grid', 'author', 'source']

        for line_num, puzzle in puzzles:
            # Check required fields
            for field in required_fields:
                if field not in puzzle or not puzzle[field]:
                    self.issues['missing_required'].append(
                        f"Line {line_num}: Missing required field '{field}'"
                    )
                    self.stats['errors'] += 1

            # Check recommended fields
            for field in recommended_fields:
                if field not in puzzle or not puzzle[field]:
                    self.stats['warnings'] += 1

    def _check_data_integrity(self, puzzles: List[tuple]):
        """Check data integrity and format."""
        for line_num, puzzle in puzzles:
            # Check clues format
            clues = puzzle.get('clues', [])
            if not isinstance(clues, list):
                self.issues['invalid_format'].append(
                    f"Line {line_num}: 'clues' must be a list"
                )
                self.stats['errors'] += 1
                continue

            # Check each clue
            for i, clue in enumerate(clues):
                if not isinstance(clue, dict):
                    self.issues['invalid_clue'].append(
                        f"Line {line_num}, clue {i}: Clue must be a dict"
                    )
                    continue

                # Check clue fields
                if 'clue' not in clue or 'answer' not in clue:
                    self.issues['incomplete_clue'].append(
                        f"Line {line_num}, clue {i}: Missing 'clue' or 'answer'"
                    )
                    self.stats['warnings'] += 1

                # Check direction if present
                direction = clue.get('direction', '')
                if direction and direction not in ['across', 'down', 'unknown']:
                    self.issues['invalid_direction'].append(
                        f"Line {line_num}, clue {i}: Invalid direction '{direction}'"
                    )

            # Check grid format
            grid = puzzle.get('grid', [])
            if grid and not isinstance(grid, list):
                self.issues['invalid_grid'].append(
                    f"Line {line_num}: 'grid' must be a list"
                )

            # Check size format
            size = puzzle.get('size', '')
            if size and 'x' not in str(size):
                self.issues['invalid_size'].append(
                    f"Line {line_num}: 'size' must be in format 'WxH'"
                )

    def _check_duplicates(self, puzzles: List[tuple]):
        """Check for duplicate puzzles."""
        seen_dates = {}
        seen_content = {}

        for line_num, puzzle in puzzles:
            # Check duplicate by date
            date = puzzle.get('date', '')
            source = puzzle.get('source', '')

            if date and source:
                key = f"{source}:{date}"
                if key in seen_dates:
                    self.issues['duplicate_date'].append(
                        f"Line {line_num}: Duplicate puzzle for {key} (also on line {seen_dates[key]})"
                    )
                    self.stats['warnings'] += 1
                else:
                    seen_dates[key] = line_num

            # Check duplicate by content (grid hash)
            grid = puzzle.get('grid', [])
            if grid:
                grid_hash = hash(tuple(grid))
                if grid_hash in seen_content:
                    self.issues['duplicate_content'].append(
                        f"Line {line_num}: Duplicate grid content (also on line {seen_content[grid_hash]})"
                    )
                    self.stats['warnings'] += 1
                else:
                    seen_content[grid_hash] = line_num

    def _check_grid_validity(self, puzzles: List[tuple]):
        """Check if grids are valid."""
        for line_num, puzzle in puzzles:
            grid = puzzle.get('grid', [])
            if not grid:
                continue

            # Check if all rows are same length
            if grid:
                row_lengths = [len(row) for row in grid]
                if len(set(row_lengths)) > 1:
                    self.issues['irregular_grid'].append(
                        f"Line {line_num}: Grid rows have different lengths: {row_lengths}"
                    )
                    self.stats['warnings'] += 1

                # Check if size matches grid
                size = puzzle.get('size', '')
                if size and 'x' in str(size):
                    try:
                        width, height = map(int, str(size).split('x'))
                        actual_height = len(grid)
                        actual_width = len(grid[0]) if grid else 0

                        if width != actual_width or height != actual_height:
                            self.issues['size_mismatch'].append(
                                f"Line {line_num}: Size {size} doesn't match grid {actual_width}x{actual_height}"
                            )
                            self.stats['warnings'] += 1
                    except ValueError:
                        pass

    def _check_clue_answer_consistency(self, puzzles: List[tuple]):
        """Check if clues and answers are consistent."""
        for line_num, puzzle in puzzles:
            clues = puzzle.get('clues', [])

            for i, clue in enumerate(clues):
                if not isinstance(clue, dict):
                    continue

                answer = clue.get('answer', '')
                clue_text = clue.get('clue', '')

                # Check answer is not empty
                if not answer:
                    self.issues['empty_answer'].append(
                        f"Line {line_num}, clue {i}: Empty answer"
                    )
                    self.stats['warnings'] += 1

                # Check clue is not empty
                if not clue_text:
                    self.issues['empty_clue'].append(
                        f"Line {line_num}, clue {i}: Empty clue text"
                    )
                    self.stats['warnings'] += 1

                # Check answer format (should be letters, possibly with spaces)
                if answer and not all(c.isalpha() or c.isspace() or c == '-' for c in answer):
                    self.issues['unusual_answer'].append(
                        f"Line {line_num}, clue {i}: Unusual characters in answer '{answer}'"
                    )

    def _print_report(self):
        """Print validation report."""
        logger.info("\n" + "=" * 70)
        logger.info("VALIDATION REPORT")
        logger.info("=" * 70)
        logger.info(f"Total puzzles: {self.stats['total_puzzles']}")
        logger.info(f"Valid puzzles: {self.stats['valid_puzzles']}")
        logger.info(f"Invalid puzzles: {self.stats['invalid_puzzles']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"Warnings: {self.stats['warnings']}")
        logger.info("=" * 70)

        if self.issues:
            logger.info("\nISSUES FOUND:")
            logger.info("-" * 70)
            for issue_type, issue_list in sorted(self.issues.items()):
                logger.info(f"\n{issue_type.upper().replace('_', ' ')} ({len(issue_list)}):")
                # Show first 10 issues of each type
                for issue in issue_list[:10]:
                    logger.info(f"  - {issue}")
                if len(issue_list) > 10:
                    logger.info(f"  ... and {len(issue_list) - 10} more")

        logger.info("\n" + "=" * 70)

        if self.stats['errors'] == 0:
            logger.info("✓ Dataset validation PASSED")
        else:
            logger.info("✗ Dataset validation FAILED")

        logger.info("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Validate crossword dataset')
    parser.add_argument('dataset_file', help='Path to JSONL dataset file')
    parser.add_argument('--output', help='Save validation report to file')

    args = parser.parse_args()

    validator = DatasetValidator(args.dataset_file)
    result = validator.validate()

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Validation report saved to: {args.output}")

    # Exit with error code if validation failed
    if not result['valid']:
        exit(1)


if __name__ == '__main__':
    main()
