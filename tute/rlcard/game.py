"""Tute card game with RL Card.
"""
from typing import Tuple

import pandas as pd

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
        self.deck.location = self.locations['pile']
        self.deal(self.current_player)
        self.current_player = (self.current_player + 1) % self.num_players
        return self.get_state(self.current_player), self.current_player

    def step(self, card: pd.DataFrame) -> Tuple[dict, int]:
        """Perform game action and return next player number, and the state for next player.

        Args:
            action (int): action to perform (card to play)

        Returns:
            dict: next player state
            int: next player
        """
        assert card.location == self.locations[f'player {self.current_player + 1} hand']
        self.move(card, f'player {self.current_player + 1} face up')
        winning_player = self.post_move(card)
        self.current_player = winning_player or (self.current_player +
                                                 1) % self.num_players
        return self.get_state(self.current_player), self.current_player

    def step_back(self):
        """Takes one step backward and restore to the last state.
        """
        raise NotImplementedError

    def get_num_players(self) -> int:
        """Return the number of players in the game.

        Returns:
            int: number of players
        """
        return self.num_players

    def get_num_actions(self) -> int:
        """Return the number of possible actions in the game.

        Returns:
            int: number of possible actions
        """
        return len(self.deck)

    def get_player_id(self) -> int:
        """Return the current player that will take actions soon.

        Returns:
            int: number of current player
        """
        return self.current_player

    def is_over(self) -> bool:
        """Return whether the current game is over.

        Returns:
            bool: True if game has finished
        """
        return len(self.get_hand(0)) == 0

    def get_state(self, player: int) -> dict:
        """Returns everything the player can know about the state of the game.

        Args:
            player (int): number of player

        Returns:
            dict: current state known by player
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

    def get_legal_actions(self) -> list:
        """Get all legal actions for current state.

        Returns:
            list: a list of legal action ids
        """
        possible_cards = self.pre_move(self.current_player)
        hand = self.get_hand(self.current_player)
        return [hand.iloc[card].name for card in possible_cards]

    def decode_action(self, action_id: int) -> pd.DataFrame:
        """Action id -> the action_event in the game.

        Args:
            action_id (int): the id of the action

        Returns:
            str: the action that will be passed to the game engine
        """
        return self.deck[self.deck.index == action_id].iloc[0]
