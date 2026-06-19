from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from harness_runtime.manifest import checksum_file, write_json

PublishChannel = Literal["repo"]


@dataclass(frozen=True)
class PublishResult:
    channel: PublishChannel
    dry_run: bool
    manifest_path: Path
    artifacts: list[dict[str, Any]]
    artifact_path: Path | None = None


def publish_campaign(
    campaign_name: str,
    channel: str = "repo",
    outputs_dir: Path = Path("outputs"),
    publish: bool = False,
    repo_dir: Path | None = None,
) -> PublishResult:
    if channel != "repo":
        raise ValueError("marketing-harness skill only supports --channel repo")

    output_dir = outputs_dir / campaign_name
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"{manifest_path} does not exist; render the campaign first")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return publish_repo(
        output_dir,
        manifest,
        publish=publish,
        repo_dir=repo_dir,
    )


def publish_repo(
    output_dir: Path,
    manifest: dict[str, Any],
    publish: bool,
    repo_dir: Path | None = None,
) -> PublishResult:
    campaign_name = str(manifest["campaign"])
    brand = repo_brand_info(manifest)
    portfolio = repo_portfolio_info(manifest, brand)
    artifact_root = repo_dir or Path("published")
    portfolio_snapshot_dir = artifact_root / "portfolios" / portfolio["id"] / portfolio["version"]
    snapshot_dir = artifact_root / "products" / portfolio["id"] / brand["id"] / brand["version"]
    artifact_dir = snapshot_dir / "artifacts" / campaign_name
    repo_manifest_path = artifact_dir / "manifest.json"

    published_manifest = json.loads(json.dumps(manifest))
    published_manifest["portfolio"] = portfolio
    published_manifest["brand"] = brand
    published_manifest["brand_lock_version"] = brand["version"]
    published_manifest["publish_channel"] = "repo"
    published_manifest["storage"] = {
        "channel": "repo",
        "root": artifact_root.as_posix(),
        "portfolio_snapshot_path": portfolio_snapshot_dir.as_posix(),
        "snapshot_path": snapshot_dir.as_posix(),
        "artifact_path": artifact_dir.as_posix(),
    }

    artifacts: list[dict[str, Any]] = []
    for asset in published_manifest["assets"]:
        asset_path = artifact_dir / asset["file"]
        asset_rel_path = Path("artifacts") / campaign_name / asset["file"]
        url = f"repo://{asset_path.as_posix()}"
        artifacts.append(
            {
                "id": asset["id"],
                "file": asset["file"],
                "path": asset_path.as_posix(),
                "url": url,
            }
        )
        asset["path"] = asset_rel_path.as_posix()
        asset["url"] = url
        asset["checksum_sha256"] = checksum_file(output_dir / asset["file"])

    artifacts.append(
        {
            "id": "manifest",
            "file": "manifest.json",
            "path": repo_manifest_path.as_posix(),
            "url": f"repo://{repo_manifest_path.as_posix()}",
        }
    )

    if publish:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        published_manifest["published_at"] = datetime.now(timezone.utc).isoformat()
        for asset in published_manifest["assets"]:
            shutil.copy2(output_dir / asset["file"], artifact_dir / asset["file"])
        write_json(repo_manifest_path, published_manifest)

        run_lock_path = output_dir / "run.lock.json"
        if run_lock_path.exists():
            shutil.copy2(run_lock_path, artifact_dir / "run.lock.json")

    return PublishResult(
        channel="repo",
        dry_run=not publish,
        manifest_path=repo_manifest_path,
        artifacts=artifacts,
        artifact_path=snapshot_dir,
    )


def repo_brand_info(manifest: dict[str, Any]) -> dict[str, str]:
    brand = manifest.get("brand")
    if isinstance(brand, dict):
        brand_id = str(brand.get("id") or "unknown-brand")
        brand_name = str(brand.get("name") or brand_id)
        brand_version = str(brand.get("version") or manifest.get("brand_lock_version") or "0.0.0")
    else:
        brand_id = "unknown-brand"
        brand_name = "Unknown Brand"
        brand_version = str(manifest.get("brand_lock_version") or "0.0.0")

    return {
        "id": safe_path_segment(brand_id, "brand id"),
        "name": brand_name,
        "version": safe_version_segment(brand_version),
    }


def repo_portfolio_info(manifest: dict[str, Any], brand: dict[str, str]) -> dict[str, str]:
    portfolio = manifest.get("portfolio")
    if isinstance(portfolio, dict):
        portfolio_id = str(portfolio.get("id") or brand["id"])
        portfolio_name = str(portfolio.get("name") or portfolio_id)
        portfolio_version = str(portfolio.get("version") or brand["version"])
    else:
        portfolio_id = brand["id"]
        portfolio_name = brand["name"]
        portfolio_version = brand["version"]

    return {
        "id": safe_path_segment(portfolio_id, "portfolio id"),
        "name": portfolio_name,
        "version": safe_version_segment(portfolio_version),
    }


def safe_path_segment(value: str, label: str) -> str:
    if not value or "/" in value or value in {".", ".."}:
        raise ValueError(f"{label} is not safe for repo publishing: {value}")
    return value


def safe_version_segment(value: str) -> str:
    if "/" in value or value in {"", ".", ".."}:
        raise ValueError(f"brand version is not safe for repo publishing: {value}")
    return value
