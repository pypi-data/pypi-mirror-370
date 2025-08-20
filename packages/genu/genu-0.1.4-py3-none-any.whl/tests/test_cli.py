import unittest
from uuid_cli.cli import generate_uuid
import uuid
from typing import List


class TestUUIDGenerator(unittest.TestCase):
    def test_generate_uuid_v1(self):
        uuids: List[uuid.UUID] = generate_uuid(1, 5)
        self.assertEqual(len(uuids), 5)
        for u in uuids:
            self.assertTrue(isinstance(u, uuid.UUID))

    def test_generate_uuid_v3(self):
        uuids: List[uuid.UUID] = generate_uuid(3, 5, namespace='example.com')
        self.assertEqual(len(uuids), 5)
        for u in uuids:
            self.assertTrue(isinstance(u, uuid.UUID))

    def test_generate_uuid_v5(self):
        uuids: List[uuid.UUID] = generate_uuid(5, 5, namespace='example.com')
        self.assertEqual(len(uuids), 5)
        for u in uuids:
            self.assertTrue(isinstance(u, uuid.UUID))

    def test_generate_uuid_invalid_version(self):
        with self.assertRaises(ValueError):
            generate_uuid(7, 1)  # UUIDv7 should raise an error if uuid6 is not installed

    def test_generate_uuid_count(self):
        uuids: List[uuid.UUID] = generate_uuid(4, 10)
        self.assertEqual(len(uuids), 10)


if __name__ == "__main__":
    unittest.main()