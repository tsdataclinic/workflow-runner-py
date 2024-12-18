import json
import unittest

from pathlib import Path

from workflow_runner_py.workflow_runner import process_workflow
from workflow_runner_py.models.workflow_schema import WorkflowSchema

DIR = Path(__file__).resolve().parent
SCHEMA_PATH = DIR / "sample_schema/workflow_schema.json"
GOOD_DATA_PATH = DIR / "data/good.csv"
BAD_DATA_PATH = DIR / "data/bad.csv"


class TestWorkflowRunner(unittest.TestCase):

    def setUp(self):
        self.schema = WorkflowSchema.model_validate(json.loads(SCHEMA_PATH.read_text()))

    def test_on_good_data(self):
        failures = process_workflow(
            "tests/data/good.csv", 
            param_values={
                "allowed_subjects": ["Math", "History", "Science"],
            }, 
            schema=self.schema
        )
        self.assertEqual(failures, [])

    def test_on_bad_data(self):
        failures = process_workflow(
            "tests/data/bad.csv", 
            param_values={
                "allowed_subjects": ["Math", "History", "Science"],
            }, 
            schema=self.schema
        )
        
        self.assertEqual(len(failures), 2)
