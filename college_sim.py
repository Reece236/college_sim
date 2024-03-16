import random
import numpy as np
import joblib
import datetime
import pandas as pd

class GameSimulator:
    def __init__(self, transition_probs, dist_bt, lineup, lg_dist, stat_col, bunt_thresholds=None):
        self.transition_probs = transition_probs
        self.dist_bt = dist_bt
        self.game_lineup = lineup
        self.stat_col = stat_col
        self.batter = 0
        self.lg_dist = lg_dist
        self.runs = []
        self.bunt_thresholds = bunt_thresholds

    def update_matchup_stats(self):

        batter_stats = {}

        # Loop through each batter in game_lineup and append their stats to batter_stats
        for n, batterId in enumerate(self.game_lineup):
            batter_stats[n] = self.dist_bt[batterId]

        return batter_stats

    def simulate_game(self):


            ### Set up the game ##


            batter_stats = self.update_matchup_stats()

            for _ in range(9):
                current_state = '0/000'
                inning_runs = 0
                while current_state != '3/000':
                    try:
                        weights = list(batter_stats[self.batter])
                    except:
                        return batter_stats, self.batter
                    if self.bunt_thresholds != None and current_state in self.transition_probs[
                        'Bunt'].keys() and current_state in self.bunt_thresholds.keys():
                        batter_rv = batter_stats.iloc[self.batter][current_state]
                        if batter_rv < self.bunt_thresholds[current_state]:
                            result = 'Bunt'
                        else:
                            result = random.choices(self.stat_col, weights=weights)[0]
                    else:
                        result = random.choices(self.stat_col, weights=weights)[0]

                    if current_state not in self.transition_probs[result] and (
                            result == 'Triple' and result == 'Home Run'):
                        print(f'No transition from {current_state} to {result}')
                        break

                    if result == 'Triple' or result == 'Home Run':
                        if result == 'Home Run':
                            next_state = f'{current_state[0]}/000'
                        else:
                            next_state = f'{current_state[0]}/001'
                    else:
                        next_state_probs = self.transition_probs[result][current_state]
                        next_states = list(next_state_probs.keys())
                        next_state = random.choices(next_states, weights=list(next_state_probs.values()))[0]

                        # Calculate runs scored based on the difference between new and old state values
                        old_outs, old_runners = map(int, current_state.split('/'))
                        old_runner = 0
                        for runner in str(old_runners):
                            if runner != '0':
                                old_runner += 1
                        old_runners = old_runner
                        old_state_value = old_outs + old_runners + 1
                        new_outs, new_runners = map(int, next_state.split('/'))
                        new_runner = 0
                        for runner in str(new_runners):
                            if runner != '0':
                                new_runner += 1
                        new_runners = new_runner
                        new_state_value = new_outs + new_runners
                        if next_state != '3/000':
                            runs_scored = old_state_value - new_state_value
                        else:
                            runs_scored = 0
                        current_state = next_state
                        inning_runs += runs_scored
                        if self.batter >= 8:
                            self.batter = 0
                        else:
                            self.batter += 1

                        batter_stats = self.update_matchup_stats()

                self.runs.append(inning_runs)

            return sum(self.runs)

def main():
    # Only edit these 4 variables
    split = 'rhp'
    team = 'UCSB'
    n = 15000
    lineups = [['N. Oakley', 'Z. Darby', 'A. Parker', 'J. Trimble', 'R. Calvin', 'L. Mccollum', 'J. Brown', 'B. Durfee', 'J. Mendez']]

    # Load the data
    transition_probs = joblib.load( 'college_transitions.pkl')
    lg_dist = joblib.load('college_lg_avg.pkl')
    stat_col = joblib.load('college_stat_cols.pkl')
    bat_stats = pd.read_csv(f'{split}_stats.csv')
    if team != '':
        team_lineups = [[f'{player} ({team})' for player in lineup] for lineup in lineups]
    else:
        team_lineups = lineups

    bat_stats['NameTeam'] = bat_stats['Name'].astype(str) + ' (' + bat_stats['Team'] + ')'
    bat_stats = bat_stats[bat_stats['NameTeam'].isin([player for lineup in team_lineups for player in lineup])]

    tm_stats = {'BB': 'Walk', '1B': 'Single', '2B': 'Double', '3B': 'Triple', 'HR': 'Home Run',
                'ROE': 'Reached on Error', 'K': 'Strikeout', 'HBP': 'Hit By Pitch', 'FO': 'Fly Out', 'GO': 'Ground Out',
                'LO': 'Line Out', 'PO': 'Pop Out'}


    bat_stats = dict(bat_stats[['NameTeam'] + list(tm_stats.keys())].rename(columns=tm_stats).set_index('NameTeam').T)

    game_logs = []


    then = datetime.datetime.now()

    for lineup in range(len(team_lineups)):
        if (lineup % 5 == 0 and lineup != 0) or (lineup == 1):
            now = datetime.datetime.now()
            print(now - then)
            time_per_game = (now - then) / lineup
            print(f'ETA: {now + (n - lineup) * time_per_game}')

        # Create an instance of the GameSimulator
        game_simulator = GameSimulator(transition_probs, bat_stats, team_lineups[lineup], lg_dist, stat_col)

        # Simulate a game
        for i in range(n):
            game_simulator.simulate_game()

        runs = game_simulator.simulate_game()

        game_logs.append(runs / n)

    print(datetime.datetime.now() - then)
    for n in range(len(lineups)):
        print(f'{lineups[n]}: {round(game_logs[n],2)} Runs/Game')

if __name__ == '__main__':
    main()
