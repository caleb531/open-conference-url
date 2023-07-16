#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import TypedDict


class EventDictRequiredKeys(TypedDict):
    title: str
    startDate: str
    endDate: str


class EventDict(EventDictRequiredKeys, total=False):
    isAllDay: str
    location: str
    notes: str
