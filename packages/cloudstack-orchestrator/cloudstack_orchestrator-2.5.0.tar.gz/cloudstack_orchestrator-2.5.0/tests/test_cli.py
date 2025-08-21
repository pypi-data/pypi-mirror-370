"""Tests for CloudStack Orchestrator CLI."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, AsyncMock
import sys

from cloudstack_orchestrator.cli import app
from cloudstack_orchestrator.core import CloudProvider

runner = CliRunner()


def test_validate_command_success():
    """Test validate command with all prerequisites met."""
    with patch('shutil.which') as mock_which, \
         patch('subprocess.run') as mock_run:
        
        # Mock that all commands exist
        mock_which.return_value = '/usr/bin/command'
        
        # Mock successful kubectl cluster-info
        mock_run.return_value = MagicMock(returncode=0)
        
        result = runner.invoke(app, ["validate"])
        
        assert result.exit_code == 0
        assert "✅ kubectl" in result.stdout
        assert "✅ helm" in result.stdout
        assert "✅ git" in result.stdout
        assert "✅ Kubernetes cluster connected" in result.stdout
        assert "All prerequisites satisfied! ✨" in result.stdout


def test_validate_command_missing_tools():
    """Test validate command with missing tools."""
    with patch('shutil.which') as mock_which:
        # Mock that kubectl is missing
        def which_side_effect(cmd):
            if cmd == 'kubectl':
                return None
            return f'/usr/bin/{cmd}'
        
        mock_which.side_effect = which_side_effect
        
        result = runner.invoke(app, ["validate"])
        
        assert result.exit_code == 1
        assert "❌ kubectl not found" in result.stdout
        assert "✅ helm" in result.stdout
        assert "✅ git" in result.stdout
        assert "❌ Some prerequisites are missing" in result.stdout


def test_validate_command_no_k8s_connection():
    """Test validate command when Kubernetes is not accessible."""
    with patch('shutil.which') as mock_which, \
         patch('subprocess.run') as mock_run:
        
        # All commands exist
        mock_which.return_value = '/usr/bin/command'
        
        # kubectl cluster-info fails
        mock_run.return_value = MagicMock(returncode=1)
        
        result = runner.invoke(app, ["validate"])
        
        assert result.exit_code == 1
        assert "✅ kubectl" in result.stdout
        assert "❌ Cannot connect to Kubernetes cluster" in result.stdout


def test_status_command():
    """Test status command."""
    with patch('cloudstack_orchestrator.cli.Orchestrator') as mock_orchestrator:
        # Mock the orchestrator instance
        mock_instance = MagicMock()
        mock_orchestrator.return_value = mock_instance
        
        # Mock get_status to return a valid status
        mock_instance.get_status = AsyncMock(return_value={
            "kubernetes": {"connected": True},
            "argocd": {"installed": True},
            "platform": {"deployed": False}
        })
        
        result = runner.invoke(app, ["status"])
        
        assert result.exit_code == 0
        assert "📊 CloudStack Orchestrator Status" in result.stdout
        assert "Kubernetes: Connected" in result.stdout
        assert "ArgoCD: Installed" in result.stdout
        assert "Platform: Not deployed" in result.stdout


def test_setup_interactive_cancelled():
    """Test setup command when user cancels."""
    with patch('typer.prompt') as mock_prompt, \
         patch('typer.confirm') as mock_confirm:
        
        mock_prompt.side_effect = [
            "platform.local",  # domain
            "my-org",          # github org
            "ghp_token123"     # github token
        ]
        
        # User cancels the setup
        mock_confirm.return_value = False
        
        result = runner.invoke(app, ["setup"])
        
        assert result.exit_code == 0
        assert "⚠️ Setup cancelled" in result.stdout


def test_setup_non_interactive_missing_params():
    """Test setup command in non-interactive mode with missing parameters."""
    result = runner.invoke(app, [
        "setup",
        "--non-interactive",
        "--github-org", "my-org"
        # Missing domain and token
    ])
    
    assert result.exit_code == 1
    assert "Error: Missing required configuration" in result.stdout


def test_setup_non_interactive_success():
    """Test successful non-interactive setup."""
    with patch('cloudstack_orchestrator.cli.Orchestrator') as mock_orchestrator:
        # Mock the orchestrator instance
        mock_instance = MagicMock()
        mock_orchestrator.return_value = mock_instance
        
        # Mock successful setup
        mock_instance.setup = AsyncMock(return_value={
            "prerequisites": {"valid": True},
            "secrets": {"count": 5, "created": True},
            "argocd": {
                "installed": True,
                "admin_password": "test-password",
                "url": "http://localhost:30080"
            }
        })
        
        result = runner.invoke(app, [
            "setup",
            "--non-interactive",
            "--domain", "platform.local",
            "--github-org", "my-org",
            "--github-token", "ghp_token123"
        ])
        
        assert result.exit_code == 0
        assert "🚀 CloudStack Orchestrator Setup" in result.stdout
        assert "✅ Setup completed successfully!" in result.stdout
        assert "ArgoCD URL:" in result.stdout
        assert "📌 Next steps:" in result.stdout


def test_secrets_list_command():
    """Test secrets list command."""
    result = runner.invoke(app, ["secrets", "list"])
    
    assert result.exit_code == 0
    assert "Secret management coming soon!" in result.stdout


def test_secrets_rotate_command():
    """Test secrets rotate command."""
    result = runner.invoke(app, ["secrets", "rotate", "github-token"])
    
    assert result.exit_code == 0
    assert "Rotating github-token coming soon!" in result.stdout


def test_module_list_command():
    """Test module list command."""
    result = runner.invoke(app, ["module", "list"])
    
    assert result.exit_code == 0
    assert "Module listing coming soon!" in result.stdout


def test_module_deploy_command():
    """Test module deploy command."""
    result = runner.invoke(app, ["module", "deploy", "voicefuse"])
    
    assert result.exit_code == 0
    assert "Deploying voicefuse coming soon!" in result.stdout


@pytest.mark.parametrize("provider,expected", [
    ("local", CloudProvider.LOCAL),
    ("aws", CloudProvider.AWS),
    ("gcp", CloudProvider.GCP),
    ("azure", CloudProvider.AZURE),
])
def test_setup_provider_options(provider, expected):
    """Test different provider options."""
    with patch('cloudstack_orchestrator.cli.Orchestrator') as mock_orchestrator, \
         patch('typer.confirm') as mock_confirm:
        
        mock_confirm.return_value = False  # Cancel to avoid full setup
        
        result = runner.invoke(app, [
            "setup",
            "--provider", provider,
            "--domain", "test.com",
            "--github-org", "org",
            "--github-token", "token"
        ])
        
        # Verify the orchestrator was called with correct provider
        if mock_orchestrator.called:
            config_arg = mock_orchestrator.call_args[0][0]
            assert config_arg.provider == expected
        else:
            # If cancelled before orchestrator creation, just verify no error
            assert result.exit_code == 0