# -*- coding: utf-8 -*-
from __future__ import division
from . import models
from ._builtin import Page, WaitPage
from otree.common import Currency as c, currency_range
from .models import Constants
import otree_redwood.abstract_views as redwood_views

from django.utils import timezone
from datetime import timedelta
import json
import logging

class Introduction(Page):
    timeout_seconds = 100

    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        payoff_grid = self.subsession.get_cur_payoffs()
        if (self.player.id_in_group == 1):
            return {
                "my_A_A_payoff": payoff_grid[0][0],
                "my_A_B_payoff": payoff_grid[1][0],
                "my_B_A_payoff": payoff_grid[2][0],
                "my_B_B_payoff": payoff_grid[3][0],
                "other_A_A_payoff": payoff_grid[0][1],
                "other_A_B_payoff": payoff_grid[1][1],
                "other_B_A_payoff": payoff_grid[2][1],
                "other_B_B_payoff": payoff_grid[3][1],
                "total_q": 1
            }
        else:
            return {
                "my_A_A_payoff": payoff_grid[0][1],
                "my_A_B_payoff": payoff_grid[1][1],
                "my_B_A_payoff": payoff_grid[2][1],
                "my_B_B_payoff": payoff_grid[3][1],
                "other_A_A_payoff": payoff_grid[0][0],
                "other_A_B_payoff": payoff_grid[1][0],
                "other_B_A_payoff": payoff_grid[2][0],
                "other_B_B_payoff": payoff_grid[3][0],
                "total_q": 1
            }


class DecisionWaitPage(WaitPage):
    body_text = 'Waiting for all players to be ready'


class Decision(redwood_views.Page):
    timeout_seconds = Constants.period_length + 10

    def when_all_players_ready(self):
        # calculate start and end times for the period
        start_time = timezone.now()
        end_time = start_time + timedelta(seconds=Constants.period_length)

        self.log_decision_bookends(
            start_time, end_time, -1)
        self.start_period_timer(Constants.period_length)

    def vars_for_template(self):
        payoff_grid = self.subsession.get_cur_payoffs()
        if (self.player.id_in_group == 1):
            return {
                "my_A_A_payoff": payoff_grid[0][0],
                "my_A_B_payoff": payoff_grid[1][0],
                "my_B_A_payoff": payoff_grid[2][0],
                "my_B_B_payoff": payoff_grid[3][0],
                "other_A_A_payoff": payoff_grid[0][1],
                "other_A_B_payoff": payoff_grid[1][1],
                "other_B_A_payoff": payoff_grid[2][1],
                "other_B_B_payoff": payoff_grid[3][1],
                "total_q": 1,
                'payoff_matrix': payoff_grid
            }
        else:
            return {
                "my_A_A_payoff": payoff_grid[0][1],
                "my_A_B_payoff": payoff_grid[1][1],
                "my_B_A_payoff": payoff_grid[2][1],
                "my_B_B_payoff": payoff_grid[3][1],
                "other_A_A_payoff": payoff_grid[0][0],
                "other_A_B_payoff": payoff_grid[1][0],
                "other_B_A_payoff": payoff_grid[2][0],
                "other_B_B_payoff": payoff_grid[3][0],
                "total_q": 1,
                'payoff_matrix': payoff_grid
            }


class Results(Page):

    def vars_for_template(self):
        self.player.set_payoff()

        return {
            'decisions_over_time': self.player.decisions_over_time,
            'total_plus_base': self.player.payoff + Constants.base_points
        }


page_sequence = [
        Introduction,
        DecisionWaitPage,
        Decision,
        Results
    ]
