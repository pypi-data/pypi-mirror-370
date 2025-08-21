# CloudStack Orchestrator

A unified SDK and CLI for automated Kubernetes platform management using GitOps principles.

## Features

- 🚀 **Zero-touch cluster bootstrapping** - Automated setup with minimal manual steps
- 🔐 **Integrated secrets management** - AWS Secrets Manager support with automatic generation
- 🤖 **Multiple interfaces** - Use as CLI or SDK for programmatic access
- ☁️ **Multi-cloud ready** - Support for AWS, GCP, Azure, and local development
- 🔄 **GitOps native** - Built on ArgoCD with the app-of-apps pattern

## Installation

```bash
# Install from PyPI
uv tool install cloudstack-orchestrator

# Or add to your project
uv add cloudstack-orchestrator
```

## Quick Start

### CLI Usage

```bash
# Interactive setup
cso setup

# Non-interactive setup
cso setup \
  --provider aws \
  --cluster my-cluster \
  --domain platform.example.com \
  --github-org my-org \
  --region us-east-1

# Check status
cso status

# Validate prerequisites
cso validate
```

### SDK Usage

```python
from cloudstack_orchestrator import CloudStackSDK, Config, CloudProvider
from cloudstack_orchestrator.core.config import GitHubConfig

# Create configuration
config = Config(
    provider=CloudProvider.AWS,
    region="us-east-1", 
    cluster_name="my-cluster",
    domain="platform.example.com",
    github=GitHubConfig(
        org="my-org",
        token="ghp_..."
    )
)

# Initialize SDK
sdk = CloudStackSDK(config)

# Run setup
await sdk.setup()

# Check status
status = await sdk.get_status()
```


## Architecture

CloudStack Orchestrator sets up:

- **ArgoCD** - GitOps continuous delivery
- **Istio** - Service mesh for traffic management
- **Keycloak** - Identity and access management
- **Prometheus/Grafana** - Monitoring and observability
- **Cert-Manager** - Automatic TLS certificate management

## Development

```bash
# Clone the repository
git clone https://github.com/killerapp/cloudstack-orchestrator
cd cloudstack-orchestrator/cso-cli

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run CLI in development
uv run python -m cloudstack_orchestrator.cli
```

## Publishing to PyPI

```bash
# Build the package
uv build

# Publish to PyPI
uv publish
```

## License

MIT