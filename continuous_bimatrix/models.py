# -*- coding: utf-8 -*-
from __future__ import division
import random

from otree import widgets
from otree.db import models
from otree.constants import BaseConstants
from otree.common import Currency as c, currency_range
from otree.models import BaseSubsession, BaseGroup, BasePlayer

from otree_redwood.models import Decision

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

    #payoff grid
    payoff_grid = [
        [ 800, 0   ], [ 0,   200 ],
        [ 0,   200 ], [ 200, 0   ],
    ]

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
                group=self.group.id_in_subsession).order_by("timestamp")

        payoff = 0

        # default state when no decisions have been made
        my_state = .5
        other_state = .5

        payoff_grid = Constants.payoff_grid
        
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

        for i, change in enumerate(self.decisions_over_time):
            # skip end dummy decisions
            if change.value is None:
                break

            if change.value == -1:
                # don't change state for front dummy decisions
                pass
            elif change.participant == self.participant:
                my_state = change.value
            else:
                other_state = change.value

            cur_payoff = ((A_A_payoff * my_state * other_state) +
                          (A_B_payoff * my_state * (1 - other_state)) +
                          (B_A_payoff * (1 - my_state) * other_state) +
                          (B_B_payoff * (1 - my_state) * (1 - other_state))) / Constants.period_length

            next_change_time = self.decisions_over_time[i + 1].timestamp
            payoff += (next_change_time - change.timestamp).total_seconds() * cur_payoff

        self.payoff = payoff
