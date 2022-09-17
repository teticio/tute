"""Tute env for RL Card.
"""

from collections import OrderedDict

import numpy as np

from rlcard.envs import Env
from .game import TuteGame


class TuteEnv(Env):  # pylint: disable=abstract-method
    """Tute Environment.
    """

    def __init__(self, config):
        self.name = 'tute'
        self.game = TuteGame()
        self.num_players = self.game.num_players

        assert len(self.game.locations) >= 2 * len(self.game.suits) + 1
        self.state_shape = [[
            # first row of state space one-hot encodes suit and trump_suit and follow_suit
            len(self.game.deck) + 1,
            # the following rows one-hot encode the location of each card
            len(self.game.locations)
        ]] * self.num_players
        self.action_shape = [[len(self.game.deck)]] * self.num_players

        super().__init__(config=config)

    def _extract_state(self, state: np.array) -> dict:
        """ Encode state.

        Args:
            state (dict): dict of original state.

        Returns:
            dict: encoded state
        """
        suit = np.eye(len(self.game.suits))[state['suit'] or 0]
        trump_suit = np.eye(len(self.game.suits))[state['trump_suit']]
        deck = np.eye(len(self.game.locations))[state['locations']]
        follow_suit = [self.game.get_follow_suit()]
        obs = np.concatenate([
            np.concatenate([
                suit, trump_suit, follow_suit,
                np.zeros(
                    len(self.game.locations) - 2 * len(self.game.suits) - 1)
            ])[:, np.newaxis].transpose(), deck
        ],
                             axis=0)

        extracted_state = {
            'obs': obs,
            'legal_actions': self._get_legal_actions(),
            'raw_legal_actions': list(self._get_legal_actions().keys())
        }
        extracted_state['raw_obs'] = obs
        return extracted_state

    def get_payoffs(self) -> list:
        """Get the payoffs of players. Must be implemented in the child class.

        Returns:
            list: a list of payoffs for each player
        """
        return np.array([
            self.game.calc_points(player) for player in range(self.num_players)
        ])

    def _decode_action(self, action_id: int) -> str:
        """Action id -> the action in the game. Must be implemented in the child class.

        Args:
            action_id (int): The id of the action.

        Returns:
            str: the action that will be passed to the game engine
        """
        return self.game.decode_action(action_id=action_id)

    def _get_legal_actions(self) -> dict:
        """Get all legal actions for current state.

        Returns:
            dict: a list of legal action ids
        """
        legal_actions = self.game.get_legal_actions()
        legal_actions_ids = {action: None for action in legal_actions}
        return OrderedDict(legal_actions_ids)
