import os
import tempfile
import pytest
import yaml
from click.testing import CliRunner
from src.multi_cloud_cicd_for_fea_docker_tools.cli import main as cli_main

def create_config(path, valid=True):
    if valid:
        config = {'pipeline': {'steps': ['build', 'test', 'deploy'], 'notifications': ['slack', 'email'], 'triggers': ['push', 'pull_request']}}
    else:
        config = {'pipeline': {'steps': []}}
    with open(path, 'w') as f:
        yaml.dump(config, f)

# Test setup, deploy, and status for all providers and environments
def test_full_pipeline_all_providers_envs(tmp_path):
    config_path = tmp_path / 'pipeline.yaml'
    create_config(str(config_path))
    runner = CliRunner()
    for provider in ['aws', 'gcp', 'azure']:
        result = runner.invoke(cli_main, ['setup', '--provider', provider, '--config', str(config_path)])
        assert result.exit_code == 0
        assert 'Pipeline setup complete' in result.output
        for env in ['prod', 'staging', 'dev']:
            result = runner.invoke(cli_main, ['deploy', '--provider', provider, '--image', 'fea:latest', '--env', env])
            assert result.exit_code == 0
            assert 'Deployment complete' in result.output
            result = runner.invoke(cli_main, ['status', '--provider', provider, '--env', env])
            assert result.exit_code == 0
            assert 'Status for' in result.output

# Test error handling: invalid provider, invalid config, missing image/env
def test_error_handling(tmp_path):
    runner = CliRunner()
    config_path = tmp_path / 'pipeline.yaml'
    create_config(str(config_path))
    # Invalid provider
    result = runner.invoke(cli_main, ['setup', '--provider', 'digitalocean', '--config', str(config_path)])
    assert result.exit_code != 0 or 'Error' in result.output
    result = runner.invoke(cli_main, ['deploy', '--provider', 'digitalocean', '--image', 'fea:latest', '--env', 'prod'])
    assert result.exit_code != 0 or 'Error' in result.output
    result = runner.invoke(cli_main, ['status', '--provider', 'digitalocean', '--env', 'prod'])
    assert result.exit_code != 0 or 'Error' in result.output
    # Invalid config
    bad_config_path = tmp_path / 'bad_pipeline.yaml'
    create_config(str(bad_config_path), valid=False)
    result = runner.invoke(cli_main, ['setup', '--provider', 'aws', '--config', str(bad_config_path)])
    assert result.exit_code != 0 or 'Error' in result.output
    # Missing image/env
    result = runner.invoke(cli_main, ['deploy', '--provider', 'aws', '--image', '', '--env', ''])
    assert result.exit_code != 0 or 'Error' in result.output
    result = runner.invoke(cli_main, ['status', '--provider', 'aws', '--env', ''])
    assert result.exit_code != 0 or 'Error' in result.output

# Test repeated setups and deployments
def test_repeated_setups_deployments(tmp_path):
    config_path = tmp_path / 'pipeline.yaml'
    create_config(str(config_path))
    runner = CliRunner()
    for _ in range(3):
        for provider in ['aws', 'gcp', 'azure']:
            runner.invoke(cli_main, ['setup', '--provider', provider, '--config', str(config_path)])
            for env in ['prod', 'staging', 'dev']:
                runner.invoke(cli_main, ['deploy', '--provider', provider, '--image', 'fea:latest', '--env', env])
                result = runner.invoke(cli_main, ['status', '--provider', provider, '--env', env])
                assert result.exit_code == 0
                assert 'Status for' in result.output

# Test stress: batch pipeline setups and deployments
def test_stress_batch_pipelines(tmp_path):
    config_path = tmp_path / 'pipeline.yaml'
    create_config(str(config_path))
    runner = CliRunner()
    for i in range(10):
        for provider in ['aws', 'gcp', 'azure']:
            runner.invoke(cli_main, ['setup', '--provider', provider, '--config', str(config_path)])
            for env in ['prod', 'staging', 'dev']:
                runner.invoke(cli_main, ['deploy', '--provider', provider, '--image', 'fea:latest', '--env', env])
                result = runner.invoke(cli_main, ['status', '--provider', provider, '--env', env])
                assert result.exit_code == 0
                assert 'Status for' in result.output 