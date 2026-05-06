#!/usr/bin/env python3
"""
validate_enz_project.py - Structural QA for Evacuationz project files.

Responsibilities:
- Parse XML and GraphML files in a project folder.
- Classify common Evacuationz file roles and flag structural risks.
- Check scenario file references and key modelling assumptions.

Usage:
    python validate_enz_project.py path/to/project
    python validate_enz_project.py path/to/scenario.xml --json
    python validate_enz_project.py path/to/project --strict --output qa.json

Exit Codes:
    0  - Success
    1  - General failure
    2  - Invalid arguments
    10 - Validation failure
    11 - Verification failure
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


SCENARIO_ROOTS = {"ENZ_Scenario", "Evacuationz_Scenario"}
ROLE_BY_ROOT = {
    "ENZ_Map": "map",
    "ENZ_AgentType": "agent_type",
    "ENZ_Populate": "populate",
    "ENZ_Simulation": "simulation",
    "ENZ_ExitBehaviour": "exit_behaviour",
    "ENZ_System": "system",
}
INPUT_FILE_TAGS = {
    "Map",
    "Populate",
    "AgentType",
    "ExitBehaviour",
    "Simulation",
    "System",
    "SystemType",
}
OUTPUT_TAGS = {
    "Results",
    "Evacuation",
    "Nodes",
    "PreEvacuation",
    "Agents",
    "Log",
    "Base",
    "Yed",
    "YED",
}
NUMERIC_TAGS = {
    "Length",
    "Width",
    "Height",
    "Elevation",
    "Tread",
    "Riser",
    "Speed",
    "PreEvacuation",
    "StartDistance",
    "MaximumTime",
    "TimeStep",
    "OutputFrequency",
    "SpecificFlow",
}
UNIT_RECOMMENDED_TAGS = {
    "Length",
    "Width",
    "Height",
    "Elevation",
    "Tread",
    "Riser",
    "Speed",
    "PreEvacuation",
    "StartDistance",
    "MaximumTime",
    "TimeStep",
    "OutputFrequency",
}


@dataclass
class Result:
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.success

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def element_text(element: ET.Element) -> str:
    return " ".join(part.strip() for part in element.itertext() if part.strip())


def direct_children(element: ET.Element, name: str) -> List[ET.Element]:
    return [child for child in list(element) if local_name(child.tag) == name]


def iter_named(element: ET.Element, name: str) -> Iterable[ET.Element]:
    for child in element.iter():
        if local_name(child.tag) == name:
            yield child


def first_named(element: ET.Element, name: str) -> Optional[ET.Element]:
    for child in iter_named(element, name):
        return child
    return None


def parse_float(text: str) -> Optional[float]:
    match = re.search(r"[-+]?\d+(?:\.\d+)?", text or "")
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def resolve_reference(base_file: Path, raw_path: str) -> Path:
    candidate = Path(raw_path.strip().strip('"'))
    if candidate.is_absolute():
        return candidate
    if "%InputFolder%" in raw_path:
        normalized = raw_path.replace("/", "\\")
        parts = [part for part in normalized.split("\\") if part and part != "%InputFolder%"]
        if parts:
            direct = base_file.parent / parts[-1]
            if direct.exists():
                return direct.resolve()
    return (base_file.parent / candidate).resolve()


def classify_root(root_name: str, file_path: Path) -> str:
    if root_name in SCENARIO_ROOTS or re.fullmatch(r"Evacuat[a-zA-Z]*_Scenario", root_name):
        return "scenario"
    if root_name in ROLE_BY_ROOT:
        return ROLE_BY_ROOT[root_name]
    match = re.fullmatch(r"Evacuat[a-zA-Z]*_(Map|AgentType|Populate|Simulation|ExitBehaviour|System|SystemType)", root_name)
    if match:
        return {
            "Map": "map",
            "AgentType": "agent_type",
            "Populate": "populate",
            "Simulation": "simulation",
            "ExitBehaviour": "exit_behaviour",
            "System": "system",
            "SystemType": "system",
        }[match.group(1)]
    if root_name.lower() == "graphml" or file_path.suffix.lower() == ".graphml":
        return "graphml"
    return "unknown"


def analyze_scenario(root: ET.Element, file_path: Path) -> Tuple[Dict[str, Any], List[str], List[str]]:
    info: Dict[str, Any] = {"input_references": [], "requested_outputs": [], "smokeview": False}
    errors: List[str] = []
    warnings: List[str] = []

    files_blocks = list(iter_named(root, "Files"))
    if not files_blocks:
        warnings.append(f"{file_path}: scenario has no Files block")
        return info, errors, warnings

    for files in files_blocks:
        for child in list(files):
            tag = local_name(child.tag)
            text = element_text(child)
            if tag in INPUT_FILE_TAGS and text:
                resolved = resolve_reference(file_path, text)
                exists = resolved.exists()
                info["input_references"].append(
                    {"tag": tag, "path": text, "resolved": str(resolved), "exists": exists}
                )
                if not exists:
                    warnings.append(f"{file_path}: referenced {tag} file not found: {text}")
            elif tag in INPUT_FILE_TAGS and not text:
                warnings.append(f"{file_path}: {tag} file tag is present but empty")
            elif tag in OUTPUT_TAGS:
                info["requested_outputs"].append(tag)

    smokeview = first_named(root, "Smokeview")
    if smokeview is not None:
        info["smokeview"] = True

    if "Log" not in info["requested_outputs"]:
        warnings.append(f"{file_path}: Log output is not explicitly requested")

    return info, errors, warnings


def analyze_map(root: ET.Element, file_path: Path) -> Tuple[Dict[str, Any], List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    nodes = list(iter_named(root, "Node"))
    connections = list(iter_named(root, "Connection"))
    safe_nodes = [node for node in nodes if (node.get("type") or "").lower() == "enz_safe"]
    connection_types: Dict[str, int] = {}

    for connection in connections:
        node_refs = direct_children(connection, "NodeRef")
        if len(node_refs) != 2:
            warnings.append(f"{file_path}: connection has {len(node_refs)} direct NodeRef elements")
        for ctype in direct_children(connection, "ConnectionType"):
            ctype_name = ctype.get("type", "unspecified")
            connection_types[ctype_name] = connection_types.get(ctype_name, 0) + 1

    if not nodes:
        errors.append(f"{file_path}: map contains no Node elements")
    if not connections:
        warnings.append(f"{file_path}: map contains no Connection elements")
    if not safe_nodes:
        warnings.append(f"{file_path}: map contains no Node type='enz_safe'")

    info = {
        "nodes": len(nodes),
        "safe_nodes": len(safe_nodes),
        "connections": len(connections),
        "connection_types": connection_types,
    }
    return info, errors, warnings


def analyze_agent_types(root: ET.Element, file_path: Path) -> Tuple[Dict[str, Any], List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    definitions = list(iter_named(root, "AgentTypeDefinition"))
    names: List[str] = []
    distributions = 0
    attributes = 0

    for definition in definitions:
        name = first_named(definition, "Name")
        if name is None or not element_text(name):
            warnings.append(f"{file_path}: AgentTypeDefinition without Name")
        else:
            names.append(element_text(name))
        distributions += len(list(iter_named(definition, "Distribution")))
        attributes += len(list(iter_named(definition, "Attribute")))

    if not definitions:
        warnings.append(f"{file_path}: no AgentTypeDefinition elements found")

    info = {
        "definitions": len(definitions),
        "names": names,
        "distributions": distributions,
        "attributes": attributes,
    }
    return info, errors, warnings


def analyze_populate(root: ET.Element, file_path: Path) -> Tuple[Dict[str, Any], List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    populations = list(iter_named(root, "PopulationDefinition"))
    fixed_agent_total = 0
    unknown_agent_counts = 0
    missing_agent_type = 0

    for population in populations:
        agents = first_named(population, "Agents")
        if agents is None or not element_text(agents):
            warnings.append(f"{file_path}: PopulationDefinition without Agents value")
            unknown_agent_counts += 1
        else:
            value = parse_float(element_text(agents))
            if value is None:
                unknown_agent_counts += 1
            else:
                fixed_agent_total += int(value)

        if first_named(population, "NodeRef") is None:
            warnings.append(f"{file_path}: PopulationDefinition without NodeRef")
        if first_named(population, "AgentType") is None:
            missing_agent_type += 1

    if not populations:
        warnings.append(f"{file_path}: no PopulationDefinition elements found")
    if missing_agent_type:
        warnings.append(f"{file_path}: {missing_agent_type} PopulationDefinition elements do not specify AgentType")

    info = {
        "population_definitions": len(populations),
        "fixed_agent_total": fixed_agent_total,
        "unknown_agent_counts": unknown_agent_counts,
        "missing_agent_type": missing_agent_type,
    }
    return info, errors, warnings


def analyze_system(root: ET.Element, file_path: Path) -> Tuple[Dict[str, Any], List[str], List[str]]:
    systems = {}
    for element in root.iter():
        tag = local_name(element.tag)
        if tag in {"Alarm", "Smoke", "Lighting", "SystemDefinition", "NodeDelay"}:
            systems[tag] = systems.get(tag, 0) + 1
    return {"system_elements": systems}, [], []


def analyze_simulation(root: ET.Element, file_path: Path) -> Tuple[Dict[str, Any], List[str], List[str]]:
    warnings: List[str] = []
    info: Dict[str, Any] = {
        "sampling": root.get("sampling"),
        "agent_process": root.get("agent_process"),
        "counterflow": None,
        "edm": None,
    }

    for tag in ("MaximumTime", "TimeStep", "OutputFrequency"):
        element = first_named(root, tag)
        if element is None:
            warnings.append(f"{file_path}: simulation does not explicitly set {tag}")
        else:
            info[tag] = element_text(element)

    counterflow = first_named(root, "Counterflow")
    if counterflow is not None:
        info["counterflow"] = dict(counterflow.attrib)
    edm = first_named(root, "EDM")
    if edm is not None:
        info["edm"] = dict(edm.attrib)

    return info, [], warnings


def analyze_common(root: ET.Element, file_path: Path) -> Tuple[Dict[str, Any], List[str], List[str]]:
    warnings: List[str] = []
    errors: List[str] = []
    numeric_values: List[Dict[str, Any]] = []
    missing_units: List[str] = []

    for element in root.iter():
        tag = local_name(element.tag)
        if tag in NUMERIC_TAGS:
            text = element_text(element)
            value = parse_float(text)
            if value is not None:
                numeric_values.append({"tag": tag, "value": value})
                if value < 0:
                    errors.append(f"{file_path}: {tag} has negative value {value}")
            if tag in UNIT_RECOMMENDED_TAGS and text and "units" not in element.attrib:
                missing_units.append(tag)

    if missing_units:
        unique = sorted(set(missing_units))
        warnings.append(f"{file_path}: explicit units not found for {', '.join(unique)}")

    return {"numeric_values": len(numeric_values), "missing_unit_tags": sorted(set(missing_units))}, errors, warnings


def scan_file(file_path: Path) -> Tuple[Dict[str, Any], List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    info: Dict[str, Any] = {"path": str(file_path), "suffix": file_path.suffix.lower()}

    try:
        tree = ET.parse(file_path)
    except ET.ParseError as exc:
        return {**info, "role": "parse_error"}, [f"{file_path}: XML parse error: {exc}"], warnings
    except OSError as exc:
        return {**info, "role": "read_error"}, [f"{file_path}: read error: {exc}"], warnings

    root = tree.getroot()
    root_name = local_name(root.tag)
    role = classify_root(root_name, file_path)
    info["root"] = root_name
    info["role"] = role

    common_info, common_errors, common_warnings = analyze_common(root, file_path)
    info["common"] = common_info
    errors.extend(common_errors)
    warnings.extend(common_warnings)

    analyzers = {
        "scenario": analyze_scenario,
        "map": analyze_map,
        "agent_type": analyze_agent_types,
        "populate": analyze_populate,
        "simulation": analyze_simulation,
        "system": analyze_system,
    }
    analyzer = analyzers.get(role)
    if analyzer is not None:
        role_info, role_errors, role_warnings = analyzer(root, file_path)
        info[role] = role_info
        errors.extend(role_errors)
        warnings.extend(role_warnings)
    elif role == "graphml":
        info["graphml"] = {"xml_root": root_name}
    else:
        warnings.append(f"{file_path}: unrecognized Evacuationz root '{root_name}'")

    return info, errors, warnings


def collect_files(path: Path) -> List[Path]:
    if path.is_file():
        return [path]
    files: List[Path] = []
    for pattern in ("*.xml", "*.graphml"):
        files.extend(path.rglob(pattern))
    return sorted(set(files))


def process(path: Path, strict: bool) -> Result:
    if not path.exists():
        return Result(False, f"Path not found: {path}", errors=[f"Path not found: {path}"])

    files = collect_files(path)
    if not files:
        return Result(False, f"No XML or GraphML files found in {path}", errors=["No files to scan"])

    scanned: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []
    role_counts: Dict[str, int] = {}

    for file_path in files:
        info, file_errors, file_warnings = scan_file(file_path)
        scanned.append(info)
        role = info.get("role", "unknown")
        role_counts[role] = role_counts.get(role, 0) + 1
        errors.extend(file_errors)
        warnings.extend(file_warnings)

    if role_counts.get("scenario", 0) == 0:
        warnings.append("No scenario file root was detected")
    if role_counts.get("map", 0) == 0 and role_counts.get("graphml", 0) == 0:
        warnings.append("No map XML or GraphML file was detected")

    success = not errors and (not strict or not warnings)
    message = "Validation passed" if success else "Validation found issues"
    data = {
        "target": str(path),
        "files_scanned": len(files),
        "role_counts": role_counts,
        "issue_counts": {"errors": len(errors), "warnings": len(warnings)},
        "files": scanned,
        "strict": strict,
    }
    return Result(success, message, data=data, errors=errors, warnings=warnings)


def verify_result(result: Result) -> Tuple[bool, str]:
    data = result.data
    if "files_scanned" not in data or data["files_scanned"] <= 0:
        return False, "Result did not record scanned files"
    if len(data.get("files", [])) != data["files_scanned"]:
        return False, "File detail count does not match files_scanned"
    issue_counts = data.get("issue_counts", {})
    if issue_counts.get("errors") != len(result.errors):
        return False, "Error count mismatch"
    if issue_counts.get("warnings") != len(result.warnings):
        return False, "Warning count mismatch"
    return True, "Verification passed"


def print_text(result: Result) -> None:
    print(result.message)
    print(f"Files scanned: {result.data.get('files_scanned', 0)}")
    print(f"Roles: {json.dumps(result.data.get('role_counts', {}), sort_keys=True)}")
    for warning in result.warnings:
        print(f"Warning: {warning}", file=sys.stderr)
    for error in result.errors:
        print(f"Error: {error}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Evacuationz XML/GraphML project structure")
    parser.add_argument("path", type=Path, help="Project directory or XML/GraphML file")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as validation failures")
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    parser.add_argument("--output", "-o", type=Path, help="Write full JSON result to file")
    parser.add_argument("--no-verify", action="store_true", help="Skip result self-verification")
    args = parser.parse_args()

    result = process(args.path, args.strict)

    if not args.no_verify:
        ok, message = verify_result(result)
        if not ok:
            result.success = False
            result.errors.append(f"Self-verification failed: {message}")

    payload = result.to_dict()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2))

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_text(result)

    if result.success:
        sys.exit(0)
    if any("Self-verification failed" in error for error in result.errors):
        sys.exit(11)
    sys.exit(10)


if __name__ == "__main__":
    main()

