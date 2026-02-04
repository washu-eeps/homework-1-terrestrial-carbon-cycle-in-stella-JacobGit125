#!/usr/bin/env python3
"""
HW1 Autograder for EEPS 3230 Biogeochemistry

Parses .stmx (XMILE XML) files and checks for required elements, feedback
implementation, scenario design, and calibration.

Usage:
    python hw1_autograder.py submission.stmx [--json]
"""

import xml.etree.ElementTree as ET
import sys
import json
import re
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


XMILE_NS = {'xmile': 'http://docs.oasis-open.org/xmile/ns/XMILE/v1.0'}


@dataclass
class Variable:
    """Represents a Stella variable (stock, flow, or aux)."""
    name: str
    var_type: str  # 'stock', 'flow', 'aux'
    equation: str = ''
    inflows: list = field(default_factory=list)
    outflows: list = field(default_factory=list)


@dataclass
class CheckResult:
    """Result of a single check."""
    name: str
    passed: bool
    message: str
    points: float = 0.0
    max_points: float = 0.0


def normalize_name(name: str) -> str:
    """Normalize variable names for comparison (spaces to underscores, case-insensitive)."""
    # XMILE uses spaces in names, but equations use underscores
    return name.lower().strip().replace(' ', '_').replace('-', '_')


def find_child(parent, tag: str):
    """Find child element trying with and without namespace."""
    elem = parent.find(f'xmile:{tag}', XMILE_NS)
    if elem is None:
        elem = parent.find(tag)
    return elem


def find_all_children(parent, tag: str) -> list:
    """Find all child elements trying with and without namespace."""
    elems = parent.findall(f'xmile:{tag}', XMILE_NS)
    if not elems:
        elems = parent.findall(tag)
    return elems


def parse_stmx(filepath: str) -> dict[str, Variable]:
    """Parse an .stmx file and extract all variables."""
    tree = ET.parse(filepath)
    root = tree.getroot()

    variables = {}

    # Find the model element
    model = root.find('.//xmile:model', XMILE_NS)
    if model is None:
        model = root.find('.//model')

    if model is None:
        raise ValueError("Could not find model element in STMX file")

    # Find variables container
    vars_elem = find_child(model, 'variables')

    if vars_elem is None:
        raise ValueError("Could not find variables element in STMX file")

    # Parse stocks
    for stock in find_all_children(vars_elem, 'stock'):
        name = stock.get('name', '')
        eqn_elem = find_child(stock, 'eqn')
        equation = eqn_elem.text if eqn_elem is not None and eqn_elem.text else ''

        inflows = []
        outflows = []
        for inflow in find_all_children(stock, 'inflow'):
            if inflow.text:
                inflows.append(inflow.text)
        for outflow in find_all_children(stock, 'outflow'):
            if outflow.text:
                outflows.append(outflow.text)

        var = Variable(name=name, var_type='stock', equation=equation,
                      inflows=inflows, outflows=outflows)
        variables[normalize_name(name)] = var

    # Parse flows
    for flow in find_all_children(vars_elem, 'flow'):
        name = flow.get('name', '')
        eqn_elem = find_child(flow, 'eqn')
        equation = eqn_elem.text if eqn_elem is not None and eqn_elem.text else ''

        var = Variable(name=name, var_type='flow', equation=equation)
        variables[normalize_name(name)] = var

    # Parse auxiliaries (converters)
    for aux in find_all_children(vars_elem, 'aux'):
        name = aux.get('name', '')
        eqn_elem = find_child(aux, 'eqn')
        equation = eqn_elem.text if eqn_elem is not None and eqn_elem.text else ''

        var = Variable(name=name, var_type='aux', equation=equation)
        variables[normalize_name(name)] = var

    return variables


def check_base_model(variables: dict[str, Variable]) -> list[CheckResult]:
    """Check that all required base model elements are present."""
    results = []

    # Required stocks
    required_stocks = ['atmosphere', 'vegetation', 'som']
    missing_stocks = []
    for stock in required_stocks:
        if stock not in variables or variables[stock].var_type != 'stock':
            missing_stocks.append(stock)

    if missing_stocks:
        results.append(CheckResult(
            name='Required Stocks',
            passed=False,
            message=f'Missing stocks: {", ".join(missing_stocks)}',
            points=0,
            max_points=4
        ))
    else:
        results.append(CheckResult(
            name='Required Stocks',
            passed=True,
            message='All 3 stocks present (Atmosphere, Vegetation, SOM)',
            points=4,
            max_points=4
        ))

    # Required flows
    required_flows = [
        'gpp', 'autotrophic_respiration', 'litterfall',
        'heterotrophic_respiration', 'emissions'
    ]
    missing_flows = []
    for flow in required_flows:
        if flow not in variables or variables[flow].var_type != 'flow':
            missing_flows.append(flow)

    if missing_flows:
        results.append(CheckResult(
            name='Required Flows',
            passed=False,
            message=f'Missing flows: {", ".join(missing_flows)}',
            points=0,
            max_points=8
        ))
    else:
        results.append(CheckResult(
            name='Required Flows',
            passed=True,
            message='All 5 flows present',
            points=8,
            max_points=8
        ))

    # Required converters
    required_auxs = ['gpp_base', 'scenario', 'total_carbon', 'rmse']
    missing_auxs = []
    for aux in required_auxs:
        if aux not in variables or variables[aux].var_type != 'aux':
            missing_auxs.append(aux)

    if missing_auxs:
        results.append(CheckResult(
            name='Required Converters',
            passed=False,
            message=f'Missing converters: {", ".join(missing_auxs)}',
            points=0,
            max_points=8
        ))
    else:
        results.append(CheckResult(
            name='Required Converters',
            passed=True,
            message='All required converters present (GPP_base, Scenario, Total_Carbon, RMSE)',
            points=8,
            max_points=8
        ))

    return results


def check_calibration(variables: dict[str, Variable]) -> CheckResult:
    """Check that GPP_base is in reasonable calibrated range."""
    if 'gpp_base' not in variables:
        return CheckResult(
            name='Calibration',
            passed=False,
            message='GPP_base converter not found',
            points=0,
            max_points=25
        )

    equation = variables['gpp_base'].equation.strip()

    # Try to extract numeric value
    try:
        value = float(equation)
    except ValueError:
        return CheckResult(
            name='Calibration',
            passed=False,
            message=f'GPP_base is not a simple numeric value: "{equation}"',
            points=10,  # partial credit for having the converter
            max_points=25
        )

    # Check if in calibrated range
    if 100 <= value <= 120:
        if 108 <= value <= 112:  # Near optimal
            return CheckResult(
                name='Calibration',
                passed=True,
                message=f'GPP_base = {value} (well calibrated)',
                points=25,
                max_points=25
            )
        else:
            return CheckResult(
                name='Calibration',
                passed=True,
                message=f'GPP_base = {value} (acceptable range but not optimal)',
                points=20,
                max_points=25
            )
    else:
        return CheckResult(
            name='Calibration',
            passed=False,
            message=f'GPP_base = {value} (outside expected range 100-120)',
            points=5,
            max_points=25
        )


def check_feedback(variables: dict[str, Variable]) -> CheckResult:
    """Detect which feedback mechanism was implemented and verify correctness."""

    # Option A: Q10 temperature feedback
    q10_elements = ['q10', 'temperature', 't_ref']
    has_q10 = all(elem in variables for elem in q10_elements)

    # Option B: Nitrogen limitation
    n_elements = ['available_n', 'kn']
    has_n_limit = all(elem in variables for elem in n_elements)

    # Option C: Deforestation
    has_deforestation = (
        'deforestation_rate' in variables and
        'deforestation' in variables and
        variables['deforestation'].var_type == 'flow'
    )

    if not (has_q10 or has_n_limit or has_deforestation):
        return CheckResult(
            name='Feedback Mechanism',
            passed=False,
            message='No feedback mechanism detected. Need: (Q10+Temperature+T_ref) OR (Available_N+Kn) OR (Deforestation_Rate+Deforestation flow)',
            points=0,
            max_points=25
        )

    # Check equation implementation
    points = 15  # Base points for having the elements
    feedback_type = ''
    details = []

    if has_q10:
        feedback_type = 'Option A: Q10 Temperature Feedback'
        # Check if Het_Resp uses Q10
        het_resp = variables.get('heterotrophic_respiration')
        if het_resp and 'Q10' in het_resp.equation.upper():
            points += 10
            details.append('Het_Resp equation contains Q10')
        else:
            details.append('WARNING: Het_Resp equation does not reference Q10')

        # Check Temperature equation
        temp = variables.get('temperature')
        if temp and 'atmosphere' in temp.equation.lower():
            details.append('Temperature depends on Atmosphere')
        else:
            details.append('WARNING: Temperature should depend on Atmosphere')

    elif has_n_limit:
        feedback_type = 'Option B: Nitrogen Limitation'
        # Check if GPP uses nitrogen
        gpp = variables.get('gpp')
        if gpp and 'available_n' in gpp.equation.lower():
            points += 10
            details.append('GPP equation contains nitrogen term')
        else:
            details.append('WARNING: GPP equation does not reference Available_N')

    elif has_deforestation:
        feedback_type = 'Option C: Deforestation'
        # Check Deforestation flow equation
        deforest = variables.get('deforestation')
        if deforest:
            eq = deforest.equation.lower()
            if 'vegetation' in eq and 'deforestation_rate' in eq:
                points += 10
                details.append('Deforestation flow properly defined')
            else:
                details.append('WARNING: Deforestation should use Vegetation and Deforestation_Rate')

    return CheckResult(
        name='Feedback Mechanism',
        passed=True,
        message=f'{feedback_type}. {"; ".join(details)}',
        points=points,
        max_points=25
    )


def check_scenarios(variables: dict[str, Variable]) -> CheckResult:
    """Check that Emissions equation has proper IF/THEN scenario logic."""

    if 'emissions' not in variables:
        return CheckResult(
            name='Scenario Design',
            passed=False,
            message='Emissions flow not found',
            points=0,
            max_points=20
        )

    emissions_eq = variables['emissions'].equation.upper()

    # Check for IF/THEN logic
    has_if = 'IF' in emissions_eq
    has_then = 'THEN' in emissions_eq
    has_scenario = 'SCENARIO' in emissions_eq

    if not (has_if and has_then):
        return CheckResult(
            name='Scenario Design',
            passed=False,
            message='Emissions equation does not contain IF/THEN logic',
            points=5,
            max_points=20
        )

    if not has_scenario:
        return CheckResult(
            name='Scenario Design',
            passed=False,
            message='Emissions equation does not reference Scenario converter',
            points=10,
            max_points=20
        )

    # Check for multiple scenarios (should have multiple conditions)
    scenario_count = emissions_eq.count('SCENARIO')
    if scenario_count >= 2:
        # Likely has at least 2-3 scenarios
        return CheckResult(
            name='Scenario Design',
            passed=True,
            message=f'Emissions uses IF/THEN with Scenario ({scenario_count} Scenario references)',
            points=20,
            max_points=20
        )
    else:
        return CheckResult(
            name='Scenario Design',
            passed=True,
            message='Emissions uses IF/THEN with Scenario (may only have partial scenarios)',
            points=15,
            max_points=20
        )


def check_mass_conservation(variables: dict[str, Variable]) -> CheckResult:
    """Check that Total_Carbon converter exists and sums the three stocks."""

    if 'total_carbon' not in variables:
        return CheckResult(
            name='Mass Conservation',
            passed=False,
            message='Total_Carbon converter not found',
            points=0,
            max_points=10
        )

    tc = variables['total_carbon']
    eq = tc.equation.lower()

    # Check that it sums the three stocks
    has_atmosphere = 'atmosphere' in eq
    has_vegetation = 'vegetation' in eq
    has_som = 'som' in eq

    if has_atmosphere and has_vegetation and has_som:
        return CheckResult(
            name='Mass Conservation',
            passed=True,
            message='Total_Carbon = Atmosphere + Vegetation + SOM',
            points=10,
            max_points=10
        )
    else:
        missing = []
        if not has_atmosphere:
            missing.append('Atmosphere')
        if not has_vegetation:
            missing.append('Vegetation')
        if not has_som:
            missing.append('SOM')

        return CheckResult(
            name='Mass Conservation',
            passed=False,
            message=f'Total_Carbon missing: {", ".join(missing)}',
            points=5,
            max_points=10
        )


def grade_submission(filepath: str) -> dict:
    """Run all checks and produce a grade report."""

    try:
        variables = parse_stmx(filepath)
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to parse file: {e}',
            'score': 0,
            'max_score': 100,
            'checks': []
        }

    all_results = []

    # Base model (20%)
    base_results = check_base_model(variables)
    all_results.extend(base_results)

    # Calibration (25%)
    all_results.append(check_calibration(variables))

    # Feedback (25%)
    all_results.append(check_feedback(variables))

    # Scenarios (20%)
    all_results.append(check_scenarios(variables))

    # Mass conservation (10%)
    all_results.append(check_mass_conservation(variables))

    # Calculate totals
    total_points = sum(r.points for r in all_results)
    max_points = sum(r.max_points for r in all_results)

    return {
        'success': True,
        'filepath': filepath,
        'score': round(total_points, 1),
        'max_score': round(max_points, 1),
        'percentage': round(100 * total_points / max_points, 1) if max_points > 0 else 0,
        'checks': [asdict(r) for r in all_results]
    }


def print_report(report: dict):
    """Print a human-readable report."""

    if not report['success']:
        print(f"ERROR: {report['error']}")
        return

    print("=" * 60)
    print(f"HW1 Autograder Report")
    print(f"File: {Path(report['filepath']).name}")
    print("=" * 60)
    print()

    for check in report['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']}: {check['points']}/{check['max_points']} pts")
        print(f"  {check['message']}")
        print()

    print("-" * 60)
    print(f"TOTAL: {report['score']}/{report['max_score']} ({report['percentage']}%)")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Autograder for HW1 Terrestrial Carbon Cycle Model'
    )
    parser.add_argument('filepath', help='Path to .stmx file')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')

    args = parser.parse_args()

    if not Path(args.filepath).exists():
        print(f"Error: File not found: {args.filepath}")
        sys.exit(1)

    report = grade_submission(args.filepath)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    # Exit with non-zero if score below 60%
    if report['success'] and report['percentage'] >= 60:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
