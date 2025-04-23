"""
Visualization utilities for NFL play-by-play analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
from scripts.data_loader import get_team_colors

# Set plot style
plt.style.use('ggplot')
sns.set_palette('colorblind')


def plot_field(ax=None, show_yard_lines=True, show_field_labels=True):
    """
    Create a football field visualization.
    
    Parameters:
    -----------
    ax : matplotlib.axes, optional
        Axes to plot on
    show_yard_lines : bool
        Whether to show yard lines
    show_field_labels : bool
        Whether to show yard line labels
        
    Returns:
    --------
    matplotlib.axes
        Axes with football field
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6.33))
    
    # Field dimensions
    field_length = 120  # 100 yards + 2 end zones of 10 yards each
    field_width = 53.3
    
    # Draw the field
    rect = patches.Rectangle((0, 0), field_length, field_width, linewidth=2, 
                            edgecolor='black', facecolor='#3d9238', alpha=0.3)
    ax.add_patch(rect)
    
    # Draw end zones
    end_zone1 = patches.Rectangle((0, 0), 10, field_width, linewidth=2,
                                edgecolor='black', facecolor='#3d9238', alpha=0.6)
    end_zone2 = patches.Rectangle((field_length-10, 0), 10, field_width, linewidth=2,
                                edgecolor='black', facecolor='#3d9238', alpha=0.6)
    ax.add_patch(end_zone1)
    ax.add_patch(end_zone2)
    
    if show_yard_lines:
        # Draw yard lines
        for yard in range(10, field_length-10, 5):
            ax.axvline(x=yard, color='white', linestyle='-', alpha=0.7)
            
            if yard % 10 == 0 and show_field_labels:
                # Add yard line labels
                yard_label = yard - 10
                if yard_label <= 50:
                    ax.text(yard, field_width/2, str(yard_label), 
                          horizontalalignment='center', verticalalignment='bottom',
                          color='black', fontsize=10)
                else:
                    ax.text(yard, field_width/2, str(100 - yard_label), 
                          horizontalalignment='center', verticalalignment='bottom',
                          color='black', fontsize=10)
    
    # Set limits and remove axes
    ax.set_xlim(0, field_length)
    ax.set_ylim(0, field_width)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    
    return ax


def plot_play_heatmap(df, play_type=None, down=None, ax=None):
    """
    Plot heatmap of play frequency by field position and down.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Play-by-play dataframe
    play_type : str, optional
        Filter by play type ('PASS' or 'RUSH')
    down : int, optional
        Filter by down (1, 2, 3, or 4)
    ax : matplotlib.axes, optional
        Axes to plot on
        
    Returns:
    --------
    matplotlib.axes
        Axes with heatmap
    """
    # Filter data
    plot_df = df.copy()
    
    if play_type:
        plot_df = plot_df[plot_df['PlayType'] == play_type]
    
    if down:
        plot_df = plot_df[plot_df['Down'] == down]
    
    # Check if there's enough data
    if len(plot_df) < 10:
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Not enough data for visualization', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        return ax
    
    # Create 2D histogram
    if 'field_position' in plot_df.columns and 'Down' in plot_df.columns:
        # Group data into bins
        bins_x = np.arange(0, 101, 5)  # field position in 5-yard increments
        bins_y = [0.5, 1.5, 2.5, 3.5, 4.5]  # downs
        
        # Filter valid data
        valid_data = plot_df[
            (~pd.isna(plot_df['field_position'])) & 
            (~pd.isna(plot_df['Down'])) &
            (plot_df['Down'].isin([1, 2, 3, 4]))
        ]
        
        # Create histogram
        hist, x_edges, y_edges = np.histogram2d(
            valid_data['field_position'], 
            valid_data['Down'],
            bins=[bins_x, bins_y]
        )
        
        # Create heatmap
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 4))
        
        im = ax.imshow(hist.T, cmap='viridis', origin='lower', aspect='auto',
                     extent=[0, 100, 1, 4])
        
        # Add colorbar
        plt.colorbar(im, ax=ax, label='Play frequency')
        
        # Set labels
        ax.set_xlabel('Field Position (Distance from Own Goal)')
        ax.set_ylabel('Down')
        ax.set_yticks([1, 2, 3, 4])
        
        # Add title
        title = 'Play Frequency by Field Position and Down'
        if play_type:
            title = f'{play_type} {title}'
        ax.set_title(title)
        
        return ax
    else:
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Required columns not available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        return ax


def plot_team_run_pass_ratio(df, top_n=16):
    """
    Plot run-pass ratio for NFL teams.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Play-by-play dataframe
    top_n : int
        Number of teams to display
        
    Returns:
    --------
    matplotlib.figure
        Figure with run-pass ratio plot
    """
    # Filter relevant plays
    play_df = df[(df['PlayType'].isin(['PASS', 'RUSH'])) & (~pd.isna(df['OffenseTeam']))]
    
    # Calculate run-pass ratio
    team_counts = play_df.groupby(['OffenseTeam', 'PlayType']).size().unstack(fill_value=0)
    
    # Ensure the columns exist, even if with zeros
    if 'PASS' not in team_counts.columns:
        team_counts['PASS'] = 0
    if 'RUSH' not in team_counts.columns:
        team_counts['RUSH'] = 0
    
    # Calculate totals and percentages
    team_counts['Total'] = team_counts['PASS'] + team_counts['RUSH']
    team_counts['Pass_Pct'] = team_counts['PASS'] / team_counts['Total']
    team_counts['Rush_Pct'] = team_counts['RUSH'] / team_counts['Total']
    
    # Reset index for easier access
    team_ratios = team_counts.reset_index()
    
    # Sort by rush percentage
    team_ratios = team_ratios.sort_values('Rush_Pct', ascending=False).head(top_n)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create stacked bars
    team_colors = get_team_colors()
    bar_colors = [team_colors.get(team, ('#1f77b4', '#aec7e8')) for team in team_ratios['OffenseTeam']]
    primary_colors = [color[0] for color in bar_colors]
    
    # Plot stacked bars
    bars1 = ax.barh(team_ratios['OffenseTeam'], team_ratios['Rush_Pct'], 
                  color='#1f77b4', alpha=0.8, label='Rush')
    bars2 = ax.barh(team_ratios['OffenseTeam'], team_ratios['Pass_Pct'], 
                  left=team_ratios['Rush_Pct'], color='#ff7f0e', 
                  alpha=0.8, label='Pass')
    
    # Add percentage labels
    for i, (team, rush_pct) in enumerate(zip(team_ratios['OffenseTeam'], team_ratios['Rush_Pct'])):
        if rush_pct > 0.1:  # Only show percentage if there's enough space
            ax.text(rush_pct/2, i, f"{rush_pct:.0%}", 
                  va='center', ha='center', color='white', fontweight='bold')
        
        pass_pct = team_ratios.loc[team_ratios['OffenseTeam'] == team, 'Pass_Pct'].values[0]
        if pass_pct > 0.1:  # Only show percentage if there's enough space
            ax.text(rush_pct + pass_pct/2, i, f"{pass_pct:.0%}", 
                  va='center', ha='center', color='white', fontweight='bold')
    
    # Customize plot
    ax.set_xlabel('Percentage of Plays')
    ax.set_title('Run-Pass Ratio by Team (2024 Season)', fontsize=14)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)
    ax.set_xlim(0, 1)
    
    # Add gridlines
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    return fig


def plot_down_distance_heatmap(df, team=None):
    """
    Create a heatmap of play calling based on down and distance.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Play-by-play dataframe
    team : str, optional
        Team abbreviation to filter for
        
    Returns:
    --------
    matplotlib.figure
        Figure with heatmap
    """
    # Filter data
    plot_df = df.copy()
    
    if team:
        plot_df = plot_df[plot_df['OffenseTeam'] == team]
    
    # Filter relevant plays and columns
    play_df = plot_df[
        (plot_df['PlayType'].isin(['PASS', 'RUSH'])) & 
        (~pd.isna(plot_df['Down'])) &
        (~pd.isna(plot_df['ToGo']))
    ]
    
    # Check if there's enough data
    if len(play_df) < 20:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Not enough data for visualization', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        return fig
    
    # Create pivot table for play calling
    # Bin distances to make visualization cleaner
    play_df['DistanceBin'] = pd.cut(
        play_df['ToGo'], 
        bins=[0, 1, 2, 3, 5, 7, 10, 15, 20, 100],
        labels=['1', '2', '3', '4-5', '6-7', '8-10', '11-15', '16-20', '20+']
    )
    
    # Create pivoted data
    pivot_data = play_df.pivot_table(
        index='Down',
        columns='DistanceBin',
        values='PlayType',
        aggfunc=lambda x: sum(x == 'PASS') / len(x) if len(x) > 0 else np.nan
    )
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create heatmap
    sns.heatmap(pivot_data, cmap='RdBu_r', vmin=0, vmax=1, annot=True, 
              fmt='.0%', linewidths=.5, ax=ax, cbar_kws={'label': 'Pass Play %'})
    
    # Customize plot
    title = 'Pass Play Percentage by Down and Distance (2024 Season)'
    if team:
        title = f'{team} {title}'
    ax.set_title(title, fontsize=14)
    
    # Ensure all downs are shown
    ax.set_yticks([1, 2, 3, 4])
    
    plt.tight_layout()
    return fig


def plot_epa_by_team(df, min_plays=100):
    """
    Plot Expected Points Added (EPA) per play by team.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Play-by-play dataframe with EPA data
    min_plays : int
        Minimum number of plays required for inclusion
        
    Returns:
    --------
    matplotlib.figure
        Figure with EPA plot
    """
    # Check if EPA column exists, if not return placeholder
    if 'EPA' not in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'EPA data not available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        return fig
    
    # Filter relevant plays
    play_df = df[
        (df['PlayType'].isin(['PASS', 'RUSH'])) & 
        (~pd.isna(df['EPA'])) &
        (~pd.isna(df['OffenseTeam']))
    ]
    
    # Group by team
    team_epa = play_df.groupby('OffenseTeam').agg(
        epa_per_play=('EPA', 'mean'),
        play_count=('EPA', 'count')
    ).reset_index()
    
    # Filter teams with minimum plays
    team_epa = team_epa[team_epa['play_count'] >= min_plays]
    
    # Sort by EPA per play
    team_epa = team_epa.sort_values('epa_per_play', ascending=False)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Get team colors
    team_colors = get_team_colors()
    bar_colors = [team_colors.get(team, ('#1f77b4', '#aec7e8'))[0] for team in team_epa['OffenseTeam']]
    
    # Create bars
    bars = ax.bar(team_epa['OffenseTeam'], team_epa['epa_per_play'], color=bar_colors)
    
    # Add average line
    avg_epa = team_epa['epa_per_play'].mean()
    ax.axhline(y=avg_epa, color='r', linestyle='--', alpha=0.7, label=f'League Avg: {avg_epa:.3f}')
    
    # Add labels
    for bar in bars:
        height = bar.get_height()
        if height >= 0:
            va = 'bottom'
            y_pos = height + 0.01
        else:
            va = 'top'
            y_pos = height - 0.01
        ax.text(bar.get_x() + bar.get_width()/2., y_pos,
                f'{height:.3f}', ha='center', va=va, rotation=90)
    
    # Customize plot
    ax.set_ylabel('EPA per Play')
    ax.set_title('Expected Points Added (EPA) per Play by Team (2024 Season)', fontsize=14)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    # Test plots
    from scripts.data_loader import load_pbp_data
    
    data_path = Path(__file__).parent.parent / 'data' / 'pbp-2024.csv'
    df = load_pbp_data(str(data_path))
    
    # Example visualization
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_field(ax)
    plt.tight_layout()
    plt.savefig('field_template.png')
    plt.close()
    
    print("Visualization utilities loaded successfully") 