#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import abc


# A base calendar class which defines a standard protocol for retrieving event
# data to feed into Open Conference URL
class BaseCalendar(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_event_dicts(self):
        raise NotImplementedError
