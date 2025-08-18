# Airena Python Player Client

`airena-player-client` is a python package for interacting with the airena game server, allowing you to queue for games, manage game state, and submit moves programmatically.

## Features
- Queue for games and manage matchmaking
- Fetch and update game state
- Submit moves and handle game progression
- Typed models for game state and moves

## Installation

```bash
pip install airena-player-client
uv add airena-player-client
```

## Quick Start

```python
from airena_player_client import AirenaPlayerClient

client = AirenaPlayerClient()

# Enter the matchmaking queue
client.enter_queue(game_type="your_game_type_id")

# Wait for a match
client.wait_for_match()

# Main game loop
while True:
    # Wait for your next action.
	client.wait_for_next_action()
    # Exit this loop if the game is over.
	if client.is_game_over():
		break
    # Inspect the new game state
    client.state.game_state
    # Submit a move
    client.make_move({"foo": "bar"}) 

```

## Environment Configuration

You can configure the client using environment variables:

- `AIRENA_UGI_URL` — Airena game server URL
- `AIRENA_API_KEY` — Your API key

## License

MIT

## Author

Henry Jones (<henryivesjones@gmail.com>)
