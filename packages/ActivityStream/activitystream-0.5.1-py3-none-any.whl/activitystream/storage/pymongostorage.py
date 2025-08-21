import pymongo

from .base import (
        StoredNode,
        StoredActivity,
        Storage,
        )


class PymongoStorage(Storage):
    """Pymongo storage engine."""

    def __init__(self, conf):
        """Initialize storage backend.

        :param conf: dictionary of config values

        """
        self.conf = conf
        self.connection = self._get_connection(conf)
        self.db = self.connection[conf['activitystream.database']]
        self.activity_collection = \
                self.db[conf['activitystream.activity_collection']]
        self.node_collection = \
                self.db[conf['activitystream.node_collection']]

    def _get_connection(self, conf):
        if conf['activitystream.master'].startswith('mim://'):
            try:
                from ming import mim
            except ImportError as e:
                raise ImportError(str(e) + '. To use mim:// you must have the '
                        'ming package installed.')
            else:
                return mim.Connection()
        else:
            return pymongo.MongoClient(conf['activitystream.master'])

    def create_edge(self, from_node, to_node):
        """Create a directed edge from :class:`Node` ``follower`` to
        :class:`Node` ``following``.

        """
        self.node_collection.update_many({"node_id": from_node.node_id},
                {"$addToSet": {"following": to_node.node_id}}, upsert=True)
        self.node_collection.update_many({"node_id": to_node.node_id},
                {"$addToSet": {"followers": from_node.node_id}}, upsert=True)

    def destroy_edge(self, from_node, to_node):
        """Destroy a directed edge from :class:`Node` ``follower`` to
        :class:`Node` ``following``.

        """
        self.node_collection.update_many({"node_id": from_node.node_id},
                {"$pull": {"following": to_node.node_id}})
        self.node_collection.update_many({"node_id": to_node.node_id},
                {"$pull": {"followers": from_node.node_id}})

    def edge_exists(self, from_node, to_node):
        """Determine if there is a directed edge from :class:`Node`
        ``follower`` to :class:`Node` ``following``.

        """
        result = self.node_collection.find_one({"node_id": from_node.node_id,
                "following": to_node.node_id})
        return result is not None

    def get_node(self, node_id):
        """Return the node for the given node_id.

        """
        d = self.node_collection.find_one({"node_id": node_id})
        return StoredNode(**d) if d else None

    def get_nodes(self, node_ids):
        """Return nodes for the given node_ids.

        """
        return [StoredNode(**doc) for doc in
                self.node_collection.find({"node_id": {"$in": node_ids}})]

    def create_node(self, node_id, **kw):
        """Create a new node.

        """
        return self.save_node(StoredNode(node_id=node_id, **kw))

    def save_node(self, node):
        """Save a node.

        """
        if hasattr(node, '_id'):
            result = self.node_collection.replace_one({'_id': node._id}, vars(node), upsert=True)
        else:
            result = self.node_collection.insert_one(vars(node))
            setattr(node, '_id', result.inserted_id)
            
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
        d = self.node_collection.find_one_and_update(
            {'node_id': node_id, 'is_aggregating': {'$ne': True}},
            update={'$set': {'is_aggregating': True}},
            return_document=True,
        )
        return StoredNode(**d) if d else None

    def save_activity(self, activity):
        """Save an activity.

        """
        self.activity_collection.insert_one(activity.to_dict())
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
        it = self.activity_collection.find(q, sort=sort, limit=limit, skip=skip)
        return [StoredActivity(**doc) for doc in it]

    def save_timeline(self, owner_id, activities):
        """Save a list of activities to a node's timeline.

        """
        for a in activities:
            self.activity_collection.insert_one(a.to_dict(owner_id=owner_id))

    def get_timeline(self, node_id, sort=None, limit=None, skip=0, query=None):
        """Return the timeline for node_id.

        Timeline is the already-aggregated list of activities in mongo.

        """
        q = {'owner_id': node_id}
        if query:
            q.update(query)
        timeline = self.activity_collection.find(q, sort=sort, limit=limit, skip=skip)
        return [StoredActivity(**doc) for doc in timeline]
