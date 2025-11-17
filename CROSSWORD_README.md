# Crossword Puzzle Dataset Builder

Build a crossword puzzle dataset for personal LLM fine-tuning experimentation. This tool collects crossword puzzles from legal sources and converts them into a structured format suitable for machine learning.

**⚠️ For educational/personal use only, not for distribution.**

## Legal Data Sources

This tool uses **legally accessible** crossword data:

1. **xd.saul.pw** - Free crossword puzzle data in .xd format
   - Pre-1965 NYT puzzles (public domain)
   - Thousands of puzzles from various publishers
   - Download at: https://xd.saul.pw/data

2. **CrosswordQA** - Hugging Face dataset
   - 6M+ clue-answer pairs
   - Available at: https://huggingface.co/datasets/albertxu/CrosswordQA

## Features

- ✅ Parse .xd format crossword files
- ✅ Extract complete puzzle data (clues, answers, grid, metadata)
- ✅ Output in JSONL format (one puzzle per line)
- ✅ Generate CSV summary statistics
- ✅ Progress tracking and resume capability
- ✅ Data validation
- ✅ Statistical analysis
- ✅ Error handling and logging

## Output Format

### JSONL Format
Each line is a JSON object representing one puzzle:

```json
{
  "date": "2024-01-15",
  "day": "Monday",
  "size": "15x15",
  "clues": [
    {
      "number": 1,
      "direction": "across",
      "clue": "Feline pet",
      "answer": "CAT"
    }
  ],
  "grid": ["CAT", "APE", "RAT"],
  "theme": "",
  "author": "John Constructor",
  "editor": "Will Shortz",
  "publisher": "Sample Publisher",
  "source": "xd.saul.pw"
}
```

### CSV Summary
Includes: date, day, size, number of clues, average answer length, author, publisher, theme presence, source.

## Installation

```bash
# Install dependencies
pip install -r requirements_crossword.txt

# Optional: For HuggingFace dataset support
pip install datasets huggingface-hub
```

## Quick Start

### 1. Run Demo (Test Everything)

```bash
python demo_crossword.py
```

This creates sample data and demonstrates all features.

### 2. Build Dataset from Real Data

**Step 1: Download crossword data**

Visit https://xd.saul.pw/data and download:
- Individual puzzle collections, or
- xd-clues.zip (millions of clues)

Place downloaded files in `crossword_data/raw/`

**Step 2: Run the builder**

```bash
# Process all .xd files
python crossword_dataset_builder.py

# Limit to first 500 puzzles
python crossword_dataset_builder.py --limit 500

# Also download CrosswordQA from HuggingFace
python crossword_dataset_builder.py --download-hf
```

**Step 3: Validate the dataset**

```bash
python validate_dataset.py crossword_data/processed/puzzles.jsonl
```

**Step 4: Analyze statistics**

```bash
# Show statistics
python analyze_dataset.py crossword_data/processed/puzzles.jsonl

# Export stats to JSON
python analyze_dataset.py crossword_data/processed/puzzles.jsonl --export stats.json

# Show sample puzzles
python analyze_dataset.py crossword_data/processed/puzzles.jsonl --samples 5
```

## File Structure

```
crossword_data/
├── raw/                          # Raw .xd files
│   ├── samples/                  # Sample data
│   └── [downloaded files]
├── processed/
│   ├── puzzles.jsonl            # Main dataset (JSONL)
│   ├── puzzles_summary.csv      # CSV summary
│   └── stats.json               # Statistics export
├── builder_state.json            # Resume state
├── failed_puzzles.log           # Failed parsing log
└── crossword_builder.log        # Main log file
```

## Scripts

### 1. `xd_parser.py`
Parses .xd format crossword files.

```python
from xd_parser import XDParser

parser = XDParser()
puzzle = parser.parse_file('puzzle.xd')
print(puzzle['date'], puzzle['size'], len(puzzle['clues']))
```

### 2. `crossword_dataset_builder.py`
Main dataset builder with progress tracking.

```bash
python crossword_dataset_builder.py --help
```

Options:
- `--output-dir DIR` - Output directory (default: crossword_data)
- `--limit N` - Process only first N puzzles
- `--download-hf` - Download CrosswordQA from HuggingFace
- `--force-download` - Force re-download

### 3. `validate_dataset.py`
Validates dataset for completeness and quality.

```bash
python validate_dataset.py crossword_data/processed/puzzles.jsonl --output validation_report.json
```

Checks:
- Required fields present
- Data integrity
- No duplicates
- Grid validity
- Clue/answer consistency

### 4. `analyze_dataset.py`
Generates comprehensive statistics.

```bash
python analyze_dataset.py crossword_data/processed/puzzles.jsonl --export stats.json --samples 3
```

Shows:
- Distribution by day of week
- Grid size distribution
- Answer length patterns
- Publisher/author statistics
- Temporal trends
- Sample puzzles

## Dataset Statistics

The analyzer shows:

- **Overview**: Total puzzles, total clues, average clues per puzzle
- **Day Distribution**: How many puzzles per day of week
- **Size Distribution**: Most common grid sizes (15x15, 21x21, etc.)
- **Answer Lengths**: Min/max/average/median letter counts
- **Clue Complexity**: Word count in clue text
- **Sources**: Which sources contributed most puzzles
- **Temporal**: Puzzle distribution by year

## Resume Capability

The builder saves state periodically. If interrupted:

```bash
# Simply run again - it will resume from where it left off
python crossword_dataset_builder.py
```

State is saved in `builder_state.json`.

## Error Handling

- Failed parses are logged to `failed_puzzles.log`
- All operations logged to `crossword_builder.log`
- Network operations have retry logic with exponential backoff
- Malformed JSON entries are skipped with warnings

## Use Cases for LLM Fine-tuning

This dataset is suitable for training models to:

1. **Generate clues from answers**
   - Input: COMPUTER
   - Output: Electronic device for processing data

2. **Solve clues (answer prediction)**
   - Input: Electronic device for processing data (8 letters)
   - Output: COMPUTER

3. **Crossword construction**
   - Generate themed puzzle sets
   - Suggest intersecting words

4. **Difficulty estimation**
   - Predict puzzle difficulty based on day
   - Analyze clue complexity

5. **Theme detection**
   - Identify puzzle themes
   - Generate themed word lists

## Dataset Size Recommendations

For meaningful fine-tuning:

- **Minimum**: 100-500 puzzles (~10,000-50,000 clues)
- **Recommended**: 1,000-5,000 puzzles (~100,000-500,000 clues)
- **Optimal**: 5,000+ puzzles (500,000+ clues)

The xd.saul.pw archive contains thousands of puzzles, which should provide sufficient data.

## Legal and Ethical Considerations

- ✅ Uses only legally accessible public domain and freely available data
- ✅ Pre-1965 NYT puzzles are public domain
- ✅ xd.saul.pw provides data for free use
- ✅ CrosswordQA is openly available on HuggingFace
- ⚠️ For personal/educational use only
- ⚠️ Do not distribute scraped copyrighted content
- ⚠️ Respect robots.txt and rate limits

## Troubleshooting

**No puzzles found**
- Ensure .xd files are in `crossword_data/raw/`
- Check file permissions
- Extract any .zip files first

**Parsing errors**
- Check `failed_puzzles.log` for details
- Some .xd files may use non-standard formats
- Parser handles most common variations

**Out of memory**
- Use `--limit` to process in batches
- Process subset at a time
- Dataset is streamed, but large batches use more memory

**HuggingFace download fails**
- Ensure `datasets` library is installed: `pip install datasets`
- Check internet connection
- Some datasets are large (may take time)

## References

- **xd format specification**: https://github.com/century-arcade/xd/blob/master/doc/xd-format.md
- **xd.saul.pw**: https://xd.saul.pw/
- **CrosswordQA**: https://huggingface.co/datasets/albertxu/CrosswordQA
- **Related tools**: https://www.georgeho.org/crosswords-datasets-dictionaries/

## License

This code is provided for educational purposes. The crossword puzzle data itself remains subject to its original copyright. Pre-1965 NYT puzzles are public domain.

## Contributing

This is a personal educational project. Feel free to adapt for your own use.

## Acknowledgments

- Saul Pwanson for creating the .xd format and xd.saul.pw
- Albert Xu for the CrosswordQA dataset
- The crossword construction community for open data sharing
