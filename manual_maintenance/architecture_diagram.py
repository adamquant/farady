#!/usr/bin/env python3
"""Generate architecture diagram for farady-py.

This script creates a Mermaid.js flowchart diagram showing:
- All data entry points (Tally forms, CLI, Tests)
- Lambda wrappers for SA services
- Convergence on core algorithm
- Internal calculation flow
- Output processing matched to inputs

Usage:
    python manual_maintenance/architecture_diagram.py

Outputs:
    - docs/architecture.md (Mermaid diagram in markdown)
    - docs/architecture.png (rendered image, requires mmdc/mermaid-cli)

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
    subgraph EXTERNAL["EXTERNAL INPUTS"]
        direction LR
        TALLY_FE["Tally Form<br/>(Free Estimate)"]
        TALLY_OW["Tally Form<br/>(OneWasiya)"]
        CLI_USER["CLI User"]
        TEST_SUITE["Test Suite"]
    end

    subgraph LAMBDA["AWS LAMBDA LAYER (Wrappers)"]
        direction TB
        subgraph LAMBDA_FE_GRP["sa_free_report Lambda"]
            LAMBDA_FE_HANDLER["lambda_handler()"]
            LAMBDA_FE_EXTRACT["extract_response()"]
            LAMBDA_FE_WRAPPER["farady_wrapper.calculate()"]
        end
        subgraph LAMBDA_OW_GRP["one-wasiya Lambda"]
            LAMBDA_OW_HANDLER["lambda_handler()"]
            LAMBDA_OW_EXTRACT["extract_response()"]
            LAMBDA_OW_GETFAM["get_family_members_for_farady()"]
            LAMBDA_OW_WRAPPER["farady_wrapper.calculate_inheritance_for_will()"]
        end
    end

    subgraph CONVERGE["CONVERGENCE POINT (farady-py)"]
        direction TB
        CALC_DICT["calculate_from_dict()"]
        CALC_KWARGS["calculate_inheritance()"]
        CASE_FROM_DICT["InheritanceCase.from_dict()"]
        CSV_LOADER["load_csv_cases()"]
    end

    subgraph CORE["CORE CALCULATION ENGINE"]
        direction TB
        CALCULATOR["InheritanceCalculator.calculate()"]
        
        subgraph STEPS["Distribution Steps"]
            direction LR
            ZAWJAYN["_zawjayn()<br/>Spouse shares"]
            USOOL["_usool()<br/>Parents/Grandparents"]
            FUROO["_furoo()<br/>Descendants"]
            HAWASHI["_hawashi()<br/>Siblings/Nephews/Uncles"]
            KALALA["_kalala()<br/>Special cases"]
        end
        
        subgraph ADJUST["Adjustment Methods"]
            direction LR
            AWL["_awl()<br/>Over-subscription"]
            TASEEB["_taseeb()<br/>Residual distribution"]
            RADD["_radd()<br/>Under-subscription"]
        end
        
        RESULT["InheritanceResult"]
    end

    subgraph OUTPUT_SOCK["OUTPUT SOCKETS"]
        RESULT_DICT["distribution: Dict[str, float]"]
        RESULT_ENDING["ending: str"]
        RESULT_ASIB["asib: str"]
        RESULT_TOTAL["total: float"]
        RESULT_STATUS["status: str"]
        RESULT_DENOM["denominator: int"]
        RESULT_NUMERS["numerators: Dict[str, int]"]
    end

    subgraph OUT_PROC["OUTPUT PROCESSING"]
        direction TB
        subgraph CLI_OUT_GRP["CLI Output"]
            CLI_FORMAT["format_result()"]
            CLI_PRINT["print() to console"]
        end
        subgraph FE_OUT_GRP["Free Estimate Output"]
            PRETTY_FE["prettify_names()"]
            CREATE_PDF["create_pdf()"]
            SEND_EMAIL["send_email()"]
            EMAIL_OUT["Email with PDF Report"]
        end
        subgraph OW_OUT_GRP["OneWasiya Output"]
            FORMAT_DOC["format_distribution_for_document()"]
            GEN_WILL["generate_will_document()"]
            SAVE_DOC["save_document()"]
            S3_LOCAL["S3 or local file"]
        end
    end

    %% External to Lambda flows
    TALLY_FE --> LAMBDA_FE_HANDLER
    TALLY_OW --> LAMBDA_OW_HANDLER

    %% Lambda internal flows
    LAMBDA_FE_HANDLER --> LAMBDA_FE_EXTRACT --> LAMBDA_FE_WRAPPER
    LAMBDA_OW_HANDLER --> LAMBDA_OW_EXTRACT --> LAMBDA_OW_GETFAM --> LAMBDA_OW_WRAPPER

    %% Convergence flows
    LAMBDA_FE_WRAPPER --> CALC_DICT
    LAMBDA_OW_WRAPPER --> CALC_DICT
    CLI_USER --> CALC_DICT
    CLI_USER --> CALC_KWARGS
    TEST_SUITE --> CALC_DICT

    CSV_LOADER --> CASE_FROM_DICT
    CALC_DICT --> CASE_FROM_DICT
    CALC_KWARGS --> CALCULATOR

    CASE_FROM_DICT --> CALCULATOR

    %% Core algorithm flow
    CALCULATOR --> ZAWJAYN & USOOL & FUROO & HAWASHI & KALALA
    ZAWJAYN & USOOL & FUROO & HAWASHI & KALALA --> AWL & TASEEB & RADD
    AWL & TASEEB & RADD --> RESULT

    %% Result to output sockets
    RESULT --> RESULT_DICT & RESULT_ENDING & RESULT_ASIB & RESULT_TOTAL & RESULT_STATUS & RESULT_DENOM & RESULT_NUMERS

    %% Output processing flows (matched to inputs)
    CLI_USER -.->|CLI uses| CLI_FORMAT --> CLI_PRINT
    RESULT_DICT --> CLI_FORMAT

    LAMBDA_FE_HANDLER -.->|Free Estimate uses| PRETTY_FE --> CREATE_PDF --> SEND_EMAIL --> EMAIL_OUT
    RESULT_DICT --> PRETTY_FE

    LAMBDA_OW_HANDLER -.->|OneWasiya uses| FORMAT_DOC --> GEN_WILL --> SAVE_DOC --> S3_LOCAL
    RESULT_DICT & RESULT_DENOM --> FORMAT_DOC

    %% Styling
    classDef external fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef lambda fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef converge fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef core fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef output fill:#fce4ec,stroke:#880e4f,stroke-width:2px

    class TALLY_FE,TALLY_OW,CLI_USER,TEST_SUITE external
    class LAMBDA_FE_HANDLER,LAMBDA_FE_EXTRACT,LAMBDA_FE_WRAPPER,LAMBDA_OW_HANDLER,LAMBDA_OW_EXTRACT,LAMBDA_OW_GETFAM,LAMBDA_OW_WRAPPER lambda
    class CALC_DICT,CALC_KWARGS,CASE_FROM_DICT,CSV_LOADER converge
    class CALCULATOR,ZAWJAYN,USOOL,FUROO,HAWASHI,KALALA,AWL,TASEEB,RADD,RESULT core
    class RESULT_DICT,RESULT_ENDING,RESULT_ASIB,RESULT_TOTAL,RESULT_STATUS,RESULT_DENOM,RESULT_NUMERS,CLI_FORMAT,CLI_PRINT,PRETTY_FE,CREATE_PDF,SEND_EMAIL,EMAIL_OUT,FORMAT_DOC,GEN_WILL,SAVE_DOC,S3_LOCAL output
```
"""

MARKDOWN_TEMPLATE = """# Farady-py Architecture Diagram

> Generated: {timestamp}

## Overview

This diagram shows the complete data flow through the farady-py library, from external inputs through the core calculation engine to output processing.

## Architecture Diagram

{diagram}

## Component Descriptions

### External Inputs

| Component | Description |
|-----------|-------------|
| Tally Form (Free Estimate) | Webhook from Tally form for free inheritance estimates |
| Tally Form (OneWasiya) | Webhook from Tally form for will generation service |
| CLI User | Command-line user running `farady --ibn 2 --bint 1 --zawja` |
| Test Suite | Pytest tests calling the library directly |

### Lambda Layer (Wrappers)

| Component | Description |
|-----------|-------------|
| sa_free_report Lambda | AWS Lambda for free estimate service |
| one-wasiya Lambda | AWS Lambda for will generation service |
| extract_response() | Parses Tally webhook JSON into family data dict |
| farady_wrapper.calculate() | Wraps farady for Free Estimate service |
| farady_wrapper.calculate_inheritance_for_will() | Wraps farady for OneWasiya service |

### Convergence Point

| Function | Description |
|----------|-------------|
| `calculate_from_dict()` | Main entry point for dict input |
| `calculate_inheritance()` | Entry point for kwargs input |
| `InheritanceCase.from_dict()` | Converts dict to InheritanceCase |
| `load_csv_cases()` | Loads cases from CSV file |

### Core Calculation Engine

| Component | Description |
|-----------|-------------|
| `InheritanceCalculator.calculate()` | Main calculation orchestrator |
| `_zawjayn()` | Calculates spouse shares |
| `_usool()` | Calculates parents/grandparents shares |
| `_furoo()` | Calculates descendants shares |
| `_hawashi()` | Calculates siblings/nephews/uncles shares |
| `_kalala()` | Handles special kalala cases |
| `_awl()` | Handles over-subscription (awl) |
| `_taseeb()` | Handles residual distribution |
| `_radd()` | Handles under-subscription (radd) |

### Output Sockets

| Field | Type | Description |
|-------|------|-------------|
| `distribution` | `Dict[str, float]` | Heir name → share (decimal) |
| `ending` | `str` | How distribution ended (awl/radd/taseeb/etc.) |
| `asib` | `str` | The residual heir if present |
| `total` | `float` | Total shares accounted for (should be 1.0) |
| `status` | `str` | Complete/Failed/Unknown |
| `denominator` | `int` | Total number of shares (raas) |
| `numerators` | `Dict[str, int]` | Heir name → share count (numerator) |

### Output Processing

| Service | Processing Flow |
|---------|-----------------|
| CLI | `format_result()` → `print()` to console |
| Free Estimate | `prettify_names()` → `create_pdf()` → `send_email()` |
| OneWasiya | `format_distribution_for_document()` → `generate_will_document()` → `save_document()` |

## Key Insights

1. **Single Convergence Point**: All inputs eventually call `InheritanceCalculator.calculate()` through `calculate_from_dict()` or `calculate_inheritance()`

2. **Lambda Independence**: Lambda functions are pure wrappers - they don't interact with CLI at all

3. **Output Socket Matching**: Each input source has corresponding output processing:
   - CLI → console print
   - Free Estimate → PDF + email
   - OneWasiya → will document + S3/local storage

4. **No Public API Yet**: The library is consumed internally by SA services, not exposed as a public API
"""


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def generate_markdown(output_path: Path) -> None:
    """Generate the markdown file with embedded Mermaid diagram."""
    content = MARKDOWN_TEMPLATE.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        diagram=MERMAID_DIAGRAM,
    )
    output_path.write_text(content)
    print(f"Generated: {output_path}")


def render_png(md_path: Path, png_path: Path) -> bool:
    """Render Mermaid diagram to PNG using mermaid-cli (mmdc).

    Tries in order:
    1. mmdc (global install)
    2. npx @mermaid-js/mermaid-cli (no install needed)
    """
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
    """Generate architecture diagram files."""
    project_root = get_project_root()
    docs_dir = project_root / "docs"
    docs_dir.mkdir(exist_ok=True)

    md_path = docs_dir / "architecture.md"
    png_path = docs_dir / "architecture.png"

    generate_markdown(md_path)

    if render_png(md_path, png_path):
        print("\nSuccessfully generated both markdown and PNG diagrams.")
    else:
        print("\nGenerated markdown only. Install mermaid-cli for PNG generation.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
