import pytest
import unittest
from unittest.mock import MagicMock
from fabric.dataagent.client._fabric_data_agent_mgmt import Datasource
from fabric.dataagent.client._fabric_data_agent_api import FabricDataAgentAPI
from fabric.dataagent.client._tagged_value import TaggedValue


class TestDatasource(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock(spec=FabricDataAgentAPI)
        self.datasource_id = "test_datasource_id"
        self.datasource = Datasource(self.mock_client, self.datasource_id)

    def test_init(self):
        self.assertEqual(self.datasource._client, self.mock_client)
        self.assertEqual(self.datasource._id, self.datasource_id)

    def test_repr(self):
        expected_repr = f"Datasource({self.datasource_id})"
        self.assertEqual(repr(self.datasource), expected_repr)

    def test_pretty_print(self):
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "display_name": "test_datasource",
                "elements": [
                    {
                        "display_name": "Element1",
                        "type": "semantic_model.table",
                        "is_selected": True,
                        "children": [],
                    },
                    {
                        "display_name": "Element2",
                        "type": "semantic_model.table",
                        "is_selected": False,
                        "children": [],
                    },
                ],
            },
            "etag",
        )
        self.datasource.pretty_print(include_type=True)

    def test_get_fewshots(self):
        self.mock_client.get_datasource_fewshots.return_value = TaggedValue(
            {
                "fewShots": [
                    {
                        "id": "1",
                        "question": "Q1",
                        "query": "Query1",
                        "state": "State1",
                        "embedding": "Embedding1",
                    },
                    {
                        "id": "2",
                        "question": "Q2",
                        "query": "Query2",
                        "state": "State2",
                        "embedding": "Embedding2",
                    },
                ]
            },
            "etag",
        )
        fewshots = self.datasource.get_fewshots()
        self.assertEqual(len(fewshots), 2)

    def test_add_fewshots(self):
        self.mock_client.get_datasource_fewshots.return_value = TaggedValue(
            {"fewShots": []}, "etag"
        )
        fewshot_id = self.datasource.add_fewshots({"Q1": "Query1"})

        self.mock_client.set_datasource_fewshots.assert_called_once()

    def test_remove_fewshot(self):
        self.mock_client.get_datasource_fewshots.return_value = TaggedValue(
            {
                "fewShots": [
                    {
                        "id": "1",
                        "question": "Q1",
                        "query": "Query1",
                        "state": "State1",
                        "embedding": "Embedding1",
                    }
                ]
            },
            "etag",
        )
        self.datasource.remove_fewshot("1")
        self.mock_client.set_datasource_fewshots.assert_called_once()

    def test_successful_update_configuration(self):
        self.mock_client.get_datasource.return_value = TaggedValue(
            {"type": "lakehouse_tables"}, "etag"
        )
        self.datasource.update_configuration(
            instructions="New instructions",
            schema_mode="New schema mode",
            user_description="New description",
        )
        self.mock_client.set_datasource.assert_called_once()

    def test_failing_update_configuration(self):
        self.mock_client.get_datasource.return_value = TaggedValue(
            {"type": "semantic_model"}, "etag"
        )
        with pytest.raises(ValueError):
            self.datasource.update_configuration(
                instructions="New instructions",
                schema_mode="New schema mode",
                user_description="New description",
            )

    def test_select0(self):
        # Case 1: 0 items selected
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "id": self.datasource_id,
                "elements": [
                    {
                        "display_name": "Element1",
                        "is_selected": False,
                        "type": "semantic_model.table",
                        "children": [],
                    }
                ],
            },
            "etag",
        )
        self.datasource.select("Element1")
        self.mock_client.set_datasource.assert_called_once()

    def test_select1(self):
        # Case 2: Path with 3 levels
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "id": self.datasource_id,
                "elements": [
                    {
                        "display_name": "Level1",
                        "is_selected": False,
                        "children": [
                            {
                                "display_name": "Level2",
                                "is_selected": False,
                                "children": [
                                    {
                                        "display_name": "Level3",
                                        "type": "warehouse_tables.table",
                                        "is_selected": False,
                                        "children": [],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
            "etag",
        )
        self.datasource.select("Level1", "Level2", "Level3")

        # Extract the actual call arguments
        actual_args = self.mock_client.set_datasource.call_args[0][0].value

        expected_args = {
            "id": self.datasource_id,
            "elements": [
                {
                    "display_name": "Level1",
                    "is_selected": False,
                    "children": [
                        {
                            "display_name": "Level2",
                            "is_selected": False,
                            "children": [
                                {
                                    "display_name": "Level3",
                                    "type": "warehouse_tables.table",
                                    "is_selected": True,
                                    "children": [],
                                }
                            ],
                        }
                    ],
                }
            ],
        }

        self.assertEqual(actual_args, expected_args)

    def test_unselect(self):
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "elements": [
                    {
                        "display_name": "Element1",
                        "is_selected": True,
                        "children": [],
                        "type": "lakehouse_tables.table",
                    }
                ]
            },
            "etag",
        )
        self.datasource.unselect("Element1")
        self.mock_client.set_datasource.assert_called_once()

    def test_select_parent(self):
        # Case: Selecting a parent element should mark all child elements as selected
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "id": self.datasource_id,
                "elements": [
                    {
                        "display_name": "dbo",
                        "is_selected": False,
                        "children": [
                            {
                                "display_name": "table1",
                                "type": "kusto.table",
                                "is_selected": False,
                                "children": [
                                    {
                                        "display_name": "col1",
                                        "is_selected": True,
                                        "children": [],
                                    },
                                    {
                                        "display_name": "col2",
                                        "is_selected": False,
                                        "children": [],
                                    },
                                    {
                                        "display_name": "col3",
                                        "is_selected": False,
                                        "children": [],
                                    },
                                ],
                            }
                        ],
                    }
                ],
            },
            "etag",
        )
        self.datasource.select("dbo", "table1")

        # Extract the actual call arguments
        actual_args = self.mock_client.set_datasource.call_args[0][0].value

        expected_args = {
            "id": self.datasource_id,
            "elements": [
                {
                    "display_name": "dbo",
                    "is_selected": False,
                    "children": [
                        {
                            "display_name": "table1",
                            "type": "kusto.table",
                            "is_selected": True,
                            "children": [
                                {
                                    "display_name": "col1",
                                    "is_selected": True,
                                    "children": [],
                                },
                                {
                                    "display_name": "col2",
                                    "is_selected": False,
                                    "children": [],
                                },
                                {
                                    "display_name": "col3",
                                    "is_selected": False,
                                    "children": [],
                                },
                            ],
                        }
                    ],
                }
            ],
        }

        self.assertEqual(actual_args, expected_args)

    def test_select_many(self):
        # Case: Selecting a parent element should mark all child elements as selected
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "id": self.datasource_id,
                "elements": [
                    {
                        "display_name": "dbo",
                        "is_selected": False,
                        "children": [
                            {
                                "display_name": "table1",
                                "type": "kusto.table",
                                "is_selected": False,
                                "children": [
                                    {
                                        "display_name": "col1",
                                        "is_selected": False,
                                        "children": [],
                                    },
                                ],
                            },
                            {
                                "display_name": "table2",
                                "type": "kusto.table",
                                "is_selected": False,
                                "children": [
                                    {
                                        "display_name": "col2",
                                        "is_selected": False,
                                        "children": [],
                                    },
                                ],
                            },
                            {
                                "display_name": "table3",
                                "type": "kusto.table",
                                "is_selected": False,
                                "children": [
                                    {
                                        "display_name": "col3",
                                        "is_selected": False,
                                        "children": [],
                                    },
                                ],
                            }
                        ],
                    }
                ],
            },
            "etag",
        )
        self.datasource.select(["dbo", "table1"], ["dbo", "table3"])

        # Extract the actual call arguments
        actual_args = self.mock_client.set_datasource.call_args[0][0].value

        expected_args = {
            "id": self.datasource_id,
            "elements": [
                {
                    "display_name": "dbo",
                    "is_selected": False,
                    "children": [
                        {
                            "display_name": "table1",
                            "type": "kusto.table",
                            "is_selected": True,
                            "children": [
                                {
                                    "display_name": "col1",
                                    "is_selected": False,
                                    "children": [],
                                },
                            ],
                        },
                        {
                            "display_name": "table2",
                            "type": "kusto.table",
                            "is_selected": False,
                            "children": [
                                {
                                    "display_name": "col2",
                                    "is_selected": False,
                                    "children": [],
                                },
                            ],
                        },
                        {
                            "display_name": "table3",
                            "type": "kusto.table",
                            "is_selected": True,
                            "children": [
                                {
                                    "display_name": "col3",
                                    "is_selected": False,
                                    "children": [],
                                },
                            ],
                        }
                    ],
                }
            ],
        }

        self.assertEqual(actual_args, expected_args)

    def test_select_column(self):
        # Case 1: 0 items selected
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "id": self.datasource_id,
                "elements": [
                    {
                        "display_name": "Element1",
                        "is_selected": False,
                        "type": "semantic_model.column",
                        "children": [],
                    }
                ],
            },
            "etag",
        )

        with pytest.raises(ValueError):
            self.datasource.select("Element1")

    def test_successful_update_description(self):
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "type": "lakehouse_tables",
                "elements": [
                    {
                        "display_name": "dbo",
                        "type": "lakehouse_tables.schema",
                        "children": [
                            {
                                "display_name": "table1",
                                "type": "lakehouse_tables.table",
                                "description": None,
                                "children": [
                                    {
                                        "display_name": "col1",
                                        "type": "lakehouse_tables.column",
                                        "description": None,
                                        "children": [],
                                    },
                                ],
                            }
                        ],
                    }
                ],
            },
            "etag",
        )

        self.datasource.update_description(
            {
                ("dbo", "table1"): "table1 description",
                ("dbo", "table1", "col1"): "col1 description",
            }
        )

        # Check that set_datasource was called and descriptions were updated
        args = self.mock_client.set_datasource.call_args[0][0].value
        table = args["elements"][0]["children"][0]
        col = table["children"][0]
        self.assertEqual(table["description"], "table1 description")
        self.assertEqual(col["description"], "col1 description")

    def test_update_description_unsupported_datasource_type(self):
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "type": "semantic_model",
                "elements": [],
            },
            "etag",
        )
        with pytest.raises(ValueError):
            self.datasource.update_description({("dbo", "table1"): "desc"})

    def test_update_description_path_not_found(self):
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "type": "lakehouse_tables",
                "elements": [
                    {
                        "display_name": "dbo",
                        "type": "lakehouse_tables.schema",
                        "children": [
                            {
                                "display_name": "table1",
                                "type": "lakehouse_tables.table",
                                "description": None,
                                "children": [],
                            }
                        ],
                    }
                ],
            },
            "etag",
        )
        with pytest.raises(ValueError):
            self.datasource.update_description({("dbo", "table2"): "desc"})

    def test_update_description_unsupported_datasource(self):
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "type": "kusto",
                "elements": [],
            },
            "etag",
        )
        with pytest.raises(ValueError):
            self.datasource.update_description({("dbo", "table1"): "desc"})

    def test_update_description_wrong_type(self):
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "type": "lakehouse_tables",
                "elements": [
                    {
                        "display_name": "dbo",
                        "type": "lakehouse_tables.schema",
                        "children": [
                            {
                                "display_name": "file1",
                                "type": "lakehouse_files.directory",
                                "description": None,
                                "children": [],
                            }
                        ],
                    }
                ],
            },
            "etag",
        )
        with pytest.raises(ValueError):
            self.datasource.update_description({("dbo", "file1"): "desc"})

    def test_set_is_selected_all(self):
        # Test _set_is_selected_all for selecting all elements
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "elements": [
                    {"display_name": "Element1", "type": "lakehouse_tables.table", "is_selected": False, "children": []},
                    {"display_name": "Element2", "type": "warehouse_tables.table", "is_selected": False, "children": []},
                ]
            },
            "etag",
        )
        # Use _set_is_selected_all directly
        config = self.datasource._set_is_selected_all(True)
        for elem in config.value["elements"]:
            self.assertTrue(elem["is_selected"])

    def test_set_is_selected_invalid_type(self):
        # Test _set_is_selected with invalid type
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "elements": [
                    {"display_name": "Element1", "type": "not_selectable", "is_selected": False, "children": []}
                ]
            },
            "etag",
        )
        with self.assertRaises(ValueError):
            self.datasource._set_is_selected(True, "Element1")

    def test_set_is_selected_path_not_found(self):
        # Test _set_is_selected with a path that does not exist
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "elements": [
                    {"display_name": "Element1", "type": "lakehouse_tables.table", "is_selected": False, "children": []}
                ]
            },
            "etag",
        )
        # Should warn but not raise
        self.datasource._set_is_selected(True, "NonExistent")

    def test_set_is_selected_all_with_children(self):
        # Test _set_is_selected_all with nested children
        self.mock_client.get_datasource.return_value = TaggedValue(
            {
                "elements": [
                    {
                        "display_name": "Parent",
                        "type": "lakehouse_tables.table",
                        "is_selected": False,
                        "children": [
                            {"display_name": "Child", "type": "lakehouse_tables.table", "is_selected": False, "children": []}
                        ],
                    }
                ]
            },
            "etag",
        )
        config = self.datasource._set_is_selected_all(True)
        self.assertTrue(config.value["elements"][0]["is_selected"])
        self.assertTrue(config.value["elements"][0]["children"][0]["is_selected"])
