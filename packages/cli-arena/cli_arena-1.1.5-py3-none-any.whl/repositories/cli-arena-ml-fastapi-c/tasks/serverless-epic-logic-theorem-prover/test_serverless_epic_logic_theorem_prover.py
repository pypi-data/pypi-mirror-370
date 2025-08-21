import pytest
from click.testing import CliRunner
from src.serverless_epic_logic_theorem_prover.cli import main as cli_main

# Test submitting multiple theorems and retrieving their results
def test_submit_multiple_theorems_and_results():
    runner = CliRunner()
    job_ids = []
    theorems = [
        'A -> B',
        'A & B -> B & A',
        '(A -> B) & (B -> C) -> (A -> C)',
        'A | (B & C) -> (A | B) & (A | C)',
        'not (A & B) -> (not A) | (not B)'
    ]
    for thm in theorems:
        result = runner.invoke(cli_main, ['submit', '--theorem', thm])
        assert result.exit_code == 0
        assert 'Proof job submitted. Job ID:' in result.output
        job_id = result.output.split('Job ID:')[1].strip()
        job_ids.append(job_id)
    for job_id in job_ids:
        status = runner.invoke(cli_main, ['status', '--job-id', job_id])
        assert status.exit_code == 0
        assert 'Status for job' in status.output
        result = runner.invoke(cli_main, ['result', '--job-id', job_id])
        assert result.exit_code == 0
        assert 'Result for job' in result.output

# Test error handling: nonexistent job, empty theorem
def test_error_handling():
    runner = CliRunner()
    # Nonexistent job
    result = runner.invoke(cli_main, ['status', '--job-id', 'nonexistent'])
    assert result.exit_code != 0 or 'Error' in result.output
    result = runner.invoke(cli_main, ['result', '--job-id', 'nonexistent'])
    assert result.exit_code != 0 or 'Error' in result.output
    # Empty theorem
    result = runner.invoke(cli_main, ['submit', '--theorem', ''])
    assert result.exit_code != 0 or 'Error' in result.output

# Test repeated submissions and status/result checks
def test_repeated_submissions_and_checks():
    runner = CliRunner()
    for _ in range(3):
        result = runner.invoke(cli_main, ['submit', '--theorem', 'A -> B'])
        assert result.exit_code == 0
        job_id = result.output.split('Job ID:')[1].strip()
        for _ in range(2):
            status = runner.invoke(cli_main, ['status', '--job-id', job_id])
            assert status.exit_code == 0
            result2 = runner.invoke(cli_main, ['result', '--job-id', job_id])
            assert result2.exit_code == 0

# Test stress: batch theorem submissions and result retrievals
def test_stress_batch_theorems():
    runner = CliRunner()
    job_ids = []
    for i in range(10):
        thm = f'A{i} -> B{i}'
        result = runner.invoke(cli_main, ['submit', '--theorem', thm])
        assert result.exit_code == 0
        job_id = result.output.split('Job ID:')[1].strip()
        job_ids.append(job_id)
    for job_id in job_ids:
        status = runner.invoke(cli_main, ['status', '--job-id', job_id])
        assert status.exit_code == 0
        result2 = runner.invoke(cli_main, ['result', '--job-id', job_id])
        assert result2.exit_code == 0 