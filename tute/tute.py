"""Tute card game.
"""
# pragma pylint: disable=redefined-outer-name

import os
import logging
import argparse
from typing import Callable

import pandas as pd

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('tute')


class Tute:
    """Tute card game.
    """
    cards = {
        1: {
            'name': 'el as',
            'ranking': 1,
            'points': 11
        },
        2: {
            'name': 'el dos',
            'ranking': 12,
            'points': 0
        },
        3: {
            'name': 'el tres',
            'ranking': 2,
            'points': 10
        },
        4: {
            'name': 'el cuatro',
            'ranking': 11,
            'points': 0
        },
        5: {
            'name': 'el cinco',
            'ranking': 10,
            'points': 0
        },
        6: {
            'name': 'el seis',
            'ranking': 9,
            'points': 0
        },
        7: {
            'name': 'el siete',
            'ranking': 8,
            'points': 0
        },
        8: {
            'name': 'el ocho',
            'ranking': 7,
            'points': 0
        },
        9: {
            'name': 'el nueve',
            'ranking': 6,
            'points': 0
        },
        10: {
            'name': 'la sota',
            'ranking': 5,
            'points': 2
        },
        11: {
            'name': 'el caballo',
            'ranking': 4,
            'points': 3
        },
        12: {
            'name': 'el rey',
            'ranking': 3,
            'points': 4
        },
    }

    suits = ['oros', 'copas', 'espadas', 'bastos']

    def __init__(self, num_players: int = 2, habanero: bool = True):
        self.num_players = max(2, min(num_players, 4))
        self.num_cards_per_player = [8, 12, 10][self.num_players - 2]
        self.habanero = habanero

        self.suit = None
        self.trump_suit = None
        self.shown = set()
        self.cantes = {}
        self.last_trick_winner = None
        self.messages = []

        self.locations = {
            'unknown': 0,
            'pile': 1,
            'trump': 2,
            **{
                f'player {player + 1} hand': 3 * player + 3
                for player in range(num_players)
            },
            **{
                f'player {player + 1} tricks': 3 * player + 4
                for player in range(num_players)
            },
            **{
                f'player {player + 1} face up': 3 * player + 5
                for player in range(num_players)
            }
        }

        discards = [8, 9]
        if self.num_players == 3:
            discards += [2]

        deck = {}
        card_id = 0
        for suit in self.suits:
            for card in self.cards.items():
                if card[0] in discards:
                    continue

                deck[card_id] = {
                    'description': f"{card[1]['name']} de {suit}",
                    'suit': self.suits.index(suit),
                    'value': card[0],
                    'ranking': card[1]['ranking'],
                    'points': card[1]['points'],
                    'location': self.locations['pile']
                }
                card_id += 1

        self.deck = pd.DataFrame.from_dict(deck, orient='index')

    def shuffle(self):
        """Shuffle deck.
        """
        self.deck = self.deck.sample(frac=1)

    def move(self, card: pd.DataFrame, location: int):
        """Move card to location.

        Args:
            card (DataFrame): card to move
            location (int): location according to tute.location
        """
        logger.info(
            '%s went from %s to %s', card.description,
            dict(zip(self.locations.values(),
                     self.locations.keys()))[card.location], location)
        self.deck.loc[card.name, 'location'] = self.locations[location]

    def deal(self, dealer: int = 0):
        """Deal deck.

        Args:
            dealer (int): number of player who is dealing
        """
        self.shuffle()

        self.suit = None
        self.shown = set()
        self.cantes = {}
        self.last_trick_winner = None
        self.messages = []

        dealt = 0
        player = (dealer + 1) % self.num_players
        deck = self.deck.T.iteritems()
        for card in deck:
            self.move(card[1], f'player {player + 1} hand')
            player = (player + 1) % self.num_players
            dealt += 1
            if (self.num_cards_per_player is not None
                    and dealt == self.num_cards_per_player * self.num_players):
                break

        try:
            trump = next(deck)
            self.move(trump[1], 'trump')
            self.trump_suit = trump[1].suit

        except StopIteration:
            self.shown.add(card[0])  # pylint: disable=undefined-loop-variable
            self.trump_suit = card[1].suit  # pylint: disable=undefined-loop-variable

    def get_cards_in(self, location: int) -> pd.DataFrame:
        """Get cards in location.

        Args:
            location (int): location according to tute.location.

        Returns:
            DataFrame: cards in location
        """
        return self.deck[self.deck.location == self.locations[location]]

    def get_hand(self, player: int) -> pd.DataFrame:
        """Get cards in player's hand.

        Args:
            player (int): Number of player.

        Returns:
            DataFrame: cards in player's hand
        """
        return self.get_cards_in(f'player {player + 1} hand')

    def get_trump(self) -> pd.DataFrame:
        """Get trump card (if not in a hand).

        Returns:
            DataFrame: trump card
        """
        return self.get_cards_in('trump')

    def get_face_up(self) -> pd.DataFrame:
        """Get cards in play.

        Returns:
            DataFrame: cards in play
        """
        return self.deck[self.deck.location.isin([
            self.locations[f'player {player + 1} face up']
            for player in range(self.num_players)
        ])]

    @staticmethod
    def show_cards(cards, with_index: bool = False):
        """Convenience method to print cards.

        Args:
            cards (Series): cards to print
            with_index (bool): if True, print index of each card
        """
        for index, card in enumerate(cards.T.iteritems()):
            if with_index:
                print(f'{index + 1}: ', end='')
            print(card[1].description)

    @staticmethod
    def choose_card(
        context, hand: pd.DataFrame, possible_cards: pd.DataFrame) -> list:  # pylint: disable=unused-argument
        """Convenience method to get input from user.

        Args:
            hand (Series): cards in hand
            possible_cards (list): list of possible card indices

        Returns:
            DataFrame: Choosen card.
        """
        Tute.show_cards(hand, with_index=True)

        while True:
            choice = input(' '.join([f'{_ + 1} '
                                     for _ in possible_cards]) + '? ')
            try:
                if int(choice) - 1 in possible_cards:
                    break
            except ValueError:
                continue
        return hand.iloc[int(choice) - 1]

    def do_trick(self):
        """Process trick.
        """
        highest_ranking = None
        highest_ranking_trump = None
        for player in range(self.num_players):
            card = self.get_cards_in(f'player {player + 1} face up').iloc[0]

            if card.suit == self.suit and (highest_ranking is None
                                           or card.ranking < highest_ranking):
                highest_ranking = card.ranking
                winning_player = player
                continue

            if card.suit == self.trump_suit and (
                    highest_ranking_trump is None
                    or card.ranking < highest_ranking_trump):
                highest_ranking_trump = card.ranking
                winning_player = player

        face_up = self.get_face_up()
        for card in face_up.T.iteritems():
            self.move(card[1], f'player {winning_player + 1} tricks')

        logger.info('Player %d won trick', winning_player + 1)
        return winning_player

    def calc_points(self, player: int) -> int:
        """Tot up points for player.

        Args:
            player (int): number of player for which to calculate points.
        """
        points = 0
        if player == self.last_trick_winner:
            points += 10

        for cante in self.cantes.items():
            if cante[1] == player:
                points += 40 if cante[1] == self.trump_suit else 20

        return points + self.get_cards_in(
            f'player {player + 1} tricks').points.sum()

    def deal_new_cards(self, winning_player: int):
        """Deal cards from pile, starting with player who won the trick.

        Args:
            Winning_player (int): number of player who won the last trick
        """
        to_deal = pd.concat(
            [self.get_cards_in('pile'),
             self.get_cards_in('trump')], axis=0)

        if len(to_deal) >= self.num_players:
            for dealt, card in enumerate(to_deal.T.iteritems()):
                if dealt == self.num_players:
                    break
                self.move(
                    card[1],
                    f'player {(winning_player + dealt) % self.num_players + 1} hand'
                )

    def get_follow_suit(self) -> bool:
        """Determines whether player has to follow suit or not.

        Returns:
            bool: if True, suit must be followed
        """
        return not self.habanero or len(self.get_cards_in('pile')) + len(
            self.get_cards_in('trump')) < self.num_players

    def get_possible_cards(self, face_up: pd.DataFrame,
                           hand: pd.DataFrame) -> list:
        """Determine which cards can be played from the hand.

        Args:
            face_up (Series): cards in play.
            hand (Series): cards in hand.

        Returns:
            list: list of possible card indices.
        """
        follow_suit = self.get_follow_suit()
        if not follow_suit or len(face_up) == 0:
            return hand.T.any()

        highest_ranking = face_up[face_up.suit == self.suit].ranking.min()
        higher_ranking = (hand.suit
                          == self.suit) & (hand.ranking < highest_ranking)
        if any(higher_ranking):
            return higher_ranking

        same_suit = hand.suit == self.suit
        if any(same_suit):
            return same_suit

        highest_ranking_trump = face_up[face_up.suit ==
                                        self.trump_suit].ranking.min()
        higher_ranking_trump = (hand.suit == self.trump_suit) & (
            hand.ranking < highest_ranking_trump)
        if any(higher_ranking_trump):
            return higher_ranking_trump

        trump = hand.suit == self.trump_suit
        if any(trump):
            return trump

        return hand.T.any()

    def swap_trump(self):
        """Automatically swap trump card if possible.
        """

        def _swap_trump(trump, trump_swap):
            for player in range(self.num_players):
                if trump_swap.location == self.locations[
                        f'player {player + 1} hand']:
                    self.deck.loc[self.deck.index == trump_swap.name,
                                  'location'] = self.locations['trump']
                    self.deck.loc[self.deck.index == trump.name,
                                  'location'] = self.locations[
                                      f'player {player + 1} hand']
                    self.shown.add(trump.name)
                    self.messages += [
                        f'Player {player + 1} swapped {trump.description} \
for {trump_swap.description}'
                    ]
                    logger.info(self.messages[-1])

        trump = self.get_cards_in('trump')
        if len(trump) < 1:
            return

        trump = trump.iloc[0]
        if trump.value >= 10:
            trump_swap = self.deck[(self.deck.suit == self.trump_suit)
                                   & (self.deck.value == 7)].iloc[0]
            _swap_trump(trump, trump_swap)

        trump = self.get_cards_in('trump').iloc[0]
        if trump.value < 10:
            trump_swap = self.deck[(self.deck.suit == self.trump_suit)
                                   & (self.deck.value == 2)].iloc[0]
            _swap_trump(trump, trump_swap)

    def cantar(self, player: int):
        """Automatically "cantar".

        Args:
            player (int): number of player who is "cantando"
        """

        # To simplify we are going to "cantar" greedily.
        # Also, we are not going to allow "cantar tute".

        def _caballo_and_rey(hand, suit):
            return hand[(hand.suit == suit)
                        & ((hand.value == 11) | (hand.value == 12))]

        hand = self.get_hand(player)
        caballo_and_rey = _caballo_and_rey(hand, self.trump_suit)
        if len(self.cantes) == 0 and len(caballo_and_rey) == 2:
            self.cantes[self.trump_suit] = player
            self.shown.update(caballo_and_rey.index.tolist())
            self.messages += [
                f'Player {player + 1} canta {self.suits[self.trump_suit]}'
            ]
            logger.info(self.messages[-1])
            return

        for suit, _ in enumerate(self.suits):
            if suit == self.trump_suit or suit in self.cantes:
                continue
            caballo_and_rey = _caballo_and_rey(hand, suit)
            if len(caballo_and_rey) == 2:
                self.cantes[suit] = player
                self.shown.update(caballo_and_rey.index.tolist())
                self.messages += [
                    f'Player {player + 1} canta {self.suits[suit]}'
                ]
                logger.info(self.messages[-1])
                return

    def pre_move(self, player) -> list:
        """Everything in a turn before player's move.

        Args:
            player (int): number of player whose turn it is.

        Returns:
            list: list of possible card indices
        """
        if self.habanero:
            self.swap_trump()

        hand = self.get_hand(player)
        face_up = self.get_face_up()
        possible_cards = [
            card for card, possible in enumerate(
                self.get_possible_cards(face_up, hand)) if possible
        ]
        return possible_cards

    def post_move(self, card: pd.DataFrame) -> int:
        """Everything in a turn after player's move.

        Args:
            card (DataFrame): cards being played

        Returns:
            int: number of trick swinning player (or None)
        """

        face_up = self.get_face_up()
        if len(face_up) == 1:
            self.suit = card.suit
            return None

        winning_player = None
        if len(face_up) == self.num_players:
            winning_player = self.do_trick()
            if self.num_players != 2 or len(self.get_cards_in('pile')) > 0:
                self.cantar(winning_player)  # before dealing new cards
            self.deal_new_cards(winning_player)
            if len(self.get_hand(winning_player)) == 0:
                self.last_trick_winner = winning_player

        return winning_player

    def play_turn(self, player: int, choose_card: Callable = None) -> int:
        """Play turn.

        Args:
            player (int): number of player whose turn it is.
            choose_card (function): function to choose card (see Tute.choose_card).
        """
        choose_card = choose_card or self.choose_card
        possible_cards = self.pre_move(player)
        card = choose_card(self, self.get_hand(player), possible_cards)
        self.move(card, f'player {player + 1} face up')
        winning_player = self.post_move(card)
        return winning_player

    def retreive_messages(self) -> list:
        """Retrieve messages such as cantes etc. Also clears message list.

        Returns:
            list: List of string messages
        """
        messages = self.messages
        self.messages = []
        return messages

    @staticmethod
    def show_messages(messages: list):
        """Convenience method to print messages.
        """
        for message in messages:
            print(message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Demo Tute game.")
    parser.add_argument("--num_players",
                        type=int,
                        default=2,
                        help='number of players')
    parser.add_argument("--habanero",
                        type=bool,
                        default=True,
                        help='Tute Habanero')
    args = parser.parse_args()

    tute = Tute(num_players=args.num_players, habanero=args.habanero)
    tute.deal()

    player = 0  # pylint: disable=invalid-name
    while len(tute.get_hand(player)) > 0:
        print('Trump')
        trump = tute.get_trump()
        if len(trump) > 0:
            tute.show_cards(trump)
        else:
            print(tute.suits[tute.trump_suit])
        print()

        face_up = tute.get_face_up()
        if len(face_up) > 0:
            print('Face up')
            tute.show_cards(face_up)
            print()

        if tute.get_follow_suit():
            print('Follow suit')
            print()

        messages = tute.retreive_messages()
        if len(messages) > 0:
            tute.show_messages(messages)
            print()

        print(f'Player {player + 1}')
        winning_player = tute.play_turn(player=player)
        print()

        if winning_player is not None:
            print(f'Player {winning_player + 1} won trick')
            print(f'Points: {tute.calc_points(winning_player)}')
            print()
            player = winning_player
        else:
            player = (player + 1) % tute.num_players

        input('Press any key to change player ')
        os.system('cls' if os.name == 'nt' else 'clear')

    highest_points = None  # pylint: disable=invalid-name
    for player in range(tute.num_players):
        points = tute.calc_points(player)
        print(f'Player {player + 1} points: {points}')
        if highest_points is None or points > highest_points:
            highest_points = points
            winning_player = player
    print(f'Player {winning_player + 1} wins!')
