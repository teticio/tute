import random
from tute import Tute


def test_deck():
    tute = Tute()
    assert tute.deck.description.unique().size == 48


def test_deal():
    tute = Tute()
    tute.deal()

    for player in range(tute.num_players):
        assert len(tute.get_hand(player)) == 8
    assert tute.trump_suit is not None

def choose_card(hand, possible_cards):
    assert len(possible_cards) > 0
    return hand.iloc[random.choice(possible_cards)]

def test_turn():
    tute = Tute()
    tute.deal()

    for player in range(tute.num_players):
        winning_player = tute.play_turn(player=player, choose_card=choose_card)

    for player in range(tute.num_players):
        assert len(tute.get_hand(player)) == 8

    assert len(tute.get_cards_in(
        f'player {winning_player + 1} tricks')) == tute.num_players

def test_game():
    tute = Tute()
    tute.deal()

    player = 0
    while len(tute.get_hand(player)) > 0:
        winning_player = tute.play_turn(player=player, choose_card=choose_card)
        if winning_player is not None:
            player = winning_player
        else:
            player = (player + 1) % tute.num_players

    assert len(tute.get_cards_in('pile')) == 0
