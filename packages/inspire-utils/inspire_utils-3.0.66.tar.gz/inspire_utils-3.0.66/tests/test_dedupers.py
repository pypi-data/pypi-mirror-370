# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2024 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

from inspire_utils.dedupers import dedupe_all_lists, dedupe_list, dedupe_list_of_dicts


def test_dedupe_list():
    list_with_duplicates = ['foo', 'bar', 'foo']

    expected = ['foo', 'bar']
    result = dedupe_list(list_with_duplicates)

    assert expected == result


def test_dedupe_list_of_dicts():
    list_of_dicts_with_duplicates = [
        {'a': 123, 'b': 1234},
        {'a': 3222, 'b': 1234},
        {'a': 123, 'b': 1234},
    ]

    expected = [{'a': 123, 'b': 1234}, {'a': 3222, 'b': 1234}]
    result = dedupe_list_of_dicts(list_of_dicts_with_duplicates)

    assert expected == result


def test_dedupe_all_lists():
    obj = {
        "l0": list(range(10)) + list(range(10)),
        "o1": [{"foo": "bar"}] * 10,
        "o2": [{"foo": [1, 2]}, {"foo": [1, 1, 2]}] * 10,
    }

    expected = {"l0": list(range(10)), "o1": [{"foo": "bar"}], "o2": [{"foo": [1, 2]}]}

    assert dedupe_all_lists(obj) == expected


def test_dedupe_all_lists_honors_exclude_keys():
    obj = {
        "l0": list(range(10)) + list(range(10)),
        "o1": [{"foo": "bar"}] * 10,
        "o2": [{"foo": [1, 2]}, {"foo": [1, 1, 2]}] * 10,
    }

    expected = {
        "l0": list(range(10)),
        "o1": [{"foo": "bar"}] * 10,
        "o2": [{"foo": [1, 2]}],
    }

    assert dedupe_all_lists(obj, exclude_keys=["o1"]) == expected


def test_dedupe_all_lists_dedupes_under_excluded_keys():
    obj = {
        "l0": list(range(10)) + list(range(10)),
        "o1": [{"foo": "bar"}] * 10,
        "o2": [{"foo": [1, 2]}, {"foo": [1, 1, 2]}] * 10,
    }

    expected = {
        "l0": list(range(10)),
        "o1": [{"foo": "bar"}],
        "o2": [{"foo": [1, 2]}] * 20,
    }

    assert dedupe_all_lists(obj, exclude_keys=["o2"]) == expected
