import numpy as np
import pandas as pd


def downcast(df, show_reduction=False):
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
        reduced_mem_usage_pct = 100 * (1 - reduced_mem_usage / original_mem_usage)
        print(f'{original_mem_usage:.2f}MB -> {reduced_mem_usage:.2f}MB ({reduced_mem_usage_pct:.2f}% reduction)')
    return df


def to_datetime(df):
    cols = list(df.columns)
    date_cols = [c for c in cols if 'date' in c.lower()]
    for c in date_cols:
        try:
            df[c] = pd.to_datetime(df[c])
        except ValueError:
            pass
    return df


def to_numeric(df):
    cols = list(df.columns)
    date_cols = [c for c in cols if 'date' in c.lower()]
    cols = list(set(cols) - set(date_cols))
    for c in cols:
        try:
            df[c] = pd.to_numeric(df[c])
        except ValueError:
            pass
    return df


def optimize(df):
    df = to_datetime(df)
    df = to_numeric(df)
    df = downcast(df)
    return df


def uniform_name(x):
    raise_errors = False
    try:
        x = x.strip().lower()
    except Exception as e:
        print(f'{x} is invalid')
        return x
        if raise_errors:
            raise
        
    team_list = ['TOR', 'SFN', 'SEA', 'NYA', 'LAN', 'BAL', 'COL', 'CHN', 'MIA',
       'CLE', 'CIN', 'TEX', 'TBA', 'DET', 'ATL', 'HOU', 'MIL', 'WAS',
       'PHI', 'OAK', 'ARI', 'CHA', 'BOS', 'KCA', 'SLN', 'PIT', 'NYN',
       'MIN', 'SDN', 'ANA']
    
    
    
    team_dict = {'jays':'TOR','bluejays':'TOR', 'torontobluejays':'TOR', 'tor':'TOR', 
                 'giants':'SFN', 'sfg': 'SFN', 'sanfranciscogiants':'SFN', 'sf':'SFN', 'sfn':'SFN', 
                 'mariners':'SEA', 'seattlemariners':'SEA', 'sea':'SEA', 
                 'yankees':'NYA', 'nyy': 'NYA', 'newyorkyankees':'NYA', 'nya':'NYA', 
                 'dodgers':'LAN', 'lad':'LAN', 'losangelesdodgers':'LAN', 'la':'LAN', 'lan':'LAN', 
                 'orioles':'BAL', 'baltimoreorioles':'BAL', 'bal':'BAL', 
                 'rockies':'COL', 'coloradorockies':'COL', 'col':'COL', 
                 'cubs':'CHN', 'chc':'CHN', 'chicagocubs':'CHN', 'chn':'CHN', 
                 'marlins':'MIA', 'fla':'MIA', 'floridamarlins':'MIA', 'miamimarlins':'MIA', 'mia':'MIA', 
                 'indians':'CLE', 'clevelandindians':'CLE', 'cle':'CLE', 
                 'reds':'CIN', 'cincinnatireds':'CIN', 'cin':'CIN', 
                 'rangers':'TEX', 'texasrangers':'TEX', 'tex':'TEX', 
                 'rays':'TBA', 'devilrays':'TBA', 'tbd':'TBA', 'tampabayrays':'TBA', 'tampabaydevilrays':'TBA', 'tba':'TBA', 'tbr': 'TBA',
                 'tigers':'DET', 'detriottigers':'DET', 'det':'DET', 
                 'braves':'ATL', 'atlantabraves':'ATL', 'atl':'ATL', 
                 'astros':'HOU', 'houstonastros':'HOU', 'hou':'HOU', 
                 'brewers':'MIL', 'milwaukeebrewers':'MIL', 'mil':'MIL', 
                 'nationals':'WAS', 'wsh':' WAS', 'wsn':'WAS', 'washingtonnationals':'WAS', 'montrealexpos':'WAS', 'expos':'WAS', 'mtl':'WAS','was':'WAS', 'mon': 'WAS',
                 'phillies':'PHI', 'philadelphiaphillies':'PHI', 'phi':'PHI', 
                 'as':'OAK', 'athletics':'OAK', 'oaklandathletics':'OAK', 'oaklandas':'OAK', 'oaklanda':'OAK', 'oak':'OAK', 
                 'diamondbacks':'ARI', 'arizonadiamondbacks':'ARI', 'ari':'ARI', 
                 'whitesox':'CHA', 'cws':'CHA', 'chicagowhitesox':'CHA', 'cha':'CHA', 'chw': 'CHA', 'chw': 'CHA',
                 'redsox':'BOS', 'bostonredsox':'BOS', 'bos':'BOS', 
                 'royals':'KCA', 'kcr':'KCA', 'kansascityroyals':'KCA', 'kc':'KCA', 'kca':'KCA', 
                 'cardinals':'SLN', 'slc':'SLN', 'stl':'SLN', 'saintlouiscardinals':'SLN', 'stlouiscardinals':'SLN', 'sln':'SLN', 
                 'pirates':'PIT', 'pittsburghpirates':'PIT', 'pit':'PIT', 
                 'mets':'NYN', 'nym':'NYN', 'newyorkmets':'NYN', 'nyn':'NYN', 
                 'twins':'MIN', 'minnesotatwins':'MIN', 'min':'MIN', 
                 'padres':'SDN', 'sdp':'SDN', 'sandiegopadres':'SDN', 'sd':'SDN', 'sdn':'SDN', 
                 'angels':'ANA', 'laa':'ANA', 'losangelesangels':'ANA', 'losangelesangelsofanaheim':'ANA', 'ana':'ANA', 
                '---': 'UNK'}
    if x not in team_dict:
        if raise_errors:
            assert x in team_dict, f'{x} is not a valid team name'
        else:
            print(f'{x} is not a valid team name')
    return team_dict.get(x, x)