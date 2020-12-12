# Research Plan

To-Do as of _Dec. 10th 2020_

- Work on gathering data used in https://github.com/andrew-cui/mlb-game-prediction as well as try out the models used in that repo to make sure that they are valid.
- Need to add some more features to data
  - Using pitcher data from last year as well as the previous starts in the current season if possible
  - Get (ERA, WHIP from pitchers last 1-3 starts)
  - Avg. Home Attendance from the previous year
  - Team Ranking from previous year (could be from their W-L record or statcast has a rank column)
  - Bring in the data from the month the game was played (This should already be in there and we just need to not remove it)
  - Need to bring a feature in to measure errors (either team fielding percentage or errors/9 would work)
  
  
- One note I wanted to make is in regards to our discussion today on whether it would make more sense to predict the score because we want our model to realize that the better team should beat the lesser team by a larger margin then teams that stack up more evenly. After thinking about it more today, I don't think that would be a good idea since that part of baseball is very unpredictable. A lot of times if a team gets up by a larger amount of runs, another team can kind of throw the game making the margin larger when it reality it shouldn't be. This is just one example of the unpredicatbility of baseball scores. I think a better way to approach this and possibly a feature we could include would be looking into the record of the two teams playing each other. For example, the Yankees (NYY) and the Rockies (COL) are playing eachother. Of the times they've played this year their record is 4-1 (4 wins for the NYY). This information would prove more useful, and I feel would give a better measure of who the better team actually is.


## Check List
As of _Dec 11 2020_
- To run previous Model
  - Make sure that a majority of the keys match up with what is in the dataset - Dr. Savala
  - Load previous year pitching data for each starter into mlb_games_df (Needs to be based on starting pitchers) - Dr. Savala
  - ~Find or calculate WHIP for teams per year - Dr. Savala~
  - Fix rank for team data in team stats - Dr. Savala
  - ~Look through paper and identify the hyperparameters used in model - Morgan~
    - For XGBoost (max_depth = 3, learning_rate = 0.05, n_estimators = 300)
    - For Decision Trees (criterion = entropy, max_depth = 3, max_features = None)
    - For Random Classifier (criterion = entropy, max_depth = 4, n_estimators = 60)
  - ~Need to add rest days between games for the team - Morgan~
  - Load only columns we need for model - Morgan
  - ~Sanity read through the paper again - Morgan~
    - Need to remove 30 games that started but didn't finish
    - On Page 34, do we need to normalize the differences or is that already done? (This might be where the whole scaling vs unscaling thing comes in and they say at the end that unscaling works better)
  - Put together a notebook for splitting the data into training and testing data based on year - Morgan
  
- For Our Model
  - Create a function which takes in a team name and returns the correct abbreviation. Right now I feel like I'm always guessing what abbreviation to use
  - Load in features to dataset (Pitching Data from previous starts, avg home attendance, team rank, WAR)
  - Pull in ERA, WHIP from previous starts as well as team fielding percentage 
  - We will need to redo hyperparamter searching specifically using a lot more options compared to study
  


## Paul updates
- _Dec 11, 2020_ - Mainly worked on getting foreign keys for all pitchers, as well as game-level stats. Game-level stats are processing as I write this, so tomorrow I should be able to upload those (assuming there's no issues). I also calculated WHIP on a team-level and uploaded a file with that and other stats to the data folder. 
- _Dec 10, 2020_ - Today I mainly worked on getting together pitcher data to make future analysis/wrangling easier. My work can be found in `Notebooks/pitcher_summary.ipynb`. The highlights are:
    - Summaries of all pitchers, including names, seasons played, teams played for, and all their foreign keys for baseball reference, statscast, etc. (fetching all foreign keys in still in progress).
    - Game-level stats for pitchers. I modified code from `pybaseball` to scrape baseball reference (BR) for pitcher data. Note that this _does not_ include WHIP, but _does_ include ERA. So we'll either need to calculate WHIP by hand (it's not obvious to me that the columns included make it simple to do so), or use an alternative measure.
    - While I didn't specifically set aside home attendance, this is included in the game-level data, so it will be easy to get.
    - Same note for "team ranking from previous year"
As far as the pitcher game-level data goes, my plan is to save a CSV file for each pitcher which includes stats for every game. So it will have rows corresponding to games played, and columns for each metric we're interested in. Then I'll write some helper functions to easily load these. Hopefully that will avoid us needing to load one giant file of all games for all pitchers.

## Morgan updates
- _Dec 11, 2020_ - I worked on building out the rest of the data from the previous study. Specifically, I worked on gaining access to the pitching data from the previous year (Dr. Savala will now add in aggregate pitching data for each game based on the starting pitchers). I also worked on adding in who won each game and added in the amount of rest days between each game. Dr. Savala and I updated the check list to be clear on what we need to accomplish to go onto the next steps.
- _Dec 10, 2020_ - Today I was able to remake all of the hitting stats game to game that will be needed to test the accuracy of the predicictions of the main paper we are focusing on. The mlb_games_df.csv now contains every regular season game from 2000-2019. In it there is the date, team names, pitcher names, ELO, AVG, SLG, ISO, and OBP for both home and away teams for every game. There is also difference and percent difference columns included by subtracting home minus away for each stat. Lastly, I also included splitting the date into each of its parts into their own columns. Some challenges in this data is that pitcher name for home and away is sometimes written as their identifier and sometimes written as their actual name. We might need to scrap those columns and start from scratch using the pitching data Dr. Savala made. Going forward, I will be finishing off the pitcher statistics using previous years data and then running it through some models to check and validate the accuracy shown in our papers.
