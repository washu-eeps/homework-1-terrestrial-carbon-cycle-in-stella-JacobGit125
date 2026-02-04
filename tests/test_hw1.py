"""
Pytest wrapper for HW1 autograder.

Finds the student's .stmx submission and runs the autograder checks.
"""

import pytest
from pathlib import Path
from hw1_autograder import parse_stmx, check_base_model, check_calibration, \
    check_feedback, check_scenarios, check_mass_conservation


def find_submission() -> Path:
    """Find the student's .stmx submission file."""
    repo_root = Path(__file__).parent.parent

    # Look for any .stmx file that isn't the starter
    stmx_files = list(repo_root.glob("*.stmx"))

    # Filter out the starter file
    submissions = [f for f in stmx_files if "starter" not in f.name.lower()]

    if not submissions:
        # Maybe they edited the starter directly
        submissions = stmx_files

    if not submissions:
        pytest.fail("No .stmx file found in repository!")

    # Return the most recently modified one
    return max(submissions, key=lambda f: f.stat().st_mtime)


@pytest.fixture(scope="module")
def variables():
    """Parse the submission and return variables dict."""
    submission = find_submission()
    print(f"\nGrading: {submission.name}")
    return parse_stmx(str(submission))


class TestBaseModel:
    """Tests for base model structure (20%)."""

    def test_required_stocks(self, variables):
        """Check that all 3 stocks are present."""
        required = ['atmosphere', 'vegetation', 'som']
        missing = [s for s in required if s not in variables or variables[s].var_type != 'stock']
        assert not missing, f"Missing stocks: {', '.join(missing)}"

    def test_required_flows(self, variables):
        """Check that all 5 flows are present."""
        required = ['gpp', 'autotrophic_respiration', 'litterfall',
                   'heterotrophic_respiration', 'emissions']
        missing = [f for f in required if f not in variables or variables[f].var_type != 'flow']
        assert not missing, f"Missing flows: {', '.join(missing)}"

    def test_required_converters(self, variables):
        """Check that key converters are present."""
        required = ['gpp_base', 'scenario', 'total_carbon', 'rmse']
        missing = [c for c in required if c not in variables or variables[c].var_type != 'aux']
        assert not missing, f"Missing converters: {', '.join(missing)}"


class TestCalibration:
    """Tests for calibration (25%)."""

    def test_gpp_base_exists(self, variables):
        """GPP_base converter must exist."""
        assert 'gpp_base' in variables, "GPP_base converter not found"

    def test_gpp_base_is_numeric(self, variables):
        """GPP_base should be a numeric value."""
        if 'gpp_base' not in variables:
            pytest.skip("GPP_base not found")

        equation = variables['gpp_base'].equation.strip()
        try:
            float(equation)
        except ValueError:
            pytest.fail(f"GPP_base is not a simple numeric value: '{equation}'")

    def test_gpp_base_in_range(self, variables):
        """GPP_base should be in reasonable calibrated range."""
        if 'gpp_base' not in variables:
            pytest.skip("GPP_base not found")

        equation = variables['gpp_base'].equation.strip()
        try:
            value = float(equation)
        except ValueError:
            pytest.skip("GPP_base is not numeric")

        assert 100 <= value <= 120, f"GPP_base = {value} is outside expected range (100-120)"


class TestFeedback:
    """Tests for feedback mechanism (25%)."""

    def test_feedback_implemented(self, variables):
        """At least one feedback mechanism must be implemented."""
        # Option A: Q10 temperature feedback
        has_q10 = all(elem in variables for elem in ['q10', 'temperature', 't_ref'])

        # Option B: Nitrogen limitation
        has_n_limit = all(elem in variables for elem in ['available_n', 'kn'])

        # Option C: Deforestation
        has_deforestation = (
            'deforestation_rate' in variables and
            'deforestation' in variables and
            variables['deforestation'].var_type == 'flow'
        )

        assert has_q10 or has_n_limit or has_deforestation, \
            "No feedback mechanism detected. Need: (Q10+Temperature+T_ref) OR (Available_N+Kn) OR (Deforestation_Rate+Deforestation flow)"

    def test_feedback_equations(self, variables):
        """Feedback mechanism should be properly wired into model."""
        # Check Option A
        if all(elem in variables for elem in ['q10', 'temperature', 't_ref']):
            het_resp = variables.get('heterotrophic_respiration')
            if het_resp:
                assert 'q10' in het_resp.equation.lower(), \
                    "Q10 feedback: Heterotrophic_Respiration should reference Q10"
            return

        # Check Option B
        if all(elem in variables for elem in ['available_n', 'kn']):
            gpp = variables.get('gpp')
            if gpp:
                assert 'available_n' in gpp.equation.lower(), \
                    "N limitation feedback: GPP should reference Available_N"
            return

        # Check Option C
        if 'deforestation' in variables and variables['deforestation'].var_type == 'flow':
            deforest = variables.get('deforestation')
            if deforest:
                eq = deforest.equation.lower()
                assert 'vegetation' in eq, \
                    "Deforestation flow should reference Vegetation"


class TestScenarios:
    """Tests for scenario design (20%)."""

    def test_emissions_exists(self, variables):
        """Emissions flow must exist."""
        assert 'emissions' in variables, "Emissions flow not found"

    def test_scenario_selector_exists(self, variables):
        """Scenario converter must exist."""
        assert 'scenario' in variables, "Scenario converter not found"

    def test_emissions_uses_scenarios(self, variables):
        """Emissions equation should use IF/THEN with Scenario."""
        if 'emissions' not in variables:
            pytest.skip("Emissions not found")

        emissions_eq = variables['emissions'].equation.upper()

        assert 'IF' in emissions_eq and 'THEN' in emissions_eq, \
            "Emissions equation should use IF/THEN logic"

        assert 'SCENARIO' in emissions_eq, \
            "Emissions equation should reference Scenario converter"


class TestMassConservation:
    """Tests for mass conservation (10%)."""

    def test_total_carbon_exists(self, variables):
        """Total_Carbon converter must exist."""
        assert 'total_carbon' in variables, "Total_Carbon converter not found"

    def test_total_carbon_sums_stocks(self, variables):
        """Total_Carbon should sum all three stocks."""
        if 'total_carbon' not in variables:
            pytest.skip("Total_Carbon not found")

        tc = variables['total_carbon']
        eq = tc.equation.lower()

        assert 'atmosphere' in eq, "Total_Carbon missing Atmosphere"
        assert 'vegetation' in eq, "Total_Carbon missing Vegetation"
        assert 'som' in eq, "Total_Carbon missing SOM"
