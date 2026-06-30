---
name: banner
capability: banner
modality: image
lane: generator
description: >
  Compose brand banners — GitHub repo/README headers, social headers (X, LinkedIn,
  YouTube channel art), and OG / link-preview images. Takes the structured brand
  weight (palette, typography, references, avoid list, accepted samples) plus the
  deliverable size and produces prompt-craft for the text-to-image backend, or a
  precise SVG/HTML lockup when exact wordmark/headline text must render crisply.
---

# Banner

A read-only, instruction-grade producer. The agent reads this as procedure; the
configured `text-to-image` backend (or inline SVG/HTML) renders the pixels.

## Inputs

- Structured brand weight: palette, typography direction, references, avoid list,
  and the domain's accepted samples.
- Deliverable spec: id + size. Common banner sizes (align to multiples of 16 for
  gpt-image): GitHub social preview 1280×640, X header 1500×500, LinkedIn cover
  1584×396, YouTube channel art safe area ~1546×423, OG image 1200×630.

## Output

- **Generator path**: produce one tight prompt that places the wordmark/headline
  in a safe area (never cropped), keeps the brand palette/typography, respects
  the avoid list, and frames the product as the subject — then hand it to the
  `text-to-image` backend.
- **Exact-text path**: when the banner is mostly a wordmark + tagline on a brand
  field, prefer a deterministic SVG/HTML lockup so text is pixel-crisp, using the
  brand palette and type direction directly.

## Conventions, not technique

Borrow layout/hierarchy/spacing conventions from referenced design skills; do not
copy any specific skill's implementation unless the user asks. Keep headlines off
the frame edge, maintain generous safe margins, and never invent sponsor/brand
marks not in the brand.
