from unittest.mock import MagicMock

import pandas as pd
import pytest

from seeq.spy._errors import *
from seeq.spy.workbooks import AnalysisWorkstep
from seeq.spy.workbooks._table_toolbar import (
    TableToolbar, SimpleTableToolbar, ConditionTableToolbar, ConditionTableColumns
)
from seeq.spy.workbooks.tests.table_toolbar_fixtures import empty_worksheet, empty_workstep, worksheet, workstep


@pytest.mark.unit
def test_table_toolbar_from_worksheet(empty_worksheet):
    """Test the TableToolbar from worksheet."""
    assert isinstance(empty_worksheet.condition_table_toolbar, ConditionTableToolbar)
    table_toolbar = empty_worksheet.condition_table_toolbar

    assert isinstance(table_toolbar._getter_workstep, AnalysisWorkstep)
    assert isinstance(table_toolbar._setter_workstep, AnalysisWorkstep)

    # Test with mocked methods
    empty_worksheet.current_workstep = MagicMock()
    current_workstep = table_toolbar._getter_workstep
    assert isinstance(current_workstep, MagicMock)
    empty_worksheet.current_workstep.assert_called_once()

    empty_worksheet.branch_current_workstep = MagicMock()
    branch_current_workstep = table_toolbar._setter_workstep
    assert isinstance(branch_current_workstep, MagicMock)
    empty_worksheet.branch_current_workstep.assert_called_once()


@pytest.mark.unit
def test_table_toolbar_from_workstep(empty_workstep):
    """Test the TableToolbar from workstep."""
    assert isinstance(empty_workstep.condition_table_toolbar, ConditionTableToolbar)
    table_toolbar = empty_workstep.condition_table_toolbar

    assert table_toolbar._getter_workstep == empty_workstep
    assert table_toolbar._setter_workstep == empty_workstep


@pytest.mark.unit
def test_table_builder_get_table_store(worksheet, workstep):
    """Test the get_table_store method."""
    table_toolbar = TableToolbar(worksheet)
    table_store = table_toolbar._get_table_store(table_toolbar._getter_workstep)

    assert isinstance(table_store, dict)
    assert table_store == worksheet.current_workstep().get_workstep_stores()["sqTableBuilderStore"]


@pytest.mark.unit
def test_table_toolbar_view(empty_worksheet, empty_workstep):
    """Test the view property of TableToolbar."""
    # Test from worksheet
    table_toolbar = TableToolbar(empty_worksheet)
    table_toolbar.view = "Table"
    assert table_toolbar.view == empty_worksheet.view
    assert empty_worksheet.view == "Table"

    # Test from workstep
    table_toolbar = SimpleTableToolbar(empty_workstep)
    table_toolbar.view = "Table"
    assert table_toolbar.view == empty_workstep.view
    assert empty_workstep.view == "Table"


@pytest.mark.unit
def test_table_toolbar_table_mode(worksheet):
    """Test table_mode property for TableToolbar."""
    table_toolbar = TableToolbar(worksheet)

    assert table_toolbar.table_mode == worksheet.table_mode

    table_toolbar.table_mode = 'simple'
    assert table_toolbar.table_mode == 'simple'
    assert worksheet.table_mode == 'simple'


@pytest.mark.unit
def test_table_toolbar_transpose(worksheet):
    """Test transpose property for TableToolbars."""
    # SimpleTableToolbar
    simple_toolbar = SimpleTableToolbar(worksheet)

    assert simple_toolbar.transpose is False

    simple_toolbar.transpose = True
    assert simple_toolbar.transpose is True
    assert simple_toolbar._get_table_store(simple_toolbar._getter_workstep)["isTransposed"]["simple"] is True

    # Verify type checking
    with pytest.raises(SPyTypeError, match="'transpose' must be a boolean"):
        simple_toolbar.transpose = "invalid"

    # ConditionTableToolbar
    condition_toolbar = ConditionTableToolbar(worksheet)
    assert condition_toolbar.transpose is True

    condition_toolbar.transpose = False
    assert condition_toolbar.transpose is False
    assert condition_toolbar._get_table_store(condition_toolbar._getter_workstep)["isTransposed"]["condition"] is False

    # Verify type checking
    with pytest.raises(SPyTypeError, match="'transpose' must be a boolean"):
        condition_toolbar.transpose = "invalid"


@pytest.mark.unit
def test_table_toolbar_striped(worksheet):
    """Test striped property for TableToolbars."""
    # SimpleTableToolbar
    simple_toolbar = SimpleTableToolbar(worksheet)

    assert simple_toolbar.striped is False

    simple_toolbar.striped = True
    assert simple_toolbar.striped is True
    assert simple_toolbar._get_table_store(simple_toolbar._getter_workstep)["isTableStriped"]["simple"] is True

    # Verify type checking
    with pytest.raises(SPyTypeError, match="'striped' must be a boolean"):
        simple_toolbar.striped = "invalid"

    # ConditionTableToolbar
    condition_toolbar = ConditionTableToolbar(worksheet)
    assert condition_toolbar.striped is False

    condition_toolbar.striped = False
    assert condition_toolbar.striped is False
    assert (condition_toolbar._get_table_store(condition_toolbar._getter_workstep)["isTableStriped"]["condition"] is
            False)

    # Verify type checking
    with pytest.raises(SPyTypeError, match="'striped' must be a boolean"):
        condition_toolbar.striped = "invalid"


@pytest.mark.unit
def test_table_toolbar_group(worksheet):
    """Test group property for TableToolbars."""
    # SimpleTableToolbar
    simple_toolbar = SimpleTableToolbar(worksheet)

    assert simple_toolbar.group is False

    simple_toolbar.group = True
    assert simple_toolbar.group is True
    assert simple_toolbar._get_table_store(simple_toolbar._getter_workstep)["autoGroupColumn"]["simple"] == {}

    # Verify type checking
    with pytest.raises(SPyTypeError, match="'group' must be a boolean"):
        simple_toolbar.group = "invalid"

    # ConditionTableToolbar
    condition_toolbar = ConditionTableToolbar(worksheet)
    assert condition_toolbar.group is True

    condition_toolbar.group = False
    assert condition_toolbar.group is False
    assert (condition_toolbar._get_table_store(condition_toolbar._getter_workstep)["autoGroupColumn"]["condition"] is
            None)

    # Verify type checking
    with pytest.raises(SPyTypeError, match="'group' must be a boolean"):
        condition_toolbar.group = "invalid"


@pytest.mark.unit
def test_table_toolbar_columns(worksheet):
    condition_toolbar = worksheet.condition_table_toolbar
    assert isinstance(condition_toolbar.columns, ConditionTableColumns)

    # test column getters with both keys and index
    assert condition_toolbar.columns['Batch ID'] == condition_toolbar.columns[1]

    with pytest.raises(IndexError, match="Column with key 'Test' not found"):
        condition_toolbar.columns['Test']

    with pytest.raises(IndexError, match='list index out of range'):
        condition_toolbar.columns[9000]


@pytest.mark.unit
def test_condition_table_toolbar_add_remove_rows(worksheet):
    """Test adding and removing rows in ConditionTableToolbar."""
    condition_toolbar = ConditionTableToolbar(worksheet)

    # column labels
    column_labels = condition_toolbar.add_row_column_labels()
    assert 'name' in condition_toolbar.columns._get_columns()
    assert column_labels._get_column_definition() == {
        "key": "name",
        "headerTextAlign": "center",
        "headerTextStyle": [
            "bold"
        ],
        "textStyle": [
            "bold"
        ],
        "headerBackgroundColor": "#000000",
        "header": "Column Label Header Cell",
        "backgroundColor": "#FF0000",
        "headerTextColor": "#ffffff",
        "textColor": "#ffffff"
    }

    condition_toolbar.remove_row_column_labels()
    assert 'name' not in condition_toolbar.columns._get_columns()

    # unit of measure
    assert 'valueUnitOfMeasure' in condition_toolbar.columns._get_columns()
    column_labels = condition_toolbar.remove_row_unit_of_measure()
    assert 'valueUnitOfMeasure' not in condition_toolbar.columns._get_columns()

    # custom text
    # add a row of custom text, check that the column definition is correct
    custom_row_1 = condition_toolbar.add_row_custom_text(['Column 1', 'Column 2'])

    custom_row_1_key = custom_row_1.key
    assert custom_row_1._get_column_definition() == {
        "key": custom_row_1_key,
        "type": "text",
        "headerTextAlign": "center",
        "headerTextStyle": [
            "bold"
        ],
        "cells": {
            "0F021DAE-E12E-EC10-819E-200AD2370298": 'Column 1',
            "Batch ID": 'Column 2'
        },
    }

    custom_row_2 = condition_toolbar.add_row_custom_text({
        '0F021DAE-E12E-EC10-819E-200AD2370298': 'Column 1',
        'Batch ID': 'Column 2',
        'startTime': 'Column 3',
        'Priority Name': 'Column 4'
    })
    custom_row_2_key = custom_row_2.key
    assert custom_row_2._get_column_definition() == {
        "key": custom_row_2_key,
        "type": "text",
        "headerTextAlign": "center",
        "headerTextStyle": [
            "bold"
        ],
        "cells": {
            "0F021DAE-E12E-EC10-819E-200AD2370298": 'Column 1',
            "Batch ID": 'Column 2',
            "startTime": 'Column 3',
            "Priority Name": 'Column 4'
        }}
    # remove the custom text rows and verify they're gone
    condition_toolbar.remove_row_custom_text()
    assert custom_row_1_key not in condition_toolbar.columns._get_columns()
    assert custom_row_2_key not in condition_toolbar.columns._get_columns()
    assert "hPiM9Bh8nXuXCTM7BXg2pQ" not in condition_toolbar.columns._get_columns()
    # check that giving too long of a list raises an error
    with pytest.raises(SPyValueError, match="6 column values provided, but only 5 columns exist"):
        condition_toolbar.add_row_custom_text(['Column 1', 'Column 2', 'Column 3', 'Column 4', 'Column 5', 'Column 6'])


@pytest.mark.unit
def test_condition_table_toolbar_column_property(worksheet):
    """Test adding and removing property columns in ConditionTableToolbar."""
    condition_toolbar = ConditionTableToolbar(worksheet)

    # get existing capsule property column
    batch_id_column = condition_toolbar.columns.add_column_property('Batch ID')
    batch_id_column_index = condition_toolbar.columns.index('Batch ID')
    assert batch_id_column == condition_toolbar.columns[batch_id_column_index]

    # add new capsule property column
    test_column = condition_toolbar.columns.add_column_property('Test Column')
    assert 'Test Column' in condition_toolbar.columns
    assert test_column._get_column_definition() == {
        "key": "Test Column",
        "type": "capsuleProperty",
        "headerTextAlign": "center",
        "headerTextStyle": [
            "bold"
        ]
    }
    condition_toolbar.columns.remove_column_property('Test Column')
    assert 'Test Column' not in condition_toolbar.columns

    # add reserved property column
    name_column = condition_toolbar.columns.add_column_property('name')
    assert 'nameExpression' in condition_toolbar.columns._get_columns()
    assert name_column._get_column_definition() == {
        "key": "nameExpression",
        'headerTextAlign': 'center',
        'headerTextStyle': [
            "bold"
        ]
    }
    # ensure we can remove the same way
    condition_toolbar.columns.remove_column_property('name')
    assert 'nameExpression' not in condition_toolbar.columns._get_columns()


@pytest.mark.unit
def test_condition_table_toolbar_column_statistic(worksheet):
    """Test adding and removing signal statistic columns in ConditionTableToolbar."""
    condition_toolbar = ConditionTableToolbar(worksheet)

    # get existing statistic column
    max_column = condition_toolbar.columns.add_column_statistic('09FD94FB-3DE9-4B2C-8FEE-3BA35DD30FE4', 'maximum')
    max_column_index = condition_toolbar.columns.index('statistics.maximum_09FD94FB-3DE9-4B2C-8FEE-3BA35DD30FE4')
    assert max_column == condition_toolbar.columns[max_column_index]

    assert max_column._get_column_definition() == {
        "key": "statistics.maximum_09FD94FB-3DE9-4B2C-8FEE-3BA35DD30FE4",
        "statisticKey": "statistics.maximum",
        "signalId": "09FD94FB-3DE9-4B2C-8FEE-3BA35DD30FE4",
        "headerTextAlign": "center",
        "headerTextStyle": [
            "bold"
        ]
    }

    # add new statistic column
    end_val_column = condition_toolbar.columns.add_column_statistic('09FD94FB-3DE9-4B2C-8FEE-3BA35DD30FE4',
                                                                    'value at end')
    assert 'statistics.endValue_09FD94FB-3DE9-4B2C-8FEE-3BA35DD30FE4' in condition_toolbar.columns
    assert end_val_column._get_column_definition() == {
        "key": "statistics.endValue_09FD94FB-3DE9-4B2C-8FEE-3BA35DD30FE4",
        "statisticKey": "statistics.endValue",
        "signalId": "09FD94FB-3DE9-4B2C-8FEE-3BA35DD30FE4",
        "headerTextAlign": "center",
        "headerTextStyle": [
            "bold"
        ]
    }

    # add a statistic column for item not in details pane
    with pytest.raises(SPyValueError, match="Item with ID 12345678-1234-1234-1234-123456789012 must be added to the "
                                            "details pane before adding as a column"):
        condition_toolbar.columns.add_column_statistic('12345678-1234-1234-1234-123456789012', 'maximum')

    # add a statistic that doesn't exist
    with pytest.raises(SPyValueError):
        condition_toolbar.columns.add_column_statistic('09FD94FB-3DE9-4B2C-8FEE-3BA35DD30FE4', 'coolness')

    # adding multiple at a time
    signals = worksheet.display_items[worksheet.display_items['Type'] == 'Signal']
    condition_toolbar.columns.add_column_statistic(signals, 'average')
    assert 'statistics.average_9EBD52A0-55F8-4806-BB49-A3519DEF99DE' in condition_toolbar.columns

    # add statistic column for a condition
    with pytest.raises(SPyValueError, match="Item with ID 0F021DAD-3901-EE30-91F8-B0306B7563A6 is not a signal"):
        condition_toolbar.columns.add_column_statistic('0F021DAD-3901-EE30-91F8-B0306B7563A6', 'maximum')

    # remove statistic column
    condition_toolbar.columns.remove_column_statistic('9EBD52A0-55F8-4806-BB49-A3519DEF99DE', 'average')
    assert 'statistics.average_9EBD52A0-55F8-4806-BB49-A3519DEF99DE' not in condition_toolbar.columns

    with pytest.raises(SPyValueError, match="Items must be a non-empty list, DataFrame, Series, or string"):
        condition_toolbar.columns.add_column_statistic([], 'maximum')


@pytest.mark.unit
def test_condition_table_toolbar_column_metric(worksheet):
    """Test retrieving metric column"""
    condition_toolbar = ConditionTableToolbar(worksheet)
    # get existing metric column
    assert "0F021DAE-E12E-EC10-819E-200AD2370298" in condition_toolbar.columns
    metric_column_index = condition_toolbar.columns.index('0F021DAE-E12E-EC10-819E-200AD2370298')
    metric_column = condition_toolbar.columns[metric_column_index]
    assert metric_column.metric_id == "0F021DAE-E12E-EC10-819E-200AD2370298"
    assert metric_column.type is None


@pytest.mark.unit
def test_condition_table_toolbar_grouped_columns(worksheet):
    """Test adding and removing grouped columns in ConditionTableToolbar."""
    condition_toolbar = ConditionTableToolbar(worksheet)
    # check which columns are currently grouped in the workstep
    batch_id_column = condition_toolbar.columns.add_column_property('Batch ID')
    assert condition_toolbar.columns.grouped_columns == [batch_id_column]
    assert batch_id_column.group_order == 0
    assert batch_id_column.grouping is True
    # assign new grouped columns and check the workstep
    priority_name_column = condition_toolbar.columns.add_column_property('Priority Name')
    assert priority_name_column.grouping is False
    assert priority_name_column.group_order is None

    condition_toolbar.columns.grouped_columns = [priority_name_column, batch_id_column]
    assert condition_toolbar.columns.grouped_columns == [priority_name_column, batch_id_column]
    assert priority_name_column.group_order == 0
    assert priority_name_column.grouping is True
    assert batch_id_column.group_order == 1
    assert batch_id_column.grouping is True

    # remove one of the grouped columns and verify the group order adjusts
    condition_toolbar.columns.grouped_columns = [batch_id_column]
    assert condition_toolbar.columns.grouped_columns == [batch_id_column]
    assert batch_id_column.group_order == 0
    assert batch_id_column.grouping is True
    assert priority_name_column.grouping is False
    assert priority_name_column.group_order is None

    # remove all grouped columns
    condition_toolbar.columns.grouped_columns = []
    assert condition_toolbar.columns.grouped_columns == []
    assert batch_id_column.group_order is None
    assert batch_id_column.grouping is False


@pytest.mark.unit
def test_condition_table_toolbar_column_attributes(worksheet):
    """Test the attributes that can be given to condition table columns"""
    condition_toolbar = ConditionTableToolbar(worksheet)
    # get existing capsule property column and verify settings correct
    batch_id_column = condition_toolbar.columns.add_column_property('Batch ID')
    assert batch_id_column.header is None
    assert batch_id_column.header_text_align == 'center'
    assert batch_id_column.header_text_style == ['bold']
    assert batch_id_column.text_align is None
    assert batch_id_column.text_style is None
    assert batch_id_column.width is None
    assert batch_id_column.aggregation_function is None

    # set new attributes and verify
    batch_id_column.header = 'Batch ID Header'
    batch_id_column.header_text_align = 'left'
    batch_id_column.header_text_style = ['italic']
    batch_id_column.text_align = 'left'
    batch_id_column.text_style = ['italic']
    batch_id_column.aggregation_function = 'sum'
    batch_id_column.width = 100

    # check that the attributes were set correctly
    assert batch_id_column._get_column_definition() == {
        "key": "Batch ID",
        "type": "capsuleProperty",
        "header": "Batch ID Header",
        "style": "string",
        "backingTableColumn": "item id.properties.Batch ID",
        "headerTextAlign": "left",
        "textAlign": "left",
        "headerTextStyle": [
            "italic"
        ],
        "textStyle": [
            "italic"
        ],
        "grouping": True,
        "rowGroupOrder": 0,
        "aggregationFunction": "sum",
        "width": 100
    }

    # check that setting invalid values raises errors
    with pytest.raises(SPyTypeError, match="'header' must be a string"):
        batch_id_column.header = 123

    with pytest.raises(SPyValueError):
        batch_id_column.header_text_align = "a little to the left"

    with pytest.raises(SPyValueError):
        batch_id_column.header_text_style = ["bold", "italian"]

    with pytest.raises(SPyValueError):
        batch_id_column.aggregation_function = "not a function"

    # verify key, type are read-only
    with pytest.raises(SPyValueError, match="'key' is read-only"):
        batch_id_column.key = "new key"

    with pytest.raises(SPyValueError, match="'type' is read-only"):
        batch_id_column.type = "new type"


@pytest.mark.unit
def test_trend_toolbar_color_column_output(worksheet):
    """Test trend toolbar output for various Color column scenarios."""
    # No 'Color' column, all should be displayed as None
    if 'Color' in worksheet.display_items.columns:
        worksheet.display_items = worksheet.display_items.drop(columns=['Color'])
    output = str(worksheet.trend_toolbar)
    assert output.count("Color: None") == len(worksheet.display_items)

    # Some items are given a 'Color', some are not (alternating None and 'Blue')
    items = worksheet.display_items.copy()
    items['Color'] = [None if i % 2 == 0 else 'Blue' for i in range(len(items))]
    worksheet.display_items = items
    output = str(worksheet.trend_toolbar)
    assert output.count("Color: Blue") == sum(c == 'Blue' for c in items['Color'])
    assert output.count("Color: None") == sum(c is None or pd.isna(c) for c in items['Color'])

    # All items with 'Color' as None
    items['Color'] = None
    worksheet.display_items = items
    output = str(worksheet.trend_toolbar)
    assert output.count("Color: None") == len(items)

    # All items have a valid color ('Red')
    items['Color'] = 'Red'
    worksheet.display_items = items
    output = str(worksheet.trend_toolbar)
    assert output.count("Color: Red") == len(items)
