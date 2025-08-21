from datetime import datetime

from ming import Session
from ming import schema as S
from ming.datastore import create_datastore
from ming.odm import (
        Mapper,
        FieldProperty,
        )
from ming.odm.odmsession import ThreadLocalODMSession

from ming.odm.declarative import MappedClass

from .base import (
        StoredNode,
        StoredActivity,
        ActivityObject,
        Storage,
        )

activity_doc_session = Session.by_name("activitystream")
activity_odm_session = session = ThreadLocalODMSession(activity_doc_session)

class Node(MappedClass, StoredNode):
    class __mongometa__:
        session = activity_odm_session
        name = 'nodes'
        indexes = ['node_id']

    _id = FieldProperty(S.ObjectId)
    node_id = FieldProperty(str)
    followers = FieldProperty([str])
    following = FieldProperty([str])
    last_timeline_aggregation = FieldProperty(S.DateTime)
    is_aggregating = FieldProperty(S.Bool)

class ActivityObjectType(S.Object):
    def __init__(self, actor=False, **kw):
        fields = dict(
            activity_name=S.String(),
            activity_url=S.String(),
            activity_extras=S.Object({None: None}, if_missing={}),
            )
        if actor:
            fields['node_id'] = S.String()
        super().__init__(fields=fields, **kw)

class Activity(MappedClass, StoredActivity):
    class __mongometa__:
        session = activity_odm_session
        name = 'activities'
        indexes = [
                ('node_id', 'published'),
                ('owner_id', 'score'),
                ]

    _id = FieldProperty(S.ObjectId)
    owner_id = FieldProperty(S.String, if_missing=None)
    node_id = FieldProperty(str)
    actor = FieldProperty(ActivityObjectType(actor=True))
    verb = FieldProperty(str)
    obj = FieldProperty(ActivityObjectType)
    target = FieldProperty(ActivityObjectType, if_missing=None)
    published = FieldProperty(datetime)
    score = FieldProperty(S.Float, if_missing=None)
    tags = FieldProperty([str])

Mapper.compile_all()


class MingStorage(Storage):
    """Ming storage engine."""

    def __init__(self, conf):
        """Initialize storage backend.

        :param conf: dictionary of config values

        """
        self.conf = conf
        ming_opts = {k[len('activitystream.ming.'):]: v
                     for k, v in conf.items()
                     if k.startswith('activitystream.ming.')}
        datastore = create_datastore(conf['activitystream.master'].rstrip('/') + '/' + conf['activitystream.database'],
                                     **ming_opts)
        Session._datastores['activitystream'] = datastore
        Session.by_name('activitystream').bind = datastore

    def create_edge(self, from_node, to_node):
        """Create a directed edge from :class:`Node` ``follower`` to
        :class:`Node` ``following``.

        """
        Node.query.update({"node_id": from_node.node_id},
                {"$addToSet": {"following": to_node.node_id}}, upsert=True)
        Node.query.update({"node_id": to_node.node_id},
                {"$addToSet": {"followers": from_node.node_id}}, upsert=True)

    def destroy_edge(self, from_node, to_node):
        """Destroy a directed edge from :class:`Node` ``follower`` to
        :class:`Node` ``following``.

        """
        Node.query.update({"node_id": from_node.node_id},
                {"$pull": {"following": to_node.node_id}})
        Node.query.update({"node_id": to_node.node_id},
                {"$pull": {"followers": from_node.node_id}})

    def edge_exists(self, from_node, to_node):
        """Determine if there is a directed edge from :class:`Node`
        ``follower`` to :class:`Node` ``following``.

        """
        return Node.query.find({"node_id": from_node.node_id,
                "following": to_node.node_id}).first() is not None

    def get_node(self, node_id):
        """Return the node for the given node_id.

        """
        return Node.query.get(node_id=node_id)

    def get_nodes(self, node_ids):
        """Return nodes for the given node_ids.

        """
        return Node.query.find({"node_id": {"$in": node_ids}}).all()

    def create_node(self, node_id, **kw):
        """Create a new node.

        """
        node = Node(node_id=node_id, **kw)
        session.flush()
        return node

    def save_node(self, node):
        """Save a node.

        """
        session.flush()
        return node

    def set_aggregating(self, node_id):
        """Set an ``is_aggregating`` flag for ``node_id`` if it's not already
        aggregating.

        If the node is already aggregating, return None. Otherwise, set the
        flag and return the node (creating the node if it doesn't already
        exist).

        """
        if not self.get_node(node_id):
            self.create_node(node_id, is_aggregating=False)
        return Node.query.find_one_and_update(
            {'node_id': node_id, 'is_aggregating': {'$ne': True}},
            update={'$set': {'is_aggregating': True}},
            return_document=True,
        )

    def save_activity(self, activity):
        """Save an activity.

        """
        activity = Activity(**activity.to_dict())
        session.flush()
        return activity

    def get_activities(self, nodes, since=None, sort=None, limit=None, skip=0, query=None):
        """Return all activities associated with the given nodes.

        Params:
            since (datetime) - return activities that have occured since this
                               datetime
        """
        node_ids = [node.node_id for node in nodes]
        q = {'node_id': {'$in': node_ids}}
        if since:
            q['published'] = {'$gte': since}
        if query:
            q.update(query)
        q['owner_id'] = None
        return Activity.query.find(q, sort=sort, limit=limit, skip=skip).all()

    def save_timeline(self, owner_id, activities):
        """Save a list of activities to a node's timeline.

        """
        for a in activities:
            # Don't save changes to the original activity, just use it
            # to create a new activity in the timeline.
            session.expunge(a)
            Activity(**a.to_dict(owner_id=owner_id))
        session.flush()

    def get_timeline(self, node_id, sort=None, limit=None, skip=0, query=None):
        """Return the timeline for node_id.

        Timeline is the already-aggregated list of activities in mongo.

        """
        q = {'owner_id': node_id}
        if query:
            q.update(query)
        return Activity.query.find(q, sort=sort, limit=limit, skip=skip).all()
