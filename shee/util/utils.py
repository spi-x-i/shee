#!/usr/bin/env python
# -*- coding: utf-8 -*-

def get_result_dir_name(fullpathname):
    """
    Iterates over path chars, get the first dot position, drop each char after and return the name
    :param fullpathname: file path
    :return: result directory name
    """
    for i, c in enumerate(reversed(fullpathname)):
        if c == '.':
            return fullpathname[:(-i - 1)]