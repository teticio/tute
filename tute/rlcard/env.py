"""Tute env for RL Card.
"""

import numpy as np

from rlcard.envs import Env
from .game import TuteGame


class TuteEnv(Env):  # pylint: disable=abstract-method
    """GinRummy Environment.
    """

    def __init__(self, config):
        self.name = 'tute'
        self.game = TuteGame()

        # first row of state space one-hot encodes suit and trump_suit
        assert len(self.game.locations) >= 2 * len(self.game.suits)

        # the following rows one-hot encode the location of each card
        self.state_shape = (len(self.game.deck) + 1, len(self.game.locations))
        self.action_shape = (len(self.game.deck),)

        super().__init__(config=config)

    def _extract_state(self, state: np.array) -> dict:
        """ Encode state.

        Args:
            state (dict): dict of original state.

        Returns:
        """
        return None  #extracted_state

    def get_payoffs(self) -> list:
        """Get the payoffs of players. Must be implemented in the child class.

        Returns:
            list: A list of payoffs for each player
        """
        # determine whether game completed all moves
        return None  #np.array(payoffs)

    def _decode_action(self, action_id: int) -> str:
        """Action id -> the action in the game. Must be implemented in the child class.

        Args:
            action_id (int): The id of the action.

        Returns:
            str: The action that will be passed to the game engine.
        """
        return self.game.decode_action(action_id=action_id)

    def _get_legal_actions(self) -> list:
        """Get all legal actions for current state.

        Returns:
            list: A list of legal action ids.
        """
        return None  #OrderedDict(legal_actions_ids)
