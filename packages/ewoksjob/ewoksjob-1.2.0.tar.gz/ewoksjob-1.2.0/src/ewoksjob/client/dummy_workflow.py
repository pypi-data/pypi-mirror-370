def result(value=False, filename=None):
    if filename:
        with open(filename, "w"):
            pass
    return value is None


def dummy_workflow():
    return {
        "graph": {"id": "sleepgraph", "schema_version": "1.0"},
        "nodes": [
            {
                "id": "sleep",
                "task_type": "method",
                "task_identifier": "time.sleep",
                "default_inputs": [{"name": 0, "value": 0}],
            },
            {
                "id": "result",
                "task_type": "method",
                "task_identifier": "ewoksjob.client.dummy_workflow.result",
                "default_inputs": [
                    {"name": "value", "value": None},
                    {"name": "filename", "value": None},
                ],
            },
        ],
        "links": [
            {
                "source": "sleep",
                "target": "result",
                "data_mapping": [
                    {"source_output": "return_value", "target_input": "value"}
                ],
            },
        ],
    }
