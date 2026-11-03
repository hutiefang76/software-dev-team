import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validate", ROOT / "scripts/validate.py")
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)
EXAMPLE = json.loads((validation.REFERENCES / "dispatch-example.json").read_text(encoding="utf-8"))


class TaskContracts(unittest.TestCase):
    def task(self):
        return copy.deepcopy(EXAMPLE)

    def test_example_has_a_valid_read_only_boundary(self):
        self.assertEqual(validation.validate_task(self.task()), [])

    def test_read_only_task_cannot_claim_writable_files(self):
        task = self.task()
        task["scope"]["write_files"] = ["src/profile.ts"]
        self.assertTrue(validation.validate_task(task))

    def test_read_only_task_cannot_claim_runtime_resources(self):
        task = self.task()
        task["scope"]["runtime_resources"] = ["customer-host"]
        self.assertTrue(validation.validate_task(task))

    def test_writes_need_an_explicit_writer(self):
        task = self.task()
        task["scope"].update(mode="write", write_files=["src/profile.ts"])
        self.assertTrue(validation.validate_task(task))
        task["owners"]["writer"] = "Codex / frontend / example-member-id"
        self.assertEqual(validation.validate_task(task), [])

    def test_runtime_resources_need_an_explicit_owner(self):
        task = self.task()
        task["scope"].update(mode="execute", allowed_commands=["npm test"], runtime_resources=["isolated-test"])
        self.assertTrue(validation.validate_task(task))
        task["owners"]["resource_owner"] = "Codex / qa / example-member-id"
        self.assertEqual(validation.validate_task(task), [])

    def test_execution_needs_explicit_commands(self):
        task = self.task()
        task["scope"]["mode"] = "execute"
        self.assertTrue(validation.validate_task(task))

    def test_external_disclosure_needs_destination_and_content(self):
        task = self.task()
        task["binding"]["disclosure"]["destination"] = "approved-cli"
        self.assertTrue(validation.validate_task(task))
        task["binding"]["disclosure"]["allowed_content"] = ["provided redacted fixture"]
        self.assertEqual(validation.validate_task(task), [])

    def test_none_destination_cannot_authorize_content(self):
        task = self.task()
        task["binding"]["disclosure"]["allowed_content"] = ["src/profile.ts"]
        self.assertTrue(validation.validate_task(task))

    def test_unknown_role_and_empty_acceptance_are_rejected(self):
        task = self.task()
        task["role_id"] = "imaginary-admin"
        task["acceptance"] = []
        self.assertGreaterEqual(len(validation.validate_task(task)), 2)

    def test_unknown_scope_fields_do_not_silently_grant_access(self):
        task = self.task()
        task["scope"]["all_files_writable"] = True
        self.assertTrue(validation.validate_task(task))

    def test_reference_must_remain_inside_installed_package(self):
        test_root = ROOT / ".validation-tmp"
        test_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=test_root) as directory:
            root = Path(directory)
            self.assertTrue(root.resolve().is_relative_to(test_root.resolve()))
            package = root / "skill"
            package.mkdir()
            (root / "private.txt").write_text("outside", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "escapes package"):
                validation.resolve_inside(package, "../private.txt", package)


if __name__ == "__main__":
    unittest.main()
