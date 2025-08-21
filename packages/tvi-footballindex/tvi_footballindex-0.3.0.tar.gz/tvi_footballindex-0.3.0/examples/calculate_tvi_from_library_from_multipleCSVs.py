import glob
import os
import pandas as pd
from tvi_footballindex.parsing import f24_parser
from tvi_footballindex.tvi import calculator

# read output files and concatenate
input_dir = "examples/data/F24 - CSVs/"

# read all csv files in the output directory
files = glob.glob(os.path.join(input_dir, "*"))
input_dfs = []
for file in files:
    df = pd.read_csv(file)
    input_dfs.append(df)
# concatenate all dataframes
input_df = pd.concat(input_dfs, ignore_index=True)

# 1. Parse F24 data
print("Parsing F24 data...")
event_df = f24_parser.parsef24_csv(input_df)

# 2. Calculate player playtime
print("Calculating player playtime...")
play_time = f24_parser.calculate_player_playtime(event_df, min_playtime=30, from_processed=True)

# Defensive Actions
interceptions = f24_parser.get_interceptions(event_df, from_processed=True)
tackles = f24_parser.get_tackles(event_df, from_processed=True)
aerials = f24_parser.get_aerials(event_df, from_processed=True)

# Possession Actions
progressive_passes = f24_parser.get_progressive_passes(event_df, from_processed=True)
dribbles = f24_parser.get_dribbles(event_df, from_processed=True)

# Offensive Actions
key_passes = f24_parser.get_key_passes(event_df, from_processed=True)
#deep_completions = f24_parser.get_deep_completions(event_df, from_processed=True)
shots_on_target = f24_parser.get_shots_on_target(event_df, from_processed=True)

# Combine all actions into a single DataFrame
all_metric_events = pd.concat([
    interceptions, tackles, aerials, progressive_passes, dribbles, key_passes, shots_on_target#, deep_completions
])
all_metric_events['player_id'] = all_metric_events['player_id'].astype(int).astype(str)

# Calculate TVI
tvi_df, q95_values = calculator.calculate_tvi(
    events_df=all_metric_events, 
    playtime_df=play_time,
    C = 90/38
)
print("TVI calculation completed.")
print(f"Q95 values (used to weight, lower -> mor weight): {q95_values}")

# Aggregate TVI by player
aggregated_tvi = calculator.aggregate_tvi_by_player(tvi_df)

# 5. Add player names and filter
print("Adding player names and filtering...")
player_names = (
    event_df[["player_id", "player", "team_id", "team"]].drop_duplicates().dropna()
)
player_names.rename(
    columns={"player": "player_name", "team": "team_name"}, inplace=True
)
aggregated_tvi['player_id'] = aggregated_tvi['player_id'].astype(int)
tvi_final = pd.merge(player_names, aggregated_tvi, on='player_id', how='right')

# write the final DataFrame to a CSV file
tvi_final.sort_values('TVI', ascending=False).to_csv(f"./examples/data/output/withoutDeepCompletion_withWeights/All_Leagues_24-25_TVI.csv", index=False)

# Filter out goalkeepers and players with low playtime
tvi_final = tvi_final[tvi_final['position'] != 'Goalkeeper']
tvi_final_filtered = tvi_final[tvi_final['play_time'] > 450].sort_values('TVI', ascending=False).reset_index(drop=True)

# 6. Display results
print("\n--- Top 20 Players by TVI ---")
print(tvi_final_filtered.head(20))
