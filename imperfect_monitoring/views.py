# -*- coding: utf-8 -*-
from __future__ import division
from . import models
from ._builtin import Page, WaitPage
from otree.common import Currency as c, currency_range
from .models import Constants
import otree_redwood.abstract_views as redwood_views
from otree_redwood import consumers
from otree_redwood.models import Event

from django.utils import timezone
import logging
import random

def vars_for_all_templates(self):
    if (self.player.id_in_group == 1):
        return {
            "my_A_A_payoff": Constants.p1_A_p2_A_amount,
            "my_A_B_payoff": Constants.p1_A_p2_B_amount,
            "my_B_A_payoff": Constants.p1_B_p2_A_amount,
            "my_B_B_payoff": Constants.p1_B_p2_B_amount,
            "other_A_A_payoff": Constants.p2_A_p1_A_amount,
            "other_A_B_payoff": Constants.p2_A_p1_B_amount,
            "other_B_A_payoff": Constants.p2_B_p1_A_amount,
            "other_B_B_payoff": Constants.p2_B_p1_B_amount,
            "total_q": 1
        }
    else:
        return {
            "my_A_A_payoff": Constants.p2_A_p1_A_amount,
            "my_A_B_payoff": Constants.p2_A_p1_B_amount,
            "my_B_A_payoff": Constants.p2_B_p1_A_amount,
            "my_B_B_payoff": Constants.p2_B_p1_B_amount,
            "other_A_A_payoff": Constants.p1_A_p2_A_amount,
            "other_A_B_payoff": Constants.p1_A_p2_B_amount,
            "other_B_A_payoff": Constants.p1_B_p2_A_amount,
            "other_B_B_payoff": Constants.p1_B_p2_B_amount,
            "total_q": 1
        }


class Introduction(Page):
    timeout_seconds = 100

    def is_displayed(self):
        return self.round_number == 1


class DecisionWaitPage(WaitPage):
    body_text = 'Waiting for all players to be ready'


class Decision(redwood_views.ContinuousDecisionPage):
    initial_decision = 0
    
    def __init__(self, *args, **kwargs):
        self.period_length = Constants.num_subperiods * Constants.subperiod_length
        super().__init__(*args, **kwargs)
        self.fixedGroupDecisions = None

    def when_all_players_ready(self):
        super().when_all_players_ready()

        self.state = 'results'
        self.t = 0

        emitter = redwood_views.DiscreteEventEmitter(1, self.period_length, self.group, self.tick)
        emitter.start()

    def tick(self, current_interval, intervals, group):
        msg = {}
        if self.state == 'results':
            msg = {
                'realizedPayoff': self.realizedPayoff()
            }
        elif self.state == 'pause':
            if self.t == 6:
                msg = {
                    'updateStrategy': True,
                    'pauseProgress': 1/6.
                }
            else:
                msg = {
                    'pauseProgress': (self.t-5)/6.
                }
                if self.t == 11:
                    msg['clearGraph'] = True
        else:
            raise ValueError('invalid state {}'.format(self.state))

        consumers.send(self.group, 'tick', msg)

        self.t += 1
        if self.t == 6:
            self.state = 'pause'
        if self.t == 12:
            self.state = 'results'
            self.t = 0
            self.fixedGroupDecisions = dict(self.group_decisions)


    def realizedPayoff(self):
        choices = [Constants.p1_A_p2_A_amount, Constants.p1_A_p2_B_amount, Constants.p1_B_p2_A_amount, Constants.p1_B_p2_B_amount]
        myDecision, otherDecision = None, None
        if self.fixedGroupDecisions:
            myDecision = self.fixedGroupDecisions[self.player.participant.code]
            otherDecision = self.fixedGroupDecisions[self.get_partner().participant.code]
        else:
            myDecision = random.choice([0, 1])
            otherDecision = random.choice([0, 1])
        
        return random.choice(choices)


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
