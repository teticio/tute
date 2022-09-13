# https://www.ludoteka.com/clasika/tute-habanero.html

# TODO:
# scoring
# los cantes
# 10 points for last trick
# player can know suit, trump (+ swaps), tricks, his hand, cantes

import os
import logging
from pprint import pprint

import pandas as pd

logging.basicConfig(format='%(message)s', level=logging.INFO)


class Tute:
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

    def __init__(self, num_players=2, habanero=True):
        self.num_players = max(2, min(num_players, 4))
        self.num_cards_per_player = [8, 12, 10][self.num_players - 2]
        self.habanero = habanero

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
            for card in self.cards:
                if card in discards:
                    continue

                deck[card_id] = {
                    'description': f"{self.cards[card]['name']} de {suit}",
                    'suit': self.suits.index(suit),
                    'value': card,
                    'ranking': self.cards[card]['ranking'],
                    'points': self.cards[card]['points'],
                    'location': self.locations['pile']
                }
                card_id += 1

        self.deck = pd.DataFrame.from_dict(deck, orient='index')

    def shuffle(self):
        self.deck = self.deck.sample(frac=1)

    def move(self, card, location):
        self.deck.loc[card.name, 'location'] = self.locations[location]

    def deal(self, dealer=0):
        self.shuffle()

        self.suit = None
        self.shown = set()
        self.cantes = {}
        self.last_trick_winner = None

        player = (dealer + 1) % self.num_players
        self.current_player = player

        dealt = 0
        deck = self.deck.T.iteritems()
        for card in deck:
            self.move(card[1], f'player {player + 1} hand')
            player = (player + 1) % self.num_players
            dealt += 1
            if self.num_cards_per_player is not None and dealt == self.num_cards_per_player * self.num_players:
                break

        try:
            trump = deck.__next__()
            self.move(trump[1], 'trump')
            self.trump_suit = trump[1].suit

        except StopIteration:
            self.shown.add(card[0])
            self.trump_suit = card[1].suit

    def get_cards_in(self, location):
        return self.deck[self.deck.location == self.locations[location]]

    def get_hand(self, player):
        return self.get_cards_in(f'player {player + 1} hand')

    def get_trump(self):
        return self.get_cards_in('trump')

    def get_face_up(self):
        return self.deck[self.deck.location.isin([
            self.locations[f'player {player + 1} face up']
            for player in range(self.num_players)
        ])]

    @staticmethod
    def choose_card(context, hand, possible_cards):
        pprint([
            f'{_ + 1}: {card}'
            for _, card in enumerate(hand.description.tolist())
        ])

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

        return winning_player

    def calc_points(self, player):
        points = 0
        if player == self.last_trick_winner:
            points += 10

        for cante in self.cantes:
            if self.cantes[cante] == player:
                points += 40 if cante == self.trump_suit else 20

        return points + self.get_cards_in(
            f'player {player + 1} tricks').points.sum()

    def deal_new_cards(self, winning_player):
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

    def get_follow_suit(self):
        return not self.habanero or len(self.get_cards_in('pile')) + len(
            self.get_cards_in('trump')) < self.num_players

    def get_possible_cards(self, face_up, hand):
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
                    logging.info(
                        f'Player {player + 1} swapped {trump.description} for {trump_swap.description}'
                    )

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

    def cantar(self, player):
        # To simplify we are going to "cantar" greedily.
        # Also, we are not going to allow "cantar tute".

        def _have_caballo_and_rey(hand, suit):
            return len(hand[(hand.suit == suit)
                            & ((hand.value == 11) | (hand.value == 12))]) == 2

        hand = self.get_hand(player)
        if len(self.cantes) == 0 and _have_caballo_and_rey(hand, self.trump_suit):
            self.cantes[self.trump_suit] = player
            logging.info(f'Player {player + 1} canta {self.suits[self.trump_suit]}')
            return
        
        for suit in range(len(self.suits)):
            if suit == self.trump_suit:
                continue
            if suit not in self.cantes and _have_caballo_and_rey(hand, suit):
                self.cantes[suit] = player
                logging.info(f'Player {player + 1} canta {self.suits[suit]}')
                return

    def play_turn(self, player, choose_card=None):
        choose_card = choose_card or self.choose_card

        if self.habanero:
            self.swap_trump()

        hand = self.get_hand(player)
        face_up = self.get_face_up()
        possible_cards = [
            card for card, possible in enumerate(
                self.get_possible_cards(face_up, hand)) if possible
        ]

        card = choose_card(self, hand, possible_cards)
        self.move(card, f'player {player + 1} face up')
        if len(face_up) == 0:
            self.suit = card.suit

        winning_player = None
        face_up = self.get_face_up()
        if len(face_up) == self.num_players:
            winning_player = self.do_trick()
            if self.num_players != 2 or len(self.get_cards_in('pile')) > 0:
                self.cantar(winning_player)  # before dealing new cards
            self.deal_new_cards(winning_player)
            if len(self.get_hand(winning_player)) == 0:
                self.last_trick_winner = winning_player

        return winning_player


if __name__ == '__main__':
    tute = Tute()
    tute.deal()

    player = 0
    while len(tute.get_hand(player)) > 0:
        print('Trump')
        print(tute.get_trump())

        face_up = tute.get_face_up()
        if len(face_up) > 0:
            print('Face up')
            print(face_up)

        if tute.get_follow_suit():
            print('Follow')

        print(f'Player {player + 1}')
        winning_player = tute.play_turn(player=player)
        if winning_player is not None:
            print(f'Player {winning_player + 1} won trick')
            print(f'Points: {tute.calc_points(winning_player)}')
            player = winning_player
        else:
            player = (player + 1) % tute.num_players

        input('Press any key to change player')
        os.system('cls' if os.name == 'nt' else 'clear')

    highest_points = None
    for player in range(tute.num_players):
        points = tute.calc_points(player)
        print(f'Player {player + 1} points: {points}')
        if highest_points is None or points > highest_points:
            highest_points = points
            winning_player = player
    print(f'Player {winning_player + 1} wins!')
