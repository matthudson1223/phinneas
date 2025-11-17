"""
Demo script for Crossword Dataset Builder

Creates sample data and demonstrates all the tools:
1. Creates sample .xd files
2. Runs the dataset builder
3. Validates the dataset
4. Generates statistics
"""

import os
import json
from pathlib import Path
from xd_parser import XDParser, parse_xd_simple
from crossword_dataset_builder import CrosswordDatasetBuilder
from validate_dataset import DatasetValidator
from analyze_dataset import DatasetAnalyzer


def create_sample_xd_files(output_dir: Path):
    """Create sample .xd format files for testing."""
    print("Creating sample .xd files...")

    samples = [
        {
            'filename': 'sample1.xd',
            'content': """Title: Monday Puzzle
Author: John Constructor
Editor: Will Shortz
Date: 2024-01-15
Publisher: Sample Publisher
Copyright: © 2024 Sample Publisher

CAT
APE
RAT

A1. Feline pet ~ CAT
A2. Small primate ~ APE
A3. Lab animal ~ RAT
D1. Vehicle ~ CAR
D2. Part of speech ~ ADT
D3. Rodent relative ~ TET
"""
        },
        {
            'filename': 'sample2.xd',
            'content': """Title: Tuesday Teaser
Author: Jane Puzzler
Editor: Will Shortz
Date: 2024-01-16
Publisher: Sample Publisher
Theme: Animals

DOGS
OREO
GOAT
STAR

A1. Canine pets ~ DOGS
A2. Cookie brand ~ OREO
A3. Farm animal ~ GOAT
A4. Celestial body ~ STAR
D1. Canines ~ DOGS
D2. Cookie ~ OREO
D3. Hoofed mammal ~ GOAT
D4. Twinkler ~ STAR
"""
        },
        {
            'filename': 'sample3.xd',
            'content': """Title: Wednesday Challenge
Author: Bob Crossword
Editor: Will Shortz
Date: 2024-01-17
Publisher: Sample Publisher

BREAD
RADIO
ALIVE
NOTED
DERBY

A1. Bakery item ~ BREAD
A2. AM/FM device ~ RADIO
A3. Living ~ ALIVE
A4. Observed ~ NOTED
A5. Hat or race ~ DERBY
D1. Loaf ~ BREAD
D2. Station player ~ RADIO
D3. Not dead ~ ALIVE
D4. Saw ~ NOTED
D5. Kentucky event ~ DERBY
"""
        }
    ]

    sample_dir = output_dir / 'raw' / 'samples'
    sample_dir.mkdir(parents=True, exist_ok=True)

    for sample in samples:
        filepath = sample_dir / sample['filename']
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(sample['content'])

    print(f"✓ Created {len(samples)} sample .xd files in {sample_dir}")
    return sample_dir


def test_parser(sample_dir: Path):
    """Test the .xd parser."""
    print("\n" + "=" * 70)
    print("TESTING XD PARSER")
    print("=" * 70)

    parser = XDParser()
    sample_file = list(sample_dir.glob('*.xd'))[0]

    print(f"\nParsing: {sample_file.name}")
    result = parser.parse_file(sample_file)

    print(f"\nParsed data:")
    print(f"  Date: {result['date']}")
    print(f"  Day: {result['day']}")
    print(f"  Size: {result['size']}")
    print(f"  Author: {result['author']}")
    print(f"  Publisher: {result['publisher']}")
    print(f"  Theme: {result['theme']}")
    print(f"  Number of clues: {len(result['clues'])}")
    print(f"  Grid dimensions: {len(result['grid'])}x{len(result['grid'][0]) if result['grid'] else 0}")

    if result['clues']:
        print(f"\n  Sample clues:")
        for i, clue in enumerate(result['clues'][:3], 1):
            print(f"    {i}. [{clue.get('number')} {clue.get('direction')}] {clue.get('clue')}")
            print(f"       Answer: {clue.get('answer')}")

    if result['grid']:
        print(f"\n  Grid:")
        for row in result['grid']:
            print(f"    {row}")

    print("\n✓ Parser test successful")


def test_builder(output_dir: Path):
    """Test the dataset builder."""
    print("\n" + "=" * 70)
    print("TESTING DATASET BUILDER")
    print("=" * 70)

    builder = CrosswordDatasetBuilder(output_dir=str(output_dir))
    builder.process_xd_files()
    builder.generate_csv_summary()
    builder.print_statistics()

    print(f"\n✓ Dataset built successfully")
    print(f"  Output: {builder.output_file}")
    print(f"  CSV: {builder.csv_file}")


def test_validator(output_dir: Path):
    """Test the dataset validator."""
    print("\n" + "=" * 70)
    print("TESTING DATASET VALIDATOR")
    print("=" * 70)

    dataset_file = output_dir / 'processed' / 'puzzles.jsonl'
    validator = DatasetValidator(str(dataset_file))
    result = validator.validate()

    if result['valid']:
        print("\n✓ Validation test successful")
    else:
        print("\n⚠ Validation found issues (expected for demo)")


def test_analyzer(output_dir: Path):
    """Test the dataset analyzer."""
    print("\n" + "=" * 70)
    print("TESTING DATASET ANALYZER")
    print("=" * 70)

    dataset_file = output_dir / 'processed' / 'puzzles.jsonl'
    analyzer = DatasetAnalyzer(str(dataset_file))

    if not analyzer.load_data():
        print("✗ Failed to load data")
        return

    analyzer.analyze()

    # Export stats
    stats_file = output_dir / 'processed' / 'stats.json'
    analyzer.export_stats(str(stats_file))

    print(f"\n✓ Analysis complete")
    print(f"  Stats exported to: {stats_file}")


def show_sample_output(output_dir: Path):
    """Show sample output in the requested format."""
    print("\n" + "=" * 70)
    print("SAMPLE OUTPUT (3 EXAMPLE ENTRIES)")
    print("=" * 70)

    dataset_file = output_dir / 'processed' / 'puzzles.jsonl'

    with open(dataset_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"\nShowing {min(3, len(lines))} entries from {len(lines)} total puzzles:\n")

    for i, line in enumerate(lines[:3], 1):
        puzzle = json.loads(line)
        print(f"--- Entry {i} ---")
        print(json.dumps(puzzle, indent=2))
        print()


def main():
    """Run the demo."""
    print("=" * 70)
    print("CROSSWORD DATASET BUILDER DEMO")
    print("=" * 70)
    print("\nThis demo will:")
    print("1. Create sample .xd files")
    print("2. Parse and build a dataset")
    print("3. Validate the dataset")
    print("4. Generate statistics")
    print("5. Show sample outputs")

    # Use demo directory
    output_dir = Path('crossword_demo')

    # Step 1: Create sample data
    sample_dir = create_sample_xd_files(output_dir)

    # Step 2: Test parser
    test_parser(sample_dir)

    # Step 3: Test builder
    test_builder(output_dir)

    # Step 4: Test validator
    test_validator(output_dir)

    # Step 5: Test analyzer
    test_analyzer(output_dir)

    # Step 6: Show sample output
    show_sample_output(output_dir)

    print("\n" + "=" * 70)
    print("DEMO COMPLETE!")
    print("=" * 70)
    print("\nAll files have been created in the 'crossword_demo' directory.")
    print("\nTo use with real data:")
    print("1. Download data from https://xd.saul.pw/data")
    print("2. Place .xd files in crossword_data/raw/")
    print("3. Run: python crossword_dataset_builder.py")
    print("\nFor help: python crossword_dataset_builder.py --help")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
