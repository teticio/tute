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

    def __init__(self,
                 num_players=2,
                 num_cards_per_player=8,
                 habanero=True,
                 discard_eights_and_nines=True):
        self.num_players = max(2, min(num_players, 4))
        self.num_cards_per_player = num_cards_per_player
        self.habanero = habanero
        self.discard_eights_and_nines = discard_eights_and_nines

        self.trump_suit = None
        self.suit = None

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

        deck = {}
        card_id = 0
        for suit in self.suits:
            for card in self.cards:
                if self.discard_eights_and_nines and card in [8, 9]:
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
            self.trump_suit = trump[1]['suit']
            
        except StopIteration:
            # TODO: "show" trump
            self.trump_suit = card[1]['suit']

        remainder = len(self.deck) % self.num_players
        self.deck.drop(self.deck.tail(remainder).index, inplace = True)

        self.cantes = {k: 0 for k in self.suits}

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

            if card.suit == self.suit and (
                    highest_ranking is None
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
        # TODO: cantes etc
        return self.get_cards_in(f'player {player + 1} tricks').points.sum()

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

    def get_possible_cards(self, face_up, hand):
        follow_suit = not self.habanero or len(
            self.get_cards_in('pile')) + 1 < self.num_players
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

    def play_turn(self, player, choose_card=None):
        choose_card = choose_card or self.choose_card
        # TODO: automatically cantar, swap trump

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
            self.deal_new_cards(winning_player)
        return winning_player


if __name__ == '__main__':
    tute = Tute()
    tute.deal()

    player = 0
    while len(tute.get_hand(player)) > 0:
        print('TRUMP')
        print(tute.get_trump())

        face_up = tute.get_face_up()
        if len(face_up) > 0:
            print('FACE UP')
            print(face_up)

        if not tute.habanero or len(
                tute.get_cards_in('pile')) + 1 < tute.num_players:
            print('FOLLOW')

        print(f'PLAYER {player + 1}')
        winning_player = tute.play_turn(player=player)
        if winning_player is not None:
            print(f'PLAYER {winning_player + 1} WON TRICK')
            print(f'POINTS: {tute.calc_points(winning_player)}')
            player = winning_player
        else:
            player = (player + 1) % tute.num_players

        input('NEXT PLAYER')
        os.system('cls' if os.name == 'nt' else 'clear')

    highest_points = None
    for player in range(tute.num_players):
        points = tute.calc_points(player)
        print(f'PLAYER {player + 1} POINTS: {points}')
        if highest_points is None or points > highest_points:
            highest_points = points
            winning_player = player
    print(f'PLAYER {winning_player + 1} WINS!')
