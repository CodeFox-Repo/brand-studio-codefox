# Producer provenance

Bundled producers and where they came from. The vendored ones are imported
read-only for **internal use in this private repo**; the agent reads each
`SKILL.md` as procedure (they are not Skill-tool registered). Adaptation to the
brand-studio producer contract (added `capability` / `modality` / `lane`
frontmatter) is kept in a separate commit from the raw import.

| producer | source | commit | license |
| --- | --- | --- | --- |
| `logo` | github.com/op7418/logo-generator-skill | `bf4e9ac` | none declared (all rights reserved) — internal use only |
| `social` | github.com/itchernetski/threads-carousel-claude-skill | `cc775b6` | MIT (see `social/LICENSE`) |
| `video` | github.com/remotion-dev/remotion · `packages/skills/skills/remotion` | `80472b5` | Remotion License — the remotion runtime is installed in the **product repo** at render, never committed here |
| `banner` | authored in-repo (no suitable upstream found) | — | this repo |

Updating a vendored producer: re-fetch the upstream subtree, replace the files in
the raw-import commit, then re-apply the contract frontmatter. Keep the two
concerns in separate commits so the upstream delta stays auditable.
