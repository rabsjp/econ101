# -*- coding: utf-8 -*-
from __future__ import division

from django.contrib.contenttypes.models import ContentType
from otree.constants import BaseConstants
from otree.models import BasePlayer, BaseSubsession

from otree_redwood.models import Event, ContinuousDecisionGroup

doc = """
This is a continuous time/continuous space bimatrix game.
Two players can simultaneously choose a mixed strategy for the bimatrix game
defined by the "payoff_grid" variable below. They can change their choice at
any time and that change will be reflected on their counterpart's page. Payoff
is determined by the integrating the instantaneous flow payoffs over time (i.e
the longer you are at a payoff spot, the more it contributes to your final
payoff).
"""


class Constants(BaseConstants):
    name_in_url = 'continuous_bimatrix'
    players_per_group = 2
    num_rounds = 12

    #payoff grids
    payoff_grids = [
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


class Subsession(BaseSubsession):
    def before_session_starts(self):
        self.group_randomly()

    def get_cur_payoffs(self):
        roundno = self.round_number

        if roundno in [1, 2, 3]:
            return Constants.payoff_grids[2]
        elif roundno in [4, 5, 6]:
            return Constants.payoff_grids[3]
        elif roundno in [7, 8, 9]:
            return Constants.payoff_grids[0]
        elif roundno in [10, 11, 12]:
            return Constants.payoff_grids[1]
        else:
            print("invalid round number!")


class Group(ContinuousDecisionGroup):

    def period_length(self):
        return Constants.period_length

    def initial_decision(self):
        return 0.5


class Player(BasePlayer):

    def other_player(self):
        return self.get_others_in_group()[0]

    def set_payoff(self):
        decisions = list(Event.objects.filter(
                channel='decisions',
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

        payoff_grid = self.subsession.get_cur_payoffs()

        self.payoff = self.get_payoff(period_start, period_end, decisions, payoff_grid)
        

    def get_payoff(self, period_start, period_end, decisions, payoff_grid):
        period_duration = period_end.timestamp - period_start.timestamp

        payoff = 0

        if (self.id_in_group == 1):
            A_a_payoff = payoff_grid[0][0]
            A_b_payoff = payoff_grid[1][0]
            B_a_payoff = payoff_grid[2][0]
            B_b_payoff = payoff_grid[3][0]
            row_player = self.participant
        else:
            A_a_payoff = payoff_grid[0][1]
            A_b_payoff = payoff_grid[1][1]
            B_a_payoff = payoff_grid[2][1]
            B_b_payoff = payoff_grid[3][1]
            row_player = self.get_others_in_group()[0].participant

        q1, q2 = self.group.initial_decision(), self.group.initial_decision()
        for i, d in enumerate(decisions):
            if d.participant == row_player:
                q1 = d.value
            else:
                q2 = d.value
            flow_payoff = ((A_a_payoff * q1 * q2) +
                          (A_b_payoff * q1 * (1 - q2)) +
                          (B_a_payoff * (1 - q1) * q2) +
                          (B_b_payoff * (1 - q1) * (1 - q2)))

            if i + 1 < len(decisions):
                next_change_time = decisions[i + 1].timestamp
            else:
                next_change_time = period_end.timestamp
            payoff += (next_change_time - d.timestamp).total_seconds() * flow_payoff

        return payoff / period_duration.total_seconds()
