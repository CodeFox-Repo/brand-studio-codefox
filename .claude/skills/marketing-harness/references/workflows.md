# Marketing Harness Workflows

Run commands from the repository root.

## Setup

```bash
uv sync
cp .env.example .env
```

Edit `.env` locally:

```env
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://api.openai.com/v1
HARNESS_REPO_PUBLISH_DIR=published
```

`.env` is ignored by git. Never paste key values into committed files.

## Validate Existing Campaign

```bash
uv run harness validate workspace/products/codefox/codefox/campaigns/example.campaign.yaml \
  --brand workspace/products/codefox/codefox/brand.lock.yaml
```

## Dry-Run Render

```bash
uv run harness render workspace/products/codefox/codefox/campaigns/example.campaign.yaml \
  --brand workspace/products/codefox/codefox/brand.lock.yaml \
  --dry-run
```

Expected output:

```text
outputs/feature-x-launch/
├── *.svg
├── manifest.json
└── run.lock.json
```

## Live Render With OpenAI

Confirm with the user before running because this calls OpenAI and can incur cost.

```bash
uv run harness render workspace/products/codefox/codefox/campaigns/example.campaign.yaml \
  --brand workspace/products/codefox/codefox/brand.lock.yaml
```

Expected output:

```text
outputs/feature-x-launch/
├── *.png
├── manifest.json
└── run.lock.json
```

This is only the local render buffer. For any output the user expects projects
to consume, immediately run the repo publish step below.

## Publish To Repo

Dry-run:

```bash
uv run harness publish feature-x-launch --channel repo
```

Write versioned artifacts:

```bash
uv run harness publish feature-x-launch --channel repo --publish
```

Expected output:

```text
published/portfolios/<portfolio-id>/<portfolio-version>/
├── portfolio.meta.yaml
├── elements.yaml
└── accepted.yaml

published/products/<portfolio-id>/<brand-id>/<brand-lock-version>/
├── portfolio/
├── metadata/
├── brand/brand.lock.yaml
├── campaigns/feature-x-launch.campaign.yaml
├── references/
└── artifacts/feature-x-launch/
    ├── *.png
    ├── manifest.json
    └── run.lock.json
```

## Produce Style Proposal

Use this when a design skill, Claude, or Codex is responsible for style production.

Design skill routing is intentionally fuzzy:

- If the user writes a hint after an explicit skill mention such as `$marketing-harness`, honor it first, for example "use local frontend-design" or "prefer claude-design".
- If the user does not name one, use an already-installed local design skill that fits brand/frontend/visual design.
- If none is available, stop. Do not install, clone, or download a fallback unless the user explicitly asks.
- The built-in local harness producer is only a deterministic scaffold; do not treat it as a replacement for creative style production from scratch unless the user explicitly accepts that tradeoff.

```bash
uv run harness style propose \
  --base workspace/products/codefox/codefox/brand.lock.yaml \
  --brief workspace/products/codefox/codefox/brief.md \
  --source workspace/products/codefox/codefox/references/ \
  --out workspace/products/codefox/codefox/proposals/<brand-name>.lock.yaml \
  --version <next-version>
```

Then validate:

```bash
uv run harness validate workspace/products/codefox/codefox/campaigns/example.campaign.yaml \
  --brand workspace/products/codefox/codefox/proposals/<brand-name>.lock.yaml
```

Run regression before promotion:

```bash
uv run harness regression \
  --brand workspace/products/codefox/codefox/proposals/<brand-name>.lock.yaml \
  --dry-run
```

Promote only after user review:

```bash
uv run harness style promote \
  workspace/products/codefox/codefox/proposals/<brand-name>.lock.yaml \
  --to workspace/products/codefox/<brand-name>/brand.lock.yaml
```

## External Design Producer

Use `--producer command` when an external design skill or script will generate the complete brand lock proposal:

```bash
uv run harness style propose \
  --producer command \
  --producer-command "./scripts/design-skill-producer" \
  --base workspace/products/codefox/codefox/brand.lock.yaml \
  --brief workspace/products/codefox/codefox/brief.md \
  --source workspace/products/codefox/codefox/references/ \
  --out workspace/products/codefox/codefox/proposals/<brand-name>.lock.yaml \
  --version <next-version>
```

The command contract is documented in `references/design-producer-protocol.md`.

## Regression Review

Regression does not auto-score image quality.

```bash
uv run harness regression --brand workspace/products/codefox/codefox/brand.lock.yaml
```

Fill in the generated `scores.csv` manually. If quality drops, do not promote or publish the style change.
