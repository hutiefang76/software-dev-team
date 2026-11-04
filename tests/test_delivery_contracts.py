import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("governance_validation", ROOT / "scripts/validate.py")
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)
EXAMPLE = json.loads((validation.REFERENCES / "delivery-task-example.json").read_text(encoding="utf-8"))


class DeliveryContracts(unittest.TestCase):
    def task(self):
        return copy.deepcopy(EXAMPLE)

    def test_unknown_values_remain_valid_and_explicit(self):
        task = self.task()
        self.assertEqual(validation.validate_task(task), [])
        self.assertIsNone(task["delivery"]["cost_limit"])

    def test_one_accountable_and_at_least_one_responsible(self):
        for key, value in (("a", ["one", "two"]), ("a", ""), ("r", [])):
            with self.subTest(key=key, value=value):
                task = self.task()
                task["raci"][key] = value
                self.assertTrue(validation.validate_task(task))

    def test_a_can_be_r_but_not_c_or_i(self):
        task = self.task()
        task["raci"]["r"] = [task["raci"]["a"]]
        self.assertEqual(validation.validate_task(task), [])
        for field in ("c", "i"):
            task = self.task()
            task["raci"][field] = [task["raci"]["a"]]
            self.assertTrue(validation.validate_task(task))

    def test_consulted_cannot_also_be_responsible(self):
        task = self.task()
        task["raci"]["c"] = task["raci"]["r"]
        self.assertTrue(validation.validate_task(task))

    def test_itto_cannot_omit_an_output_or_exit_condition(self):
        for key in ("inputs", "tools_techniques", "outputs", "gate"):
            with self.subTest(key=key):
                task = self.task()
                del task["itto"][key]
                self.assertTrue(validation.validate_task(task))

    def test_inverted_or_partially_known_estimates_fail(self):
        for value in (dict(optimistic=8, likely=4, pessimistic=10),
                      dict(optimistic=None, likely=4, pessimistic=10)):
            with self.subTest(value=value):
                task = self.task()
                task["delivery"]["estimate_hours"] = value
                self.assertTrue(validation.validate_task(task))

    def test_known_estimate_and_money_are_accepted(self):
        task = self.task()
        task["delivery"].update(currency="CNY", cost_limit=1000, actual_cost=100, remaining_cost=200,
                                capacity_hours_per_day=6, deadline="2026-11-30", max_rework_rounds=2,
                                estimate_hours=dict(optimistic=2, likely=4, pessimistic=8))
        self.assertEqual(validation.validate_task(task), [])

    def test_money_needs_a_currency(self):
        task = self.task()
        task["delivery"]["actual_cost"] = 0
        self.assertTrue(validation.validate_task(task))

    def test_over_budget_is_not_silently_an_input_error(self):
        task = self.task()
        task["delivery"].update(currency="CNY", cost_limit=100, actual_cost=200, remaining_cost=20)
        self.assertEqual(validation.validate_task(task), [])

    def test_negative_boolean_or_infinite_costs_fail(self):
        for value in (-1, True, float("inf"), float("nan")):
            with self.subTest(value=value):
                task = self.task()
                task["delivery"].update(currency="CNY", cost_limit=value)
                self.assertTrue(validation.validate_task(task))

    def test_invalid_dates_capacity_and_retry_limits_fail(self):
        for field, value in (("deadline", "2026-02-30"), ("capacity_hours_per_day", 25),
                             ("capacity_hours_per_day", 0), ("max_rework_rounds", -1)):
            with self.subTest(field=field, value=value):
                task = self.task()
                task["delivery"][field] = value
                self.assertTrue(validation.validate_task(task))


if __name__ == "__main__":
    unittest.main()
