# -*- coding: utf-8 -*-
from __future__ import division

import asyncio
import random
import time

from django.test import TestCase
from otree.api import Bot, Submission
from otree.common import Currency as c, currency_range
from selenium import webdriver

from .models import Constants
from . import views


class PlayerBot(Bot):

    def play_round(self):
        if self.player.round_number == 1:
            yield views.Introduction
        yield Submission(views.Decision, {}, check_html=False)
        yield views.Results


    def validate_play(self):
        assert self.payoff > 0