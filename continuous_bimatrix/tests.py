# -*- coding: utf-8 -*-
from __future__ import division

import random

from django.test import TestCase
from otree.common import Currency as c, currency_range
from selenium import webdriver

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
        pass


class WebcomponentTest(TestCase):

	def test_app_load(self):
		driver = webdriver.Chrome()
		driver.get('http://localhost:8000')
		assert 'oTree' in driver.title
		driver.close()