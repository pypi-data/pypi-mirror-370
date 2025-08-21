#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0


def parse_setting_json(data):
    # check type, if invalid = init value
    mode = data.get('mode', [])
    path = data.get('path', [])
    dep_argument = data.get('dep_argument', '')
    output = data.get('output', '')
    format = data.get('format', '')
    link = data.get('link', '')
    db_url = data.get('db_url', '')
    timer = data.get('timer', False)
    raw = data.get('raw', False)
    core = data.get('core', -1)
    no_correction = data.get('no_correction', False)
    correct_fpath = data.get('correct_fpath', '')
    ui = data.get('ui', False)
    exclude_path = data.get('exclude', [])
    selected_source_scanner = data.get('selected_source_scanner', '')
    source_write_json_file = data.get('source_write_json_file', False)
    source_print_matched_text = data.get('source_print_matched_text', False)
    source_time_out = data.get('source_time_out', 120)
    binary_simple = data.get('binary_simple', False)
    str_lists = [mode, path, exclude_path]
    strings = [
        dep_argument, output, format, db_url,
        correct_fpath, link, selected_source_scanner
    ]
    booleans = [timer, raw, no_correction, ui, source_write_json_file, source_print_matched_text, binary_simple]

    is_incorrect = False

    # check if json file is incorrect format
    for i, target in enumerate(str_lists):
        if not (isinstance(target, list) and
                all(isinstance(item, str) for item in target)):
            is_incorrect = True
            str_lists[i] = []

    for i, target in enumerate(strings):
        if not isinstance(target, str):
            is_incorrect = True
            strings[i] = ''

    for i, target in enumerate(booleans):
        if not isinstance(target, bool):
            is_incorrect = True
            booleans[i] = False

    if not isinstance(core, int):
        is_incorrect = True
        core = -1

    if not isinstance(source_time_out, int):
        is_incorrect = True
        source_time_out = 120

    if is_incorrect:
        print('Ignoring some values with incorrect format in the setting file.')

    return mode, path, dep_argument, output, format, link, db_url, timer, \
        raw, core, no_correction, correct_fpath, ui, exclude_path, \
        selected_source_scanner, source_write_json_file, source_print_matched_text, source_time_out, \
        binary_simple
