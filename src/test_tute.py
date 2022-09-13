import random
from tute import Tute


def test_deck():
    tute = Tute()
    assert tute.deck.description.unique().size == 40


def test_deal():
    tute = Tute()
    tute.deal()

    for player in range(tute.num_players):
        assert len(tute.get_hand(player)) == tute.num_cards_per_player
    assert tute.trump_suit is not None


def choose_card(context, hand, possible_cards):
    assert len(possible_cards) > 0
    return hand.iloc[random.choice(possible_cards)]


def test_turn():
    tute = Tute()
    tute.deal()

    for player in range(tute.num_players):
        winning_player = tute.play_turn(player=player, choose_card=choose_card)

    for player in range(tute.num_players):
        assert len(tute.get_hand(player)) == tute.num_cards_per_player

    assert len(tute.get_cards_in(
        f'player {winning_player + 1} tricks')) == tute.num_players


def test_game():

    def _test_game(num_cards_per_player):
        tute = Tute(num_cards_per_player=num_cards_per_player)
        tute.deal()

        player = 0
        while len(tute.get_hand(player)) > 0:
            winning_player = tute.play_turn(player=player,
                                            choose_card=choose_card)
            if winning_player is not None:
                player = winning_player
            else:
                player = (player + 1) % tute.num_players

        num_cards_in_tricks = 0
        for player in range(tute.num_players):
            num_cards_in_tricks += len(
                tute.get_cards_in(f'player {player + 1} tricks'))
        assert num_cards_in_tricks == len(tute.deck)

    _test_game(num_cards_per_player=8)
    _test_game(num_cards_per_player=None)
