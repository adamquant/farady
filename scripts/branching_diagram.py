#!/usr/bin/env python3
"""Generate branching strategy diagram for farady-dev.

This script creates a Mermaid.js flowchart diagram showing:
- The hybrid branching model (TBD + Gitflow)
- Branch relationships and roles
- Release workflow to SunnaAssets

Usage:
    poetry run python scripts/branching_diagram.py

Outputs:
    - docs/branching.md (Mermaid diagram in markdown)
    - docs/branching.png (rendered image, requires mmdc/mermaid-cli)

Requirements for PNG rendering:
    npm install -g @mermaid-js/mermaid-cli
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

MERMAID_DIAGRAM = """```mermaid
flowchart TB
    subgraph FARADY_DEV["FARADY-DEV (adamquant)"]
        direction TB
        
        MAIN["main<br/>(Development Trunk)"]
        RELEASE_SA["release-sa<br/>(Pre-release Staging)"]
        PROD_SA["prod-sa<br/>(Production Trigger)"]
        
        subgraph FEATURES["Feature Branches (TBD)"]
            FB1["feat/feature-name"]
            FB2["fix/bug-fix"]
            FB3["docs/documentation"]
        end
        
        MAIN --force push--> RELEASE_SA
        RELEASE_SA --PR only--> PROD_SA
        
        FEATURES --PR merge--> MAIN
        
        subgraph TESTS_MAIN["Tests on main"]
            UT1["Unit Tests"]
        end
        
        subgraph TESTS_RELEASE["Tests on release-sa"]
            UT2["Unit Tests"]
            CT["Contract Tests"]
            E2E["E2E Tests"]
        end
        
        subgraph PROD_ACTIONS["On merge to prod-sa"]
            TAG["Create Tag<br/>vX.Y.Z-sa.N"]
            DISPATCH["repository_dispatch<br/>to sunnaassets"]
        end
    end
    
    MAIN --> TESTS_MAIN
    RELEASE_SA --> TESTS_RELEASE
    PROD_SA --> PROD_ACTIONS
    
    subgraph SUNNAASSETS["SUNNAASSETS REPOS"]
        direction TB
        
        subgraph FREE_EST["sunnaassets/free-estimate"]
            FE_MAIN["main"]
            FE_RELEASE["release/{version}"]
            FE_LAMBDA["Lambda: sa_free_report"]
            
            FE_RELEASE --smoke tests--> FE_LAMBDA
            FE_RELEASE --PR if pass--> FE_MAIN
            FE_MAIN --deploy--> FE_LAMBDA
        end
        
        subgraph ONEWASIYA["sunnaassets/onewasiya"]
            OW_MAIN["main"]
            OW_RELEASE["release/{version}"]
            OW_LAMBDA["Lambda: one-wasiya"]
            
            OW_RELEASE --smoke tests--> OW_LAMBDA
            OW_RELEASE --PR if pass--> OW_MAIN
            OW_MAIN --deploy--> OW_LAMBDA
        end
    end
    
    DISPATCH --> FREE_EST & ONEWASIYA
    
    DISPATCH -.->|"1. Create release/{ver}"| FE_RELEASE
    DISPATCH -.->|"2. Bump farady version"| FE_RELEASE
    DISPATCH -.->|"3. Run smoke tests"| FE_RELEASE
    
    DISPATCH -.->|"1. Create release/{ver}"| OW_RELEASE
    DISPATCH -.->|"2. Bump farady version"| OW_RELEASE
    DISPATCH -.->|"3. Run smoke tests"| OW_RELEASE

    %% Styling
    classDef primary fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px
    classDef staging fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef production fill:#fce4ec,stroke:#880e4f,stroke-width:3px
    classDef feature fill:#e3f2fd,stroke:#1565c0,stroke-width:1px
    classDef test fill:#f3e5f5,stroke:#4a148c,stroke-width:1px
    classDef action fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    classDef external fill:#eceff1,stroke:#455a64,stroke-width:2px
    
    class MAIN primary
    class RELEASE_SA staging
    class PROD_SA production
    class FB1,FB2,FB3 feature
    class TESTS_MAIN,TESTS_RELEASE,UT1,UT2,CT,E2E test
    class TAG,DISPATCH action
    class FREE_EST,ONEWASIYA,FE_MAIN,OW_MAIN,FE_RELEASE,OW_RELEASE,FE_LAMBDA,OW_LAMBDA external
```
"""

MARKDOWN_TEMPLATE = """# Farady-dev Branching Strategy

> Generated: {timestamp}

## Overview

This project uses a **hybrid branching model** combining:

1. **Trunk-Based Development (TBD)** for core module development
2. **Gitflow** for production releases to SunnaAssets

## Branch Architecture Diagram

{diagram}

## Branch Roles

| Repo | Branch | Role |
|------|--------|------|
| farady-dev | `main` | Development trunk (TBD) |
| farady-dev | `release-sa` | Pre-release staging (no infra tests) |
| farady-dev | `prod-sa` | Production trigger, dispatches to SA |
| sunnaassets/* | `main` | Production, deploys Lambda |
| sunnaassets/* | `release/{{version}}` | Auto-created per release, smoke tests run here |

## Workflow

### Feature Development (TBD on `main`)

1. **Create Issue** - Use gh cli
2. **Create Branch** - From `main`, naming: `feat/`, `fix/`, `docs/`
3. **Do Work** - Implement the feature/fix
4. **Commit & Push** - Commit changes and push to remote
5. **Create PR** - Raise pull request to `main`
6. **Merge** - After review, merge to `main`

### SunnaAssets Release (Gitflow)

1. **Stage Release** - Force push `main` to `release-sa`:
   ```bash
   git push origin main:release-sa --force
   ```

2. **Tests Run on farady-dev** - Unit, contract, and E2E tests (no AWS access needed)

3. **Create PR** - From `release-sa` to `prod-sa`

4. **Merge Triggers**:
   - Version tag created automatically in farady-dev
   - `repository_dispatch` sent to sunnaassets repos
   - Each sunnaassets repo:
     - Creates `release/{{version}}` branch
     - Updates requirements.txt with new farady version
     - Runs smoke tests against deployed Lambda
     - If pass: creates PR to main (manual merge required)
     - If fail: creates issue with `release-failed` label

## Version Format

```
vX.Y.Z-sa.N

X.Y.Z = Semantic version (major.minor.patch)
sa     = SunnaAssets release identifier
N      = Release number for that version

Examples:
  v0.1.0-sa.1  (first SA release)
  v0.1.0-sa.2  (second release, same version)
  v0.2.0-sa.1  (new minor version)
```

## Key Rules

### For Feature Development
- **NEVER** work directly on `main` branch
- **ALWAYS** use a feature branch for ANY change
- **ALWAYS** follow: issue → branch → work → commit → PR → merge

### For Releases
- **NEVER** push directly to `prod-sa`
- **ALWAYS** go through: main → release-sa → PR → prod-sa
- **ONLY** PRs from `release-sa` are valid for `prod-sa`

## Test Isolation

### farady-dev
- **Unit tests** (`tests/`) - Run on `main` branch via CI
- **Contract tests** (`tests/integration/test_api_contract.py`) - Schema validation
- **E2E tests** (`tests/integration/test_e2e.py`) - Calculation logic

All tests in farady-dev run **without AWS access**.

### sunnaassets repos
- **Smoke tests** (`tests/smoke/test_lambda_smoke.py`) - Invoke actual Lambda functions
- Run on `release/{{version}}` branch before PR to main
- Use sunnaassets' own AWS credentials
"""


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def generate_markdown(output_path: Path) -> None:
    content = MARKDOWN_TEMPLATE.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        diagram=MERMAID_DIAGRAM,
    )
    output_path.write_text(content)
    print(f"Generated: {output_path}")


def render_png(md_path: Path, png_path: Path) -> bool:
    import tempfile

    mmdc_cmd = None

    try:
        result = subprocess.run(
            ["mmdc", "--version"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            mmdc_cmd = ["mmdc"]
    except FileNotFoundError:
        pass

    if not mmdc_cmd:
        print("mmdc not found globally, trying npx...")
        try:
            result = subprocess.run(
                ["npx", "--yes", "@mermaid-js/mermaid-cli", "--version"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                mmdc_cmd = ["npx", "--yes", "@mermaid-js/mermaid-cli"]
        except FileNotFoundError:
            pass

    if not mmdc_cmd:
        print("mermaid-cli not available.")
        print("Install with: npm install -g @mermaid-js/mermaid-cli")
        print("Or use npx (requires Node.js): npx @mermaid-js/mermaid-cli")
        return False

    mermaid_content = MERMAID_DIAGRAM.strip()
    if mermaid_content.startswith("```mermaid"):
        mermaid_content = mermaid_content[len("```mermaid") :]
    if mermaid_content.endswith("```"):
        mermaid_content = mermaid_content[: -len("```")]
    mermaid_content = mermaid_content.strip()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as tmp_file:
        tmp_file.write(mermaid_content)
        tmp_mmd_path = Path(tmp_file.name)

    try:
        result = subprocess.run(
            mmdc_cmd
            + [
                "-i",
                str(tmp_mmd_path),
                "-o",
                str(png_path),
                "-b",
                "white",
                "-t",
                "default",
                "--scale",
                "4",
            ],
            capture_output=True,
            text=True,
        )
    finally:
        tmp_mmd_path.unlink(missing_ok=True)

    if result.returncode == 0:
        print(f"Generated: {png_path}")
        return True
    else:
        print(f"Error rendering PNG: {result.stderr}")
        return False


def main() -> int:
    project_root = get_project_root()
    docs_dir = project_root / "docs"
    docs_dir.mkdir(exist_ok=True)

    md_path = docs_dir / "branching.md"
    png_path = docs_dir / "branching.png"

    generate_markdown(md_path)

    if render_png(md_path, png_path):
        print("\nSuccessfully generated both markdown and PNG diagrams.")
    else:
        print("\nGenerated markdown only. Install mermaid-cli for PNG generation.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
