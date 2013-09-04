import time
import logging
import copy

logger = logging.getLogger(__name__)

from nymms.data_types import NymmsDataType, ValidationError

# state constants
OK = 0
WARN = WARNING = 1
CRIT = CRITICAL = 2
UNKNOWN = 3

# Anything over state 2 is unknown
states = ['ok', 'warning', 'critical', 'unknown']

# state type constants
SOFT = 0
HARD = 1

state_types = ['soft', 'hard']


def get_state_type_name(state_type_code):
    return state_types[state_type_code]


def get_state_name(state_code):
    if state_code > 3:
        return "unknown"
    return states[state_code]


def validate_state(state):
    value = state
    exc = ValidationError('state', value)
    if isinstance(value, basestring):
        try:
            return states.index(value.lower())
        except ValueError:
            raise exc
    elif isinstance(value, int):
        try:
            return states[value] and value
        except IndexError:
            raise exc
    raise exc


def validate_state_type(state_type):
    value = state_type
    exc = ValidationError('state_type', value)
    if isinstance(value, basestring):
        try:
            return state_types.index(value.lower())
        except ValueError:
            raise exc
    elif isinstance(value, int):
        try:
            return state_types[value] and value
        except IndexError:
            raise exc
    raise exc


class StateMixin(object):
    def validate_state(self):
        self.state = validate_state(self.state)

    def validate_state_type(self):
        self.state_type = validate_state_type(self.state_type)

    def validate_timestamp(self):
        self.timestamp = int(self.timestamp or time.time())

    @property
    def state_name(self):
        self.validate_state()
        return get_state_name(self.state)

    @property
    def state_type_name(self):
        self.validate_state_type()
        return get_state_type_name(self.state_type)


class Result(NymmsDataType, StateMixin):
    required_fields = ['state', 'state_type']

    def __init__(self, object_id, state=None, state_type=None, timestamp=None,
                 output=None, task_context=None, origin=None):
        super(Result, self).__init__(object_id=object_id, origin=origin)
        self.state = state
        self.state_type = state_type
        self.timestamp = timestamp
        self.output = output or ''
        self.task_context = task_context or {}

    def _serialize(self):
        self._cleaned['state_name'] = get_state_name(self.state)
        self._cleaned['state_type_name'] = get_state_type_name(self.state_type)

    @classmethod
    def _deserialize(cls, item):
        new_item = super(Result, cls)._deserialize(item)
        new_item = copy.deepcopy(item)
        del(new_item['state_name'])
        del(new_item['state_type_name'])
        return new_item


class StateRecord(NymmsDataType, StateMixin):
    required_fields = ['state', 'state_type']

    def __init__(self, object_id, timestamp=None, state=None, state_type=None):
        super(StateRecord, self).__init__(object_id=object_id, origin=None)
        self.timestamp = timestamp
        self.state = state
        self.state_type = state_type
        self._cleaned = {}

    @classmethod
    def decode_value(cls, value):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return str(value)

    @classmethod
    def _deserialize(cls, item):
        item_dict = {}
        for k, v in item.iteritems():
            item_dict[k] = cls.decode_value(v)
        return item_dict
