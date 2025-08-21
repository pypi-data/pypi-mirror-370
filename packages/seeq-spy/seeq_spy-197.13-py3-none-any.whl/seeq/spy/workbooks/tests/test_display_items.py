import re

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from seeq.spy.workbooks import AnalysisWorksheet, AnalysisWorkstep, Analysis


@pytest.fixture
def empty_worksheet():
    workbook = Analysis()
    worksheet = AnalysisWorksheet(workbook)
    worksheet.current_workstep().definition["Data"]["version"] = 66
    return worksheet


@pytest.fixture
def empty_workstep():
    workstep = AnalysisWorkstep()
    workstep.definition["Data"]["version"] = 66
    return workstep


@pytest.fixture
def workstep():
    workstep = AnalysisWorkstep()
    # The below stores are based on a real workstep from Workstep Version 66 (2025-02). Update as needed.
    workstep.definition["Data"]["version"] = 66
    workstep.get_workstep_stores()["sqTrendSeriesStore"] = {"items": [
        {
            "axisAlign": "A",
            "axisAutoScale": True,
            "lane": 1,
            "rightAxis": False,
            "dashStyle": "Solid",
            "lineWidth": 1,
            "autoDisabled": False,
            "axisVisibility": True,
            "yAxisType": "linear",
            "sampleDisplayOption": "line",
            "id": "00000000-0000-0000-0000-000000000000",
            "name": "Signal 0",
            "selected": False,
            "color": "#9D248F",
            "interpolationMethod": "Linear",
        },
        {
            "axisAlign": "B",
            "axisAutoScale": True,
            "lane": 2,
            "rightAxis": False,
            "dashStyle": "Solid",
            "lineWidth": 1,
            "autoDisabled": False,
            "axisVisibility": True,
            "yAxisType": "linear",
            "sampleDisplayOption": "line",
            "showDataLabels": True,
            "id": "00000000-0000-0000-0000-000000000001",
            "name": "Signal 1",
            "selected": True,
            "color": "#068C45",
            "interpolationMethod": "Linear",
        },
    ]}
    workstep.get_workstep_stores()["sqTrendConditionStore"] = {"items": [
        {
            "lane": 3,
            "lineWidth": 1,
            "autoDisabled": False,
            "id": "00000000-0000-0000-0000-000000000002",
            "name": "Condition 0",
            "selected": False,
            "color": "#CE561B"
        },
        {
            "lane": 4,
            "lineWidth": 1,
            "autoDisabled": False,
            "id": "00000000-0000-0000-0000-000000000003",
            "name": "Condition 1",
            "selected": True,
            "color": "#00A2DD",
            "overlay": 1,
        },
        {
            "lane": 4,
            "lineWidth": 1,
            "autoDisabled": False,
            "id": "00000000-0000-0000-0000-000000000010",
            "name": "Condition 2",
            "selected": False,
            "color": "#00A2DD",
            "overlay": 2,
        },
        {
            "lane": 4,
            "lineWidth": 1,
            "autoDisabled": False,
            "id": "00000000-0000-0000-0000-000000000011",
            "name": "Condition 3",
            "selected": False,
            "color": "#00A2DD",
            "overlay": 3,
        }
    ]}
    workstep.get_workstep_stores()["sqTrendScalarStore"] = {"items": [
        {
            "axisAlign": "C",
            "axisAutoScale": True,
            "lane": 5,
            "rightAxis": False,
            "dashStyle": "Dash",
            "lineWidth": 1,
            "autoDisabled": False,
            "axisVisibility": True,
            "yAxisType": "linear",
            "id": "00000000-0000-0000-0000-000000000004",
            "name": "Scalar 0",
            "selected": False,
            "color": "#AE6A8B",
        },
        {
            "axisAlign": "D",
            "axisAutoScale": True,
            "lane": 6,
            "rightAxis": False,
            "dashStyle": "Dash",
            "lineWidth": 1,
            "autoDisabled": False,
            "axisVisibility": True,
            "yAxisType": "linear",
            "showDataLabels": True,
            "id": "00000000-0000-0000-0000-000000000005",
            "name": "Scalar 1",
            "selected": True,
            "color": "#36937E",
        },
    ]}
    workstep.get_workstep_stores()["sqTrendMetricStore"] = {"items": [
        {
            "axisAlign": "E",
            "axisAutoScale": True,
            "lane": 7,
            "rightAxis": False,
            "dashStyle": "Solid",
            "lineWidth": 1,
            "autoDisabled": False,
            "axisVisibility": True,
            "yAxisConfig": {
                "min": 39.3,
                "max": 60.7
            },
            "yAxisMin": 40,
            "yAxisMax": 60,
            "yAxisType": "linear",
            "sampleDisplayOption": "line",
            "id": "00000000-0000-0000-0000-000000000006",
            "name": "Metric 0",
            "selected": False,
            "color": "#2DBBA7"
        },
        {
            "axisAlign": "F",
            "axisAutoScale": True,
            "lane": 8,
            "rightAxis": False,
            "dashStyle": "Solid",
            "lineWidth": 1,
            "autoDisabled": False,
            "axisVisibility": True,
            "yAxisConfig": {
                "min": 39.3,
                "max": 60.7
            },
            "yAxisMin": "40",
            "yAxisMax": "60.5",
            "yAxisType": "linear",
            "sampleDisplayOption": "line",
            "showDataLabels": True,
            "id": "00000000-0000-0000-0000-000000000007",
            "name": "Metric 1",
            "selected": True,
            "color": "#AE752A"
        }
    ]}
    workstep.get_workstep_stores()["sqTrendTableStore"] = {"items": [
        {
            "autoDisabled": False,
            "stack": False,
            "id": "00000000-0000-0000-0000-000000000008",
            "name": "Histogram 0",
            "selected": False,
            "color": "#767538",
            "binConfig": {}
        },
        {
            "autoDisabled": True,
            "stack": True,
            "id": "00000000-0000-0000-0000-000000000009",
            "name": "Histogram 1",
            "selected": True,
            "color": "#542B7C",
            "binConfig": {},
        },
    ]}
    return workstep


@pytest.mark.unit
def test_display_items_empty(empty_worksheet, empty_workstep, workstep):
    """Test that an empty display_items DF is created when the workstep is empty"""
    assert len(empty_workstep.display_items) == 0
    assert empty_workstep.display_items.columns.to_list() == ['Name', 'ID']


@pytest.mark.unit
def test_items_from_stores(empty_worksheet, empty_workstep, workstep):
    """Test that the various item types are pulled from their respective stores."""
    items = workstep.display_items

    # Overall size
    assert len(items['Name']) == 12

    # Columns
    expected_columns = set(['Name', 'ID', 'Type'] + list(workstep._workstep_display_user_to_workstep.keys()))
    assert set(items.columns.to_list()) == expected_columns

    # Specific item names and types
    assert items[items['Type'] == 'Signal']['Name'].to_list() == ['Signal 0', 'Signal 1']
    assert items[items['Type'] == 'Condition']['Name'].to_list() == ['Condition 0', 'Condition 1', 'Condition 2',
                                                                     'Condition 3']
    assert items[items['Type'] == 'Scalar']['Name'].to_list() == ['Scalar 0', 'Scalar 1']
    assert items[items['Type'] == 'Metric']['Name'].to_list() == ['Metric 0', 'Metric 1']
    assert items[items['Type'] == 'Table']['Name'].to_list() == ['Histogram 0', 'Histogram 1']

    # Various string properties
    for color in items['Color']:
        assert re.match(r'#[0-9A-Fa-f]{6}', color)
    for line_style in items['Line Style']:
        assert pd.isna(line_style) or line_style in AnalysisWorkstep._workstep_dashStyle_user_to_workstep.keys()
    for samples_display in items['Samples Display']:
        assert (pd.isna(samples_display) or samples_display in
                AnalysisWorkstep._workstep_sampleDisplay_user_to_workstep.keys())
    for axis_align in items['Axis Align']:
        assert pd.isna(axis_align) or axis_align in AnalysisWorkstep._workstep_rightAxis_user_to_workstep.keys()
    for axis_group in items['Axis Group']:
        assert pd.isna(axis_group) or axis_group in ['A', 'B', 'C', 'D', 'E', 'F']

    # Various numeric properties
    for lane in items['Line Width']:
        assert pd.isna(lane) or 0 < lane <= 10
    for lane_width in items['Line Width']:
        assert pd.isna(lane_width) or 0 < lane_width <= 10

    # Various boolean properties
    boolean_properties = ['Axis Auto Scale', 'Axis Show', 'Selected', 'Stack', 'Values']
    for boolean_property in boolean_properties:
        for prop_value in items[boolean_property]:
            assert pd.isna(prop_value) or prop_value in [True, False]


@pytest.mark.unit
def test_modify_display_items(empty_worksheet, empty_workstep, workstep):
    """Test that modifying the dataframe modifies the workstep stores."""
    original = workstep.display_items.copy()
    modified = original.drop(original[original['Selected'] == False].index).reset_index(drop=True)  # noqa: E712
    modified.at[0, 'Values'] = False
    modified.at[0, 'Axis Type'] = 'Logarithmic'
    modified.at[1, 'Line Width'] = 5.0
    modified.at[2, 'Selected'] = False
    modified.at[3, 'Lane'] = 2
    modified.at[4, 'Color'] = '#000000'
    empty_worksheet.display_items = modified

    # Check that the workstep stores were updated
    # Only one of each type should be present and they should have the modified values
    original_stores = workstep.get_workstep_stores()
    current_stores = empty_worksheet.current_workstep().get_workstep_stores()

    assert len(current_stores["sqTrendSeriesStore"]["items"]) == 1
    assert current_stores["sqTrendSeriesStore"]["items"][0]['name'] == 'Signal 1'
    assert current_stores["sqTrendSeriesStore"]["items"][0]['showDataLabels'] is False
    assert current_stores["sqTrendSeriesStore"]["items"][0]['yAxisType'] == "logarithmic"

    # verify no attributes were unintentionally thrown out
    original_attributes = {x for x in original_stores["sqTrendSeriesStore"]["items"][-1].keys() if isinstance(x, str)}
    current_attributes = {x for x in current_stores["sqTrendSeriesStore"]["items"][-1].keys() if isinstance(x, str)}
    assert original_attributes - {'autoDisabled', 'interpolationMethod'} == current_attributes

    assert len(current_stores["sqTrendConditionStore"]["items"]) == 1
    assert current_stores["sqTrendConditionStore"]["items"][0]['name'] == 'Condition 1'
    assert current_stores["sqTrendConditionStore"]["items"][0]['lineWidth'] == 5.0
    # since there's only one condition in this lane now, overlay should be gone
    with pytest.raises(KeyError):
        assert current_stores["sqTrendConditionStore"]["items"][0]['overlay'] == 1

    assert len(current_stores["sqTrendScalarStore"]["items"]) == 1
    assert current_stores["sqTrendScalarStore"]["items"][0]['name'] == 'Scalar 1'
    assert current_stores["sqTrendScalarStore"]["items"][0]['selected'] is False

    assert len(current_stores["sqTrendMetricStore"]["items"]) == 1
    assert current_stores["sqTrendMetricStore"]["items"][0]['name'] == 'Metric 1'
    assert current_stores["sqTrendMetricStore"]["items"][0]['lane'] == 2

    # verify y-axis min and max were not changed
    assert current_stores["sqTrendMetricStore"]["items"][0]['yAxisMin'] == 40
    assert current_stores["sqTrendMetricStore"]["items"][0]['yAxisMax'] == 60.5

    assert len(current_stores["sqTrendTableStore"]["items"]) == 1
    assert current_stores["sqTrendTableStore"]["items"][0]['name'] == 'Histogram 1'
    assert current_stores["sqTrendTableStore"]["items"][0]['color'] == '#000000'


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_overlay, expected_overlay",
    [
        ([1, None, None, None], [1, 2, 3, None]),  # if one condition is overlaid column, fill down the rest
        ([None, None, None, None], [None, None, None, None]),  # if conditions not overlaid, don't touch
        ([4, 3, 2, 1], [3, 2, 1, 1]),  # if gaps in overlay, reorder (signal doesn't count)
        ([2, 3, 1, None], [2, 3, 1, None]),  # if everything good, don't reorder
        ([4, 10, 2, 1], [2, 3, 1, 1]),  # if gaps in overlay, reorder (signal doesn't count)
        ([1], [np.nan])  # overlay not possible if only one condition in lane
    ]
)
def test_validate_and_fill_overlay_column(workstep, input_overlay, expected_overlay):
    test_data = pd.DataFrame({
        'Name': ['Condition 0', 'Condition 1', 'Condition 2', 'Signal 0'],
        'ID': ['00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000003',
               '00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000011'],
        'Type': ['Condition', 'Condition', 'Condition', 'Signal'],
        'Lane': [1, 1, 1, 1],
        'Selected': [False, True, False, False],
    })

    test_data = test_data.head(len(input_overlay))
    test_data['Overlay'] = input_overlay

    test_data = AnalysisWorkstep._validate_and_fill_overlay_column(test_data)
    expected = pd.Series(expected_overlay)
    assert_series_equal(expected, test_data['Overlay'], check_dtype=False, check_exact=False,
                        check_names=False)


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_overlay, expected_overlay",
    [
        # if overlay not enabled, keep it that way
        ([np.nan, np.nan, np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan, np.nan, np.nan]),
        # if only one condition in lane, disable overlay
        ([1, np.nan, np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan, np.nan, np.nan]),
        # fill overlay down if one condition is overlaid in a lane
        ([np.nan, np.nan, 1, np.nan, np.nan], [np.nan, 2, 1, 3, np.nan]),
    ]
)
def test_validate_and_fill_overlay_column_multiple_lanes(workstep, input_overlay, expected_overlay):
    test_data = pd.DataFrame({
        'Name': ['Condition 0', 'Condition 1', 'Condition 2', 'Condition 3', 'Signal 0'],
        'ID': ['00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000003',
               '00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000011',
               '00000000-0000-0000-0000-000000000012'],
        'Type': ['Condition', 'Condition', 'Condition', 'Condition', 'Signal'],
        'Lane': [1, 2, 2, 2, 2],
    })

    test_data = test_data.head(len(input_overlay))
    test_data['Overlay'] = input_overlay

    test_data = AnalysisWorkstep._validate_and_fill_overlay_column(test_data)
    expected = pd.Series(expected_overlay)
    assert_series_equal(expected, test_data['Overlay'], check_dtype=False, check_exact=False,
                        check_names=False)
