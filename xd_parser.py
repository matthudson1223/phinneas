"""
Parser for .xd crossword format files.
Converts .xd format to structured Python dictionaries.

The .xd format is a plain-text format for crossword puzzles.
Specification: https://github.com/century-arcade/xd/blob/master/doc/xd-format.md
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime


class XDParser:
    """Parser for .xd (crossword) format files."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset parser state."""
        self.metadata = {}
        self.grid = []
        self.clues = []
        self.answers = {}
        self.current_section = 'metadata'

    def parse_file(self, filepath: str) -> Dict[str, Any]:
        """Parse an .xd format file and return structured data."""
        self.reset()

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        return self.parse_content(content)

    def parse_content(self, content: str) -> Dict[str, Any]:
        """Parse .xd format content and return structured data."""
        self.reset()

        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].rstrip()

            # Empty line - might indicate section change
            if not line:
                i += 1
                continue

            # Metadata (Key: Value format)
            if ':' in line and self.current_section == 'metadata':
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                self.metadata[key.lower()] = value

                # Check if we're done with metadata (grid follows)
                if i + 1 < len(lines) and not ':' in lines[i + 1] and lines[i + 1].strip():
                    if not any(char.isalpha() and char.islower() for char in lines[i + 1]):
                        self.current_section = 'grid'
                i += 1
                continue

            # Grid section (lines with # and .)
            if self.current_section == 'grid' or (line and all(c in '#.ABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in line.strip())):
                if line.strip() and not line.startswith('##'):
                    self.current_section = 'grid'
                    self.grid.append(line.strip())
                    i += 1
                    continue
                elif line.strip() == '':
                    # Empty line after grid - clues follow
                    self.current_section = 'clues'
                    i += 1
                    continue

            # Clues section
            if self.current_section in ['clues', 'grid']:
                # Check if this looks like a clue (starts with direction or number)
                if line.strip():
                    self.current_section = 'clues'
                    clue_match = re.match(r'^([A-Z]\d+)\.\s*(.+?)\s*~\s*(.+)$', line)
                    if clue_match:
                        number_dir, clue_text, answer = clue_match.groups()
                        direction = 'across' if number_dir[0] == 'A' else 'down'
                        number = int(number_dir[1:])

                        self.clues.append({
                            'number': number,
                            'direction': direction,
                            'clue': clue_text.strip(),
                            'answer': answer.strip()
                        })
                        self.answers[f"{number}{direction[0].upper()}"] = answer.strip()
                    else:
                        # Try alternative formats
                        # Format: "1. Clue text ~ ANSWER"
                        alt_match = re.match(r'^(\d+)\.\s*(.+?)\s*~\s*(.+)$', line)
                        if alt_match:
                            number, clue_text, answer = alt_match.groups()
                            # Try to determine direction from context or grid
                            self.clues.append({
                                'number': int(number),
                                'direction': 'unknown',
                                'clue': clue_text.strip(),
                                'answer': answer.strip()
                            })

            i += 1

        # Extract grid size
        grid_height = len(self.grid)
        grid_width = len(self.grid[0]) if self.grid else 0

        return {
            'metadata': self.metadata,
            'date': self.metadata.get('date', ''),
            'day': self._get_day_of_week(self.metadata.get('date', '')),
            'size': f"{grid_width}x{grid_height}",
            'grid': self.grid,
            'clues': self.clues,
            'answers': self.answers,
            'theme': self.metadata.get('theme', ''),
            'author': self.metadata.get('author', ''),
            'editor': self.metadata.get('editor', ''),
            'copyright': self.metadata.get('copyright', ''),
            'publisher': self.metadata.get('publisher', '')
        }

    def _get_day_of_week(self, date_str: str) -> str:
        """Extract day of week from date string."""
        if not date_str:
            return ''

        try:
            # Try various date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%A')
                except ValueError:
                    continue
        except:
            pass

        return ''


def parse_xd_simple(content: str) -> Dict[str, Any]:
    """
    Simple .xd format parser for common patterns.

    .xd format structure:
    1. Metadata (Key: Value pairs)
    2. Empty line
    3. Grid (# for black squares, . for white)
    4. Empty line
    5. Clues (format: "A1. Clue text ~ ANSWER" or "D1. Clue text ~ ANSWER")
    """
    lines = [line.rstrip() for line in content.split('\n')]

    metadata = {}
    grid = []
    clues = []

    section = 'metadata'

    for line in lines:
        if not line:
            continue

        # Parse metadata
        if ':' in line and section == 'metadata':
            parts = line.split(':', 1)
            if len(parts) == 2:
                key, value = parts
                metadata[key.strip().lower()] = value.strip()
                continue

        # Parse grid (lines with # and . and letters)
        if section in ['metadata', 'grid']:
            if line and all(c in '#.ABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in line):
                section = 'grid'
                grid.append(line)
                continue
            elif section == 'grid':
                section = 'clues'

        # Parse clues
        if section == 'clues':
            # Match patterns like "A1. Clue ~ ANSWER" or "D12. Clue ~ ANSWER"
            match = re.match(r'^([AD])(\d+)\.\s*(.+?)\s*~\s*(.+)$', line)
            if match:
                direction_letter, num, clue_text, answer = match.groups()
                direction = 'across' if direction_letter == 'A' else 'down'
                clues.append({
                    'number': int(num),
                    'direction': direction,
                    'clue': clue_text.strip(),
                    'answer': answer.strip()
                })

    # Calculate grid size
    grid_height = len(grid)
    grid_width = len(grid[0]) if grid else 0

    # Get day of week
    date_str = metadata.get('date', '')
    day = ''
    if date_str:
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            day = dt.strftime('%A')
        except:
            pass

    return {
        'metadata': metadata,
        'date': date_str,
        'day': day,
        'size': f"{grid_width}x{grid_height}",
        'grid': grid,
        'clues': clues,
        'theme': metadata.get('theme', ''),
        'author': metadata.get('author', ''),
        'editor': metadata.get('editor', ''),
        'copyright': metadata.get('copyright', ''),
        'publisher': metadata.get('publisher', '')
    }


if __name__ == '__main__':
    # Test with a sample .xd format
    sample = """Title: Sample Puzzle
Author: John Doe
Editor: Jane Smith
Date: 2024-01-15
Publisher: Test Publisher

ABC
DEF
GHI

A1. First across clue ~ ABC
A2. Second across clue ~ GHI
D1. First down clue ~ ADG
D2. Second down clue ~ BEH
"""

    parser = XDParser()
    result = parser.parse_content(sample)

    print("Parsed puzzle:")
    print(f"Date: {result['date']}")
    print(f"Day: {result['day']}")
    print(f"Size: {result['size']}")
    print(f"Clues: {len(result['clues'])}")
    print(f"Grid: {result['grid']}")
    print(f"First clue: {result['clues'][0] if result['clues'] else 'None'}")
