# -*- coding: utf-8 -*-
from __future__ import division

from django.contrib.contenttypes.models import ContentType
from otree.constants import BaseConstants
from otree.models import BasePlayer, BaseSubsession

from otree_redwood.models import Event, DiscreteDecisionGroup

doc = """
This is a discrete time/continuous space bimatrix game.
Two players can simultaneously choose a mixed strategy for the bimatrix game
defined by the "payoff_matrices" variable below. They can change their choice at
any time but that change is only  reflected on their counterpart's page at the
start of the next subperiod. Payoff is determined by the integrating the
subperiod payoffs over time (i.e the longer you are at a payoff spot, the more
it contributes to your final payoff).
"""


class Constants(BaseConstants):
    name_in_url = 'discrete_time_bimatrix'
    players_per_group = 2
    num_rounds = 12

    payoff_matrices = [
        [
            [800, 0], [0, 200],
            [0, 200], [200, 0],
        ],
        [
            [500, 100], [0, 200],
            [0, 200], [300, 0],
        ],
        [
            [300, 300], [0, 800],
            [800, 0], [100, 100],
        ],
        [
            [300, 400], [100, 0],
            [0, 100], [400, 300],
        ]
    ]

    base_points = 0

    # Amount of time the game stays on the decision page in seconds.
    period_length = 120

    num_subperiods = 12


class Subsession(BaseSubsession):
    def before_session_starts(self):
        self.group_randomly()

    def get_cur_payoffs(self):
        roundno = self.round_number

        if roundno in [1, 2, 3]:
            return Constants.payoff_matrices[2]
        elif roundno in [4, 5, 6]:
            return Constants.payoff_matrices[3]
        elif roundno in [7, 8, 9]:
            return Constants.payoff_matrices[0]
        elif roundno in [10, 11, 12]:
            return Constants.payoff_matrices[1]
        else:
            print("invalid round number!")


class Group(DiscreteDecisionGroup):

    def period_length(self):
        return Constants.period_length

    def num_subperiods(self):
        return Constants.num_subperiods


class Player(BasePlayer):

    def initial_decision(self):
        return 0.5

    def other_player(self):
        return self.get_others_in_group()[0]

    def set_payoff(self):
        group_decisions = list(Event.objects.filter(
                channel='group_decisions',
                content_type=ContentType.objects.get_for_model(self.group),
                group_pk=self.group.pk).order_by("timestamp"))

        payoff_matrix = self.subsession.get_cur_payoffs()

        self.payoff = self.get_payoff(group_decisions, payoff_matrix)
        

    def get_payoff(self, group_decisions, payoff_matrix):

        payoff = 0

        Aa = payoff_matrix[0][self.id_in_group-1]
        Ab = payoff_matrix[1][self.id_in_group-1]
        Ba = payoff_matrix[2][self.id_in_group-1]
        Bb = payoff_matrix[3][self.id_in_group-1]
        
        if self.id_in_group == 1:
            row_player = self.participant
        else:
            row_player = self.other_player().participant

        for decisions in group_decisions:
            my_decision = decisions.value[self.participant.code]
            other_decision = decisions.value[self.other_player().participant.code]
            if self.id_in_group == 1:
                q1, q2 = my_decision, other_decision
            else:
                q1, q2 = other_decision, my_decision
            subperiod_payoff = ((Aa * q1 * q2) +
                                (Ab * q1 * (1 - q2)) +
                                (Ba * (1 - q1) * q2) +
                                (Bb * (1 - q1) * (1 - q2)))

            payoff += subperiod_payoff

        return payoff / len(group_decisions) if group_decisions else 0
