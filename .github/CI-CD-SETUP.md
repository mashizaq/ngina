# CI/CD Pipeline Setup Guide

This document describes the GitHub Actions CI/CD pipeline for the ngina project.

## Overview

The CI/CD pipeline automates:
- **Code Quality**: Linting and formatting checks for Python and TypeScript
- **Testing**: Unit and integration tests for both services
- **Docker Builds**: Building and pushing Docker images to Docker Hub
- **Validation**: Docker Compose configuration validation

## Pipeline Structure

### Triggers

The pipeline runs on:
- **Push events** to `main` and `develop/ngina-orchestrator` branches
- **Pull requests** targeting `main` and `develop/ngina-orchestrator` branches

### Jobs

#### 1. Python Lint & Format (`python-lint`)
- Runs on Ubuntu latest
- Checks code formatting with `black`
- Validates import ordering with `isort`
- Runs linting with `flake8`
- **Continue on error**: Warnings don't block pipeline

#### 2. Python Tests (`python-test`)
- Executes pytest test suite
- Generates coverage reports
- Uploads coverage to Codecov
- **Requirements**: Tests should be in `tests/` directory

#### 3. TypeScript Lint (`node-lint`)
- Checks code quality with ESLint
- Validates TypeScript compilation
- Located in `src/backend/`

#### 4. Node.js Tests (`node-test`)
- Runs Jest test suite
- Located in `src/backend/`

#### 5. Docker Build & Push (`docker-build`)
- Builds two images:
  - `ngina-python-api` from root `Dockerfile`
  - `ngina-node-publisher` from `src/backend/Dockerfile`
- Tags:
  - `main` branch → `latest` + git SHA
  - `develop/ngina-orchestrator` → `develop` + git SHA
  - PRs → `pr-{PR_number}` (build only, no push)
- Only pushes on push events, not on PRs
- Requires Docker Hub credentials

#### 6. Docker Compose Validation (`docker-compose-validate`)
- Validates `docker-compose.yml` syntax
- Runs on every push and PR

#### 7. Integration Tests (`integration-test`)
- Runs only on push events
- Starts Mosquitto MQTT broker service
- Tests API and MQTT connectivity
- Tests in `tests/integration/` directory

#### 8. CI Success Check (`ci-success`)
- Summarizes all job results
- Fails if any critical job fails

## GitHub Secrets Setup

To use this pipeline, configure these secrets in your GitHub repository:

### Settings → Secrets and variables → Actions

1. **`DOCKER_HUB_USERNAME`** (Required for Docker push)
   - Your Docker Hub username
   - Example: `your-docker-username`

2. **`DOCKER_HUB_TOKEN`** (Required for Docker push)
   - Docker Hub Personal Access Token
   - **Create at**: https://hub.docker.com/settings/security
   - Do NOT use your Docker Hub password
   - Give it "Read, Write, Delete" permissions

### How to Create Docker Hub Token:

1. Go to https://hub.docker.com/settings/security
2. Click "New Access Token"
3. Name: `github-actions` (or similar)
4. Set permissions to "Read, Write, Delete"
5. Copy the token
6. Add to GitHub repo secrets as `DOCKER_HUB_TOKEN`

### How to Add Secrets to GitHub:

1. Go to repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add `DOCKER_HUB_USERNAME` and `DOCKER_HUB_TOKEN`
4. Click **Add secret**

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

### Install Dependencies

**Python:**
```bash
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 isort pylint
```

**Node.js:**
```bash
npm install
cd src/backend
npm install
```

### Running Tests Locally

**Python tests:**
```bash
pytest tests/ -v --cov=app
```

**Node.js tests:**
```bash
cd src/backend
npm test
```

**Linting:**
```bash
# Python
black app.py
flake8 app.py
isort app.py

# TypeScript
cd src/backend
npm run lint
npm run lint:fix
```

### Building Docker Images Locally

```bash
# Python API
docker build -t ngina-python-api:local .

# Node.js Publisher
docker build -t ngina-node-publisher:local src/backend/

# Compose all services
docker-compose up
```

## Workflow Files

- **CI/CD Pipeline**: [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)
- **Linting Config**: [.eslintrc.json](src/backend/.eslintrc.json), [pytest.ini](pytest.ini)
- **Test Config**: [jest.config.js](src/backend/jest.config.js)

## Troubleshooting

### Docker Push Fails

**Error**: `denied: requested access to the resource is denied`

**Solution**:
1. Verify `DOCKER_HUB_TOKEN` is a Personal Access Token (not your password)
2. Verify `DOCKER_HUB_USERNAME` matches your Docker Hub username
3. Regenerate token with "Read, Write, Delete" permissions
4. Update GitHub secrets

### Tests Don't Run

**Error**: `pytest: command not found`

**Solution**: Add `pytest` to `requirements.txt`:
```
pytest>=7.0.0
pytest-cov>=4.0.0
```

### TypeScript Compilation Fails

**Error**: `Cannot find module...`

**Solution**:
```bash
cd src/backend
npm install
npm run build
```

## Customization

### Changing Test Coverage Threshold

Edit `src/backend/jest.config.js`:
```javascript
coverageThreshold: {
  global: {
    statements: 70,  // Change these values
    branches: 60,
    functions: 70,
    lines: 70
  }
}
```

### Adding More Images to Docker Build

Edit `.github/workflows/ci-cd.yml` in the `docker-build` job matrix:
```yaml
strategy:
  matrix:
    include:
      - dockerfile: Dockerfile
        image-name: my-image
        context: .
```

### Deploying to Additional Registries

Add additional `Build and push` steps or use `docker/build-push-action@v4` with different registry credentials.

## Monitoring Pipeline

Visit your GitHub repository → **Actions** tab to:
- View live workflow runs
- Check job logs
- See artifact results
- Monitor Docker image builds

## Performance Tips

1. **Cache dependencies** (already enabled for pip/npm)
2. **Use matrix strategy** for parallel jobs
3. **Skip integration tests** on PRs to speed up feedback
4. **Set reasonable coverage thresholds** to avoid excessive test requirements

## Next Steps

1. Configure GitHub secrets (see above)
2. Ensure all tests pass locally
3. Push to a branch to trigger the pipeline
4. Monitor Actions tab for results
5. Fix any failures before merging PRs

---

For more information, see:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
