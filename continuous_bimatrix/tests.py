# -*- coding: utf-8 -*-
from __future__ import division

import random

from django.test import TestCase
from otree.common import Currency as c, currency_range
from otree_redwood.models import Decision

from ._builtin import Bot
from .models import Constants
from . import views


class PlayerBot(Bot):

    def play_round(self):
        pass

    def validate_play(self):
        pass


class PayoffFunctionTestCase(TestCase):

    def test_payoff_function(self):
        self.assertEqual(True, False)