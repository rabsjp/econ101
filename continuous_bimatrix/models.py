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
This is a one-shot "Prisoner's Dilemma". Two players are asked separately
whether they want to cooperate or defect. Their choices directly determine the
payoffs.
"""


class Constants(BaseConstants):
    name_in_url = 'continuous_bimatrix'
    players_per_group = 2
    num_rounds = 10

    #p1 payoffs
    p1_A_p2_A_amount = 800
    p1_A_p2_B_amount = 0
    p1_B_p2_A_amount = 0
    p1_B_p2_B_amount = 200

    #p2 payoffs
    p2_A_p1_A_amount = 0
    p2_A_p1_B_amount = 200
    p2_B_p1_A_amount = 200
    p2_B_p1_B_amount = 0

    base_points = 0

    # Amount of time the game stays on the decision page in seconds.
    period_length = 120


class Subsession(BaseSubsession):
    def before_session_starts(self):
        self.group_randomly()


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    def other_player(self):
        return self.get_others_in_group()[0]

    def set_payoff(self):
        self.decisions_over_time = Decision.objects.filter(
                component='otree-bimatrix',
                session=self.session,
                subsession=self.subsession.name(),
                round=self.round_number,
                group=self.group.id_in_subsession)

        payoff = 0

        # default state when no decisions have been made
        my_state = .5
        other_state = .5

        if (self.id_in_group == 1):
            A_A_payoff = Constants.p1_A_p2_A_amount
            A_B_payoff = Constants.p1_A_p2_B_amount
            B_A_payoff = Constants.p1_B_p2_A_amount
            B_B_payoff = Constants.p1_B_p2_B_amount
        else:
            A_A_payoff = Constants.p2_A_p1_A_amount
            A_B_payoff = Constants.p2_A_p1_B_amount
            B_A_payoff = Constants.p2_B_p1_A_amount
            B_B_payoff = Constants.p2_B_p1_B_amount

        cur_payoff = (A_A_payoff + A_B_payoff + B_A_payoff + B_B_payoff) * .25 / Constants.period_length
        if (len(self.decisions_over_time) > 0):
            next_change_time = self.decisions_over_time[0].timestamp
        else:
            next_change_time = self.session.vars['end_time_{}'.format(self.group.id_in_subsession)]
        payoff += (next_change_time - self.session.vars['start_time_{}'.format(self.group.id_in_subsession)]).total_seconds() * cur_payoff

        for i, change in enumerate(self.decisions_over_time):
            if change.participant == self.participant:
                my_state = change.value
            else:
                other_state = change.value

            cur_payoff = ((A_A_payoff * my_state * other_state) +
                          (A_B_payoff * my_state * (1 - other_state)) +
                          (B_A_payoff * (1 - my_state) * other_state) +
                          (B_B_payoff * (1 - my_state) * (1 - other_state))) / Constants.period_length

            if i == len(self.decisions_over_time) - 1:
                next_change_time = self.session.vars['end_time_{}'.format(self.group.id_in_subsession)]
            else:
                next_change_time = self.decisions_over_time[i + 1].timestamp

            payoff += (next_change_time - change.timestamp).total_seconds() * cur_payoff

        self.payoff = payoff
