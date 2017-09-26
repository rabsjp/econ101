from collections import namedtuple
from otree.api import Bot, Submission
from . import views


class PlayerBot(Bot):

    def play_round(self):
        if self.player.round_number == 1:
            yield views.Introduction
        test_get_payoff()
        yield Submission(views.Decision, {}, check_html=False)
        yield views.Results


    def validate_play(self):
        assert self.payoff == 0


def test_get_payoff():
    '''
        Test the get_payoff function for the Player model.

        Initializes a session, participants, etc, then creates mock events.
    '''
    from otree_redwood.models import Event
    from otree.models.participant import Participant
    from otree.models.session import Session
    import random
    from django.utils import timezone
    from . import models

    sess = Session.objects.create(code=str(random.randint(0, 500000)))
    p1 = Participant.objects.create(session=sess, code='test_p1_'+str(random.randint(0, 500000)))
    p2 = Participant.objects.create(session=sess, code='test_p2_'+str(random.randint(0, 500000)))
    start = timezone.now()

    MockEvent = namedtuple('Event', ['channel', 'value', 'participant', 'timestamp'])
    group_decisions = []

    group_decisions.append(MockEvent('group_decisions', {
        p1.code: 0.2,
        p2.code: 0.5,
    }, None, start+timezone.timedelta(seconds=10)))

    group_decisions.append(MockEvent('group_decisions', {
        p1.code: 0.3,
        p2.code: 0.8,
    }, None, start+timezone.timedelta(seconds=20)))

    group_decisions.append(MockEvent('group_decisions', {
        p1.code: 0.1,
        p2.code: 0.4,
    }, None, start+timezone.timedelta(seconds=20)))

    group_decisions.append(MockEvent('group_decisions', {
        p1.code: 0.8,
        p2.code: 0.1,
    }, None, start+timezone.timedelta(seconds=20)))
 
    payoff_grid = [
        [ 100, 100 ], [   0, 800 ],
        [ 800,   0 ], [ 300, 300 ]
    ]

    subsession = models.Subsession.objects.create(session=sess, round_number=1)
    player1 = models.Player.objects.create(session=sess, subsession=subsession, participant=p1, id_in_group=1)
    player2 = models.Player.objects.create(session=sess, subsession=subsession, participant=p2, id_in_group=2)
    group = models.Group.objects.create(session=sess, subsession=subsession)
    # player_set isn't part of the group model, not actually sure how it's assigned in oTree
    # but it's required to tell row players and column players apart.
    group.player_set = { player1, player2 }
    player1.group, player2.group = group, group

    payoff1 = player1.get_payoff(group_decisions, payoff_grid)
    payoff2 = player2.get_payoff(group_decisions, payoff_grid)

    assert 0 <= payoff1 and payoff1 <= 800
    assert 0 <= payoff2 and payoff2 <= 800
    assert abs(payoff1 - 374) < 1
    assert abs(payoff2 - 294) < 1