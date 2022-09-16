"""TuteHumanAgent module
"""


class TuteHumanAgent(object):
    """A human agent for Tute. It can be used to play against trained models.
    """

    def __init__(self, player, tute):
        """Initilize the human agent.

        Args:
            num_actions (int): the size of the ouput action space
        """
        self.use_raw = False

        self.player = player
        self.tute = tute

    def step(self, state):
        """Human agent will display the state and make decisions through interfaces.

        Args:
            state (dict): A dictionary that represents the current state

        Returns:
            action (int): The action decided by human
        """
        messages = self.tute.retreive_messages()
        if len(messages) > 0:
            self.tute.show_messages(messages)
            print()

        trump = self.tute.get_cards_in('trump')
        if len(trump) > 0:
            print('\n================= Trump =================')
            self.tute.show_cards(trump)
            print()

        face_up = self.tute.get_face_up()
        if len(face_up) > 0:
            print('\n================ Face up ================')
            self.tute.show_cards(face_up)
            print()

        if self.tute.get_follow_suit():
            print('Follow suit')
            print()

        print('\n=============== Your Hand ===============')
        hand = self.tute.get_hand(self.player)
        possible_cards = [
            index for index, card in enumerate(hand.T.iteritems())
            if card[1].name in state['raw_legal_actions']
        ]
        card = self.tute.choose_card(self.tute, hand, possible_cards)
        print()

        return card.name

    def eval_step(self, state):
        """Predict the action given the curent state for evaluation. The same to step here.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
        """
        return self.step(state), {}
