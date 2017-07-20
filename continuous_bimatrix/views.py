# -*- coding: utf-8 -*-
from __future__ import division
from . import models
from ._builtin import Page, WaitPage
from otree.common import Currency as c, currency_range
from .models import Constants
import otree_redwood.abstract_views as redwood_views

from collections import defaultdict
import datetime
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


class Decision(redwood_views.ContinuousDecisionPage):
    period_length = Constants.period_length
    initial_decision = 0.5

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
    timeout_seconds = 30

    def vars_for_template(self):
        self.player.set_payoff()

        return {
            'decisions_over_time': self.player.decisions_over_time,
            'total_plus_base': self.player.payoff + Constants.base_points
        }


def get_output_table(session_events):
    groups = max(e.group for e in session_events)
    rounds = max(e.round for e in session_events)
    events_by_round_then_group = defaultdict(lambda: defaultdict(lambda: []))
    for e in session_events:
        events_by_round_then_group[e.round][e.group].append(e)
    for events_by_group in events_by_round_then_group.values():
        for group_events in events_by_group.values():
            players = set(e.participant.code for e in group_events if e.participant)
            minT = min(e.timestamp for e in group_events)
            maxT = max(e.timestamp for e in group_events)
            for tick in range((maxT - minT).seconds):
                currT = minT + datetime.timedelta(seconds=tick)
                tick_events = []
                while group_events[0].timestamp <= currT:
                    tick_events.append(group_events.pop(0))
                print(tick, len(tick_events))
    raise Exception('not implemented')


page_sequence = [
        Introduction,
        DecisionWaitPage,
        Decision,
        Results
    ]
