#!/usr/bin/env python3
"""Validate and estimate a small software delivery plan. Python 3.10+, stdlib only."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

ZERO = Decimal(0)
CENT = Decimal("0.01")


class PlanError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise PlanError(message)


def obj(value, label):
    require(isinstance(value, dict), f"{label}: expected object")
    return value


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"{label}: expected nonempty string")
    return value


def number(value, label, positive=False, maximum=None):
    require(isinstance(value, (int, float)) and not isinstance(value, bool),
            f"{label}: expected number")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise PlanError(f"{label}: invalid number") from exc
    require(result.is_finite(), f"{label}: must be finite")
    require(result > 0 if positive else result >= 0, f"{label}: out of range")
    if maximum is not None:
        require(result <= maximum, f"{label}: above maximum {maximum}")
    return result


def strings(value, label, nonempty=False):
    require(isinstance(value, list), f"{label}: expected list")
    if nonempty:
        require(bool(value), f"{label}: list must not be empty")
    for entry in value:
        text(entry, label)
    require(len(value) == len(set(value)), f"{label}: duplicate entries")
    return value


def iso_date(value, label):
    text(value, label)
    require(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)), f"{label}: use YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise PlanError(f"{label}: invalid date") from exc


def validate(data):
    obj(data, "plan")
    text(data.get("name"), "name")
    text(data.get("currency"), "currency")
    start = iso_date(data.get("start_date"), "start_date")
    deadline = iso_date(data["deadline"], "deadline") if data.get("deadline") is not None else None
    holidays = {iso_date(x, "holiday") for x in strings(data.get("holidays", []), "holidays")}
    roles = set(strings(data.get("roles"), "roles", True))
    resources = obj(data.get("resources"), "resources")
    require(bool(resources), "resources: must not be empty")
    normalized_resources = {}
    for rid, raw in resources.items():
        text(rid, "resource id")
        obj(raw, rid)
        assigned = set(strings(raw.get("roles"), f"{rid}.roles", True))
        require(assigned <= roles, f"{rid}: unknown role")
        capacity = number(raw.get("daily_capacity_hours"), f"{rid}.capacity", True, 24)
        rate = number(raw["hourly_rate"], f"{rid}.rate") if raw.get("hourly_rate") is not None else None
        normalized_resources[rid] = {"roles": assigned, "capacity": capacity, "rate": rate}

    raw_tasks = data.get("tasks")
    require(isinstance(raw_tasks, list) and 0 < len(raw_tasks) <= 1000, "tasks: require 1..1000 tasks")
    tasks = {}
    for raw in raw_tasks:
        obj(raw, "task")
        tid = text(raw.get("id"), "task.id")
        require(tid not in tasks, f"duplicate task id: {tid}")
        text(raw.get("name"), f"{tid}.name")
        role = text(raw.get("role"), f"{tid}.role")
        rid = text(raw.get("resource"), f"{tid}.resource")
        require(rid in normalized_resources, f"{tid}: unknown resource")
        require(role in normalized_resources[rid]["roles"], f"{tid}: resource cannot perform role")
        depends = strings(raw.get("depends_on"), f"{tid}.depends_on")
        strings(raw.get("acceptance"), f"{tid}.acceptance", True)
        estimate = obj(raw.get("estimate_hours"), f"{tid}.estimate_hours")
        o, m, p = [number(estimate.get(k), f"{tid}.{k}", True)
                   for k in ("optimistic", "likely", "pessimistic")]
        require(o <= m <= p, f"{tid}: require optimistic <= likely <= pessimistic")
        tasks[tid] = {"name": raw["name"], "role": role, "resource": rid, "depends": depends,
                      "optimistic": o, "expected": (o + 4 * m + p) / 6, "pessimistic": p}
    for tid, task in tasks.items():
        require(set(task["depends"]) <= tasks.keys(), f"{tid}: unknown dependency")
        require(tid not in task["depends"], f"{tid}: self dependency")
    order, pending = [], list(tasks)
    while pending:
        ready = next((tid for tid in pending if set(tasks[tid]["depends"]) <= set(order)), None)
        require(ready is not None, "dependency cycle")
        order.append(ready)
        pending.remove(ready)

    raci = data.get("raci")
    require(isinstance(raci, list) and bool(raci), "raci: require at least one row")
    deliverables = set()
    for row in raci:
        obj(row, "raci row")
        name = text(row.get("deliverable"), "raci.deliverable")
        require(name not in deliverables, "raci: duplicate deliverable")
        deliverables.add(name)
        accountable = text(row.get("a"), f"raci.{name}.a")
        r, c, i = [set(strings(row.get(k), f"raci.{name}.{k}", k == "r")) for k in ("r", "c", "i")]
        require({accountable} | r | c | i <= roles, f"raci.{name}: unknown role")
        require(not (c & (r | i | {accountable}) or i & (r | {accountable})),
                f"raci.{name}: overlapping C/I responsibilities")

    itto = data.get("itto")
    require(isinstance(itto, list) and bool(itto), "itto: require at least one process")
    processes = set()
    for row in itto:
        obj(row, "itto row")
        name = text(row.get("process"), "itto.process")
        require(name not in processes, "itto: duplicate process")
        processes.add(name)
        require(text(row.get("owner_role"), "itto.owner_role") in roles, "itto: unknown owner")
        for field in ("inputs", "tools_techniques", "outputs"):
            strings(row.get(field), f"itto.{name}.{field}", True)
        text(row.get("gate"), f"itto.{name}.gate")

    extras = data.get("extra_costs", [])
    require(isinstance(extras, list), "extra_costs: expected list")
    costs = []
    for raw in extras:
        obj(raw, "extra_cost")
        name = text(raw.get("name"), "extra_cost.name")
        amount = number(raw["amount"], name) if raw.get("amount") is not None else None
        costs.append((name, amount))
    contingency = number(data.get("contingency_percent", 0), "contingency_percent", maximum=100)
    limit = number(data["budget_limit"], "budget_limit") if data.get("budget_limit") is not None else None
    return start, deadline, holidays, normalized_resources, tasks, order, costs, contingency, limit


def rounded(value, places="0.01"):
    return float(value.quantize(Decimal(places), rounding=ROUND_HALF_UP))


def calculate(data):
    start, deadline, holidays, resources, tasks, order, extras, contingency, limit = validate(data)
    days = []
    cursor = start

    def workday(index):
        nonlocal cursor
        require(index < 3660, "planning horizon exceeds 3660 working days")
        while len(days) <= index:
            while cursor.weekday() >= 5 or cursor in holidays:
                cursor += timedelta(days=1)
            days.append(cursor)
            cursor += timedelta(days=1)
        return days[index]

    scenarios = {}
    for mode in ("optimistic", "expected", "pessimistic"):
        usage = {rid: {} for rid in resources}
        endings, scheduled, labor = {}, [], ZERO
        unknown = []
        for tid in order:
            task = tasks[tid]
            rid = task["resource"]
            resource = resources[rid]
            remaining = task[mode]
            index = max((endings[x] + 1 for x in task["depends"]), default=0)
            allocations = []
            while remaining > 0:
                current = workday(index)
                available = resource["capacity"] - usage[rid].get(index, ZERO)
                if available > 0:
                    take = min(available, remaining)
                    usage[rid][index] = usage[rid].get(index, ZERO) + take
                    allocations.append({"date": current.isoformat(), "hours": rounded(take, "0.000001")})
                    remaining -= take
                if remaining > 0:
                    index += 1
            endings[tid] = index
            if resource["rate"] is None:
                unknown.append(f"hourly_rate:{rid}:{tid}")
            else:
                labor += task[mode] * resource["rate"]
            scheduled.append({"id": tid, "name": task["name"], "role": task["role"], "resource": rid,
                              "depends_on": task["depends"], "hours": rounded(task[mode], "0.000001"),
                              "start": allocations[0]["date"], "finish": allocations[-1]["date"],
                              "allocations": allocations})
        extra = sum((amount for _, amount in extras if amount is not None), ZERO)
        unknown.extend(f"extra_cost:{name}" for name, amount in extras if amount is None)
        subtotal = labor + extra
        total = subtotal * (1 + contingency / 100) if not unknown else None
        finish = workday(max(endings.values()))
        if unknown:
            budget_status = "unknown"
        elif limit is None:
            budget_status = "not_set"
        else:
            budget_status = "within_limit" if total <= limit else "over_limit"
        deadline_status = "not_set" if deadline is None else ("within_deadline" if finish <= deadline else "late")
        scenarios[mode] = {
            "effort_hours": rounded(sum((t[mode] for t in tasks.values()), ZERO), "0.000001"),
            "finish": finish.isoformat(), "working_days": max(endings.values()) + 1,
            "known_labor_cost": rounded(labor), "known_extra_cost": rounded(extra),
            "known_cost_subtotal": rounded(subtotal), "cost_complete": not unknown,
            "unknown_costs": unknown, "total_with_contingency": rounded(total) if total is not None else None,
            "budget_status": budget_status, "deadline_status": deadline_status, "tasks": scheduled,
        }
    return {
        "schema_version": 1, "name": data["name"], "currency": data["currency"],
        "start_date": start.isoformat(), "deadline": deadline.isoformat() if deadline else None,
        "budget_limit": rounded(limit) if limit is not None else None,
        "contingency_percent": rounded(contingency),
        "method": "input-priority greedy resource schedule; finish-to-start next working day",
        "warnings": [
            "Scenarios are assumptions, not confidence intervals or delivery commitments.",
            "Weekdays only; public holidays and working-weekend adjustments are not inferred.",
            "No optimality claim, automatic critical-path analysis, actual-cost tracking, or agent runtime prediction.",
            "Resource IDs must represent shared real capacity; aliases can double-count the same executor.",
            "RACI/ITTO structural checks do not prove completeness, authority, or real execution.",
        ],
        "scenarios": scenarios,
    }


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_plan(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan")
    parser.add_argument("--out")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        report = calculate(read_plan(args.plan))
        rendered = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.out:
            target = Path(args.out)
            require(target.resolve() != Path(args.plan).resolve(), "output must not overwrite input")
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("w" if args.overwrite else "x", encoding="utf-8", newline="\n") as stream:
                stream.write(rendered)
            print(f"Report written: {target}")
        else:
            print(rendered, end="")
        return 0
    except (ValueError, OSError, OverflowError, RecursionError) as exc:
        print(f"Invalid plan or output: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
