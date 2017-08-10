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
    num_rounds = 10

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
            [100, 0], [0, 200],
            [200, 100], [50, 0],
        ],
        [
            [300, 200], [100, 100],
            [100, 150], [150, 350],
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
            return Constants.payoff_grids[0]
        elif roundno in [4, 5, 6]:
            return Constants.payoff_grids[1]
        elif roundno in [7, 8]:
            return Constants.payoff_grids[2]
        elif roundno in [9, 10]:
            return Constants.payoff_grids[3]
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
        group_decisions = list(Event.objects.filter(
                channel='group_decisions',
                content_type=ContentType.objects.get_for_model(self.group),
                group_pk=self.group.pk).order_by("timestamp"))

        period_start = Event.objects.get(
                channel='state',
                content_type=ContentType.objects.get_for_model(self.group),
                group_pk=self.group.pk,
                value='period_start')

        try:
            period_end = Event.objects.get(
                    channel='state',
                    content_type=ContentType.objects.get_for_model(self.group),
                    group_pk=self.group.pk,
                    value='period_end')
        except Event.DoesNotExist:
            raise Exception(list(Event.objects.filter(
                    channel='state',
                    content_type=ContentType.objects.get_for_model(self.group),
                    group_pk=self.group.pk)))

        period_duration = period_end.timestamp - period_start.timestamp

        payoff = 0

        payoff_grid = self.subsession.get_cur_payoffs()

        if (self.id_in_group == 1):
            A_A_payoff = payoff_grid[0][0]
            A_B_payoff = payoff_grid[1][0]
            B_A_payoff = payoff_grid[2][0]
            B_B_payoff = payoff_grid[3][0]
        else:
            A_A_payoff = payoff_grid[0][1]
            A_B_payoff = payoff_grid[1][1]
            B_A_payoff = payoff_grid[2][1]
            B_B_payoff = payoff_grid[3][1]

        my_state = None
        other_state = None
        for i, d in enumerate(group_decisions):
            my_state = d.value[self.participant.code]
            other_state = d.value[self.get_others_in_group()[0].participant.code]

            cur_payoff = ((A_A_payoff * my_state * other_state) +
                          (A_B_payoff * my_state * (1 - other_state)) +
                          (B_A_payoff * (1 - my_state) * other_state) +
                          (B_B_payoff * (1 - my_state) * (1 - other_state))) / period_duration.total_seconds()

            if i + 1 < len(group_decisions):
                next_change_time = group_decisions[i + 1].timestamp
            else:
                next_change_time = period_end.timestamp
            payoff += (next_change_time - d.timestamp).total_seconds() * cur_payoff

        self.payoff = payoff
