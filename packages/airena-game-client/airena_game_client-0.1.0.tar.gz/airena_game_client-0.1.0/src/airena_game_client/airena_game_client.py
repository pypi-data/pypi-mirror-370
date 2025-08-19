import json
import time
from logging import getLogger
from typing import Any, Dict, List, Literal, Optional

import httpx
from pydantic import BaseModel

from .env import AirenaClientSettings

logger = getLogger("airena-game-client")


class GameStateResponse(BaseModel):
    """
    Represents the response containing the current game state.

    Attributes:
        player_moves (dict[int, Optional[Dict[str, Any]]]):
            A mapping from player IDs to their moves for the current tick.
            The value is either a dictionary describing the move or None if no move was made.
        tick (int):
            The current tick or turn number in the game.
    """

    player_moves: dict[int, Optional[Dict[str, Any]]]
    tick: int


class AirenaGameClient:
    """
    AirenaGameClient provides an interface for interacting with the Airena Game Control Interface (GCI) server.
    This client manages game state, player moves, and communication with the server for starting, updating, and ending game sessions.
        config (AirenaClientSettings): Configuration settings for the client, including server URL, game ID, and secrets.
        client (httpx.Client): HTTP client used for server communication.
        tick (int): Current game tick.
        player_moves (Dict[int, Optional[Dict[str, Any]]]): Dictionary storing moves for each player.
    Methods:
        __init__(config: Optional[AirenaClientSettings] = None):
            Initializes the client with the provided or default configuration.
        players:
            Returns a list of player IDs for the current game.
        _raise_on_error(response: httpx.Response):
            Raises an exception if the HTTP response indicates an error.
        _update_client_state(game_state: GameStateResponse) -> bool:
            Updates internal state from a GameStateResponse. Returns True if state changed.
        start_game(player_public_states: Dict[int, Dict[str, Any]], players_accepting_moves: List[int]):
            Starts a new game session with initial player states and accepting moves.
        get_state() -> bool:
            Fetches the current game state from the server and updates internal state.
        wait_for_changes(delay: float = 0.25) -> Literal[True]:
            Polls the server until a change in game state is detected.
        reject_moves(player_move_rejections: Dict[int, str]):
            Rejects specified player moves and provides reasons for each rejection.
        update_game(player_public_states: Dict[int, Dict[str, Any]], players_accepting_moves: List[int]):
            Sends updated game state to the server, advancing the game by one tick.
        end_game(winners: List[int]):
            Ends the game session and declares the specified players as winners.
    """

    config: AirenaClientSettings
    client: httpx.Client

    tick: int

    player_moves: Dict[int, Optional[Dict[str, Any]]]

    def __init__(self, config: Optional[AirenaClientSettings] = None):
        """
        Initializes the Airena game client with the provided configuration.

        Args:
            config (Optional[AirenaClientSettings]): Optional configuration settings for the client.
                If not provided, a default AirenaClientSettings instance is used.

        Attributes:
            config (AirenaClientSettings): The configuration settings for the client.
            client (httpx.Client): The HTTP client used to communicate with the Airena server.
            tick (int): The current game tick, initialized to -1.
            player_moves (dict): Dictionary to store player moves.
        """
        if config is None:
            config = AirenaClientSettings()
        self.config = config
        self.client = httpx.Client(
            base_url=f"{self.config.cgi_url}/{self.config.game_id}",
            headers={"x-game-secret": f"{config.game_secret}"},
        )
        self.tick = -1
        self.player_moves = {}

    @property
    def players(self):
        return [player_id for player_id in range(self.config.player_count)]

    @classmethod
    def _raise_on_error(cls, response: httpx.Response):
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(response.content)
            raise e

    def _update_client_state(self, game_state: GameStateResponse) -> bool:
        """
        Updates the client's internal state based on the provided game state response.

        Compares the current tick and player moves with those in the new game state.
        If either the tick or player moves have changed, updates the internal state and returns True.
        Otherwise, returns False.

        Args:
            game_state (GameStateResponse): The latest game state received from the server.

        Returns:
            bool: True if the client state was updated with new data, False otherwise.
        """
        _return_val = self.tick != game_state.tick or json.dumps(
            self.player_moves, sort_keys=True
        ) != json.dumps(game_state.player_moves, sort_keys=True)
        self.tick = game_state.tick
        self.player_moves = game_state.player_moves
        return _return_val

    def start_game(
        self,
        player_public_states: Dict[int, Dict[str, Any]],
        players_accepting_moves: List[int],
    ):
        """
        Starts a new game session by sending the initial player states and the list of players accepting moves to the server.

        Args:
            player_public_states (Dict[int, Dict[str, Any]]):
                A dictionary mapping player IDs to their public state information.
            players_accepting_moves (List[int]):
                A list of player IDs who are currently accepting moves.
            players_accepting_moves (List[int]):
                A list of player IDs who are currently accepting moves.

        Raises:
            Exception: If the server response indicates an error.

        Returns:
            None
        """
        resp = self.client.post(
            "/start",
            json={
                "player_public_states": player_public_states,
                "players_accepting_moves": players_accepting_moves,
            },
        )
        self._raise_on_error(resp)
        self._update_client_state(GameStateResponse.model_validate(resp.json()))
        return

    def get_state(self) -> bool:
        """
        Fetches the current game state from the Game Client Interface (GCI).

        Sends a GET request to the "/state" endpoint, validates the response,
        and updates the internal client state. Returns True if there are any
        updates to the state, otherwise returns False.

        Returns:
            bool: True if the game state was updated, False otherwise.

        Raises:
            HTTPError: If the response from the GCI indicates an error.
            ValidationError: If the response data cannot be validated against the GameStateResponse model.
        """
        resp = self.client.get("/state")
        self._raise_on_error(resp)
        return self._update_client_state(GameStateResponse.model_validate(resp.json()))

    def wait_for_changes(self, delay: float = 0.25) -> Literal[True]:
        """
        Polls the GCI for game state blocking until changes are detected.

        After starting the game the main portion of the game logic should live within this loop.

        Example:
            ```python
            while client.wait_for_changes():
                # Do game logic...
                # If game is over
                client.end_game()
                break
            ```

        Args:
            delay (float, optional): Time in seconds to wait between polling attempts. Defaults to 0.25.

        Returns:
            Literal[True]: Returns True when a change in game state is detected.

        Raises:
            httpx.HTTPStatusError: If the server responds with an error status code.
        """
        while not self.get_state():
            logger.debug(f"No changes detected. Waiting {delay} before fetching again.")
            time.sleep(delay)
        return True

    def reject_moves(self, player_move_rejections: Dict[int, str]):
        """
        Rejects specified player moves and provides a reason for each rejection.

        This method sends a POST request to the server to reject the moves of the specified players,
        mutates the local game state by removing the rejected moves from this client, and sets the
        corresponding player moves to None.

        Args:
            player_move_rejections (Dict[int, str]):
                A dictionary mapping player IDs to the reason for rejecting their moves.

        Raises:
            HTTPError: If the server responds with an error status code.
        """

        response = self.client.post(
            "/reject", json={"player_move_rejections": player_move_rejections}
        )
        self._raise_on_error(response)
        for player_id in player_move_rejections:
            self.player_moves[player_id] = None

    def update_game(
        self,
        player_public_states: Dict[int, Dict[str, Any]],
        players_accepting_moves: List[int],
    ):
        """
        Sends an updated game state to the Game Control Interface (GCI), advancing the game by one tick.

        This method should be called after all required players have submitted their moves for the current tick.

        Args:
            player_public_states (Dict[int, Dict[str, Any]]): The public state for each player, keyed by player ID.
            players_accepting_moves (List[int]): List of player IDs who are eligible to submit moves in the next tick.

        Notes:
            - Each player's public state must be less than 128KB when encoded as JSON.
            - This triggers the GCI to process the next tick and update the game state.

        Returns:
            None

        Raises:
            Raises an exception if the server responds with an error.
        """
        resp = self.client.post(
            "/update",
            json={
                "player_public_states": player_public_states,
                "players_accepting_moves": players_accepting_moves,
            },
        )
        self._raise_on_error(resp)
        self._update_client_state(GameStateResponse.model_validate(resp.json()))
        return

    def end_game(self, winners: List[int]):
        """
        Ends the current game session and notifies the server of the winners.

        Args:
            winners (List[int]): A list of player IDs representing the winners.

        Returns:
            None

        Raises:
            Raises an exception if the server responds with an error.
        """

        resp = self.client.post("/end", json={"winners": winners})
        self._raise_on_error(resp)
        return
