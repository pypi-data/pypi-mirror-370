from click.testing import CliRunner
from src.chem_aware_rest_api_in_kubernetes.cli import main as cli_main
import pytest

@pytest.mark.parametrize('namespace', ['chem-ns1', 'chem-ns2', 'chem-ns3'])
def test_deploy_and_status(namespace):
    runner = CliRunner()
    result = runner.invoke(cli_main, ['deploy', '--namespace', namespace])
    assert result.exit_code == 0
    assert 'API deployed to namespace' in result.output
    result = runner.invoke(cli_main, ['status', '--namespace', namespace])
    assert result.exit_code == 0
    assert 'API status for' in result.output
    assert 'deployed' in result.output

@pytest.mark.parametrize('smiles,expected', [
    ('C', 'Methane'),
    ('O', 'Oxygen'),
    ('CCO', 'Ethanol'),
    ('N', ''),
    ('C1CCCCC1', 'Cyclohexane'),
    ('C=O', 'Formaldehyde'),
    ('C#N', 'Hydrogen cyanide')
])
def test_query(smiles, expected):
    runner = CliRunner()
    result = runner.invoke(cli_main, ['query', '--smiles', smiles])
    assert result.exit_code == 0
    assert 'Query result' in result.output
    if expected:
        assert expected in result.output

# Test error handling for unknown namespace
def test_error_handling_unknown_ns():
    runner = CliRunner()
    result = runner.invoke(cli_main, ['status', '--namespace', 'unknown-ns'])
    assert result.exit_code == 0
    assert 'not deployed' in result.output

# Test error handling for invalid SMILES
def test_error_handling_invalid_smiles():
    runner = CliRunner()
    result = runner.invoke(cli_main, ['query', '--smiles', 'INVALID'])
    assert result.exit_code != 0 or 'Error' in result.output

# Test redeploying to the same namespace
def test_redeploy_namespace():
    runner = CliRunner()
    ns = 'chem-ns-redeploy'
    runner.invoke(cli_main, ['deploy', '--namespace', ns])
    result = runner.invoke(cli_main, ['deploy', '--namespace', ns])
    assert result.exit_code == 0
    assert 'already deployed' in result.output or 'API deployed' in result.output

# Test status with no deployment
def test_status_no_deployment():
    runner = CliRunner()
    ns = 'chem-ns-never-deployed'
    result = runner.invoke(cli_main, ['status', '--namespace', ns])
    assert result.exit_code == 0
    assert 'not deployed' in result.output 