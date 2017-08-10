# -*- coding: utf-8 -*-
from __future__ import division
from ._builtin import Page, WaitPage
from .models import Constants


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


class Decision(Page):
    pass


class Results(Page):

    def vars_for_template(self):
        self.player.set_payoff()

        return {
            'total_plus_base': self.player.payoff + Constants.base_points
        }


def get_output_table(events):
    table = []
    for e in events:
        if e.channel == 'decisions':
            table.append(e.value),
            table.append(e.participant.code) 
        if e.channel == 'tick':
            if 'realizedPayoffs' in e.value:
                table.append(e.value ['realizedPayoffs'])
            if 'fixedDecisions' in e.value:
                table.append(e.value ['fixedDecisions'])
    print(table)
    return table


page_sequence = [
        Introduction,
        DecisionWaitPage,
        Decision,
        Results
    ]
