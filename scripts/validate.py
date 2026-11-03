#!/usr/bin/env python3
"""Validate the distributable skill and its task contracts."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "software-dev-team"
REFERENCES = SKILL / "references"


def load_json(file: Path):
    return json.loads(file.read_text(encoding="utf-8"))


def resolve_inside(base: Path, relative: str, boundary: Path) -> Path:
    target = (base / relative).resolve()
    if not target.is_relative_to(boundary.resolve()):
        raise ValueError(f"Reference escapes package: {relative}")
    if not target.is_file():
        raise ValueError(f"Referenced file is missing: {relative}")
    return target


def validate_task(task: dict) -> list[str]:
    schema = load_json(REFERENCES / "task-card.schema.json")
    return [f"{'.'.join(map(str, error.absolute_path))}: {error.message}"
            for error in Draft202012Validator(schema).iter_errors(task)]


def validate_package(skill: Path = SKILL) -> list[str]:
    errors = []
    frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)",
                           (skill / "SKILL.md").read_text(encoding="utf-8"), re.S)
    if not frontmatter:
        return ["SKILL.md is missing valid YAML frontmatter"]
    metadata = yaml.safe_load(frontmatter.group(1))
    if not isinstance(metadata, dict):
        return ["Skill frontmatter must be a mapping"]
    if metadata.get("name") != skill.name:
        errors.append("Skill name must match its installable directory")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        errors.append("Skill description must be nonempty and at most 1024 characters")
    ui = yaml.safe_load((skill / "agents/openai.yaml").read_text(encoding="utf-8"))
    if f"${skill.name}" not in ui["interface"]["default_prompt"]:
        errors.append("UI default prompt must mention the skill")
    if ui.get("policy", {}).get("allow_implicit_invocation", True) is not True:
        errors.append("Normal automatic discovery must remain enabled")

    references = skill / "references"
    catalog = load_json(references / "roles.json")
    ids = [role["id"] for role in catalog["roles"]]
    if len(ids) != len(set(ids)):
        errors.append("Role IDs must be unique")
    for relative in catalog.get("specialty_files", {}).values():
        resolve_inside(references, relative, skill)
    for key in ("policy_file", "stack_file", "task_schema_file"):
        resolve_inside(references, catalog[key], skill)
    for role in catalog["roles"]:
        role_file = resolve_inside(references, role["prompt_file"], skill)
        if role_file.stem != role["id"]:
            errors.append(f"Role ID and filename disagree: {role['id']}")
        if role.get("default_mode") != "read-only":
            errors.append(f"A role must not grant write permissions: {role['id']}")
        if not role.get("work_types") or not role.get("technical_references"):
            errors.append(f"Role needs work types and technical references: {role['id']}")
        for relative in role.get("technical_references", []):
            resolve_inside(references, relative, skill)

    schema = load_json(references / "task-card.schema.json")
    Draft202012Validator.check_schema(schema)
    if set(schema["properties"]["role_id"]["enum"]) != set(ids):
        errors.append("Task role enum must match the role catalog")
    errors.extend(error.message for error in Draft202012Validator(schema).iter_errors(
        load_json(references / "dispatch-example.json")))

    for file in skill.rglob("*"):
        if not file.is_file():
            continue
        if file.suffix.lower() in {".js", ".mjs", ".py", ".ps1", ".sh", ".exe", ".dll", ".zip"}:
            errors.append(f"Executable or runtime artifact in instruction-only skill: {file.relative_to(skill)}")
        if file.suffix in {".json", ".yaml", ".md", ".mjs"}:
            contents = file.read_text(encoding="utf-8")
            if re.search(r"\b[A-Za-z]:[\\/]", contents):
                errors.append(f"Personal drive path in portable package: {file.relative_to(skill)}")
            if re.search(r"gh[pousr]_[A-Za-z0-9]{25,}", contents):
                errors.append(f"Possible credential in package: {file.relative_to(skill)}")
        if file.suffix == ".json":
            load_json(file)
        if file.suffix == ".md":
            for destination in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", contents):
                destination = destination.strip("<>")
                url = urlsplit(destination)
                if url.scheme or not url.path:
                    continue
                try:
                    resolve_inside(file.parent, unquote(url.path), skill)
                except ValueError as error:
                    errors.append(f"{file.relative_to(skill)}: {error}")
    return errors


def main() -> int:
    try:
        errors = validate_package()
    except (ValueError, KeyError, OSError, yaml.YAMLError) as error:
        errors = [str(error)]
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    count = len(load_json(REFERENCES / "roles.json")["roles"])
    print(f"Validated self-contained skill, {count} roles, local references, and task contracts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
