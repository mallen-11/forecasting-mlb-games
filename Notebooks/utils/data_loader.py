import pandas as pd
import numpy as np
import os
from datetime import datetime

from pathlib import Path


base_dir = Path('../data')

class Files:
    # Game-by-game covariate data, coming from the paper
    games = base_dir / Path('mlb_games_df.csv')
    # Pitchers summary data, (primarily reference keys, not much in the way of stats)
    pitchers = base_dir / Path('pitchers_summary.csv')
    # Team-level pitching stats year-by-year
    team_pitching = base_dir / Path('team_pitching_stats.csv')
    # Team-level general data (attendance, W-L, etc)
    teams = base_dir / Path('team_stats.csv')
    # Game-level pitcher stats
    pitchers_games = base_dir / Path('pitchers_games.csv')
    
class Dataset:
    def __init__(self, name):
        self.name = name
        
        self.created_at = datetime.now()
        self.modified_at = self.created_at
        
        self.data = None
        
    def load_games(self, start_date='2000-01-01', end_date='2015-12-31', cols=None):
        '''
        Load all games between supplied dates.
        start_date (str or date): (Default 2000-01-01) 
        end_date (str or date): (Default 2015-12-31) 
        cols (list): (Default None) By default include all columns. Otherwise, supply a list
        of columns and those will be included. 
        '''
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
        self.data = games_df
        self.data = self._downcast(self.data)
        self.modified_at = datetime.now()
        return self.data
        
    def add_team_pitching_stats(self, year_offset=-1, cols=[]):
        '''
        Load team pitching data and join it to the game data. Note that you can run this more
        than once to join several years of pitching data.
        year_offset (int): (Default -1) If None, join pitching data for the same year as the
            game occurred in. So a year_offset of -1 means games in 2015 would join in pitching
            data from 2014 (one year earlier).
        cols (list): (Default []) Columns from team pitching data to include. By default no
            data is included.
        '''
        assert self.data is not None, 'First run Dataset.load_games() to load some games into memory'
        if isinstance(cols, str):
            cols = [cols]
        
        pitching_df = pd.read_csv(Files.team_pitching)
        
        # Append columns for the home team
        self.data = self.data.merge(pitching_df[['Team', 'Year'] + cols], left_on='home_team', right_on='Team')
        self.data = self.data[self.data['Y'] + year_offset == self.data['Year']]
        self.data = self.data.drop(['Team', 'Year'], axis='columns')
        all_cols = list(self.data.columns)
        all_cols[-len(cols):] = [f'team_home_{c}_offset{np.abs(year_offset)}year' for c in all_cols[-len(cols):]]
        self.data.columns = all_cols
        self.data = self._downcast(self.data)
        
        # Repeat for away team
        self.data = self.data.merge(pitching_df[['Team', 'Year'] + cols], left_on='away_team', right_on='Team')
        self.data = self.data[self.data['Y'] + year_offset == self.data['Year']]
        self.data = self.data.drop(['Team', 'Year'], axis='columns')
        all_cols = list(self.data.columns)
        all_cols[-len(cols):] = [f'team_away_{c}_offset{np.abs(year_offset)}year' for c in all_cols[-len(cols):]]
        self.data.columns = all_cols
        self.data = self._downcast(self.data)
        self.modified_at = datetime.now()
        return self.data
    
    def add_team_stats(self, year_offset=1, cols=[]):
        '''
        Load team statistics (attendance, W-L%, etc.). Note that you can run this more
        than once to join several years of data.
        year_offset (int): (Default 1) If None, join team data for the same year as the
            game occurred in. So a year_offset of 1 means games in 2015 would join in team
            data from 2014 (one year earlier).
        cols (list): (Default []) Columns from team data to include. By default no
            data is included.
        '''
        assert self.data is not None, 'First run Dataset.load_games() to load some games into memory'
        if isinstance(cols, str):
            cols = [cols]
            
        teams_df = pd.read_csv(Files.teams)
        
        # Append columns for the home team
        self.data = self.data.merge(teams_df[['Team', 'Year'] + cols], left_on='home_team', right_on='Team')
        self.data = self.data[self.data['Y'] - year_offset == self.data['Year']]
        self.data = self.data.drop(['Team', 'Year'], axis='columns')
        all_cols = list(self.data.columns)
        all_cols[-len(cols):] = [f'home_{c}_offset{np.abs(year_offset)}year' for c in all_cols[-len(cols):]]
        self.data.columns = all_cols
        self.data = self._downcast(self.data)
        
        # Repeat for away team
        self.data = self.data.merge(teams_df[['Team', 'Year'] + cols], left_on='away_team', right_on='Team')
        self.data = self.data[self.data['Y'] - year_offset == self.data['Year']]
        self.data = self.data.drop(['Team', 'Year'], axis='columns')
        all_cols = list(self.data.columns)
        all_cols[-len(cols):] = [f'away_{c}_offset{np.abs(year_offset)}year' for c in all_cols[-len(cols):]]
        self.data.columns = all_cols
        self.data = self._downcast(self.data)
        self.modified_at = datetime.now()
        return self.data
    
    def add_pitcher_stats(self, game_offset=1, cols=[]):
        '''
        Load pitcher statistics (IP, ERA, etc.). Note that you can run this more
        than once to join several games worth of data.
        game_offset (int): (Default 1) If None, join pitcher data for the same game as the
            game occurred in. So a game_offset of 1 means games on 2015-01-30 would join on the
            the first game occurring before this (one game backward).
        cols (list): (Default []) Columns from pitcher data to include. By default no
            data is included.
        '''
        assert self.data is not None, 'First run Dataset.load_games() to load some games into memory'
        if isinstance(cols, str):
            cols = [cols]
            
        # Home team
        pitchers_df = pd.read_csv(Files.pitchers_games)
        pitchers_df = self._downcast(pitchers_df)
        pitchers_df['Date'] = pd.to_datetime(pitchers_df['Date'])
        pitchers_df['Year'] = pitchers_df['Date'].dt.year
        pitchers_df = pitchers_df[['name', 'Date', 'Year'] + cols]
        self.data = self.data.merge(pitchers_df, left_on=['home_pitcher', 'Y'], right_on=['name', 'Year'], how='left')
        # Do <= in case it's the pitchers first ever start. If you do < then that row of data
        # will just be thrown away (not good!)
        self.data = self.data[self.data['Date'] <= self.data['date']]
        
        processed_df = None
        for _, game_df in self.data.groupby(['home_pitcher', 'date']):
            # Check if this is the pitchers first start, i.e. only "previous" game is the
            # one they're currently playing. If so, null-out the stats.
            if game_df.shape[0] == 1:
                game_df[cols] = None
            game_df = game_df.sort_values('Date', ascending=False)
            game_df = game_df.iloc[[game_offset-1]]
            if processed_df is None:
                processed_df = game_df
            else:
                processed_df = pd.concat([processed_df, game_df])
        
        processed_df = processed_df.drop(['name', 'Year', 'Date'], axis='columns')
        self.data = processed_df
        all_cols = list(self.data.columns)
        all_cols[-len(cols):] = [f'pitcher_home_{c}_offset{np.abs(game_offset)}game' for c in all_cols[-len(cols):]]
        self.data.columns = all_cols
        self.data = self._downcast(self.data)
        
        # Away team
        pitchers_df = pd.read_csv(Files.pitchers_games)
        pitchers_df = self._downcast(pitchers_df)
        pitchers_df['Date'] = pd.to_datetime(pitchers_df['Date'])
        pitchers_df['Year'] = pitchers_df['Date'].dt.year
        pitchers_df = pitchers_df[['name', 'Date', 'Year'] + cols]
        self.data = self.data.merge(pitchers_df, left_on=['away_pitcher', 'Y'], right_on=['name', 'Year'], how='left')
        # Do <= in case it's the pitchers first ever start. If you do < then that row of data
        # will just be thrown away (not good!)
        self.data = self.data[self.data['Date'] <= self.data['date']]
        
        processed_df = None
        for _, game_df in self.data.groupby(['away_pitcher', 'date']):
            # Check if this is the pitchers first start, i.e. only "previous" game is the
            # one they're currently playing. If so, null-out the stats.
            if game_df.shape[0] == 1:
                game_df[cols] = None
            game_df = game_df.sort_values('Date', ascending=False)
            game_df = game_df.iloc[[game_offset-1]]
            if processed_df is None:
                processed_df = game_df
            else:
                processed_df = pd.concat([processed_df, game_df])
        
        processed_df = processed_df.drop(['name', 'Year', 'Date'], axis='columns')
        self.data = processed_df
        all_cols = list(self.data.columns)
        all_cols[-len(cols):] = [f'pitcher_away_{c}_offset{np.abs(game_offset)}game' for c in all_cols[-len(cols):]]
        self.data.columns = all_cols
        self.data = self._downcast(self.data)
        self.modified_at = datetime.now()
        return self.data
    
    def _downcast(self, df, show_reduction=False):
        original_mem_usage = sum(df.memory_usage() / 10**6)
        for c in df.select_dtypes(int).columns:
            # Positive integers
            if df[c].min() > 0:
                if df[c].max() < 255:
                    df[c] = df[c].astype(np.uint8)
                elif df[c].max() < 65535:
                    df[c] = df[c].astype(np.uint16)
                elif df[c].max() < 4294967295:
                    df[c] = df[c].astype(np.uint32)
                else:
                    df[c] = df[c].astype(np.uint64)
            # Negative integers
            else:
                if df[c].max() < 127 and df[c].min() > -127:
                    df[c] = df[c].astype(np.int8)
                elif df[c].max() < 32767 and df[c].min() > -32767:
                    df[c] = df[c].astype(np.int16)
                elif df[c].max() < 2147483648 and df[c].min() > -2147483648:
                    df[c] = df[c].astype(np.int32)
                else:
                    df[c] = df[c].astype(np.int64)

            # Downcast all floats to 32 bits (unlikely to need more precision than that)
            for c in df.select_dtypes(float).columns:
                df[c] = df[c].astype(np.float32)

        if show_reduction:
            reduced_mem_usage = sum(df.memory_usage() / 10**6)
            print(f'{original_mem_usage:.2f}MB -> {reduced_mem_usage:.2f}MB ({100*(1-reduced_mem_usage/original_mem_usage):.2f}% reduction)')
        return df
    
    def save(self):
        self.data.to_csv(f'../data/saved_datasets/{self.name}.csv', index=False)
    

    def load(self):
        self.data = pd.read_csv(f'../data/saved_datasets/{self.name}.csv')