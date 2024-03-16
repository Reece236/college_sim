# college_sim

## Inputs
Only edit the following:

### `splits`

Options: `'rhp'` or `'lhp'`

Dictates whether to use RHP or LHP stats


### `team `

Ex. `'UCSB'`

The team's lineup being simulated. If using players from multiple teams, set `team` to ''.


### `N`

n = 10000

Number of simulations to run for each lineup. 10,000 is recomended.


### `lineups `

Ex. `[['N. Oakley', 'Z. Darby', 'A. Parker', 'J. Trimble', 'R. Calvin', 'L. Mccollum', 'J. Brown', 'B. Durfee', 'J. Mendez'], ['Z. Darby', 'N. Oakley', 'A. Parker', 'J. Trimble', 'R. Calvin', 'L. Mccollum', 'J. Brown', 'B. Durfee', 'J. Mendez']]`

Batting lineups stored in a list of lists. Use first letter of name and last name format `'N. Oakley'`. If using multiple teams, add team after name `'N. Oakley (UCSB)'`
