# -*- coding: utf-8 -*-
from __future__ import division

from django.contrib.contenttypes.models import ContentType
from otree.constants import BaseConstants
from otree.models import BasePlayer, BaseSubsession

from otree_redwood.models import Event, DiscreteDecisionGroup

doc = """
This is a discrete time/continuous space bimatrix game.
Two players can simultaneously choose a mixed strategy for the bimatrix game
defined by the "payoff_matrix" variable below. They can change their choice at
any time but that change is only  reflected on their counterpart's page at the
start of the next subperiod. Payoff is determined by the integrating the
subperiod payoffs over time (i.e the longer you are at a payoff spot, the more
it contributes to your final payoff).
"""


class Constants(BaseConstants):
    name_in_url = 'discrete_bimatrix'
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

    seconds_per_tick = 10


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

    def seconds_per_tick(self):
        return Constants.seconds_per_tick


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

        try:
            period_start = Event.objects.get(
                    channel='state',
                    content_type=ContentType.objects.get_for_model(self.group),
                    group_pk=self.group.pk,
                    value='period_start')
            period_end = Event.objects.get(
                    channel='state',
                    content_type=ContentType.objects.get_for_model(self.group),
                    group_pk=self.group.pk,
                    value='period_end')
        except Event.DoesNotExist:
            return float('nan')

        payoff_matrix = self.subsession.get_cur_payoffs()

        self.payoff = self.get_payoff(period_start, period_end, group_decisions, payoff_matrix)
        

    def get_payoff(self, period_start, period_end, group_decisions, payoff_matrix):
        period_duration = period_end.timestamp - period_start.timestamp

        payoff = 0

        if self.id_in_group == 1:
            A_a_payoff = payoff_matrix[0][0]
            A_b_payoff = payoff_matrix[1][0]
            B_a_payoff = payoff_matrix[2][0]
            B_b_payoff = payoff_matrix[3][0]
            row_player = self.participant
        else:
            A_a_payoff = payoff_matrix[0][1]
            A_b_payoff = payoff_matrix[1][1]
            B_a_payoff = payoff_matrix[2][1]
            B_b_payoff = payoff_matrix[3][1]
            row_player = self.get_others_in_group()[0].participant

        for decisions in group_decisions:
            my_decision = decisions.value[self.participant.code]
            other_decision = decisions.value[self.get_others_in_group()[0]]
            if self.id_in_group == 1:
                q1, q2 = my_decision, other_decision
            else:
                q1, q2 = other_decision, my_decision
            subperiod_payoff = ((A_a_payoff * q1 * q2) +
                                (A_b_payoff * q1 * (1 - q2)) +
                                (B_a_payoff * (1 - q1) * q2) +
                                (B_b_payoff * (1 - q1) * (1 - q2)))

            payoff += subperiod_payoff

        return payoff / period_duration.total_seconds()
