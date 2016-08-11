import atexit
import fasteners
from firebase_token_generator import create_token
import json
import re
from sseclient import SSEClient
import threading


_FIREBASE_SECRET = 'uXop5iUjKkGfH20sFmdCMenX7QnUWmnWDde76WQR'
_PATH_RE = re.compile('/component/(?P<component>.*)/session/(?P<session>.*)/subsession/(?P<subsession>.*)/round/(?P<round>.*)/group/(?P<group>.*)/decisions/(?P<decisions>.*)')


def watch():
	lock = fasteners.InterProcessLock('/tmp/firewatch_lock_file')
	if not lock.acquire(blocking=False):
		return
	atexit.register(lock.release)
	t = Thread()
	t.daemon = True
	t.start()


class Thread(threading.Thread):

	def __init__(self):
		super(Thread, self).__init__()
		self.token = create_token(_FIREBASE_SECRET, {'uid': '1'})

	def run(self):
		print 'run'
		params = {'auth': self.token}
		messages = SSEClient(
			'https://otree.firebaseio.com/.json',
			params=params)
		for msg in messages:
			if msg.event == 'put':
				data = json.loads(msg.data)
				match = _PATH_RE.match(data['path'])
				if match:
					print match.groupdict()
					print int(data['data'])
