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
    num_rounds = 1

    #p1 payoffs
    #p1_A_p2_A_amount = 8
    #p1_A_p2_B_amount = 0
    #p1_B_p2_A_amount = 0
    #p1_B_p2_B_amount = 2

    #p2 payoffs
    #p2_A_p1_A_amount = 2
    #p2_A_p1_B_amount = 2
    #p2_B_p1_A_amount = 2
    #p2_B_p1_B_amount = 0

    #  Points made if player defects and the other cooperates""",
    #defect_cooperate_amount = 300

    # Points made if both players cooperate
    #cooperate_amount = 200
    #cooperate_defect_amount = 0
    #defect_amount = 100
    base_points = 50


    # Amount of time the game stays on the decision page in seconds
    game_length = 120

    training_1_choices = [
        'Alice gets 300 points, Bob gets 0 points',
        'Alice gets 200 points, Bob gets 200 points',
        'Alice gets 0 points, Bob gets 300 points',
        'Alice gets 100 points, Bob gets 100 points'
    ]

    training_1_correct = training_1_choices[0]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    training_question_1 = models.CharField(
        choices=Constants.training_1_choices,
        widget=widgets.RadioSelect(),
        #timeout_default=Constants.training_1_choices[1]
    )

    def is_training_question_1_correct(self):
        return self.training_question_1 == Constants.training_1_correct

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

        # add payoff for portion of game before any decisions were made
        cur_payoff = (Constants.cooperate_amount + Constants.cooperate_defect_amount + Constants.defect_cooperate_amount + Constants.defect_amount) * .25 / Constants.game_length
        next_change_time = self.session.vars['end_time']
        if (len(self.decisions_over_time) > 0):
            next_change_time = self.decisions_over_time[0].timestamp
        payoff += (next_change_time - self.session.vars['start_time']).total_seconds() * cur_payoff

        for i, change in enumerate(self.decisions_over_time):
            if change.participant == self.participant:
                my_state = change.decision
            else:
                other_state = change.decision

            cur_payoff = ((Constants.cooperate_amount * my_state * other_state) +
                          (Constants.cooperate_defect_amount * my_state * (1 - other_state)) +
                          (Constants.defect_cooperate_amount * (1 - my_state) * other_state) +
                          (Constants.defect_amount * (1 - my_state) * (1 - other_state))) / Constants.game_length

            if i == len(self.decisions_over_time) - 1:
                next_change_time = self.session.vars['end_time']
            else:
                next_change_time = self.decisions_over_time[i + 1].timestamp

                payoff += (next_change_time - change.timestamp).total_seconds() * cur_payoff

        self.payoff = payoff
