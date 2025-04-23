# NFL Play-by-Play Analysis

This project analyzes NFL play-by-play data to understand team offensive identities and their evolution throughout the season. The analysis includes:

- Offensive identity clustering
- Run-pass ratio analysis
- Down and distance tendencies
- Success rate analysis
- Offensive evolution tracking

## Project Structure

```
nfl-pbp-analysis/
├── data/               # Data files
├── notebooks/          # Jupyter notebooks for analysis
│   ├── 01_data_exploration.ipynb
│   ├── 02_play_type_analysis.ipynb
│   ├── 03_success_rate_analysis.ipynb
│   └── 04_offensive_identity.ipynb
└── scripts/            # Python scripts
    ├── data_loader.py
    └── visualizations.py
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nfl-pbp-analysis.git
cd nfl-pbp-analysis
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Run Jupyter Notebook:
```bash
jupyter notebook
```

## Requirements

- Python 3.8+
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn
- jupyter

## Data

The project uses NFL play-by-play data from the 2024 season. The data is stored in the `data` directory. It can also be accessed at https://nflsavant.com/about.php.

## Analysis

The analysis is organized into four main notebooks:

1. **Data Exploration**: Initial data loading and cleaning
2. **Play Type Analysis**: Analysis of run-pass ratios and play type tendencies
3. **Success Rate Analysis**: Analysis of offensive success rates
4. **Offensive Identity**: Clustering analysis of team offensive identities

## Contributing

Feel free to submit issues and enhancement requests!
