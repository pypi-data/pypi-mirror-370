# airena Python Game Client

This package provides the core client library for building games that run in the airena ecosystem.

## Overview

The airena Python Game Client enables developers to create games that interact with the airena platform. It handles communication, game state management, and integration with airena's infrastructure.

## Features
- Easy integration with airena game servers
- Utilities for game state and environment management
- Typed Python interfaces for robust development

## Getting Started

1. **Install the package**
	```bash
	pip install airena-python-game-client
	```

2. **Develop Locally**
	When developing games locally, use the [`airena-mock-server`](https://github.com/airena-dev/airena-mock-server) to simulate the airena communication layer.
    ```bash
    docker run -p 8196:8196 ghcr.io/airena-dev/airena-mock-server:latest
    ```
	Configure your game client to connect to the mock server for local testing by setting the following environment variables:
	```bash
	export airena_CGI_URL="http://localhost:8196"
	export airena_GAME_ID="00000000-0000-0000-0000-000000000000"
	export airena_GAME_SECRET="00000000-0000-0000-0000-000000000000"
    export PLAYER_COUNT=2
	```
	These values will allow your client to communicate with the mock server.

3. **Basic Usage**
	```python
	from airena_game_client import AirenaGameClient

	client = AirenaGameClient()
	client.start_game(
        player_public_states={
            0: {"foo": "bar"},
            1: {"bar": "foo"},
        },
        players_accepting_moves=[1]
    )
    while client.wait_for_changes():
        # Do move validation and reject moves if needed.
        if invalid_move:
            client.reject_moves({1: 'Invalid Move'})
            continue

        if game_over: # You decide if the game is over.
            client.end_game(winners=[1])
            break
        # Update Game State
        client.update_game(
                player_public_states={
                0: {"foo": "bar"},
                1: {"bar": "foo"},
            },
            players_accepting_moves=[1]
        )
    
	```


## License
MIT

## Resources
- [airena.dev](https://airena.dev)
- [airena Ecosystem Documentation](https://github.com/airena-dev)
- [airena-mock-server](https://github.com/airena-dev/airena-mock-server)
- [airena-python-player-client](https://github.com/airena-dev/airena-python-player-client)
