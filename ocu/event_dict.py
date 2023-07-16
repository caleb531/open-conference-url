#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, TypedDict


class EventDictRequiredKeys(TypedDict):
    title: str
    startDate: str
    endDate: str
    isAllDay: str


class EventDict(EventDictRequiredKeys, total=False):
    location: str
    notes: str
