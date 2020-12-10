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
