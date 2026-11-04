import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/estimate_delivery.py"
SPEC = importlib.util.spec_from_file_location("delivery_plan", SCRIPT)
planner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(planner)


def fixture():
    return {
        "name": "capacity and cost fixture", "currency": "CNY",
        "start_date": "2026-11-09", "deadline": "2026-11-10",
        "budget_limit": 1500, "contingency_percent": 10, "holidays": [],
        "roles": ["PM", "TL", "BE", "QA", "OWNER"],
        "resources": {"dev": {"roles": ["TL", "BE"], "daily_capacity_hours": 6, "hourly_rate": 100}},
        "extra_costs": [{"name": "CI", "amount": 100}],
        "tasks": [
            {"id": "A", "name": "architecture", "role": "TL", "resource": "dev", "depends_on": [],
             "estimate_hours": {"optimistic": 6, "likely": 6, "pessimistic": 6}, "acceptance": ["contract exists"]},
            {"id": "B", "name": "implementation", "role": "BE", "resource": "dev", "depends_on": [],
             "estimate_hours": {"optimistic": 6, "likely": 6, "pessimistic": 6}, "acceptance": ["path works"]},
        ],
        "raci": [{"deliverable": "build", "a": "TL", "r": ["BE"], "c": ["QA"], "i": ["PM"]}],
        "itto": [{"process": "implement", "owner_role": "TL", "inputs": ["contract"],
                  "tools_techniques": ["coding and testing"], "outputs": ["build"], "gate": "acceptance met"}],
    }


class PlanTests(unittest.TestCase):
    def test_known_cost_and_shared_capacity(self):
        report = planner.calculate(fixture())["scenarios"]["expected"]
        self.assertEqual(report["total_with_contingency"], 1430)
        self.assertEqual(report["finish"], "2026-11-10")
        self.assertEqual(report["budget_status"], "within_limit")
        self.assertEqual(report["deadline_status"], "within_deadline")
        self.assertNotEqual(report["tasks"][0]["start"], report["tasks"][1]["start"])

    def test_one_resource_combining_roles_does_not_double_capacity(self):
        data = fixture()
        for task in data["tasks"]:
            task["estimate_hours"] = dict(optimistic=4, likely=4, pessimistic=4)
        report = planner.calculate(data)["scenarios"]["expected"]
        by_day = {}
        for task in report["tasks"]:
            for entry in task["allocations"]:
                by_day[entry["date"]] = by_day.get(entry["date"], 0) + entry["hours"]
        self.assertEqual(by_day, {"2026-11-09": 6, "2026-11-10": 2})

    def test_dependency_starts_next_working_day_even_with_free_capacity(self):
        data = fixture()
        data["tasks"][1]["depends_on"] = ["A"]
        for task in data["tasks"]:
            task["estimate_hours"] = dict(optimistic=1, likely=1, pessimistic=1)
        report = planner.calculate(data)["scenarios"]["expected"]
        self.assertEqual(report["tasks"][1]["start"], "2026-11-10")

    def test_weekend_and_holiday(self):
        data = fixture()
        data["start_date"] = "2026-11-06"
        data["holidays"] = ["2026-11-09"]
        report = planner.calculate(data)["scenarios"]["expected"]
        self.assertEqual(report["finish"], "2026-11-10")

    def test_pert_formula_and_scenarios(self):
        data = fixture()
        data["tasks"] = [data["tasks"][0]]
        data["tasks"][0]["estimate_hours"] = dict(optimistic=2, likely=5, pessimistic=8)
        report = planner.calculate(data)["scenarios"]
        self.assertEqual([report[x]["effort_hours"] for x in ("optimistic", "expected", "pessimistic")], [2, 5, 8])
        self.assertEqual(report["expected"]["total_with_contingency"], 660)

    def test_unknown_rate_is_not_free(self):
        data = fixture()
        data["resources"]["dev"]["hourly_rate"] = None
        report = planner.calculate(data)["scenarios"]["expected"]
        self.assertFalse(report["cost_complete"])
        self.assertIsNone(report["total_with_contingency"])
        self.assertEqual(report["known_cost_subtotal"], 100)
        self.assertEqual(report["budget_status"], "unknown")

    def test_unknown_extra_cost_is_not_free(self):
        data = fixture()
        data["extra_costs"][0]["amount"] = None
        report = planner.calculate(data)["scenarios"]["expected"]
        self.assertEqual(report["budget_status"], "unknown")
        self.assertIsNone(report["total_with_contingency"])

    def test_no_deadline_or_budget_is_not_pass(self):
        data = fixture()
        data["deadline"] = data["budget_limit"] = None
        report = planner.calculate(data)["scenarios"]["expected"]
        self.assertEqual(report["deadline_status"], "not_set")
        self.assertEqual(report["budget_status"], "not_set")

    def test_over_budget_and_late_are_visible(self):
        data = fixture()
        data["budget_limit"], data["deadline"] = 1000, "2026-11-09"
        report = planner.calculate(data)["scenarios"]["expected"]
        self.assertEqual(report["budget_status"], "over_limit")
        self.assertEqual(report["deadline_status"], "late")

    def test_dependency_cycle_rejected(self):
        data = fixture()
        data["tasks"][0]["depends_on"], data["tasks"][1]["depends_on"] = ["B"], ["A"]
        with self.assertRaisesRegex(planner.PlanError, "cycle"):
            planner.calculate(data)

    def test_missing_dependency_rejected(self):
        data = fixture()
        data["tasks"][1]["depends_on"] = ["absent"]
        with self.assertRaisesRegex(planner.PlanError, "unknown dependency"):
            planner.calculate(data)

    def test_duplicate_task_rejected(self):
        data = fixture()
        data["tasks"].append(copy.deepcopy(data["tasks"][0]))
        with self.assertRaisesRegex(planner.PlanError, "duplicate task"):
            planner.calculate(data)

    def test_wrong_resource_role_rejected(self):
        data = fixture()
        data["tasks"][1]["role"] = "QA"
        with self.assertRaisesRegex(planner.PlanError, "cannot perform role"):
            planner.calculate(data)

    def test_missing_acceptance_rejected(self):
        data = fixture()
        data["tasks"][0]["acceptance"] = []
        with self.assertRaises(planner.PlanError):
            planner.calculate(data)

    def test_inverted_estimate_rejected(self):
        data = fixture()
        data["tasks"][0]["estimate_hours"]["optimistic"] = 10
        with self.assertRaisesRegex(planner.PlanError, "optimistic"):
            planner.calculate(data)

    def test_invalid_numeric_inputs_rejected(self):
        for value in (-1, 0, True, "six", float("nan"), float("inf"), 25):
            with self.subTest(value=value):
                data = fixture()
                data["resources"]["dev"]["daily_capacity_hours"] = value
                with self.assertRaises(planner.PlanError):
                    planner.calculate(data)

    def test_invalid_dates_rejected(self):
        for value in ("2026-02-30", "20261109", "tomorrow", None):
            with self.subTest(value=value):
                data = fixture()
                data["start_date"] = value
                with self.assertRaises(planner.PlanError):
                    planner.calculate(data)

    def test_raci_requires_one_accountable_role_and_responsibility(self):
        for field, value in (("a", ["TL", "PM"]), ("a", ""), ("a", "missing"), ("r", []), ("c", ["BE"])):
            with self.subTest(field=field, value=value):
                data = fixture()
                data["raci"][0][field] = value
                with self.assertRaises(planner.PlanError):
                    planner.calculate(data)

    def test_accountable_may_also_be_responsible(self):
        data = fixture()
        data["raci"][0]["r"] = ["TL"]
        self.assertTrue(planner.calculate(data)["scenarios"]["expected"]["cost_complete"])

    def test_itto_requires_inputs_tools_outputs_gate_owner(self):
        for field in ("inputs", "tools_techniques", "outputs", "gate", "owner_role"):
            with self.subTest(field=field):
                data = fixture()
                data["itto"][0].pop(field)
                with self.assertRaises(planner.PlanError):
                    planner.calculate(data)

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.json"
            path.write_text('{"name":"one","name":"two"}', encoding="utf-8")
            with self.assertRaisesRegex(planner.PlanError, "duplicate JSON"):
                planner.read_plan(path)

    def test_cli_and_no_silent_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dest = Path(tmp) / "plan.json", Path(tmp) / "report.json"
            src.write_text(json.dumps(fixture()), encoding="utf-8")
            args = [sys.executable, "-X", "utf8", str(SCRIPT), str(src), "--out", str(dest)]
            first = subprocess.run(args, capture_output=True, text=True, timeout=30)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = subprocess.run(args, capture_output=True, text=True, timeout=30)
            self.assertEqual(second.returncode, 2)
            third = subprocess.run(args + ["--overwrite"], capture_output=True, text=True, timeout=30)
            self.assertEqual(third.returncode, 0, third.stderr)
            result = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(result["scenarios"]["expected"]["total_with_contingency"], 1430)

    def test_cli_never_overwrites_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "plan.json"
            before = json.dumps(fixture())
            src.write_text(before, encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(src), "--out", str(src), "--overwrite"],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(src.read_text(encoding="utf-8"), before)

    def test_full_examples_respect_capacity_and_dependencies(self):
        for filename in ("web-plan.json", "gui-network-plan.json"):
            with self.subTest(filename=filename):
                data = planner.read_plan(ROOT / "examples" / filename)
                report = planner.calculate(data)
                for scenario in report["scenarios"].values():
                    records = {t["id"]: t for t in scenario["tasks"]}
                    usage = {}
                    for task in records.values():
                        for dep in task["depends_on"]:
                            self.assertGreater(task["start"], records[dep]["finish"])
                        for entry in task["allocations"]:
                            key = (task["resource"], entry["date"])
                            usage[key] = usage.get(key, 0) + entry["hours"]
                    for (rid, _), hours in usage.items():
                        self.assertLessEqual(hours, data["resources"][rid]["daily_capacity_hours"] + 1e-6)


if __name__ == "__main__":
    unittest.main()
