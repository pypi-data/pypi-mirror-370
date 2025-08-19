import json
from pathlib import Path
from unittest import TestCase

from easys_ordermanager.v1.serializer import Serializer


class SerializerV1TestCase(TestCase):
    def setUp(self):
        example_path = Path(__file__).parent / "example.json"
        with example_path.open() as f:
            self.fixture = json.load(f)

    def test_validate_data(self):
        s = Serializer(data=self.fixture)
        self.assertTrue(s.is_valid(raise_exception=True))
