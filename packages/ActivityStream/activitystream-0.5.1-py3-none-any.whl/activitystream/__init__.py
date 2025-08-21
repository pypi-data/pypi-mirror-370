import logging
import threading

from importlib.metadata import entry_points

from .managers import NodeManager, ActivityManager, Aggregator
from .storage import pymongostorage

log = logging.getLogger(__name__)

_director = None


class ActivityDirector(threading.local):

    def __init__(self, **conf):
        self._default_impls = {
                'director': ActivityDirector,
                'storage': pymongostorage.PymongoStorage,
                'nodemanager': NodeManager,
                'activitymanager': ActivityManager,
                'aggregator': Aggregator,
                }

        self.conf = conf
        self.entry_points = self._load_entry_points()
        storage = self._get_impl('storage')(conf)
        self.node_manager = self._get_impl('nodemanager')(storage)
        self.activity_manager = self._get_impl('activitymanager')(storage,
                self.node_manager)
        self.aggregator = self._get_impl('aggregator')(self.activity_manager,
                self.node_manager)

    def _load_entry_points(self):
        return {ep.name: ep.load() for ep in
                entry_points(group='activitystream')}

    def _get_impl(self, name):
        return self.entry_points.get(name, self._default_impls.get(name))

    def connect(self, follower, following):
        self.node_manager.follow(follower, following)

    def disconnect(self, follower, following):
        self.node_manager.unfollow(follower, following)

    def is_connected(self, follower, following):
        return self.node_manager.is_following(follower, following)

    def create_activity(self, actor, verb, obj, target=None,
            related_nodes=None, tags=None):
        return self.activity_manager.create(actor, verb, obj, target=target,
                related_nodes=related_nodes, tags=tags)

    def create_timeline(self, node_id):
        """Create an up-to-date timeline for the ``node_id`` Node.

        """
        self.aggregator.create_timeline(node_id)

    def create_timelines(self, node_id):
        """Create an up-to-date timeline for the ``node_id`` Node and all of
        its followers.

        """
        self.create_timeline(node_id)
        node = self.node_manager.get_node(node_id)
        if node and node.followers:
            for n in self.node_manager.get_nodes(node.followers):
                self.create_timeline(n.node_id)

    def get_timeline(self, *args, **kw):
        return self.aggregator.get_timeline(*args, **kw)

def configure(**conf):
    global _director
    defaults = {
            'activitystream.master': 'mongodb://127.0.0.1:27017',
            'activitystream.database': 'activitystream',
            'activitystream.activity_collection': 'activities',
            'activitystream.node_collection': 'nodes',
    }
    defaults.update(conf)
    director = ActivityDirector(**defaults)
    if director._get_impl('director') != ActivityDirector:
        director = director._get_impl('director')(**defaults)
    _director = director


def director():
    global _director
    return _director
