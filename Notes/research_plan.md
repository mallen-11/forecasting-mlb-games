# Research Plan

To-Do as of Dec. 10th 2020

- Work on gathering data used in https://github.com/andrew-cui/mlb-game-prediction as well as try out the models used in that repo to make sure that they are valid.
- Need to add some more features to data
  - Using pitcher data from last year as well as the previous starts in the current season if possible
  - Get (ERA, WHIP from pitchers last 1-3 starts)
  - Avg. Home Attendance from the previous year
  - Team Ranking from previous year (could be from their W-L record or statcast has a rank column)
  - Bring in the data from the month the game was played (This should already be in there and we just need to not remove it)
  - Need to bring a feature in to measure errors (either team fielding percentage or errors/9 would work)

## Paul updates
- _Dec 10, 2020_ - Today I mainly worked on getting together pitcher data to make future analysis/wrangling easier. My work can be found in `Notebooks/New features.ipynb`. The highlights are:
    - Summaries of all pitchers, including names, seasons played, teams played for, and all their foreign keys for baseball reference, statscast, etc. (fetching all foreign keys in still in progress).
    - Game-level stats for pitchers. I modified code from `pybaseball` to scrape baseball reference (BR) for pitcher data. Note that this _does not_ include WHIP, but _does_ include ERA. So we'll either need to calculate WHIP by hand (it's not obvious to me that the columns included make it simple to do so), or use an alternative measure.
    - While I didn't specifically set aside home attendance, this is included in the game-level data, so it will be easy to get.
    - Same note for "team ranking from previous year"
As far as the pitcher game-level data goes, my plan is to save a CSV file for each pitcher which includes stats for every game. So it will have rows corresponding to games played, and columns for each metric we're interested in. Then I'll write some helper functions to easily load these. Hopefully that will avoid us needing to load one giant file of all games for all pitchers.