# Crossword Dataset Builder - Quick Start Guide

## 🚀 5-Minute Start

### 1. Run the Demo
```bash
python demo_crossword.py
```
This creates sample data and tests all features.

### 2. Use Real Data

**Download crossword data:**
- Visit: https://xd.saul.pw/data
- Download files (e.g., collections or xd-clues.zip)
- Place in: `crossword_data/raw/`

**Build your dataset:**
```bash
# Install dependencies first
pip install -r requirements_crossword.txt

# Build dataset (process all .xd files)
python crossword_dataset_builder.py

# Or limit to 500 puzzles for testing
python crossword_dataset_builder.py --limit 500
```

**Validate:**
```bash
python validate_dataset.py crossword_data/processed/puzzles.jsonl
```

**Analyze:**
```bash
python analyze_dataset.py crossword_data/processed/puzzles.jsonl
```

## 📁 Output Files

After running, you'll have:

```
crossword_data/processed/
├── puzzles.jsonl         # Main dataset (one puzzle per line)
├── puzzles_summary.csv   # Summary statistics
└── stats.json           # Detailed statistics
```

## 💡 What You Get

### JSONL Format (puzzles.jsonl)
Each line is a complete puzzle:
```json
{
  "date": "2024-01-15",
  "day": "Monday",
  "size": "15x15",
  "clues": [
    {"number": 1, "direction": "across", "clue": "Feline pet", "answer": "CAT"}
  ],
  "grid": ["CAT", "APE", "RAT"],
  "theme": "Animals",
  "author": "John Constructor",
  "source": "xd.saul.pw"
}
```

### CSV Summary (puzzles_summary.csv)
| date | day | size | num_clues | avg_answer_length | author | publisher | has_theme | source |
|------|-----|------|-----------|-------------------|--------|-----------|-----------|--------|
| 2024-01-15 | Monday | 3x3 | 6 | 3.0 | John Constructor | Sample | no | xd.saul.pw |

### Statistics (from analyzer)
- Distribution by day of week
- Grid sizes (15x15, 21x21, etc.)
- Answer length patterns (3-15 letters)
- Clue complexity (word count)
- Temporal trends
- Top authors/publishers

## 🎯 Target Dataset Size

For LLM fine-tuning:
- **Minimum**: 100-500 puzzles (~10K-50K clues)
- **Good**: 1,000-5,000 puzzles (~100K-500K clues)
- **Optimal**: 5,000+ puzzles (500K+ clues)

The xd.saul.pw archive has **thousands** of puzzles available.

## 📊 Sample Analysis Output

```
DATASET ANALYSIS REPORT
======================================================================
Total puzzles: 3
Total clues: 24
Average clues per puzzle: 8.0

DISTRIBUTION BY DAY OF WEEK:
  Monday      :     1 ( 33.3%) ████████████████
  Tuesday     :     1 ( 33.3%) ████████████████
  Wednesday   :     1 ( 33.3%) ████████████████

ANSWER LENGTH STATISTICS:
  Minimum: 3
  Maximum: 5
  Average: 4.17
  Median: 4
```

## 🔍 Command Reference

```bash
# Build dataset
python crossword_dataset_builder.py [--limit N] [--download-hf]

# Validate dataset
python validate_dataset.py <dataset.jsonl> [--output report.json]

# Analyze dataset
python analyze_dataset.py <dataset.jsonl> [--export stats.json] [--samples 5]

# Test parser
python xd_parser.py

# Run full demo
python demo_crossword.py
```

## ⚠️ Legal Notice

- ✅ Uses only legal, freely available data sources
- ✅ Pre-1965 NYT puzzles are public domain
- ✅ For educational/personal use only
- ❌ Do not distribute copyrighted content

## 🛠️ Troubleshooting

**"No puzzles found"**
→ Ensure .xd files are in `crossword_data/raw/`

**"Parsing errors"**
→ Check `crossword_data/failed_puzzles.log`

**Out of memory**
→ Use `--limit` flag to process in batches

## 📚 Learn More

See `CROSSWORD_README.md` for complete documentation.

## 🎓 Use Cases

Train your LLM to:
1. Generate clues from answers
2. Solve crossword clues
3. Construct themed puzzles
4. Estimate puzzle difficulty
5. Analyze wordplay patterns
