# Real-Time Data Distribution With Firebase

## Decisions

Components can write to a decisions path in Firebase. The path has the form:
`/session/<session>/app/<app>/subsession/<subsession>/round/<round>/group/<group>/component/<component>/decisions/<participant_code>`.
In other words, there is one decision object per group per round. Components can watch the decision object for
the entire group to view other group members decisions - their decision will be shared with the group.

### Example Decision object:

```
/session/pxru0609/app/continuous_bimatrix/subsession/1/round/1/group/1/component/otree-bimatrix/decisions
{
  "kghjoic3": 0.52,
  "wev5qi5u": 0.38
}
```

Note that the participant code is used - each participant can refer to their unique decision variable,
and decisions are trackable across a given session.

## Decision logging

Decisions are logged as an event to the oTree SQL database. The oTree server watches Firebase for changes
and logs each change as a Decision model. The Decision model only stores a single participant's decision,
i.e. one key/value pair of the example above.

### Example Query:

The continous_bimatrix app computes an interval over time using the players decisions and a payoff matrix.
To do this, it first get the decisions over time for a given group:

```python
class Player(BasePlayer):

  def set_payoff(self):
    decisions_over_time = Decision.objects.filter(
      component='otree-bimatrix',
      session=self.session.code,
      subsession=self.subsession.name(),
      round=self.round_number,
      group=self.group.id_in_subsession)
    
    # At some time t1, the participant kghjoic3 set their decision as 0.52
    decisions_over_time[10].timestamp = <t1>
    decisions_over_time[10].participant.code == "kghjoic3"
    decisions_over_time[10].value == 0.52
    
    # Later, at t2 > t1, the participant wev5qi5u set their decision as 0.38
    decisions_over_time[11].timestamp = <t2>
    decisions_over_time[11].participant.code == "wev5qi5u"
    decisions_over_time[11].value == 0.38
```

## Initial Decisions

The `WaitPage` before the Decision component is loaded MUST create "bookends" for the round.
The bookends consist of an initial Decision logged at the start of the round and a final
Decision logged at the end of the round. This ensures the Decision table has complete
information about the round length. The `WaitPage` can use the inherited function
`log_decision_bookends(<start_time>, <end_time>, <app>, <component>, <initial_decision>)` to do so.

For example:

```python
class DecisionWaitPage(WaitPage):
  body_text = 'Waiting for all players to be ready'

  def after_all_players_arrive(self):
    # calculate start and end times for the period
    start_time = timezone.now()
    end_time = start_time + timedelta(seconds=Constants.period_length)
    self.log_decision_bookends(start_time, end_time, 'continuous_bimatrix', 'otree-bimatrix', -1)

class Decision(Page):
  timeout_seconds = Constants.period_length

# This ensures that:

decisions_over_time[0].timestamp = start_time
decisions_over_time[0].participant.code == <some participant>
decisions_over_time[0].value == -1

decisions_over_time[-1].timestamp = end_time
decisions_over_time[-1].participant.code == <some participant>
decisions_over_time[-1].value == -1
```

## Discrete-Time Subperiods (In Progress)

Subperiods split the round into discrete intervals of time. The oTree server writes to a Firebase path of the form
`/session/<session>/app/<app>/subsession/<subsession>/round/<round>/group/<group>/subperiods`. Components can listen
to this path to get updates on the decisions a subject "locked-in" at the end of the sub-period. The subperiods object
is an array, with each value being the last decision seen by the server at the end of the sub-period.

For example:
```
/session/pxru0609/app/continuous_bimatrix/subsession/1/round/1/group/1/subperiods
[
  {
    "timestamp": 1488489557696,
    "components": {
      "otree-bimatrix": {
        "kghjoic3": 0.75,
        "wev5qi5u": 0.1 
      }
    }
  }
  ...
]
```

Note that the subperiod has a namespace for the component, so multiple components can be used on the same page. It is up
to the component to track writing to the `decisions` path and watching the `subperiods` path for the locked-in decision.

## Server-Sent Variables (Rough Draft)

* Server can watch Firebase decisions.
* Server can publish changes to variables on a path that clients can watch.
