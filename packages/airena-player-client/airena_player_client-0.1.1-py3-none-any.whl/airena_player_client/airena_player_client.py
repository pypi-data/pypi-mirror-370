import time
from datetime import datetime
from enum import Enum
from logging import getLogger
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from pydantic import BaseModel

from airena_player_client.env import AirenaClientSettings

logger = getLogger("airena-game-client")


class UserGameStatus(str, Enum):
    NEVER_QUEUED = "NEVER_QUEUED"
    LEFT_QUEUE = "LEFT_QUEUE"
    IN_QUEUE = "IN_QUEUE"
    MATCHING = "MATCHING"
    MATCHED = "MATCHED"
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


class UserGameStub(BaseModel):
    """
    Represents a stub model for a user's game session.

    Attributes:
        user_id (UUID): Unique identifier for the user.
        game_type_id (UUID): Unique identifier for the type of game.
        game_id (Optional[UUID]): Unique identifier for the specific game instance, if available.
        status (UserGameStatus): Current status of the user's game session.
        created_at (datetime): Timestamp when the game session was created.
        updated_at (Optional[datetime]): Timestamp when the game session was last updated, if available.
    """

    user_id: UUID
    game_type_id: UUID
    game_id: Optional[UUID] = None
    status: UserGameStatus
    created_at: datetime
    updated_at: Optional[datetime]


class UserGameMove(BaseModel):
    """
    Represents a move made by a user in a game.

    Attributes:
        game_id (UUID): Unique identifier for the game.
        player_id (int): Identifier for the player making the move.
        tick (int): The game tick at which the move is made.
        accepting_move (bool): Indicates whether the game is currently accepting moves from this user.
        rejection_reason (Optional[str]): Reason for rejecting the move, if applicable.
    """

    game_id: UUID
    player_id: int
    tick: int
    accepting_move: bool
    rejection_reason: Optional[str] = None


class UserGameState(BaseModel):
    """
    Represents the state of a user's game session.

    Attributes:
        game_id (UUID): Unique identifier for the game.
        player_id (int): Identifier for the player.
        game_state (Dict[str, Any]): Current state of the game, represented as a dictionary.
        tick (int): The current tick or step in the game.
        winners (Optional[List[int]]): List of player IDs who have won the game, if any.
        game_over (bool): Indicates whether the game has ended.
    """

    game_id: UUID
    player_id: int
    game_state: Dict[str, Any]
    tick: int
    winners: Optional[List[int]] = None
    game_over: bool


class GameStateResponse(BaseModel):
    """
    Represents the response containing the current game state and move information.

    Attributes:
        state (UserGameState): The current state of the user's game.
        move (Optional[UserGameMove]): The user's move, if available.
        move_received (bool): Indicates whether a move has been received.
    """

    state: UserGameState
    move: Optional[UserGameMove] = None
    move_received: bool


class InvalidGameState(Exception):
    """
    Raised when attempting to perform an action when in the incorrect game state.
    """


class AirenaPlayerClient:
    """
    AirenaPlayerClient provides a client interface for interacting with the Airena game server.
    This class manages the user's lifecycle in the matchmaking queue and game, including entering and leaving the queue,
    waiting for matches, retrieving game state, submitting moves, and handling game progression. It abstracts HTTP
    communication with the Airena backend and maintains local state for the current game session.
    Attributes:
        config (AirenaClientSettings): Configuration settings for the client, including server URL and API key.
        client (httpx.Client): HTTP client used for server communication.
        status (UserGameStatus): Current status of the user in the game lifecycle.
        tick (int): Current game tick.
        game_stub (Optional[UserGameStub]): Stub containing basic information about the current game.
        move_receieved (bool): Indicates if the last move has been received by the server.
    Methods:
        __init__(config: Optional[AirenaClientSettings] = None):
            Initializes the client with the given configuration or environment variables.
        get_queue_state():
            Retrieves the user's current state in the matchmaking queue.
        enter_queue(game_type: str):
            Enters the user into the matchmaking queue for a specified game type.
        leave_queue(lock_retries: int = 2, lock_retry_delay: float = 1.0):
            Attempts to leave the matchmaking queue, retrying if locked by the matchmaker.
        wait_for_match(delay: float = 1.0):
            Blocks until the user is matched and the game has started.
        get_game_state():
            Retrieves and updates the current game state from the server.
        wait_for_next_action(delay: float = 0.25):
            Blocks until it is the user's turn to submit a move or the game is over.
        make_move(move: Dict[str, Any]):
        is_game_over():
            Returns True if the game is over, otherwise False.
        state (property):
            Returns the current game state object.
        move (property):
            Returns the current move object.
        InvalidGameState: If an operation is attempted in an invalid game state.
        httpx.RequestError: If an HTTP request fails.
        Exception: For other errors returned by the server.
    """

    config: AirenaClientSettings
    client: httpx.Client

    status: UserGameStatus

    tick: int = -1
    game_stub: Optional[UserGameStub] = None

    _move: Optional[UserGameMove] = None
    move_receieved: bool = False
    _state: Optional[UserGameState] = None

    def __init__(self, config: Optional[AirenaClientSettings] = None):
        """
        Initializes the AirenaPlayerClient instance.

        Args:
            config (Optional[AirenaClientSettings]): Configuration settings for the client.
            If not provided, a default AirenaClientSettings instance is used, which will use
            environment variables for the URL and API key if they are set.

        Side Effects:
            - Sets up the HTTP client with the specified base URL and API key (from config or environment).
            - Retrieves the initial queue state.
        """
        if config is None:
            config = AirenaClientSettings()
        self.config = config
        self.client = httpx.Client(
            base_url=f"{self.config.ugi_url}/game",
            headers={"x-api-key": self.config.api_key},
        )
        self.get_queue_state()

    @classmethod
    def _raise_on_error(cls, response: httpx.Response):
        try:
            response.raise_for_status()
        except httpx.RequestError as e:
            logger.error(response.content)
            raise e

    def get_queue_state(self):
        """
        Retrieves the user's current state in the game queue.
        Sends a GET request to the "/request" endpoint to obtain the user's queue status.
        If the response status code is 400, sets the user's status to NEVER_QUEUED and returns.
        Otherwise, validates the response, updates the game stub and the user's status accordingly.
        Raises:
            Exception: If the response contains an error other than status code 400.
        """

        resp = self.client.get("/request")
        if resp.status_code == 400:
            self.status = UserGameStatus.NEVER_QUEUED
            return
        self._raise_on_error(resp)
        game_stub = UserGameStub.model_validate(resp.json())
        self.game_stub = game_stub
        self.status = self.game_stub.status

    def enter_queue(self, game_type: str):
        """
        Enters the user into the queue for the specified game type.
        Args:
            game_type (str): The type of game to join the queue for.
        Raises:
            InvalidGameState: If the user is already in a state that prevents entering the queue.
            HTTPError: If the request to enter the queue fails.
        """

        if self.status in {
            UserGameStatus.IN_QUEUE,
            UserGameStatus.MATCHED,
            UserGameStatus.MATCHING,
            UserGameStatus.IN_PROGRESS,
        }:
            raise InvalidGameState(
                f"You are currently {self.status}. Which is an invalid state to start a game from."
            )

        resp = self.client.post("/request", json={"game_type": game_type})
        self._raise_on_error(resp)

    def leave_queue(self, lock_retries: int = 2, lock_retry_delay: float = 1.0):
        """
        Attempts to leave the matchmaking queue by sending a DELETE request to the server.
        If the client is currently locked by the matchmaker (HTTP 409 response), it will retry
        the request up to `lock_retries` times, waiting `lock_retry_delay` seconds between attempts.
        Args:
            lock_retries (int): Number of times to retry leaving the queue if locked. Default is 2.
            lock_retry_delay (float): Delay in seconds between retries if locked. Default is 1.0.
        Raises:
            Exception: If the response indicates an error other than a lock, or if all retries fail.
        """

        for _ in range(lock_retries + 1):
            resp = self.client.delete("/request")
            if resp.status_code == 409:
                logger.warning(
                    f"You are currently locked by the matchmaker. Waiting {lock_retry_delay} seconds before retrying."
                )
                time.sleep(lock_retry_delay)
                continue
            self._raise_on_error(resp)
            return

    def wait_for_match(self, delay: float = 1.0):
        """
        Blocks execution until the user is matched into a game and the game has started.
        Periodically checks the user's queue status and logs updates about the matching process.
        If the user is matched, logs the match information and continues waiting for the game to start.
        Returns when the game status transitions to 'IN_PROGRESS'.
        Raises InvalidGameState if the user's status is not valid for waiting for a match.
        Args:
            delay (float, optional): Time in seconds to wait between status checks. Defaults to 1.0.
        Raises:
            InvalidGameState: If the user's status is not valid for waiting for a match.
        """

        _matched = False
        start_time = time.time()
        while True:
            self.get_queue_state()
            logger.debug(
                f"Your current status is {self.status}. Time in queue: {time.time() - start_time:.0f}"
            )
            if self.status == UserGameStatus.MATCHED and not _matched:
                _matched = True
                assert self.game_stub is not None
                logger.info(
                    f"Matched into game {self.game_stub.game_id} of type {self.game_stub.game_type_id}. Waiting for the game to start. Time in queue: {time.time() - start_time:.0f}"
                )
            if self.status == UserGameStatus.IN_PROGRESS:
                assert self.game_stub is not None
                logger.info(
                    f"Game {self.game_stub.game_id} of type {self.game_stub.game_type_id} has started. Time in queue: {time.time() - start_time:.0f}"
                )
                return

            if self.status in {
                UserGameStatus.COMPLETED,
                UserGameStatus.FAILED,
                UserGameStatus.LEFT_QUEUE,
                UserGameStatus.NEVER_QUEUED,
            }:
                raise InvalidGameState(
                    f"Your current status of {self.status} is not valid for waiting for a match."
                )
            time.sleep(delay)

    def get_game_state(self):
        """
        Retrieves the current game state from the server and updates the relevant properties.
        Sends a GET request to the "/state" endpoint, validates the response, and sets
        the internal properties for move, state, move_received, and tick based on the
        received game state data.
        Raises:
            An exception if the server response indicates an error.
        """

        resp = self.client.get("/state")
        self._raise_on_error(resp)

        state_response = GameStateResponse.model_validate(resp.json())
        self._move = state_response.move
        self._state = state_response.state
        self.move_receieved = state_response.move_received
        self.tick = self._state.tick

    def wait_for_next_action(self, delay: float = 0.25):
        """
        Blocks execution until it is your turn to submit a move or the game is over.
        This method should be called after submitting a move. It continuously polls the game state,
        updating the relevant properties automatically, so `get_game_state` does not need to be called
        after this method returns. The method will unblock when either:
          - It is your turn to make another move, or
          - The game is over.
        During execution, it logs updates about move acceptance, game progression, and game outcome.
        If your previous move was rejected, it will log the rejection reason and return.
        Args:
            delay (float, optional): Time in seconds to wait between polling the game state. Defaults to 0.25.
        """

        while True:
            if self._move is None and self._state is None:
                self.get_game_state()

            before_move = self.move.model_copy(deep=True)
            before_move_received = self.move_receieved
            before_game_state = self.state.model_copy(deep=True)
            self.get_game_state()
            if self.state.game_over:
                assert self.state.winners is not None
                if self.state.player_id in self.state.winners:
                    logger.info(f"Game over. You WON!! Winners: {self.state.winners}")
                else:
                    logger.info(f"Game over. You Lost :( Winners: {self.state.winners}")
                return
            if (
                not before_move_received
                and self.move_receieved
                and self.move.rejection_reason is None
            ):
                logger.info(f"Your move for {before_game_state.tick} was accepted.")
            if before_move.tick != self.move.tick:
                logger.info(f"Game has progressed to tick {self.move.tick}.")

            if self.move.rejection_reason:
                logger.warning(f"Your move was rejected: {self.move.rejection_reason}")
                return
            if self.move.accepting_move and not self.move_receieved:
                logger.info(f"It is your turn. Submit a move for tick {self.tick}")
                return

            time.sleep(delay)

    def make_move(self, move: Dict[str, Any]):
        """
        Submits a move to the server for the current game tick.
        Args:
            move (Dict[str, Any]): The move data to be sent to the server.
        Raises:
            Raises an exception if the server response indicates an error.
        """

        resp = self.client.post("/move", json={"tick": self.tick, "move": move})
        self._raise_on_error(resp)
        return

    def is_game_over(self):
        return self.state.game_over

    @property
    def state(self):
        assert self._state is not None
        return self._state

    @property
    def move(self):
        assert self._move is not None
        return self._move
