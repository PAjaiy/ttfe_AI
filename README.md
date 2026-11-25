\# ttfe\_AI

Contains both a re-playable version of 2048, and an AI that can play 2048, again and again, with adjustable AI modes.



This project is still in progress, with possible inclusion of some more AI modes, or an improvement in GUI in later updates.



\## Features



\- 2048 game mechanics and GUI, built with pygame

\- three AI modes: random, raw heuristics, and expectimax-based

\- final results for every batch of games played by the AI, along with a visual of the best game played



\## Implementation / Usage



\- run graphics.py as the main program to play 2048; press R to reset a game and the arrow keys to make moves

\- game.py contains all the necessary game-initiating classes

\- ai.py contains all the necessary AI classes, each containing a function choose\_action()

\- run main.py as the main program to make the AI play a batch of 2048 games; make sure to toggle the comments to choose

an AI mode, and to edit iteration\_count to change the batch size



\## Requirements



\- Python 3

\- Pygame-CE



Install the dependency with:



```bash

pip install pygame-ce

```



\## Running



Clone the repository:



```bash

git clone <repository-url>

cd <repository-folder>

```



Run the project:



```bash

python main.py

```

