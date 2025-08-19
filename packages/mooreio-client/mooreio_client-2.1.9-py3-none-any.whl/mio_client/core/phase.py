# Copyright 2020-2025 Datum Technology Corporation
# All rights reserved.
#######################################################################################################################
from datetime import datetime, timedelta
from enum import Enum


class State(Enum):
    """
    The `State` class represents the different states of an object.

    Attributes:
    INITIALIZED : str
        Represents the initialized state.
    STARTED : str
        Represents the started state.
    FINISHED : str
        Represents the finished state.
    ERROR : str
        Represents the error state.
    """
    INITIALIZED = 'initialized'
    STARTED = 'started'
    FINISHED = 'finished'
    ERROR = 'error'


# TODO Turn this into a pydantic model and use a FileModel to store phase info to disk for performance data
class Phase:
    """
    Initialize a Phase object.

    :param root: The root object.
    :param name: The name of the phase.
    """
    def __init__(self, root: 'RootManager', name: str):
        self._root = root
        self._name = name
        self._state : State = State.INITIALIZED
        self._init_timestamp: datetime = datetime.now()
        self._start_timestamp: datetime = None
        self._end_timestamp: datetime = None
        self._error: Exception = None
        self._end_process: bool = False
        self._end_process_message: str = ""

    def __str__(self):
        return self.name

    @property
    def name(self) -> str:
        """
        :return: The name of the phase.
        :rtype: str
        """
        return self._name

    @property
    def state(self) -> State:
        """
        :return: The current state of the software.
        :rtype: State
        """
        return self._state

    @property
    def init_timestamp(self) -> datetime:
        """
        :return: The timestamp at which the phase object was created.
        :rtype: datetime
        """
        return self._init_timestamp

    @property
    def start_timestamp(self) -> datetime:
        """
        :return: The timestamp at which phase work started.
        :rtype: datetime
        """
        return self._start_timestamp

    @property
    def end_timestamp(self) -> datetime:
        """
        :return: The timestamp at which phase work finished.
        :rtype: datetime
        """
        return self._end_timestamp

    @property
    def duration(self) -> timedelta:
        """
        :return: The duration between start_timestamp and end_timestamp.
        :rtype: timedelta
        """
        return self._end_timestamp - self._start_timestamp

    @property
    def error(self) -> Exception:
        """
        :return: The error which occurred in the phase, if any.
        :rtype: Exception
        """
        return self._error

    @error.setter
    def error(self, error: Exception):
        """
        :param error: The error which occurred in the phase.
        :type error: Exception
        """
        self._error = error
        if self._error:
            self._state = State.ERROR
    
    @property
    def end_process(self) -> bool:
        """
        :return: A flag indicating whether the process must end.
        :rtype: bool
        """
        return self._end_process

    @end_process.setter
    def end_process(self, end_process: bool):
        """
        :param end_process: A flag indicating whether the process must end.
        :type end_process: bool
        """
        self._end_process = end_process

    @property
    def end_process_message(self) -> str:
        """
        :return: (optional) string as to why the process must end.
        :rtype: str
        """
        return self._end_process_message

    @end_process_message.setter
    def end_process_message(self, end_process_message: str):
        """
        :param end_process_message: A string as to why the process must end.
        :type end_process_message: str
        """
        self._end_process_message = end_process_message


    def next(self):
        """
        Pick next FSM state.
        :return:
        """
        if self.state == State.INITIALIZED:
            self._state = State.STARTED
            self._start_timestamp = datetime.now()
        elif self.state == State.STARTED:
            self._state = State.FINISHED
            self._end_timestamp = datetime.now()
        else:
            self._state = State.ERROR
        return self.state

    def has_finished(self):
        """
        :return: True if the phase has finished, False otherwise.
        """
        return self.state == State.FINISHED
