# -*- coding: utf-8 -*-
# <standard imports>
from __future__ import division
from otree.db import models
from otree.constants import BaseConstants
from otree.models import BaseSubsession, BaseGroup, BasePlayer, Decision

from otree import widgets
from otree.common import Currency as c, currency_range

import random
# </standard imports>

doc = """
This is a discrete time example game. Players are given two choices,
'A' or 'B'. Choices are distributed every N seconds, so players have
a "sub-period" of time to digest the results and strategize.
"""


class Constants(BaseConstants):
    name_in_url = 'discrete_time_example'
    players_per_group = 2
    num_rounds = 10

    # p1 payoffs
    p1_A_p2_A_amount = 800
    p1_A_p2_B_amount = 0
    p1_B_p2_A_amount = 0
    p1_B_p2_B_amount = 200

    # p2 payoffs
    p2_A_p1_A_amount = 0
    p2_A_p1_B_amount = 200
    p2_B_p1_A_amount = 200
    p2_B_p1_B_amount = 0

    base_points = 0

    # Amount of time the game stays on the decision page in seconds
    period_length = 100 
    # Number of discrete time subperiods in a single period.
    num_subperiods = 10

    training_1_choices = [
        'Alice gets 300 points, Bob gets 0 points',
        'Alice gets 200 points, Bob gets 200 points',
        'Alice gets 0 points, Bob gets 300 points',
        'Alice gets 100 points, Bob gets 100 points'
    ]

    training_1_correct = training_1_choices[0]


class Subsession(BaseSubsession):
    def before_session_starts(self):
        self.group_randomly()


class Group(BaseGroup):
    pass

class Player(BasePlayer):

    def is_training_question_1_correct(self):
        return self.training_question_1 == Constants.training_1_correct

    def other_player(self):
        return self.get_others_in_group()[0]

    def set_payoff(self):
        # TODO
        self.payoff = 0

