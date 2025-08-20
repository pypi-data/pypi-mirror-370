import pytest

from seeq.spy.workbooks import AnalysisWorksheet, AnalysisWorkstep, Analysis


@pytest.fixture
def empty_worksheet() -> AnalysisWorksheet:
    workbook = Analysis()
    worksheet = AnalysisWorksheet(workbook)
    worksheet.current_workstep().definition["Data"]["version"] = 71
    return worksheet


@pytest.fixture
def empty_workstep() -> AnalysisWorkstep:
    workstep = AnalysisWorkstep()
    workstep.definition["Data"]["version"] = 71
    return workstep


@pytest.fixture
def workstep(empty_worksheet) -> AnalysisWorkstep:
    workstep = empty_worksheet.current_workstep()
    # The below stores are from a real workstep from Workstep Version 71 (2025-04). Update as needed.
    workstep.definition["Data"]["version"] = 71
    workstep.get_workstep_stores()["sqTableBuilderStore"] = {
        "mode": "condition",
        "headers": {
            "condition": {
                "type": "startEnd",
                "format": "lll"
            },
            "simple": {
                "type": "startEnd",
                "format": ""
            }
        },
        "columns": {
            "condition": [
                {
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
                },
                {
                    "key": "0F021DAE-E12E-EC10-819E-200AD2370298",
                    "metricId": "0F021DAE-E12E-EC10-819E-200AD2370298",
                    "headerTextAlign": "center",
                    "headerTextStyle": [
                        "bold"
                    ],
                    "width": 131,
                    "aggregationFunction": "sum"
                },
                {
                    "key": "Batch ID",
                    "type": "capsuleProperty",
                    "style": "string",
                    "backingTableColumn": "item id.properties.Batch ID",
                    "headerTextAlign": "center",
                    "headerTextStyle": [
                        "bold"
                    ],
                    "grouping": True,
                    "rowGroupOrder": 0
                },
                {
                    "key": "startTime",
                    "headerTextAlign": "center",
                    "headerTextStyle": [
                        "bold"
                    ]
                },
                {
                    "key": "Priority Name",
                    "type": "capsuleProperty",
                    "style": "string",
                    "backingTableColumn": "item id.properties.Priority Name",
                    "headerTextAlign": "center",
                    "headerTextStyle": [
                        "bold"
                    ]
                },
                {
                    "key": "valueUnitOfMeasure",
                    "headerTextAlign": "center",
                    "headerTextStyle": [
                        "bold"
                    ]
                },
                {
                    "key": "hPiM9Bh8nXuXCTM7BXg2pQ",
                    "type": "text",
                    "headerTextAlign": "center",
                    "headerTextStyle": [
                        "bold"
                    ],
                    "cells": {
                        "0F021DAE-E12E-EC10-819E-200AD2370298": "Column 1",
                        "Batch ID": "Column 2",
                        "startTime": "Column 3",
                        "Priority Name": "Column 4"
                    },
                    "backgroundColor": "#ffffff",
                    "header": "Custom Text Header Cell"
                },
                {
                    "key": "statistics.maximum_09FD94FB-3DE9-4B2C-8FEE-3BA35DD30FE4",
                    "statisticKey": "statistics.maximum",
                    "signalId": "09FD94FB-3DE9-4B2C-8FEE-3BA35DD30FE4",
                    "headerTextAlign": "center",
                    "headerTextStyle": [
                        "bold"
                    ]
                }
            ],
            "simple": [
                {
                    "key": "name",
                    "accessor": "name",
                    "propertyName": "Name",
                    "style": "string",
                    "title": "NAME",
                    "shortTitle": "NAME",
                    "backingTableColumn": "item id.properties.name",
                    "headerTextAlign": "center",
                    "headerTextStyle": [
                        "bold"
                    ]
                },
                {
                    "key": "asset",
                    "headerTextAlign": "center",
                    "headerTextStyle": [
                        "bold"
                    ]
                },
                {
                    "key": "statistics.average",
                    "title": "STATISTICS.AVERAGE.LONG",
                    "shortTitle": "STATISTICS.AVERAGE.SHORT",
                    "style": "decimal",
                    "stat": "average()",
                    "invalidsFirst": True,
                    "columnSuffix": "Average",
                    "headerTextAlign": "center",
                    "headerTextStyle": [
                        "bold"
                    ]
                },
                {
                    "key": "statistics.maximum",
                    "headerTextAlign": "center",
                    "headerTextStyle": [
                        "bold"
                    ]
                },
                {
                    "key": "Formula",
                    "type": "property",
                    "style": "string",
                    "backingTableColumn": "item id.properties.Formula",
                    "headerTextAlign": "center",
                    "headerTextStyle": [
                        "bold"
                    ]
                }
            ]
        },
        "otherColumns": {
            "condition": {},
            "simple": {}
        },
        "autoGroupColumn": {
            "condition": {}
        },
        "rowGroupPaths": {
            "condition": [],
            "simple": []
        },
        "isTransposed": {
            "condition": True,
            "simple": False
        },
        "assetId": {},
        "isHomogenizeUnits": {
            "condition": False,
            "simple": False
        },
        "hasMoreData": False,
        "isMigrating": False,
        "chartView": {
            "enabled": False,
            "settings": {
                "title": "",
                "legend": True,
                "dataLabels": True,
                "categoryLabels": True,
                "rows": [],
                "columns": [],
                "categoryColumns": [
                    "name"
                ],
                "showSettings": False,
                "position": {
                    "x": 100,
                    "y": 100
                }
            },
            "conditionEnabled": False
        },
        "useSignalColorsInChart": False,
        "assetPaths": [
            {
                "id": "55jRW-epNfWBmaPe4Pw88A",
                "enabled": False,
                "backingTableColumn": "Ancestor.properties.name"
            }
        ],
        "isFormulaAcrossTable": False,
        "isFormulaAcrossTableProcessing": False,
        "isTableStriped": {
            "condition": False
        }
    }

    workstep.get_workstep_stores()["sqTrendSeriesStore"] = {
        "items": [
            {
                "axisAlign": "A",
                "axisAutoScale": True,
                "lane": 2,
                "rightAxis": False,
                "dashStyle": "Solid",
                "lineWidth": 1,
                "autoDisabled": False,
                "axisVisibility": True,
                "yAxisType": "linear",
                "sampleDisplayOption": "line",
                "id": "09FD94FB-3DE9-4B2C-8FEE-3BA35DD30FE4",
                "name": "Reactor Temperature",
                "selected": False,
                "color": "#4055A3",
                "interpolationMethod": "Linear"
            },
            {
                "axisAlign": "B",
                "axisAutoScale": True,
                "lane": 3,
                "rightAxis": False,
                "dashStyle": "Solid",
                "lineWidth": 1,
                "autoDisabled": False,
                "axisVisibility": True,
                "yAxisType": "linear",
                "sampleDisplayOption": "line",
                "id": "9EBD52A0-55F8-4806-BB49-A3519DEF99DE",
                "name": "Solution Concentration",
                "selected": False,
                "color": "#9D248F",
                "interpolationMethod": "Linear"
            }
        ],
        "editingId": None,
        "previewSeriesDefinition": {}
    }
    workstep.get_workstep_stores()["sqTrendConditionStore"] = {
        "items": [
            {
                "lane": 1,
                "lineWidth": 1,
                "autoDisabled": False,
                "id": "0F021DAD-3901-EE30-91F8-B0306B7563A6",
                "name": "Batches",
                "selected": False,
                "color": "#068C45"
            }
        ]
    }
    workstep.get_workstep_stores()["sqTrendScalarStore"] = {
        "items": []
    }
    workstep.get_workstep_stores()["sqTrendMetricStore"] = {
        "originalParameters": [],
        "advancedParametersCollapsed": True,
        "measuredItem": {
            "predicate": [
                "name",
                "measuredItem"
            ]
        },
        "boundingCondition": {
            "predicate": [
                "name",
                "boundingCondition"
            ]
        },
        "processType": "Simple",
        "aggregationOperator": {
            "key": None,
            "timeUnits": "s"
        },
        "duration": {},
        "period": {},
        "thresholds": {}
    }
    return workstep


@pytest.fixture
def worksheet(workstep) -> AnalysisWorksheet:
    return workstep.worksheet
