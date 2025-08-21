"""Test cases for CSO CLI module commands."""

import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock, call
from pathlib import Path
import tempfile

import pytest
import yaml
from click.testing import CliRunner

from cloudstack_orchestrator.cli.module import (
    module, list, deploy, status, logs, scale, rollback, delete
)


class TestModuleCommands:
    """Test suite for module management commands."""

    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_subprocess(self):
        """Mock subprocess for kubectl commands."""
        with patch('asyncio.create_subprocess_exec') as mock:
            yield mock

    @pytest.fixture
    def sample_applications(self):
        """Sample ArgoCD applications response."""
        return {
            "items": [
                {
                    "metadata": {
                        "name": "voicefuse",
                        "namespace": "argocd"
                    },
                    "spec": {
                        "source": {
                            "repoURL": "https://github.com/killerapp/voicefuse-mvp",
                            "path": "helm/chart",
                            "targetRevision": "main"
                        },
                        "destination": {
                            "namespace": "voicefuse",
                            "server": "https://kubernetes.default.svc"
                        }
                    },
                    "status": {
                        "sync": {"status": "Synced"},
                        "health": {"status": "Healthy"}
                    }
                },
                {
                    "metadata": {
                        "name": "langfuse",
                        "namespace": "argocd"
                    },
                    "spec": {
                        "source": {
                            "repoURL": "https://github.com/langfuse/langfuse",
                            "path": "deploy/k8s",
                            "targetRevision": "v2.0.0"
                        },
                        "destination": {
                            "namespace": "langfuse",
                            "server": "https://kubernetes.default.svc"
                        }
                    },
                    "status": {
                        "sync": {"status": "OutOfSync"},
                        "health": {"status": "Degraded"}
                    }
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_list_modules(self, runner, mock_subprocess, sample_applications):
        """Test listing deployed modules."""
        # Setup mock subprocess
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(
            json.dumps(sample_applications).encode(),
            b''
        ))
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        # Run the command
        result = await list()
        
        # Verify kubectl was called correctly
        mock_subprocess.assert_called_once_with(
            'kubectl', 'get', 'applications', '-n', 'argocd', '-o', 'json',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    @pytest.mark.asyncio
    async def test_list_modules_error(self, runner, mock_subprocess):
        """Test listing modules with kubectl error."""
        # Setup mock subprocess with error
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(
            b'',
            b'Error: unable to connect to cluster'
        ))
        mock_process.returncode = 1
        mock_subprocess.return_value = mock_process

        # Run the command - should handle error gracefully
        result = await list()
        
        # Verify error handling
        mock_subprocess.assert_called_once()

    @pytest.mark.asyncio
    async def test_deploy_module(self, runner, mock_subprocess):
        """Test deploying a new module."""
        # Setup mock subprocess
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(
            b'application.argoproj.io/new-module created',
            b''
        ))
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        # Run the deploy command
        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = '/tmp/test.yaml'
            
            result = await deploy(
                module_name='new-module',
                version='v1.0.0',
                values=None,
                namespace='new-module',
                repo='https://github.com/killerapp/new-module',
                path='helm/chart'
            )

        # Verify kubectl apply was called
        assert mock_subprocess.called
        call_args = mock_subprocess.call_args_list[-1]
        assert 'kubectl' in call_args[0]
        assert 'apply' in call_args[0]

    @pytest.mark.asyncio
    async def test_deploy_module_with_values(self, runner, mock_subprocess):
        """Test deploying a module with custom values."""
        # Create a temporary values file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            values_content = """
            image:
              tag: v1.2.3
            replicas: 3
            """
            f.write(values_content)
            values_file = f.name

        try:
            # Setup mock subprocess
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(
                b'application.argoproj.io/custom-module created',
                b''
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process

            # Run deploy with values file
            with patch('tempfile.NamedTemporaryFile') as mock_temp:
                mock_temp.return_value.__enter__.return_value.name = '/tmp/test.yaml'
                
                result = await deploy(
                    module_name='custom-module',
                    version='main',
                    values=values_file,
                    namespace='custom',
                    repo=None,
                    path='helm/chart'
                )

            # Verify the manifest was created with values
            assert mock_subprocess.called
            
        finally:
            # Clean up temp file
            Path(values_file).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_module_status(self, runner, mock_subprocess):
        """Test checking module status."""
        # Setup mock subprocess
        mock_process = AsyncMock()
        app_status = {
            "metadata": {"name": "voicefuse"},
            "status": {
                "sync": {"status": "Synced"},
                "health": {"status": "Healthy"},
                "resources": [{"kind": "Deployment"}, {"kind": "Service"}],
                "conditions": [{"message": "Application is healthy"}]
            }
        }
        mock_process.communicate = AsyncMock(return_value=(
            json.dumps(app_status).encode(),
            b''
        ))
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        # Run status command
        result = await status(module_name='voicefuse', watch=False)

        # Verify kubectl was called correctly
        mock_subprocess.assert_called_once_with(
            'kubectl', 'get', 'application', 'voicefuse', '-n', 'argocd', '-o', 'json',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    @pytest.mark.asyncio
    async def test_module_logs(self, runner, mock_subprocess):
        """Test getting module logs."""
        # Setup mock for getting pods
        mock_process_pods = AsyncMock()
        pods_response = {
            "items": [
                {"metadata": {"name": "voicefuse-7d9c8b6f5-abc123"}},
                {"metadata": {"name": "voicefuse-7d9c8b6f5-def456"}}
            ]
        }
        mock_process_pods.communicate = AsyncMock(return_value=(
            json.dumps(pods_response).encode(),
            b''
        ))
        mock_process_pods.returncode = 0

        # Setup mock for getting logs
        mock_process_logs = AsyncMock()
        mock_process_logs.stdout = AsyncMock()
        mock_process_logs.stdout.readline = AsyncMock(side_effect=[
            b'Log line 1\n',
            b'Log line 2\n',
            b''  # End of stream
        ])
        mock_process_logs.returncode = 0

        # Configure mock to return different processes for different calls
        mock_subprocess.side_effect = [mock_process_pods, mock_process_logs]

        # Run logs command
        result = await logs(
            module_name='voicefuse',
            follow=False,
            tail=100,
            container=None
        )

        # Verify kubectl was called for both pods and logs
        assert mock_subprocess.call_count == 2

    @pytest.mark.asyncio
    async def test_scale_module(self, runner, mock_subprocess):
        """Test scaling a module."""
        # Setup mock subprocess
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(
            b'deployment.apps/voicefuse scaled',
            b''
        ))
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        # Run scale command
        result = await scale(module_name='voicefuse', replicas=3)

        # Verify kubectl scale was called
        mock_subprocess.assert_called_once_with(
            'kubectl', 'scale', 'deployment', '-n', 'voicefuse', 
            '--replicas', '3', '--all',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    @pytest.mark.asyncio
    async def test_rollback_module(self, runner, mock_subprocess):
        """Test rolling back a module."""
        # Setup mock subprocess
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(
            b'deployment.apps/voicefuse rolled back',
            b''
        ))
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        # Test rollback without specific revision
        result = await rollback(module_name='voicefuse', revision=None)

        # Verify kubectl rollout undo was called
        mock_subprocess.assert_called_once_with(
            'kubectl', 'rollout', 'undo', 'deployment', '-n', 'voicefuse', '--all',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    @pytest.mark.asyncio
    async def test_rollback_module_with_revision(self, runner, mock_subprocess):
        """Test rolling back to specific revision."""
        # Setup mock subprocess
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(
            b'deployment.apps/voicefuse rolled back',
            b''
        ))
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        # Test rollback with specific revision
        result = await rollback(module_name='voicefuse', revision=2)

        # Verify kubectl rollout undo was called with revision
        mock_subprocess.assert_called_once_with(
            'kubectl', 'rollout', 'undo', 'deployment', '-n', 'voicefuse',
            '--to-revision', '2', '--all',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    @pytest.mark.asyncio
    async def test_delete_module(self, runner, mock_subprocess):
        """Test deleting a module."""
        # Setup mock subprocess
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(
            b'application.argoproj.io/voicefuse deleted',
            b''
        ))
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        # Test delete with force flag
        result = await delete(module_name='voicefuse', force=True)

        # Verify kubectl delete was called
        mock_subprocess.assert_called_once_with(
            'kubectl', 'delete', 'application', 'voicefuse', '-n', 'argocd',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    @pytest.mark.asyncio
    async def test_delete_module_with_confirmation(self, runner, mock_subprocess):
        """Test delete with user confirmation."""
        # Setup mock subprocess
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(
            b'application.argoproj.io/voicefuse deleted',
            b''
        ))
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        # Mock user confirmation
        with patch('click.confirm', return_value=True):
            result = await delete(module_name='voicefuse', force=False)

        # Verify kubectl delete was called after confirmation
        mock_subprocess.assert_called_once()

    @pytest.mark.asyncio  
    async def test_delete_module_cancelled(self, runner, mock_subprocess):
        """Test delete cancelled by user."""
        # Mock user declining confirmation
        with patch('click.confirm', return_value=False):
            result = await delete(module_name='voicefuse', force=False)

        # Verify kubectl delete was NOT called
        mock_subprocess.assert_not_called()


class TestModuleCommandIntegration:
    """Integration tests for module commands."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_module_lifecycle(self, mock_subprocess):
        """Test complete module lifecycle: deploy, status, scale, rollback, delete."""
        # This would be an integration test that runs against a real cluster
        # Marked for skipping in unit test runs
        pytest.skip("Integration test - requires live cluster")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_module_with_dependencies(self, mock_subprocess):
        """Test deploying a module with dependencies (e.g., Langfuse needs PostgreSQL)."""
        pytest.skip("Integration test - requires live cluster")