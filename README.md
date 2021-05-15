# Deep Q-learning Poker

Limit Texas hold'em Poker tournament.  
Written in the programming language Python 3.7.10.  
Main libraries for machine learning: PyTorch 1.3.1, Tensorboard 2.4.0

## Environment

Two files are prepared to create the python environment for this project. With the `environment.yaml` file it is
possible to create a `conda` environment. The other file is `requirements.txt` which should be fed to the `pip` command,
so it is also possible to create the environment with `virtualenv`. If either file fails to create the environment, it
should be possible to recreate it just by installing PyTorch 1.3.1 and Tensorboard 2.4.0 with all their dependencies.

## Game implementation

Main class for the game is `Table`. Global variables `INIT_CHIPS`, `SMALL_BET`, `BIG_BET` are used to easily change the
game's behaviour. `INIT_CHIPS` defines the amount of chips every player gets at the beginning of the game. `SMALL_BET`
& `BIG_BET` define the bet sizes, where `SMALL_BET` is used in the pre-flop and flop phase, and `BIG_BET` in the river
and turn phase.

The `Table` takes a list of player classes as an argument to the constructor. All players are internally initialized.
All players must be derived from the base `Player` class and implement the abstract function `make_move`.

To keep track of what is happening in the game, two observers are implemented, one that prints all information in the
terminal (`TerminalTextualObserver`), and the other (`FileTextualObserver`) writes them to textual files. Location of
those files is in the `log` directory.

A basic demonstration can be run with the `demo.py` file. It is possible to play the terminal version of the game with
the `play.py` file. A GUI has not been implemented.

## Opponent bots

Opponent bots are based on the paper Opponent Modeling in Poker by Darse Billings, Denis Papp, Jonathan Schaeffer, Duane
Szafron. In the pre-flop phase decisions are based on the Sklansky & Malmuth starting hands table. At the rest of the
phases current hand strength is calculated (the potential future hand strength takes too much computational time).
The `OpponentBot` class uses 3 thresholds (numbers between 0 and 100). Those 3 thresholds are compared against the hand
strength. `fold_thresh` value is used to determine if the agent should fold the current round, that is if the hand
strength value is greater or equal than this threshold, the agent won't fold. If raising is possible, the agent raises
if the hand strength is greater or equal the value of `raise_thresh`. An additional threshold `bluff_thresh` was added
to simulate bluffing. Every round a random number between 1 and 100 is assigned to `feeling_lucky` variable and if it is
greater or equal to the `bluff_thresh`, the agent calls or raises the current round instead of folding. With a grid
search algorithm the best thresholds are given to `OpponentBotGold` and the second best to `OpponentBotSilver`.

## Deep Q-Network Agents

A Q-learning approach was used for training a neural network to play the game. The `SimpleDqnBot` class operates on a
basic neural network with 2 hidden layers and uses q-learning methodologies to update its parameters. Learning and
monitoring the progress with tensorboard is possible with the `MonitoredSimpleDqnBot` class. The progress is saved in
the `runs` directory.

Additional classes:

- `SimpleDqnBot3l` uses 3 hidden layers instead of 2
- `CollectiveSimpleDqnBot` uses a shared neural network, which means that multiple agents train the same network.

## Training

Training can be accomplished executing the `train.py` file. It contains a lot of global variables that are meant to
change the training behaviour. The whole tournament is considered as one episode.

Training variables:

- DQN hyperparameters
    - `ALPHA`: Learning rate for the network
    - `GAMMA`: Future reward discount
    - `EPSILON`: Exploration rate
    - `SHOULD_EPSILON_DECAY`: Should exploration rate decay during training
    - `EPSILON_FLOOR`: Minimum exploration rate beyond it won't decay
    - `SHOULD_SAVE_MODEL`: If the network parameters should be saved after training (in the `models` directory)
    - `LOAD_MODEL_PATH`: Optional path of a pretrained model to load before training

- Training & validation duration
    - `TRAINING_EPISODES_AMOUNT`: Amount of episodes used in training
    - `VALIDATION_EPISODES_AMOUNT`: Amount of episodes used in validation
    - `VALIDATION_AMOUNT`: Total amount of validations during training (equally distributed)

- Monitoring
    - `MONITOR_AMOUNT`: Total amount of progress monitoring (equally distributed)
    - `SHOULD_MONITOR_TRAINING`: If the progress should be monitored during training
    - `SHOULD_MONITOR_VALIDATION`: If the progress should be monitored during validation

- Game
    - `INIT_CHIPS`: Amount of chips to be given each player at the beginning of the tournament
    - `SMALL_BET`: Bet size during pre-flop & flop phases
    - `BIG_BET`: Bet size during turn & river phases
    - `PLAYERS`: List of player classes to participate in the tournament

## Validation

To validate agents the `validate.py` file should be executed, which is meant for agents to compete against each other.
It also contains global variables to adapt validation behaviour.

Validation variables:

- `VALIDATION_EPISODES`: Amount of episodes to run
- `LOAD_MODEL_PATH`: Path of a pretrained model to load
- `INIT_CHIPS`: Amount of chips to be given each player at the beginning of the tournament
- `SMALL_BET`: Bet size during pre-flop & flop phases
- `BIG_BET`: Bet size during turn & river phases
- `PLAYERS`: List of player classes to participate in the tournament

## References

[Deeplizard, _Reinforcement learning - goal oriented
intelligence_](https://deeplizard.com/learn/playlist/PLZbbT5o_s2xoWNVdDudn51XM8lOuZ_Njv)  
[Richard S. Sutton & Andrew G. Barto, _Reinforcement learning: An
introduction_](http://www.incompleteideas.net/book/RLbook2018.pdf)  
[Darse Billings, Denis Papp, Jonathan Schaeffer, Duane Szafron, _Opponent modeling in
poker_](http://www.cs.virginia.edu/~evans/poker/wp-content/uploads/2011/02/opponent_modeling_in_poker_billings.pdf)  
[David Skalinsky & Mason Malmuth, _Starting hand
groups_](https://www.thepokerbank.com/strategy/basic/starting-hand-selection/sklansky-groups/)  
