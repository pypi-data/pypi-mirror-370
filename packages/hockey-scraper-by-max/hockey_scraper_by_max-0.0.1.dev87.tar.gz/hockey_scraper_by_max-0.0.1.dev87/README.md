<!-- README.md -->
# Hockey Scraper 🏒

A comprehensive Python package for scraping NHL hockey data with built-in analytics capabilities.

## Features

- **Complete Game Data**: Scrape play-by-play, shifts, rosters, and team statistics
- **Advanced Analytics**: Built-in functions for Corsi, Fenwick, TOI analysis, and more
- **Multiple Data Sources**: Support for NHL API and HTML sources
- **Flexible Output**: Export to pandas, polars, JSON, or CSV formats
- **Async Support**: Fast concurrent data collection
- **Easy to Use**: Simple API with powerful customization options

## Installation

```bash
pip install hockey-scraper
```

## Quick Start

```python
import hockey_scraper as hs

# Scrape team data
teams = hs.scrape_teams()

# Get game data with shifts
df, shifts = await hs.scrape_game_(2024020920, include_shifts=True)

# Build analytics matrix
matrix_df = hs.seconds_matrix(df, shifts)
strengths_df = hs.strengths_by_second(matrix_df)

# Get TOI analysis
toi_stats = hs.toi_by_strength_all(matrix_df, strengths_df)
```


## License

MIT License - see LICENSE file for details.

# LICENSE
MIT License

Copyright (c) 2024 Max Tixador

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

**Made with ❤️ for hockey analytics**
