"""Test fitting to summary statistics."""

import importlib
import pytest
import numpy as np
import pandas as pd
from psifr import fr
from cymr import analysis


@pytest.fixture()
def raw1():
    """Create raw free recall data."""
    subjects = [1, 1, 2, 2]
    lists = [1, 2, 1, 2]
    study = [
        ['absence', 'hollow', 'pupil'], 
        ['fountain', 'piano', 'pillow'],
        ['absence', 'hollow', 'pupil'], 
        ['fountain', 'piano', 'pillow'],
    ]
    recall = [
        ['hollow', 'pupil', 'empty'], 
        ['pillow', 'fountain', 'pillow'],
        ['absence', 'hollow'],
        ['piano', 'fountain', 'pillow'],
    ]
    item_index = ([[0, 1, 2], [3, 4, 5], [0, 1, 2], [3, 4, 5]], None)
    task = ([[1, 1, 1], [2, 2, 2], [1, 1, 1], [2, 2, 2]], None)
    raw = fr.table_from_lists(
        subjects, study, recall, lists, item_index=item_index, task=task
    )
    return raw


@pytest.fixture()
def raw2():
    """Create raw free recall data."""
    subjects = [1, 1, 2, 2]
    lists = [1, 2, 1, 2]
    study = [
        ['absence', 'hollow', 'pupil'], 
        ['fountain', 'piano', 'pillow'],
        ['absence', 'hollow', 'pupil'], 
        ['fountain', 'piano', 'pillow'],
    ]
    recall = [
        ['pupil', 'hollow'], 
        ['piano', 'fountain'],
        ['absence', 'pupil', 'absence'],
        ['fountain', 'piano', 'pillow'],
    ]
    item_index = ([[0, 1, 2], [3, 4, 5], [0, 1, 2], [3, 4, 5]], None)
    task = ([[1, 1, 1], [2, 2, 2], [1, 1, 1], [2, 2, 2]], None)
    raw = fr.table_from_lists(
        subjects, study, recall, lists, item_index=item_index, task=task
    )
    return raw


@pytest.fixture()
def data1(raw1):
    """Create merged free recall data."""
    data = fr.merge_free_recall(raw1, study_keys=['task', 'item_index'])
    return data


@pytest.fixture()
def data2(raw2):
    """Create merged free recall data."""
    data = fr.merge_free_recall(raw2, study_keys=['task', 'item_index'])
    return data


@pytest.fixture()
def stats_def():
    stats_def = analysis.Statistics()
    stats_def.set_stat(
        "spc", "psifr.fr:spc", ["input"], "recall", "group", conditions=["task"]
    )
    stats_def.set_stat(
        "lag_crp", "psifr.fr:lag_crp", ["lag"], "prob", "subject", conditions=["task"]
    )
    stats_def.set_stat(
        "lag_crp_compound", 
        "psifr.fr:lag_crp_compound", 
        ["previous", "current"], 
        "prob", 
        "subject", 
        conditions=["task"],
    )
    return stats_def


def test_eval_stats(data1, stats_def):
    """Test evaluation of statistics."""
    stats, results = stats_def.eval_stats(data1)
    spc = [0.5, 1, 1, 0.5, 0.5, 1]
    c1s1 = [np.nan, 0, np.nan, 1, np.nan]
    c1s2 = [np.nan, np.nan, np.nan, 1, 0]
    c2s1 = [1, 0, np.nan, np.nan, np.nan]
    c2s2 = [np.nan, 1, np.nan, 0, 1]
    dependent_expected = np.array(spc + c1s1 + c1s2 + c2s1 + c2s2)
    dependent = stats.loc[:25, "dependent"].to_numpy()
    np.testing.assert_array_equal(dependent, dependent_expected)


def test_compare_stats(data1, data2, stats_def):
    """Test comparison of stats for two datasets."""
    stats1, _ = stats_def.eval_stats(data1)
    stats2, _ = stats_def.eval_stats(data2)
    metric = stats_def.compare_stats(stats1, stats2)
    assert round(metric, 3) == 0.764
