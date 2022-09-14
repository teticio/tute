"""Tute env for RL Card.
"""

from rlcard.envs import Env
from .game import TuteGame


class TuteEnv(Env):  # pylint: disable=abstract-method
    """GinRummy Environment.
    """

    def __init__(self, config):
        self.name = 'tute'
        self.game = TuteGame()
        super().__init__(config=config)

    def _extract_state(self, state):
        """ Encode state.

        Args:
            state (dict): dict of original state

        Returns:
        """
        return None  #extracted_state

    def get_payoffs(self):
        """Get the payoffs of players. Must be implemented in the child class.

        Returns:
            payoffs (list): a list of payoffs for each player
        """
        # determine whether game completed all moves
        return None  #np.array(payoffs)

    def _decode_action(self, action_id):
        """Action id -> the action in the game. Must be implemented in the child class.

        Args:
            action_id (int): the id of the action

        Returns:
            action (ActionEvent): the action that will be passed to the game engine.
        """
        return self.game.decode_action(action_id=action_id)

    def _get_legal_actions(self):
        """Get all legal actions for current state.

        Returns:
            legal_actions (list): a list of legal actions' id
        """
        return None  #OrderedDict(legal_actions_ids)
