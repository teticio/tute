"""Tute card game with RL Card.
"""
from tute import Tute


class TuteGame(Tute):
    """Game class. This class will interact with outer environment.
    """

    def __init__(self):
        self.allow_step_back = False
        super().__init__()

    def init_game(self):
        """Initialize all characters in the game and start round 1.
        """
        #state = self.get_state(player_id=current_player_id)
        return None, None  #state, current_player_id

    def step(self, action: int) -> int:
        """Perform game action and return next player number, and the state for next player.
        """
        return action, None  #next_state, next_player_id

    def step_back(self):
        """Takes one step backward and restore to the last state.
        """
        raise NotImplementedError

    def get_num_players(self):
        """Return the number of players in the game.
        """
        return self.num_players

    def get_num_actions(self):
        """Return the number of possible actions in the game.
        """
        return None  #self.num_actions

    def get_player_id(self):
        """Return the current player that will take actions soon.
        """
        return None  #self.current_player_id

    def is_over(self):
        """Return whether the current game is over.
        """
        return None  #self.is_over

    def get_state(self, player_id: int) -> dict:
        """Get player's state.

        Returns:
            dict: The information of the state
        """
        return player_id  #state

    @staticmethod
    def decode_action(action_id: int) -> str:
        """ Action id -> the action_event in the game.

        Args:
            action_id (int): the id of the action

        Returns:
            str: the action that will be passed to the game engine
        """
        return action_id  #ActionEvent.decode_action(action_id=action_id)
