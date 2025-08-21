import abc


class NodeBase:
    """A node in the network.

    :ivar node_id: A string that uniquely identifies this node in the network.

    """

    def __init__(self):
        self.node_id = None


class ActivityObjectBase:
    """A thing which participates in an Activity.

    :ivar activity_name str:
        Unicode representation of this object.

    :ivar activity_url str:
        URL of this object.

    :ivar activity_extras dict:
        A BSON-serializable dict of extra stuff to store on the activity.

    """

    def __init__(self):
        self.activity_name = None
        self.activity_url = None
        self.activity_extras = {}


class ActivityBase:
    """Tells the story of a person performing an action on or with an object.

    Consists of an actor, a verb, an object, and optionally a target.

    Defines the following attributes:

    :ivar actor:
        The actor, or subject, of the Activity.

        Example: *John* posted a comment on ticket #42.

        :class:`NodeBase, ActivityObjectBase`

    :ivar verb:
        The verb in the Activity.

        Example: John *posted* a comment on ticket #42.

        :class:`str`

    :ivar obj:
        The object of the Activity.

        Example: John posted *a comment* on ticket #42.

        :class:`ActivityObjectBase`

    :ivar target:
        The (optional) target of the Activity.

        Example: John posted a comment on *ticket #42*.

        :class:`ActivityObjectBase`

    :ivar published:
        The datetime at which the Activity was published.

        :class:`datetime.datetime`

    """

    def __init__(self):
        self.actor = None
        self.verb = None
        self.obj = None
        self.target = None
        self.published = None


class NodeManagerBase(metaclass=abc.ABCMeta):
    """Manages the network of connected nodes.

    Knows how to connect and disconnect nodes and serialize the graph.
    """

    @abc.abstractmethod
    def follow(self, follower, following):
        """Create a directed edge from :class:`NodeBase` ``follower`` to
        :class:`NodeBase` ``following``.
        """
        return

    @abc.abstractmethod
    def unfollow(self, follower, following):
        """Destroy a directed edge from :class:`NodeBase` ``follower`` to
        :class:`NodeBase` ``following``.
        """
        return


class ActivityManagerBase(metaclass=abc.ABCMeta):
    """Serializes :class:`ActivityBase` objects."""

    @abc.abstractmethod
    def create(self, actor, verb, obj, target=None):
        """Create and serialize an :class:`ActivityBase`."""
        return

