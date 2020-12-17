import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

from .data_cleaning import optimize


class Files:
    # Data directory
    base_dir = Path('../data')
    # Game-by-game covariate data, coming from the paper
    games = base_dir / Path('mlb_games_df.csv')
    # Pitchers summary data, (primarily reference keys, not much in the way of stats)
    pitchers = base_dir / Path('pitchers_summary.csv')
    # Team-level pitching stats year-by-year
    team_pitching = base_dir / Path('team_pitching_stats.csv')
    # Team-level general data (attendance, W-L, etc)
    teams = base_dir / Path('team_stats.csv')
    # Game-level pitcher stats
    pitchers_games = base_dir / Path('starting_pitchers_games.csv')


class AggFcns:
    mean_fn = np.mean
    min_fn = np.min
    max_fn = np.max


class Dataset:
    def __init__(self, name):
        self.name = name
        
        self.created_at = datetime.now()
        self.modified_at = self.created_at
        
        self.data = None
        
    def load_games(self, start_date='2000-01-01', end_date='2015-12-31', cols=None):
        """
        Load all games between supplied dates.
        start_date (str or date): (Default 2000-01-01) 
        end_date (str or date): (Default 2015-12-31) 
        cols (list): (Default None) By default include all columns. Otherwise, supply a list
        of columns and those will be included. 
        """
        games_df = pd.read_csv(Files.games)
        if cols is not None:
            cols = ['date'] + cols
            cols = list(set(cols))
        else:
            cols = games_df.columns
        games_df = games_df[cols]
        games_df['date'] = pd.to_datetime(games_df['date'])
        games_df = games_df[games_df['date'].between(start_date, end_date)]
        games_df['Y'] = games_df['Y'].astype(int)
        self.data = optimize(games_df)
        self.modified_at = datetime.now()
        return self.data

    def add_team_X_stats(self, team_data, year_offset, cols=[], agg=None):
        """
        Load team stats for pitching or general stats, and join it to the game data. Note that you can run this more
        than once to join several years of  data. This function requires the team data to have the following columns
        (at a minimum): 'Team', 'Year'
        team_data (Files attr): The file attribute from the Files class.
        year_offset (int): (Default -1) If None, join data for the same year as the
            game occurred in. So a year_offset of -1 means games in 2015 would join on
            data from 2014 (one year earlier).
        cols (list): (Default []) Columns from team data to include. By default no
            data is included.
        agg (str): (Default None) If year_offset > 1, then optionally you can aggregate
            all the years between game - year_offset and game - 1 (e.g. by averaging them). If you
            wish to do so, supply agg as one of ['mean', 'min', 'max']. Note that if
            year_offset > 1 and agg == None, then only that single year will be returned (i.e.
            no aggregation is performed).
        """
        assert self.data is not None, 'First run Dataset.load_games() to load some games into memory'
        assert year_offset > 0, 'year_offset must be positive'
        if isinstance(cols, str):
            cols = [cols]
        if isinstance(team_data, str):
            team_data = getattr(Files, team_data)

        right_df = pd.read_csv(team_data)

        def merge_right(home_or_away):
            home_or_away = home_or_away.lower()
            assert home_or_away in ['home', 'away'], "home_or_away must be one of ['home', 'away']"

            # Append desired stats columns
            pre_merge_rows = self.data.shape[0]
            
            # If aggregating, get multiple years and apply the aggregation function. Otherwise, get just a single year.
            if agg is None:
                right_df['year_offset'] = right_df['Year'] + year_offset
                self.data = self.data.merge(right_df[['Team', 'Year', 'year_offset'] + cols], left_on=[f'{home_or_away}_team', 'Y'], right_on=['Team', 'year_offset'], how='left')
                assert self.data.shape[0] == pre_merge_rows, f'pre-merge rows = {pre_merge_rows}, post-merge rows = {self.data.shape[0]}'
            else:
                agg_fn = getattr(AggFcns, f'{agg}_fn')
                self.data = self.data[self.data['Year'].between(self.data['Y'] - year_offset, self.data['Y'] - 1)]
                num_cols = list(self.data.select_dtypes('number').columns)
                print(self.data.columns)
                print(num_cols)
                num_map = {c: agg_fn for c in num_cols}
                obj_map = {'home_pitcher': 'first', 'away_pitcher': 'first'}
                agg_map = dict(num_map, **obj_map)
                self.data = self.data.groupby(['date', 'home_team', 'away_team']).agg(agg_map)
                self.data = self.data.reset_index()

            # Get rid of columns that were only used for merging
            cols_to_drop = set(['Team', 'Year', 'year_offset']).intersection(set(self.data.columns))
            cols_to_drop = list(cols_to_drop)
            self.data = self.data.drop(cols_to_drop, axis='columns')
            all_cols = list(self.data.columns)
            if agg is None:
                all_cols[-len(cols):] = [f'{home_or_away}_{c}_offset{year_offset}year' for c in all_cols[-len(cols):]]
            else:
                all_cols[-len(cols):] = [f'{home_or_away}_{c}_offset{year_offset}year_{agg}' for c in all_cols[-len(cols):]]
            self.data.columns = all_cols
            self.data = optimize(self.data)

        merge_right('home')
        merge_right('away')

        return self.data

    def add_team_pitching_stats(self, year_offset=1, cols=[], agg=None):
        if agg is not None:
            raise NotImplementedError
        self.add_team_X_stats(Files.team_pitching, year_offset, cols, agg)
        return self.data

    def add_team_stats(self, year_offset=1, cols=[], agg=None):
        self.add_team_X_stats(Files.teams, year_offset, cols, agg)
        return self.data
    
    def add_pitcher_stats(self, game_offset=1, cols=[]):
        """
        Load pitcher statistics (IP, ERA, etc.). Note that you can run this more
        than once to join several games worth of data.
        game_offset (int): (Default 1) If None, join pitcher data for the same game as the
            game occurred in. So a game_offset of 1 means games on 2015-01-30 would join on the
            the first game occurring before this (one game backward).
        cols (list): (Default []) Columns from pitcher data to include. By default no
            data is included.
        """
        assert self.data is not None, 'First run Dataset.load_games() to load some games into memory'
        assert game_offset > 0, 'game_offset must be positive'
        if isinstance(cols, str):
            cols = [cols]

        def merge_right(home_or_away):
            home_or_away = home_or_away.lower()
            assert home_or_away in ['home', 'away'], "home_or_away must be one of ['home', 'away']"

            pitchers_df = pd.read_csv(Files.pitchers_games)
            pitchers_df = optimize(pitchers_df)
            pitchers_df['Date'] = pd.to_datetime(pitchers_df['Date'])
            pitchers_df['Year'] = pitchers_df['Date'].dt.year
            pitchers_df = pitchers_df[['name', 'Date', 'Year'] + cols]

            pitchers_df['season_game'] = pitchers_df.groupby(['name', 'Year'])['Date'].rank('min')
            pitchers_df[f'season_game_offset{game_offset}'] = pitchers_df['season_game'] + game_offset
            self.data[f'{home_or_away}_pitcher_season_game'] = self.data.groupby([f'{home_or_away}_pitcher', 'Y'])['date'].rank('min')

            self.data = self.data.merge(pitchers_df,
                                        left_on=[f'{home_or_away}_pitcher', 'Y', f'{home_or_away}_pitcher_season_game'],
                                        right_on=['name', 'Year', f'season_game_offset{game_offset}'],
                                        how='left')

            cols_to_drop = ['name', 'Year', 'Date', f'season_game_offset{game_offset}',
                            f'{home_or_away}_pitcher_season_game', 'season_game']
            self.data = self.data.drop(cols_to_drop, axis='columns')
            all_cols = list(self.data.columns)
            all_cols[-len(cols):] = [f'pitcher_{home_or_away}_{c}_offset{np.abs(game_offset)}game' for c in all_cols[-len(cols):]]
            self.data.columns = all_cols
            self.data = optimize(self.data)

        merge_right('home')
        merge_right('away')

        return self.data
    
    def save(self):
        self.data.to_csv(f'../data/saved_datasets/{self.name}.csv', index=False)

    def load(self):
        self.data = pd.read_csv(f'../data/saved_datasets/{self.name}.csv')
        self.data = optimize(self.data)