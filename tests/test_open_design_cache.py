import importlib.util
import gc
import json
import subprocess
import sys
import tempfile
import unittest
import warnings
from pathlib import Path

from tests.frontend_design_test_support import (
    commit_all,
    init_git_repo,
    run_git,
    sha256_bytes,
    snapshot_tree,
    write_files,
    write_json,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "design-stack/router/scripts/open_design_cache.py"
LICENSE = b"fixture provider license\n"


def load_open_design_module():
    spec = importlib.util.spec_from_file_location("open_design_cache", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manifest(slug: str, *, schema: str = "od-design-system-project/v1") -> dict:
    return {
        "schemaVersion": schema,
        "id": slug,
        "name": slug.title(),
        "category": "Fixture",
        "source": {"type": "bundled", "origin": "test fixture"},
        "files": {"design": "DESIGN.md", "tokens": "tokens.css"},
        "usage": "USAGE.md",
    }


def create_provider_repo(
    root: Path,
    *,
    invalid_manifest: bool = False,
    executable: bool = False,
    symlink: bool = False,
) -> tuple[Path, dict]:
    repo = root / "provider"
    init_git_repo(repo)
    write_files(
        repo,
        {
            "LICENSE": LICENSE,
            "design-systems/README.md": b"# Fixture package index\n",
            "design-systems/_schema/README.md": b"schema metadata\n",
            "design-systems/alpha/DESIGN.md": b"# Alpha\n",
            "design-systems/alpha/tokens.css": b":root { --accent: blue; }\n",
            "design-systems/alpha/USAGE.md": b"Read DESIGN.md first.\n",
            "design-systems/alpha/preview/inert.sh": b"#!/bin/sh\ntouch never-ran\n",
            "design-systems/beta/DESIGN.md": b"# Beta\n",
            "design-systems/beta/tokens.css": b":root { --accent: red; }\n",
            "design-systems/beta/USAGE.md": b"Read DESIGN.md first.\n",
        },
    )
    write_json(
        repo / "design-systems/alpha/manifest.json",
        manifest(
            "alpha",
            schema=("invalid/v1" if invalid_manifest else "od-design-system-project/v1"),
        ),
    )
    write_json(repo / "design-systems/beta/manifest.json", manifest("beta"))
    if executable:
        (repo / "design-systems/alpha/preview/inert.sh").chmod(0o755)
    if symlink:
        (repo / "design-systems/alpha/unsafe-link").symlink_to("DESIGN.md")
    revision = commit_all(repo)
    root_tree = run_git(repo, "rev-parse", "HEAD^{tree}")
    provider = {
        "schema_version": 1,
        "provider_id": "open-design",
        "repository": str(repo),
        "revision": revision,
        "root_tree": root_tree,
        "package_root": "design-systems",
        "package_index_path": "design-systems/README.md",
        "scope": "design-systems/<explicit-selection>/**",
        "authority": "optional-provider",
        "distribution": "on-demand",
        "license": {
            "spdx": "Apache-2.0",
            "status": "verified",
            "path": "LICENSE",
            "sha256": sha256_bytes(LICENSE),
            "size": len(LICENSE),
        },
        "slug_pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$",
        "required_files": ["manifest.json", "DESIGN.md", "tokens.css"],
        "manifest_contract": {
            "schema_version": "od-design-system-project/v1",
            "design": "DESIGN.md",
            "tokens": "tokens.css",
        },
        "network_policy": "explicit-demand-only",
        "cache_write_policy": "selected-package-only",
        "corrupt_cache_policy": "fail-without-mutation",
        "cache_namespace": "open-design",
        "limits": {
            "max_files": 1000,
            "max_file_bytes": 8388608,
            "max_total_bytes": 67108864,
        },
    }
    return repo, provider


class OpenDesignCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.open_design = load_open_design_module()

    def test_lists_and_fetches_only_the_selected_package_from_real_git(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _, provider = create_provider_repo(root)
            cache_root = root / "cache"
            sentinel = root / "never-ran"

            listing = self.open_design.list_packages(provider)
            self.assertEqual(listing["packages"], ["alpha", "beta"])

            result = self.open_design.fetch_package(provider, "alpha", cache_root)
            package_root = Path(result["package_root"])
            receipt_path = Path(result["receipt_path"])

            self.assertEqual(result["status"], "fetched")
            self.assertTrue((package_root / "manifest.json").is_file())
            self.assertTrue((package_root / "DESIGN.md").is_file())
            self.assertTrue((package_root / "tokens.css").is_file())
            self.assertFalse(any("beta" in path.parts for path in package_root.rglob("*")))
            self.assertFalse(any(path.name == ".git" for path in package_root.rglob("*")))
            self.assertFalse(sentinel.exists())

            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["package_slug"], "alpha")
            self.assertEqual(receipt["revision"], provider["revision"])
            self.assertEqual(receipt["root_tree"], provider["root_tree"])
            self.assertTrue(receipt["package_tree"])
            self.assertTrue(receipt["files"])
            self.assertTrue(all(record["mode"] == "100644" for record in receipt["files"]))

            verified = self.open_design.verify_package(provider, "alpha", cache_root)
            self.assertEqual(verified["status"], "verified")
            self.assertEqual(Path(verified["package_root"]), package_root)

    def test_valid_cache_is_reused_and_corrupt_cache_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _, provider = create_provider_repo(root)
            cache_root = root / "cache"
            first = self.open_design.fetch_package(provider, "alpha", cache_root)

            reused = self.open_design.fetch_package(provider, "alpha", cache_root)
            self.assertEqual(reused["status"], "reused")

            design_path = Path(first["package_root"]) / "DESIGN.md"
            design_path.write_bytes(b"corrupt but user-owned cache bytes\n")
            before = snapshot_tree(Path(first["cache_path"]))
            with self.assertRaisesRegex(ValueError, "cache|hash|differs"):
                self.open_design.fetch_package(provider, "alpha", cache_root)
            self.assertEqual(snapshot_tree(Path(first["cache_path"])), before)

    def test_offline_verify_rejects_modified_deleted_and_extra_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _, provider = create_provider_repo(root)
            cache_root = root / "cache"
            result = self.open_design.fetch_package(provider, "alpha", cache_root)
            cache_path = Path(result["cache_path"])
            design_path = Path(result["package_root"]) / "DESIGN.md"
            original = design_path.read_bytes()

            design_path.write_bytes(b"changed\n")
            with self.assertRaisesRegex(ValueError, "hash|differs"):
                self.open_design.verify_package(provider, "alpha", cache_root)
            design_path.write_bytes(original)

            design_path.unlink()
            with self.assertRaisesRegex(ValueError, "missing|file set"):
                self.open_design.verify_package(provider, "alpha", cache_root)
            design_path.write_bytes(original)

            extra = cache_path / "extra.txt"
            extra.write_bytes(b"extra\n")
            with self.assertRaisesRegex(ValueError, "unexpected|file set"):
                self.open_design.verify_package(provider, "alpha", cache_root)

    def test_rejects_invalid_slug_and_wrong_pinned_root_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _, provider = create_provider_repo(root)
            with self.assertRaisesRegex(ValueError, "slug"):
                self.open_design.fetch_package(provider, "../alpha", root / "cache")

            wrong_tree = dict(provider)
            wrong_tree["root_tree"] = "0" * 40
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", ResourceWarning)
                with self.assertRaisesRegex(ValueError, "root tree"):
                    self.open_design.list_packages(wrong_tree)
                gc.collect()
            self.assertEqual(
                [warning for warning in caught if warning.category is ResourceWarning],
                [],
            )

    def test_rejects_executable_and_symlink_entries_without_cache_mutation(self) -> None:
        for unsafe_kind in ("executable", "symlink"):
            with self.subTest(kind=unsafe_kind), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                _, provider = create_provider_repo(
                    root,
                    executable=unsafe_kind == "executable",
                    symlink=unsafe_kind == "symlink",
                )
                cache_root = root / "cache"
                with self.assertRaisesRegex(ValueError, "regular|mode|symlink"):
                    self.open_design.fetch_package(provider, "alpha", cache_root)
                target = (
                    cache_root / "open-design" / provider["revision"] / "alpha"
                )
                self.assertFalse(target.exists())

    def test_invalid_manifest_leaves_no_target_or_staging_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _, provider = create_provider_repo(root, invalid_manifest=True)
            cache_root = root / "cache"
            with self.assertRaisesRegex(ValueError, "manifest|schema"):
                self.open_design.fetch_package(provider, "alpha", cache_root)

            revision_root = cache_root / "open-design" / provider["revision"]
            self.assertFalse((revision_root / "alpha").exists())
            self.assertEqual(
                list(revision_root.glob(".alpha.staging-*"))
                if revision_root.exists()
                else [],
                [],
            )

    def test_cache_namespace_symlink_cannot_redirect_package_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _, provider = create_provider_repo(root)
            cache_root = root / "cache"
            outside = root / "outside"
            cache_root.mkdir()
            outside.mkdir()
            (cache_root / "open-design").symlink_to(
                outside,
                target_is_directory=True,
            )

            with self.assertRaisesRegex(ValueError, "symlink|cache"):
                self.open_design.fetch_package(provider, "alpha", cache_root)

            self.assertEqual(snapshot_tree(outside), {})

    def test_cli_requires_explicit_demand_before_network_or_cache_actions(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "list", "--json"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("explicit demand", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
