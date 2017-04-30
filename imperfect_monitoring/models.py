# -*- coding: utf-8 -*-
from __future__ import division
from datetime import timedelta
import random

from otree.db import models
from otree.constants import BaseConstants
from otree.models import BaseSubsession, BaseGroup, BasePlayer

from otree import widgets
from otree.common import Currency as c, currency_range

from otree_redwood.models import Event, RanPlayersReadyFunction

doc = """
This is a Prisoner's Dilemna game with discrete time. Players are given two choices,
'Cooperate' or 'Don't Cooperate. Choices are distributed every N seconds, so players have
a "sub-period" of time to digest the results and strategize.
"""


class Constants(BaseConstants):
    name_in_url = 'imperfect_monitoring'
    players_per_group = 2
    num_rounds = 10

    #p1 payoffs
    p1_A_p2_A_amount = 100
    p1_A_p2_B_amount = 0
    p1_B_p2_A_amount = 125
    p1_B_p2_B_amount = 25

    #p2 payoffs
    p2_A_p1_A_amount = 100
    p2_A_p1_B_amount = 0
    p2_B_p1_A_amount = 125
    p2_B_p1_B_amount = 25

    #p1 signals
    p1_A_p2_A_signal = .4
    p1_A_p2_B_signal = .6
    p1_B_p2_A_signal = .6
    p1_B_p2_B_signal = .8

    #p2 signals
    p2_A_p1_A_signal = .4
    p2_A_p1_B_signal = .6
    p2_B_p1_A_signal = .6
    p2_B_p1_B_signal = .8

    base_points = 0

    # Amount of time the game stays on the decision page in seconds.
    period_length = 100

    # Number of discrete time subperiods in a single period.
 #   num_periods = 10

class Subsession(BaseSubsession):
    def before_session_starts(self):
        self.group_randomly()


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    def other_player(self):
        return self.get_others_in_group()[0]

    def set_payoff(self):
        # TODO
        self.payoff = 0
