# Marketing Harness Workflows

Run commands from the product repository root. The product repo owns the
marketing paths declared in metadata; the installed skill owns workflow
instructions and the harness launcher. Do not assume a root-level `workspace/`,
`outputs/`, or `published/` tree.

Set the launcher and metadata paths once:

```bash
HARNESS_SCRIPT="$SKILL_ROOT/scripts/harness.py"
HARNESS_METADATA="packages/branding/marketing.harness.yaml"
```

The launcher runs the bundled scripts in this skill. It does not discover a
parent runtime checkout, call `uvx`, or pull a remote runtime.

## Setup

Consumer repo:

```bash
sh "$SKILL_ROOT/scripts/bootstrap_project.sh" --metadata "$HARNESS_METADATA" .
sh "$SKILL_ROOT/scripts/bootstrap_project.sh" --metadata "$HARNESS_METADATA" --write .
```

Harness development repo:

```bash
uv sync
```

Set image API credentials only if live rendering is approved and the chosen
image CLI needs them:

```env
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://api.openai.com/v1
```

Never paste key values into committed files. The marketing harness does not
read model catalogs; optional `provider.model` is passed through only when
present.

## Validate Existing Campaign

```bash
python3 "$HARNESS_SCRIPT" --metadata "$HARNESS_METADATA" validate
```

## Dry-Run Render

```bash
python3 "$HARNESS_SCRIPT" --metadata "$HARNESS_METADATA" render \
  --dry-run
```

Expected output:

```text
<metadata artifacts.scratch>/<campaign>/
├── *.svg
├── manifest.json
└── run.lock.json
```

## Live Render With Image Skill CLI

Confirm with the user before running because this calls the configured image API
through the local image skill/CLI and can incur cost. `brand.lock.yaml` should
set `provider.gateway` to `gpt-image-skill` or its alias `skill-cli`. If
`provider.model` is omitted, this skill does not pass `--model`; the underlying
image CLI chooses its default.

```bash
command -v gpt-image || true
test -f ~/.codex/skills/gpt-image/scripts/generate.py && echo "gpt-image skill installed"

python3 "$HARNESS_SCRIPT" --metadata "$HARNESS_METADATA" render
```

Expected output:

```text
<metadata artifacts.scratch>/<campaign>/
├── *.png
├── manifest.json
└── run.lock.json
```

This is only the local render buffer. Do not publish it yet unless the user
explicitly pre-approved auto-publish after render. Inspect the assets and ask
for human acceptance before any `--publish` command.

## Publish To Repo

Only enter this step after the user accepts the rendered assets, or when the
user explicitly asked to auto-publish after render. API-cost approval is not
asset approval.

Dry-run:

```bash
python3 "$HARNESS_SCRIPT" --metadata "$HARNESS_METADATA" publish
```

Write versioned artifacts:

```bash
python3 "$HARNESS_SCRIPT" --metadata "$HARNESS_METADATA" publish --publish
```

Expected output:

```text
<metadata artifacts.approved>/products/<portfolio-id>/<brand-id>/<brand-lock-version>/
└── artifacts/feature-x-launch/
    ├── *.png
    ├── manifest.json
    └── run.lock.json
```

The approved asset directory may be a public package directory, a separate
asset repository, or a git submodule inside the product repo. The harness does
not edit `.gitattributes`, run `git add`, commit, or push; commit the asset
repo/submodule after reviewing the snapshot.

## Produce Style Proposal

Use this when a design skill, Claude, or Codex is responsible for style production.

Design skill routing is intentionally fuzzy:

- If the user writes a hint after an explicit skill mention such as `$marketing-harness`, honor it first, for example "use local frontend-design" or "prefer claude-design".
- If the user does not name one, use an already-installed local design skill that fits brand/frontend/visual design.
- If none is available, stop. Do not install, clone, or download a fallback unless the user explicitly asks.
- Write the resulting proposal to `packages/branding/marketing/proposals/<brand-name>.lock.yaml` or the metadata-equivalent proposal path.

Then validate:

```bash
python3 "$HARNESS_SCRIPT" --metadata "$HARNESS_METADATA" validate \
  --brand packages/branding/marketing/proposals/<brand-name>.lock.yaml
```

Run a dry-run render before promotion:

```bash
python3 "$HARNESS_SCRIPT" render \
  --metadata "$HARNESS_METADATA" \
  --brand packages/branding/marketing/proposals/<brand-name>.lock.yaml \
  --dry-run
```

Promote only after user review by copying the accepted proposal to the official
metadata-declared `brand.lock.yaml` path.
