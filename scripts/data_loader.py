"""
Data loader module for NFL play-by-play analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set plot styles
plt.style.use('ggplot')
sns.set_palette('colorblind')


def load_pbp_data(file_path='../data/pbp-2024.csv'):
    """
    Load NFL play-by-play data and perform initial cleaning.
    
    Parameters:
    -----------
    file_path : str
        Path to the play-by-play CSV file
        
    Returns:
    --------
    pd.DataFrame
        Cleaned play-by-play dataframe
    """
    # Load the data
    df = pd.read_csv(file_path, low_memory=False)
    
    # Basic data cleaning
    # Convert boolean columns to proper boolean type
    bool_columns = [col for col in df.columns if col.startswith('Is')]
    for col in bool_columns:
        if col in df.columns:
            df[col] = df[col].astype('bool')
    
    # Handle date column
    if 'GameDate' in df.columns:
        df['GameDate'] = pd.to_datetime(df['GameDate'])
    
    # Add derived columns for analysis
    if all(col in df.columns for col in ['Quarter', 'Minute', 'Second']):
        # Create game_seconds column (time elapsed in the game)
        df['game_seconds'] = ((df['Quarter'] - 1) * 900) + ((15 - df['Minute']) * 60) - df['Second']
        
        # Identify two-minute drill situations
        df['two_min_drill'] = ((df['Quarter'] == 2) | (df['Quarter'] == 4)) & (df['Minute'] <= 2)
    
    # Add field position - distance from own goal
    if 'YardLine' in df.columns and 'YardLineDirection' in df.columns:
        df['field_position'] = np.where(
            df['YardLineDirection'] == 'OWN',
            df['YardLine'],
            100 - df['YardLine']
        )
    
    # Identify scoring plays
    if 'IsTouchdown' in df.columns:
        df['is_scoring_play'] = (
            df['IsTouchdown'] | 
            (df['PlayType'] == 'FIELD_GOAL') | 
            (df['PlayType'] == 'EXTRA_POINT')
        )
    
    # Red zone plays (inside opponent's 20-yard line)
    if 'field_position' in df.columns:
        df['is_redzone'] = df['field_position'] >= 80
    
    # Clean team abbreviations if needed
    if 'OffenseTeam' in df.columns:
        df['OffenseTeam'] = df['OffenseTeam'].str.strip()
    
    if 'DefenseTeam' in df.columns:
        df['DefenseTeam'] = df['DefenseTeam'].str.strip()
    
    return df


def get_team_colors():
    """
    Return a dictionary of NFL team colors for visualization.
    
    Returns:
    --------
    dict
        Mapping of team abbreviations to primary and secondary colors
    """
    return {
        'ARI': ('#97233F', '#000000'),  # Arizona Cardinals
        'ATL': ('#A71930', '#000000'),  # Atlanta Falcons
        'BAL': ('#241773', '#000000'),  # Baltimore Ravens
        'BUF': ('#00338D', '#C60C30'),  # Buffalo Bills
        'CAR': ('#0085CA', '#101820'),  # Carolina Panthers
        'CHI': ('#0B162A', '#C83803'),  # Chicago Bears
        'CIN': ('#FB4F14', '#000000'),  # Cincinnati Bengals
        'CLE': ('#311D00', '#FF3C00'),  # Cleveland Browns
        'DAL': ('#003594', '#869397'),  # Dallas Cowboys
        'DEN': ('#FB4F14', '#002244'),  # Denver Broncos
        'DET': ('#0076B6', '#B0B7BC'),  # Detroit Lions
        'GB':  ('#203731', '#FFB612'),  # Green Bay Packers
        'HOU': ('#03202F', '#A71930'),  # Houston Texans
        'IND': ('#002C5F', '#A2AAAD'),  # Indianapolis Colts
        'JAX': ('#101820', '#D7A22A'),  # Jacksonville Jaguars
        'KC':  ('#E31837', '#FFB81C'),  # Kansas City Chiefs
        'LV':  ('#000000', '#A5ACAF'),  # Las Vegas Raiders
        'LAC': ('#0080C6', '#FFC20E'),  # Los Angeles Chargers
        'LA':  ('#003594', '#FFA300'),  # Los Angeles Rams
        'MIA': ('#008E97', '#FC4C02'),  # Miami Dolphins
        'MIN': ('#4F2683', '#FFC62F'),  # Minnesota Vikings
        'NE':  ('#002244', '#C60C30'),  # New England Patriots
        'NO':  ('#D3BC8D', '#101820'),  # New Orleans Saints
        'NYG': ('#0B2265', '#A71930'),  # New York Giants
        'NYJ': ('#125740', '#000000'),  # New York Jets
        'PHI': ('#004C54', '#A5ACAF'),  # Philadelphia Eagles
        'PIT': ('#FFB612', '#101820'),  # Pittsburgh Steelers
        'SF':  ('#AA0000', '#B3995D'),  # San Francisco 49ers
        'SEA': ('#002244', '#69BE28'),  # Seattle Seahawks
        'TB':  ('#D50A0A', '#0A0A08'),  # Tampa Bay Buccaneers
        'TEN': ('#0C2340', '#4B92DB'),  # Tennessee Titans
        'WAS': ('#5A1414', '#FFB612'),  # Washington Commanders
    }


def team_success_rate(df, team=None):
    """
    Calculate team success rates on different downs.
    
    A play is considered successful if:
    - 1st down: Gain of 40% or more of yards to go
    - 2nd down: Gain of 60% or more of yards to go
    - 3rd/4th down: Converted for a first down
    
    Parameters:
    -----------
    df : pd.DataFrame
        Play-by-play dataframe
    team : str, optional
        Team abbreviation to filter for
        
    Returns:
    --------
    pd.DataFrame
        Success rates by down and team
    """
    # Filter for the team if specified
    if team:
        team_df = df[df['OffenseTeam'] == team]
    else:
        team_df = df.copy()
    
    # Filter out non-standard plays
    team_df = team_df[
        (team_df['Down'].isin([1, 2, 3, 4])) & 
        (team_df['PlayType'].isin(['PASS', 'RUSH']))
    ]
    
    # Define success criteria
    def is_successful(row):
        down = row['Down']
        yards = row['Yards'] if not pd.isna(row['Yards']) else 0
        to_go = row['ToGo'] if not pd.isna(row['ToGo']) else 10
        series_first_down = row['SeriesFirstDown'] if not pd.isna(row['SeriesFirstDown']) else 0
        
        if down == 1:
            return yards >= (0.4 * to_go)
        elif down == 2:
            return yards >= (0.6 * to_go)
        elif down in [3, 4]:
            return series_first_down == 1
        return False
    
    # Apply success criteria
    team_df['is_successful'] = team_df.apply(is_successful, axis=1)
    
    # Group by down and calculate success rates
    success_by_down = team_df.groupby(['OffenseTeam', 'Down'])['is_successful'].agg(
        success_rate=lambda x: x.mean(),
        play_count=lambda x: x.count()
    ).reset_index()
    
    return success_by_down


if __name__ == "__main__":
    # Test data loading
    data_path = Path(__file__).parent.parent / 'data' / 'pbp-2024.csv'
    df = load_pbp_data(str(data_path))
    print(f"Loaded {len(df)} plays from the 2024 NFL season")
    print(f"Columns: {df.columns.tolist()}") 