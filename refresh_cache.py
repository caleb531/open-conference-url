#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cache import cache


# A dedicated trigger point for refreshing the cache on command
def main():
    cache.refresh()


if __name__ == '__main__':
    main()
