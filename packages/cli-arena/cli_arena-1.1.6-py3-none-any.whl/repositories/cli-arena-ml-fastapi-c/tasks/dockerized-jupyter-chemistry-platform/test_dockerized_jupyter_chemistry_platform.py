from click.testing import CliRunner
from src.dockerized_jupyter_chemistry_platform.cli import main as cli_main
import pytest

# Test launching and checking status on multiple ports
def test_launch_and_status_multiple_ports():
    runner = CliRunner()
    for port in [8888, 8899, 8900]:
        result = runner.invoke(cli_main, ['launch', '--port', str(port)])
        assert result.exit_code == 0
        assert 'Jupyter launched at' in result.output
        result = runner.invoke(cli_main, ['status'])
        assert result.exit_code == 0
        assert 'Platform status' in result.output
        assert 'running' in result.output

# Test installing multiple chemistry packages and checking status
def test_install_multiple_packages():
    runner = CliRunner()
    runner.invoke(cli_main, ['launch'])
    for pkg in ['rdkit', 'openbabel', 'pymatgen', 'ase']:
        result = runner.invoke(cli_main, ['install', '--package', pkg])
        assert result.exit_code == 0
        assert 'Package installed' in result.output
        result = runner.invoke(cli_main, ['status'])
        assert pkg in result.output

# Test error handling: invalid package, port conflict, install before launch
def test_error_handling():
    runner = CliRunner()
    # Invalid package
    result = runner.invoke(cli_main, ['install', '--package', 'notapkg'])
    assert result.exit_code != 0 or 'Error' in result.output
    # Port conflict
    runner.invoke(cli_main, ['launch', '--port', '8888'])
    result = runner.invoke(cli_main, ['launch', '--port', '8888'])
    assert result.exit_code != 0 or 'Error' in result.output
    # Install before launch
    result = runner.invoke(cli_main, ['install', '--package', 'rdkit'])
    assert result.exit_code != 0 or 'Error' in result.output

# Test repeated launches and installs
def test_repeated_launch_install():
    runner = CliRunner()
    for _ in range(3):
        runner.invoke(cli_main, ['launch', '--port', '8901'])
        result = runner.invoke(cli_main, ['install', '--package', 'rdkit'])
        assert result.exit_code == 0
        result = runner.invoke(cli_main, ['status'])
        assert 'rdkit' in result.output

# Test stress: many package installs
def test_stress_many_installs():
    runner = CliRunner()
    runner.invoke(cli_main, ['launch'])
    for i in range(20):
        pkg = f'pkg{i}'
        runner.invoke(cli_main, ['install', '--package', pkg])
    result = runner.invoke(cli_main, ['status'])
    for i in range(20):
        assert f'pkg{i}' in result.output 