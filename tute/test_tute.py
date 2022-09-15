"""Test Tute game.
"""
import random

from rlcard import make
from rlcard.agents import RandomAgent

from tute import Tute
from tute import rlcard  # pylint: disable=unused-import


def test_deck():
    """Test deck has the right number of cards.
    """
    tute = Tute()
    assert tute.deck.description.unique().size == 40

    tute = Tute(num_players=3)
    assert tute.deck.description.unique().size == 36


def test_deal():
    """Test right number of cards are dealt.
    """
    tute = Tute()
    tute.deal()

    for player in range(tute.num_players):
        assert len(tute.get_hand(player)) == tute.num_cards_per_player
    assert tute.trump_suit is not None


def choose_card(context, hand, possible_cards):  # pylint: disable=unused-argument
    """Dummy player that always chooses a random card.
    """
    assert len(possible_cards) > 0
    return hand.iloc[random.choice(possible_cards)]


def test_round():
    """Test that a trick is won after a round.
    """
    tute = Tute()
    tute.deal()

    for player in range(tute.num_players):
        winning_player = tute.play_turn(player=player, choose_card=choose_card)

    for player in range(tute.num_players):
        assert len(tute.get_hand(player)) == tute.num_cards_per_player

    assert len(tute.get_cards_in(
        f'player {winning_player + 1} tricks')) == tute.num_players


def test_game():
    """Test that all the cards end up in tricks at the end of a game.
    """

    def _test_game(num_players, habanero):
        tute = Tute(num_players=num_players, habanero=habanero)
        tute.deal()

        player = 0
        while len(tute.get_hand(player)) > 0:
            winning_player = tute.play_turn(player=player,
                                            choose_card=choose_card)
            if winning_player is not None:
                player = winning_player
            else:
                player = (player + 1) % tute.num_players
        for player in range(tute.num_players):
            tute.calc_points(player)

        num_cards_in_tricks = 0
        for player in range(tute.num_players):
            num_cards_in_tricks += len(
                tute.get_cards_in(f'player {player + 1} tricks'))
        assert num_cards_in_tricks == len(tute.deck)

    for _ in range(10):
        _test_game(num_players=2, habanero=True)
        for num_players in range(2, 5):
            _test_game(num_players=num_players, habanero=False)


def test_rlcard():
    """Test RLCard
    """
    env = make('tute')
    agent = RandomAgent(num_actions=env.num_actions)
    env.set_agents([agent for _ in range(env.num_players)])
    env.run(is_training=False)
