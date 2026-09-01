# CI/CD Quick Start Guide

## 🎯 What's Included

Your ngina project now has a complete CI/CD pipeline that:
- ✅ Lints Python and TypeScript code
- ✅ Runs unit tests
- ✅ Runs integration tests with MQTT
- ✅ Builds Docker images
- ✅ Pushes to Docker Hub
- ✅ Validates Docker Compose configuration

## 🔧 Setup (5 minutes)

### Step 1: Configure Docker Hub Credentials

1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - **DOCKER_HUB_USERNAME**: Your Docker Hub username
   - **DOCKER_HUB_TOKEN**: Your Docker Hub Personal Access Token

**To get your Docker Hub token:**
- Visit https://hub.docker.com/settings/security
- Click "New Access Token"
- Name it `github-actions`
- Select "Read, Write, Delete" permissions
- Copy the token and add it to GitHub secrets

### Step 2: Make Your First Commit

```bash
git add .
git commit -m "Add CI/CD pipeline"
git push origin develop/ngina-orchestrator  # or main
```

### Step 3: Monitor the Pipeline

- Go to your GitHub repo → **Actions** tab
- Watch the workflow run
- Check logs for any failures

## 🚀 Local Development

### Install Everything

```bash
bash scripts/setup-cicd.sh
```

Or manually:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 isort
npm install
cd src/backend && npm install && cd ../..
```

### Run Tests

```bash
make test              # All tests
make test-python       # Python only
make test-node         # Node.js only
```

### Check Code Quality

```bash
make lint              # Run linters
make format-fix        # Auto-format code
```

### Start Services

```bash
make docker-up         # Start with Docker Compose
make docker-logs       # View logs
make docker-down       # Stop services
```

## 📋 All Available Commands

```bash
make help              # Show all commands
make install           # Install dependencies
make test              # Run all tests
make lint              # Check code quality
make format-fix        # Auto-format code
make build             # Build services
make docker-up         # Start Docker Compose
make docker-down       # Stop services
make clean             # Remove build artifacts
```

## 🔄 Pipeline Flow

```
On Push/PR to main or develop/ngina-orchestrator:
  │
  ├─► Python Lint & Format
  ├─► Python Tests
  ├─► TypeScript Lint
  ├─► Node.js Tests
  ├─► Docker Validation
  │
  └─► Docker Build & Push (only on push, not PRs)
        ├─ Build: ngina-python-api
        ├─ Build: ngina-node-publisher
        └─ Push to Docker Hub (if secrets configured)
```

## 🏷️ Docker Image Tags

Your images will be tagged and pushed as:

**On `main` branch:**
- `docker.io/YOUR_USERNAME/ngina-python-api:latest`
- `docker.io/YOUR_USERNAME/ngina-python-api:ABC123DEF...` (git SHA)

**On `develop/ngina-orchestrator` branch:**
- `docker.io/YOUR_USERNAME/ngina-python-api:develop`
- `docker.io/YOUR_USERNAME/ngina-node-publisher:develop`

**On Pull Requests:**
- Images are built but not pushed

## 📝 Test Structure

```
tests/
├── test_app.py                 # API endpoint tests
├── conftest.py                 # Pytest configuration
└── integration/
    └── test_mqtt_integration.py # MQTT integration tests

src/backend/
└── tests/
    └── mqtt-event-publisher.test.ts # Publisher tests
```

## 🐛 Troubleshooting

### "Docker Hub token invalid"
- Verify it's a **Personal Access Token**, not your password
- Ensure permissions include "Read, Write, Delete"
- Regenerate and update GitHub secrets

### "Tests fail locally but pass in CI"
- Check Python/Node.js versions match CI (Python 3.11, Node 20)
- Ensure environment variables are set (copy `.env.example` to `.env`)

### "Docker Compose won't start"
- Run `docker-compose config` to validate syntax
- Check port availability (5000 for Flask, 3000 for Node, 1883 for MQTT)

### "Linting errors block push"
- Auto-fix with `make format-fix`
- Or run `npm run lint:fix` in `src/backend/`

## 📚 Documentation

- **Full Setup Guide**: [.github/CI-CD-SETUP.md](.github/CI-CD-SETUP.md)
- **Workflow File**: [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)
- **Makefile**: [Makefile](Makefile) - All commands with help

## 🎓 Next Steps

1. ✅ Configure GitHub secrets (step above)
2. ✅ Run `make test` locally to verify everything works
3. ✅ Push your branch to trigger the pipeline
4. ✅ Check Actions tab for results
5. ✅ Fix any failures and push again

## 💡 Tips

- Use `make ci-check` to run lint + test locally before pushing
- Enable branch protection rules to require passing CI checks before merge
- Review Docker logs: `docker-compose logs -f`
- Use Docker Compose to test locally: `docker-compose up`

---

**Questions?** Check [.github/CI-CD-SETUP.md](.github/CI-CD-SETUP.md) for detailed documentation.
