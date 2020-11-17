#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cache import cache


# A dedicated trigger point for refreshing the cache on command
def main():
    has_cache_updated = cache.refresh()
    print(has_cache_updated, end='')


if __name__ == '__main__':
    main()
