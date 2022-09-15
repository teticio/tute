"""Tute card game with RL Card.
"""
from tute import Tute


class TuteGame(Tute):
    """Game class. This class will interact with outer environment.
    """

    def __init__(self):
        super().__init__()
        self.allow_step_back = False
        self.current_player = 0

    def init_game(self):
        """Initialize all characters in the game and start round 1.
        """
        self.deal(self.current_player)
        self.current_player = (self.current_player + 1) % self.num_players
        return self.get_state(self.current_player), self.current_player

    def step(self, action: int) -> int:
        """Perform game action and return next player number, and the state for next player.
        """

        def _choose_card(self, hand, possible_cards):
            assert self.deck.iloc[action] in [
                hand.iloc[card] for card in possible_cards
            ]
            return self.deck.iloc[action]

        winning_player = self.play_turn(self.current_player, _choose_card)
        self.current_player = winning_player or (self.current_player +
                                                 1) % self.num_players
        return self.get_state(self.current_player), self.current_player

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
        return len(self.deck)

    def get_player_id(self):
        """Return the current player that will take actions soon.
        """
        return self.current_player

    def is_over(self):
        """Return whether the current game is over.
        """
        return len(self.get_hand(0)) == 0

    def get_state(self, player: int) -> dict:
        """Returns everything the player can know about the state of the game.

        Args:
            player (int): Number of player.

        Returns:
            dict: Current state known by player.
        """
        cards = self.deck.copy()
        for other_player in range(self.num_players):
            if other_player == player:
                continue

            cards.loc[(cards.location == self.locations['pile']),
                      'location'] = self.locations['unknown']

            cards.loc[(cards.location ==
                       self.locations[f'player {other_player + 1} hand']) &
                      (~cards.index.isin(self.shown)),
                      'location'] = self.locations['unknown']

        return {
            'suit': self.suit,
            'trump_suit': self.trump_suit,
            'locations': cards.sort_index().location.to_list()
        }

    def decode_action(self, action_id: int) -> str:
        """Action id -> the action_event in the game.

        Args:
            action_id (int): the id of the action

        Returns:
            str: the action that will be passed to the game engine
        """
        return self.deck[self.deck.index == action_id].description
