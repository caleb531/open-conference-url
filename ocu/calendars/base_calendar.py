#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import abc

from ocu.event_dict import EventDict


# A base calendar class which defines a standard protocol for retrieving event
# data to feed into Open Conference URL
class BaseCalendar(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_event_dicts(self) -> EventDict:
        raise NotImplementedError
