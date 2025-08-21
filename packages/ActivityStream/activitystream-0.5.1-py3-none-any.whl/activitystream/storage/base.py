from ..base import (
        NodeBase,
        ActivityBase,
        ActivityObjectBase,
        )


class StoredNode(NodeBase):
    """Extends `NodeBase` with additional attributes that must be persisted by
    `Storage` implementations.

    :ivar followers: List of node ids that are following this node.
    :ivar following: List of node ids that this node is following.
    :ivar last_timeline_aggregation: Datetime of the last timeline
        aggregation for this node.

    """
    def __init__(self, **kw):
        super().__init__()
        self.followers = []
        self.following = []
        self.last_timeline_aggregation = None
        for k, v in kw.items():
            setattr(self, k, v)


class StoredActivity(ActivityBase):
    """Extends `ActivityBase` with additional attributes that must be persisted
    by `Storage` implementations.

    :ivar score:
        Ranking of this activity relative to other activities in the same
        timeline. May be None if the activity has not been aggregated into
        a timeline.

        :class:`float`

    :ivar owner_id:
        Node id of the owner of the timeline to which this activity belongs.
        May be None if the activity has not yet been aggregated into a
        timeline.

    :ivar node_id:
        Node id to which this activity belongs.

    """
    def __init__(self, **kw):
        super().__init__()
        for k, v in kw.items():
            if k in ('actor', 'obj', 'target') and isinstance(v, dict):
                v = ActivityObject(**v)
            setattr(self, k, v)

    def to_dict(self, **kw):
        d = dict(
                actor=ActivityObject.to_dict(self.actor,
                    node_id=self.actor.node_id),
                verb=self.verb,
                obj=ActivityObject.to_dict(self.obj),
                target=ActivityObject.to_dict(self.target),
                published=self.published,
                node_id=getattr(self, 'node_id', None),
                owner_id=getattr(self, 'owner_id', None),
                score=getattr(self, 'score', None),
                tags=getattr(self, 'tags', None),
                )
        d.update(kw)
        return d

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()


class ActivityObject(ActivityObjectBase):
    def __init__(self, **kw):
        super().__init__()
        for k, v in kw.items():
            setattr(self, k, v)

    @staticmethod
    def to_dict(obj, **kw):
        if not obj or not any((obj.activity_name, obj.activity_url,
                obj.activity_extras)):
            return {}
        d = dict(activity_name=obj.activity_name,
                activity_url=obj.activity_url,
                activity_extras=obj.activity_extras,
                )
        d.update(kw)
        return d


class Storage:
    def __init__(self, conf):
        """Initialize storage backend.

        :param conf: dictionary of config values

        """
        self.conf = conf

    def create_edge(self, from_node, to_node):
        """Create a directed edge from :class:`Node` ``follower`` to
        :class:`Node` ``following``.

        """
        raise NotImplementedError

    def destroy_edge(self, from_node, to_node):
        """Destroy a directed edge from :class:`Node` ``follower`` to
        :class:`Node` ``following``.

        """
        raise NotImplementedError

    def edge_exists(self, from_node, to_node):
        """Determine if there is a directed edge from :class:`Node`
        ``follower`` to :class:`Node` ``following``.

        """
        raise NotImplementedError

    def get_node(self, node_id):
        """Return the node for the given node_id.

        """
        raise NotImplementedError

    def get_nodes(self, node_ids):
        """Return nodes for the given node_ids.

        """
        raise NotImplementedError

    def create_node(self, node_id):
        """Create a new node.

        """
        raise NotImplementedError

    def save_node(self, node):
        """Save a node.

        """
        raise NotImplementedError

    def set_aggregating(self, node_id):
        """Set an ``is_aggregating`` flag for ``node_id`` if it's not already
        aggregating.

        If the node is already aggregating, return None. Otherwise, set the
        flag and return the node (creating the node if it doesn't already
        exist).

        """
        raise NotImplementedError

    def save_activity(self, activity):
        """Save an activity.

        """
        raise NotImplementedError

    def get_activities(self, nodes, since=None, sort=None, limit=None, skip=0, query=None):
        """Return all activities associated with the given nodes.

        Params:
            since (datetime) - return activities that have occured since this
                               datetime
        """
        raise NotImplementedError

    def save_timeline(self, owner_id, activities):
        """Save timeline.

        """
        raise NotImplementedError

    def get_timeline(self, node_id, sort=None, limit=None, skip=0, query=None):
        """Return the timeline for node_id.

        Timeline is the already-aggregated list of activities in mongo.

        """
        raise NotImplementedError
