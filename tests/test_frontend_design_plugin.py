import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from unittest import mock

from tests.frontend_design_test_support import (
    load_script_module,
    sha256_bytes,
    snapshot_tree,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins/frontend-design-pack"
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
SKILL_ROOT_DEPENDENCY_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_:/.-])"
    r"(?:<skill-root>/|<skills-root>/[A-Za-z0-9._-]+/)"
    r"((?:references|scripts|assets)/[A-Za-z0-9._/-]+)"
)
REFERENCE_DEPENDENCY_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_:/.-])(references/[A-Za-z0-9._/-]+)"
)
MARKDOWN_DEPENDENCY_PATTERN = re.compile(
    r"\]\(((?:references|scripts|assets)/[A-Za-z0-9._/-]+)\)"
)
EXPECTED_MENGTO_DEPENDENCY_SOURCES = {
    "apple-swiftui-debugging",
    "marketing-skills",
    "mengto-skills",
    "openai-netlify-deploy",
    "swiftui-agent-skill",
}


renderer = load_script_module("render_frontend_design_plugin.py")


def copy_render_repository(destination: Path) -> None:
    shutil.copytree(
        REPO_ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "plugins"),
    )


class FrontendDesignPluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(
            (REPO_ROOT / "design-stack/sources.json").read_text(encoding="utf-8")
        )
        cls.lock = json.loads(
            (REPO_ROOT / "design-stack/sources.lock.json").read_text(
                encoding="utf-8"
            )
        )
        cls.provenance = json.loads(
            (REPO_ROOT / "design-stack/provenance.json").read_text(
                encoding="utf-8"
            )
        )
        cls.dependencies = json.loads(
            (REPO_ROOT / "design-stack/mengto-dependencies.json").read_text(
                encoding="utf-8"
            )
        )

    def test_renderer_is_deterministic_and_tracked_output_is_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "first"
            second = root / "second"

            renderer.render_plugin(REPO_ROOT, first)
            renderer.render_plugin(REPO_ROOT, second)

            first_snapshot = snapshot_tree(first)
            self.assertEqual(first_snapshot, snapshot_tree(second))
            self.assertEqual(first_snapshot, snapshot_tree(PLUGIN_ROOT))

    def test_renderer_rejects_repository_ancestor_output_without_deleting_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ancestor = Path(temp_dir) / "ancestor"
            repo_root = ancestor / "checkout"
            copy_render_repository(repo_root)
            sentinel = ancestor / "keep.txt"
            sentinel.write_text("keep\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "ancestor"):
                renderer.render_plugin(repo_root, ancestor)

            self.assertTrue(repo_root.is_dir())
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")

    def test_renderer_rejects_unapproved_repository_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir) / "checkout"
            copy_render_repository(repo_root)
            protected_root = repo_root / "tests"
            before = snapshot_tree(protected_root)

            with self.assertRaisesRegex(ValueError, "approved plugin destination"):
                renderer.render_plugin(repo_root, protected_root)

            self.assertEqual(snapshot_tree(protected_root), before)

    def test_renderer_rejects_direct_output_symlink_without_touching_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "target"
            target.mkdir()
            sentinel = target / "keep.txt"
            sentinel.write_text("keep\n", encoding="utf-8")
            plugin_root = root / "frontend-design-pack"
            plugin_root.symlink_to(target, target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "symlink"):
                renderer.render_plugin(REPO_ROOT, plugin_root)

            self.assertTrue(plugin_root.is_symlink())
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")

    def test_late_render_failure_preserves_previous_complete_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "checkout"
            copy_render_repository(repo_root)
            plugin_root = root / "frontend-design-pack"
            plugin_root.mkdir()
            sentinel = plugin_root / "previous.txt"
            sentinel.write_text("previous\n", encoding="utf-8")
            before = snapshot_tree(plugin_root)

            broken_reference = (
                repo_root
                / "design-stack/router/references/source-precedence.md"
            )
            broken_reference.unlink()
            broken_reference.mkdir()

            with self.assertRaises(OSError):
                renderer.render_plugin(repo_root, plugin_root)

            self.assertEqual(snapshot_tree(plugin_root), before)

    def test_atomic_swap_failure_restores_previous_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plugin_root = root / "frontend-design-pack"
            renderer.render_plugin(REPO_ROOT, plugin_root)
            sentinel = plugin_root / "previous.txt"
            sentinel.write_text("previous\n", encoding="utf-8")
            before = snapshot_tree(plugin_root)
            real_replace = os.replace
            failed_install = False
            canonical_plugin_root = plugin_root.resolve()

            def fail_new_tree_swap(source: Path, destination: Path) -> None:
                nonlocal failed_install
                source = Path(source)
                destination = Path(destination)
                if (
                    not failed_install
                    and destination == canonical_plugin_root
                    and source.parent == canonical_plugin_root.parent
                    and source.name.startswith(
                        f".{canonical_plugin_root.name}.render-"
                    )
                ):
                    failed_install = True
                    raise OSError("injected swap failure")
                real_replace(source, destination)

            with mock.patch.object(
                renderer.os,
                "replace",
                side_effect=fail_new_tree_swap,
            ):
                with self.assertRaisesRegex(OSError, "injected swap failure"):
                    renderer.render_plugin(REPO_ROOT, plugin_root)

            self.assertEqual(snapshot_tree(plugin_root), before)

    def test_interrupted_render_transaction_restores_previous_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plugin_root = root / "frontend-design-pack"
            plugin_root.mkdir()
            (plugin_root / "partial.txt").write_text("partial\n", encoding="utf-8")
            transaction_root = root / ".frontend-design-pack.render-transaction"
            backup = (transaction_root / "backup").resolve()
            backup.mkdir(parents=True)
            (backup / "previous.txt").write_text("previous\n", encoding="utf-8")
            (transaction_root / "journal.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "target": "frontend-design-pack",
                        "had_target": True,
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            renderer._recover_render_transaction(plugin_root)

            self.assertEqual(
                snapshot_tree(plugin_root),
                {"previous.txt": b"previous\n"},
            )
            self.assertFalse(transaction_root.exists())

    def test_recovery_preserves_committed_output_after_partial_backup_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            plugin_root = root / "frontend-design-pack"
            plugin_root.mkdir()
            (plugin_root / "a.txt").write_text("old a\n", encoding="utf-8")
            (plugin_root / "b.txt").write_text("old b\n", encoding="utf-8")
            transaction_root = root / ".frontend-design-pack.render-transaction"
            backup = (transaction_root / "backup").resolve()
            real_rmtree = renderer.shutil.rmtree
            cleanup_failed = False

            def fail_partway_through_backup_cleanup(path: Path, *args, **kwargs) -> None:
                nonlocal cleanup_failed
                candidate = Path(path)
                if candidate.resolve() == backup and not cleanup_failed:
                    cleanup_failed = True
                    (backup / "a.txt").unlink()
                    raise OSError("injected partial cleanup failure")
                real_rmtree(candidate, *args, **kwargs)

            with mock.patch.object(
                renderer.shutil,
                "rmtree",
                side_effect=fail_partway_through_backup_cleanup,
            ), self.assertRaisesRegex(OSError, "partial cleanup failure"):
                renderer.render_plugin(REPO_ROOT, plugin_root)

            self.assertTrue(
                (plugin_root / ".codex-plugin/plugin.json").is_file(),
                "the complete new output was installed before backup cleanup failed",
            )
            self.assertTrue(transaction_root.is_dir())

            renderer._recover_render_transaction(plugin_root)

            self.assertTrue((plugin_root / ".codex-plugin/plugin.json").is_file())
            self.assertFalse((plugin_root / "a.txt").exists())
            self.assertFalse((plugin_root / "b.txt").exists())
            self.assertFalse(transaction_root.exists())

    def test_codex_and_claude_manifests_share_name_and_semver(self) -> None:
        codex = json.loads(
            (PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        claude = json.loads(
            (PLUGIN_ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        )
        marketplace = json.loads(
            (REPO_ROOT / ".claude-plugin/marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        marketplace_entry = {
            entry["name"]: entry for entry in marketplace["plugins"]
        }["frontend-design-pack"]

        self.assertEqual(codex["name"], "frontend-design-pack")
        self.assertEqual(claude["name"], "frontend-design-pack")
        self.assertEqual(codex["version"], claude["version"])
        self.assertEqual(codex["version"], marketplace_entry["version"])
        self.assertRegex(codex["version"], SEMVER_PATTERN)
        self.assertEqual(codex["skills"], "./skills/")
        self.assertEqual(
            marketplace_entry["source"], "./plugins/frontend-design-pack"
        )

    def test_codex_manifest_includes_required_interface_metadata(self) -> None:
        codex = json.loads(
            (PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )

        self.assertEqual(
            codex["interface"],
            {
                "capabilities": ["Interactive", "Read", "Write"],
                "category": "Creativity",
                "defaultPrompt": [
                    "Shape a frontend brief and choose the right design workflow",
                    "Explore three evidence-backed visual directions",
                    "Review this frontend for UX, accessibility, and polish",
                ],
                "developerName": "Hun",
                "displayName": "Frontend Design Pack",
                "longDescription": (
                    "Shape, explore, implement, review, write, and harden frontend "
                    "experiences with one evidence-first router and a reviewed "
                    "reference corpus."
                ),
                "shortDescription": "Evidence-first frontend design workflows",
            },
        )

    def test_plugin_contains_exactly_one_native_self_contained_skill(self) -> None:
        skill_files = sorted(PLUGIN_ROOT.rglob("SKILL.md"))
        self.assertEqual(
            [path.relative_to(PLUGIN_ROOT).as_posix() for path in skill_files],
            ["skills/frontend-design/SKILL.md"],
        )
        self.assertFalse(any(path.is_symlink() for path in PLUGIN_ROOT.rglob("*")))
        skill_text = skill_files[0].read_text(encoding="utf-8")
        self.assertNotIn("../", skill_text)
        for relative_path in (
            "references/source-precedence.md",
            "references/quality-gates.md",
            "references/routing.json",
            "references/reference-catalog.json",
        ):
            self.assertTrue(
                (PLUGIN_ROOT / "skills/frontend-design" / relative_path).is_file(),
                relative_path,
            )

    def test_packaged_routing_references_resolve_from_skill_root(self) -> None:
        skill_root = PLUGIN_ROOT / "skills/frontend-design"
        routing = json.loads(
            (skill_root / "references/routing.json").read_text(encoding="utf-8")
        )

        self.assertEqual(
            routing["references"],
            {
                "source-precedence": "references/source-precedence.md",
                "quality-gates": "references/quality-gates.md",
                "open-design": "references/open-design.md",
            },
        )
        for key, relative_path in routing["references"].items():
            with self.subTest(reference=key):
                path = PurePosixPath(relative_path)
                self.assertFalse(path.is_absolute())
                self.assertNotIn("..", path.parts)
                self.assertNotIn(".", path.parts)
                self.assertTrue(skill_root.joinpath(*path.parts).is_file())

    def test_plugin_validation_rejects_unresolved_routing_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_root = Path(temp_dir) / "frontend-design-pack"
            shutil.copytree(PLUGIN_ROOT, plugin_root)
            routing_path = (
                plugin_root / "skills/frontend-design/references/routing.json"
            )
            routing = json.loads(routing_path.read_text(encoding="utf-8"))
            routing["references"]["source-precedence"] = (
                "router/references/source-precedence.md"
            )
            routing_path.write_text(
                json.dumps(routing, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "routing reference.*source-precedence.*missing",
            ):
                renderer.validate_plugin_tree(plugin_root)

    def test_plugin_validation_rejects_unpinned_design_md_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_root = Path(temp_dir) / "frontend-design-pack"
            shutil.copytree(PLUGIN_ROOT, plugin_root)
            routing_path = (
                plugin_root / "skills/frontend-design/references/routing.json"
            )
            routing = json.loads(routing_path.read_text(encoding="utf-8"))
            routing["design_md_validation"]["package_spec"] = "@google/design.md"
            routing_path.write_text(
                json.dumps(routing, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "DESIGN.md validation"):
                renderer.validate_plugin_tree(plugin_root)

    def test_plugin_validation_rejects_imported_design_md_tooling_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_root = Path(temp_dir) / "frontend-design-pack"
            shutil.copytree(PLUGIN_ROOT, plugin_root)
            routing_path = (
                plugin_root / "skills/frontend-design/references/routing.json"
            )
            routing = json.loads(routing_path.read_text(encoding="utf-8"))
            authority = routing["design_md_validation"]["authority_order"]
            routing["design_md_validation"]["authority_order"] = list(
                reversed(authority)
            )
            routing_path.write_text(
                json.dumps(routing, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "DESIGN.md validation"):
                renderer.validate_plugin_tree(plugin_root)

    def test_reference_catalog_resolves_every_approved_source_decision(self) -> None:
        skill_root = PLUGIN_ROOT / "skills/frontend-design"
        catalog = json.loads(
            (skill_root / "references/reference-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        provenance = {
            (record["source_id"], record["upstream_path"]): record
            for record in self.provenance["records"]
        }
        mengto_entries = catalog["mengto_skills"]
        self.assertEqual(len(mengto_entries), 95)
        for entry in mengto_entries:
            source_key = (entry["source_id"], entry["source_path"])
            decision = provenance[source_key]
            with self.subTest(path=entry["source_path"]):
                self.assertEqual(entry["decision"], decision["decision"])
                if entry["decision"] == "included":
                    reference_path = skill_root / entry["reference_path"]
                    self.assertTrue(reference_path.is_file())
                    self.assertEqual(
                        sha256_bytes(reference_path.read_bytes()), decision["sha256"]
                    )
                else:
                    self.assertEqual(entry["decision"], "mapped-to-official")
                    self.assertNotIn("reference_path", entry)
                    self.assertEqual(
                        entry["official_mapping"], decision["official_mapping"]
                    )

        design_entries = catalog["design_md"]
        self.assertEqual(len(design_entries), 74)
        self.assertTrue(
            all(
                (skill_root / entry["reference_path"]).is_file()
                and entry["authority"] == "third-party-analysis"
                for entry in design_entries
            )
        )
        for catalog_key in ("vercel_interface", "google_design_md"):
            reference = catalog[catalog_key]
            reference_path = skill_root / reference["reference_path"]
            self.assertTrue(reference_path.is_file())
            self.assertEqual(
                sha256_bytes(reference_path.read_bytes()),
                reference["sha256"],
            )

    def test_catalog_maps_vercel_quality_guidance_to_external_runtime_skills(self) -> None:
        skill_root = PLUGIN_ROOT / "skills/frontend-design"
        catalog = json.loads(
            (skill_root / "references/reference-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        source_contract = json.loads(
            (REPO_ROOT / "design-stack/vercel-runtime-skills.json").read_text(
                encoding="utf-8"
            )
        )
        runtime = catalog["vercel_runtime_skills"]

        self.assertEqual(runtime["source_id"], "vercel-agent-skills")
        self.assertEqual(
            runtime["repository"],
            "https://github.com/vercel-labs/agent-skills",
        )
        self.assertEqual(
            runtime["revision"],
            "f8a72b9603728bb92a217a879b7e62e43ad76c81",
        )
        self.assertEqual(
            runtime["source_tree"],
            "5bd714a247baf205f05eb0371e82602e181a505d",
        )
        self.assertEqual(runtime["license_status"], "unresolved")
        self.assertEqual(runtime["distribution"], "reference-only")
        self.assertEqual(
            runtime["contract_sha256"],
            "21499d8ad770e9c5f1c7b8e481b12c2052c80dbaf5d17a2614ea641ec10683a5",
        )
        self.assertEqual(runtime["skills"], source_contract["skills"])
        for skill in runtime["skills"]:
            self.assertNotIn("reference_path", skill)
            self.assertEqual(
                skill["external_runtime_requirement"]["resolution"],
                "discover-installed-skill",
            )

        copied_vercel_skill_paths = [
            path
            for path in skill_root.rglob("*")
            if path.is_file()
            and "vercel-agent-skills" in path.relative_to(skill_root).parts
        ]
        self.assertEqual(copied_vercel_skill_paths, [])

    def test_open_design_provider_and_inert_cache_helper_are_packaged(self) -> None:
        skill_root = PLUGIN_ROOT / "skills/frontend-design"
        provider_path = skill_root / "references/open-design-provider.json"
        helper_path = skill_root / "scripts/open_design_cache.py"
        guide_path = skill_root / "references/open-design.md"

        self.assertTrue(provider_path.is_file())
        self.assertTrue(helper_path.is_file())
        self.assertTrue(guide_path.is_file())
        self.assertEqual(helper_path.stat().st_mode & 0o111, 0)

        provider = json.loads(provider_path.read_text(encoding="utf-8"))
        self.assertEqual(provider["provider_id"], "open-design")
        self.assertEqual(
            provider["repository"],
            "https://github.com/nexu-io/open-design",
        )
        self.assertEqual(
            provider["revision"],
            "81b20dc6a214da2228bdd08f8850656b98f9bcea",
        )
        self.assertEqual(
            provider["root_tree"],
            "f3b4e7ab9e965c26e07be1104b4e0977f780807a",
        )
        self.assertEqual(provider["authority"], "optional-provider")
        self.assertEqual(provider["distribution"], "on-demand")
        self.assertEqual(
            provider["required_files"],
            ["manifest.json", "DESIGN.md", "tokens.css"],
        )
        self.assertEqual(
            provider["license"]["sha256"],
            "9d95806a26532623360eb84bb17d298f394b55ef73fb4c0796d99b4319b2b0da",
        )
        self.assertEqual(provider["network_policy"], "explicit-demand-only")
        self.assertEqual(provider["cache_write_policy"], "selected-package-only")
        self.assertEqual(provider["corrupt_cache_policy"], "fail-without-mutation")
        catalog = json.loads(
            (skill_root / "references/reference-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        catalog_provider = catalog["open_design_provider"]
        self.assertEqual(
            catalog_provider["reference_path"],
            "references/open-design-provider.json",
        )
        self.assertEqual(
            catalog_provider["helper_path"],
            "scripts/open_design_cache.py",
        )
        self.assertEqual(
            catalog_provider["provider_sha256"],
            sha256_bytes(provider_path.read_bytes()),
        )
        self.assertEqual(
            catalog_provider["helper_sha256"],
            sha256_bytes(helper_path.read_bytes()),
        )
        self.assertEqual(catalog_provider["revision"], provider["revision"])
        self.assertEqual(catalog_provider["root_tree"], provider["root_tree"])

    def test_plugin_validation_rejects_mutated_open_design_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_root = Path(temp_dir) / "frontend-design-pack"
            shutil.copytree(PLUGIN_ROOT, plugin_root)
            provider_path = (
                plugin_root
                / "skills/frontend-design/references/open-design-provider.json"
            )
            provider = json.loads(provider_path.read_text(encoding="utf-8"))
            provider["network_policy"] = "automatic"
            provider_path.write_text(
                json.dumps(provider, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Open Design provider"):
                renderer.validate_plugin_tree(plugin_root)

    def test_plugin_validation_rejects_rehashed_open_design_helper_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_root = Path(temp_dir) / "frontend-design-pack"
            shutil.copytree(PLUGIN_ROOT, plugin_root)
            skill_root = plugin_root / "skills/frontend-design"
            helper_path = skill_root / "scripts/open_design_cache.py"
            helper_path.write_text(
                helper_path.read_text(encoding="utf-8") + "\n# mutation\n",
                encoding="utf-8",
            )
            catalog_path = skill_root / "references/reference-catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["open_design_provider"]["helper_sha256"] = sha256_bytes(
                helper_path.read_bytes()
            )
            catalog_path.write_text(
                json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Open Design provider helper"):
                renderer.validate_plugin_tree(plugin_root)

    def test_plugin_validation_rejects_invalid_vercel_runtime_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_root = Path(temp_dir) / "frontend-design-pack"
            shutil.copytree(PLUGIN_ROOT, plugin_root)
            catalog_path = (
                plugin_root
                / "skills/frontend-design/references/reference-catalog.json"
            )
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["vercel_runtime_skills"]["skills"][0][
                "external_runtime_requirement"
            ]["resolution"] = "guess-a-local-path"
            catalog_path.write_text(
                json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Vercel runtime"):
                renderer.validate_plugin_tree(plugin_root)

    def test_all_mengto_procedures_are_included_or_mapped_to_official(self) -> None:
        skill_root = PLUGIN_ROOT / "skills/frontend-design"
        catalog = json.loads(
            (skill_root / "references/reference-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        unavailable = {
            entry["source_path"]: entry["decision"]
            for entry in catalog["mengto_skills"]
            if entry["decision"] not in {"included", "mapped-to-official"}
        }

        self.assertEqual(unavailable, {})

    def test_mengto_dependency_map_covers_29_sources_and_30_destinations(self) -> None:
        dependencies = [
            dependency
            for procedure in self.dependencies["procedures"]
            for dependency in procedure["dependencies"]
        ]

        self.assertEqual(self.dependencies["schema_version"], 1)
        self.assertEqual(len(dependencies), 30)
        self.assertEqual(
            {dependency["source_id"] for dependency in dependencies},
            EXPECTED_MENGTO_DEPENDENCY_SOURCES,
        )
        self.assertEqual(
            len(
                {
                    (procedure["source_path"], dependency["target_path"])
                    for procedure in self.dependencies["procedures"]
                    for dependency in procedure["dependencies"]
                }
            ),
            30,
        )
        self.assertEqual(
            len(
                {
                    (dependency["source_id"], dependency["source_path"])
                    for dependency in dependencies
                }
            ),
            29,
        )

    def test_browser_evaluator_uses_discoverable_external_runtime_contract(self) -> None:
        catalog = json.loads(
            (
                PLUGIN_ROOT
                / "skills/frontend-design/references/reference-catalog.json"
            ).read_text(encoding="utf-8")
        )
        optimize = next(
            entry
            for entry in catalog["mengto_skills"]
            if entry["name"] == "optimize-web-animations"
        )

        self.assertEqual(
            optimize["external_runtime_requirements"],
            [
                {
                    "capability": "browser:control-in-app-browser",
                    "required_file": "scripts/browser-client.mjs",
                    "resolution": "discover-installed-plugin",
                }
            ],
        )
        self.assertNotIn("/Users/", json.dumps(optimize))

    def test_imported_helper_scripts_preserve_mode_as_data_but_are_inert(self) -> None:
        skill_root = PLUGIN_ROOT / "skills/frontend-design"
        catalog = json.loads(
            (skill_root / "references/reference-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        locked_files = {
            (source["id"], item["path"]): item
            for source in self.lock["sources"]
            for item in source["files"]
        }
        scripts = [
            supporting_file
            for entry in catalog["mengto_skills"]
            for supporting_file in entry.get("supporting_files", [])
            if PurePosixPath(supporting_file["target_path"]).parts[0] == "scripts"
        ]

        self.assertEqual(
            {PurePosixPath(item["target_path"]).name for item in scripts},
            {"generate_voice.py", "stitch_full_page_capture.mjs"},
        )
        for item in scripts:
            with self.subTest(path=item["reference_path"]):
                self.assertEqual(
                    locked_files[(item["source_id"], item["source_path"])]["mode"],
                    "0755",
                )
                self.assertEqual(
                    (skill_root / item["reference_path"]).stat().st_mode & 0o111,
                    0,
                )

    def test_included_mengto_procedures_resolve_all_local_dependencies(self) -> None:
        skill_root = PLUGIN_ROOT / "skills/frontend-design"
        catalog = json.loads(
            (skill_root / "references/reference-catalog.json").read_text(
                encoding="utf-8"
            )
        )

        for entry in catalog["mengto_skills"]:
            if entry["decision"] != "included":
                continue
            procedure_path = skill_root / entry["reference_path"]
            with self.subTest(source_path=entry["source_path"]):
                self.assertEqual(procedure_path.name, "procedure.md")
                dependency_contents = [
                    procedure_path.read_text(encoding="utf-8")
                ]
                for supporting_file in entry.get("supporting_files", []):
                    packaged_path = skill_root / supporting_file["reference_path"]
                    self.assertTrue(packaged_path.is_file())
                    self.assertEqual(
                        sha256_bytes(packaged_path.read_bytes()),
                        supporting_file["sha256"],
                    )
                    if packaged_path.suffix.lower() == ".md":
                        dependency_contents.append(
                            packaged_path.read_text(encoding="utf-8")
                        )
                dependencies = sorted(
                    {
                        dependency
                        for content in dependency_contents
                        for dependency in (
                            set(SKILL_ROOT_DEPENDENCY_PATTERN.findall(content))
                            | set(REFERENCE_DEPENDENCY_PATTERN.findall(content))
                            | set(MARKDOWN_DEPENDENCY_PATTERN.findall(content))
                        )
                    }
                )
                for dependency in dependencies:
                    dependency_path = PurePosixPath(dependency)
                    self.assertNotIn("..", dependency_path.parts)
                    self.assertTrue(
                        procedure_path.parent.joinpath(*dependency_path.parts).is_file(),
                        f"{entry['source_path']} -> {dependency}",
                    )

    def test_plugin_validation_rejects_missing_local_procedure_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_root = Path(temp_dir) / "frontend-design-pack"
            shutil.copytree(PLUGIN_ROOT, plugin_root)
            catalog = json.loads(
                (
                    plugin_root
                    / "skills/frontend-design/references/reference-catalog.json"
                ).read_text(encoding="utf-8")
            )
            entry = next(
                item
                for item in catalog["mengto_skills"]
                if item["decision"] == "included"
            )
            procedure_path = (
                plugin_root / "skills/frontend-design" / entry["reference_path"]
            )
            procedure_path.write_text(
                procedure_path.read_text(encoding="utf-8")
                + "\n[Missing](references/not-packaged.md)\n",
                encoding="utf-8",
            )
            entry["sha256"] = sha256_bytes(procedure_path.read_bytes())
            catalog_path = (
                plugin_root
                / "skills/frontend-design/references/reference-catalog.json"
            )
            catalog_path.write_text(
                json.dumps(catalog, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "local dependency.*not-packaged"):
                renderer.validate_plugin_tree(plugin_root)

    def test_plugin_carries_required_notices_for_every_copied_source(self) -> None:
        notices = (PLUGIN_ROOT / "THIRD_PARTY_NOTICES.md").read_text(
            encoding="utf-8"
        )
        sources = {
            source["id"]: source
            for source in self.registry["sources"]
            if source["distribution"] == "vendored"
        }
        for source_id, source in sources.items():
            with self.subTest(source=source_id):
                self.assertIn(source["repository"], notices)
                self.assertIn(source["revision"], notices)
                notice_copy = PLUGIN_ROOT / "licenses" / f"{source_id}.txt"
                self.assertTrue(notice_copy.is_file())
                self.assertEqual(
                    sha256_bytes(notice_copy.read_bytes()),
                    source["license"]["notice_sha256"],
                )

    def test_runtime_copy_validation_reports_missing_changed_and_unexpected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_root = Path(temp_dir) / "runtime"
            shutil.copytree(PLUGIN_ROOT, runtime_root)
            renderer.validate_runtime_copy(PLUGIN_ROOT, runtime_root, "Codex")

            missing = runtime_root / "skills/frontend-design/SKILL.md"
            missing.unlink()
            with self.assertRaisesRegex(ValueError, "Codex.*missing"):
                renderer.validate_runtime_copy(PLUGIN_ROOT, runtime_root, "Codex")

            shutil.copy2(
                PLUGIN_ROOT / "skills/frontend-design/SKILL.md", missing
            )
            missing.write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Codex.*changed"):
                renderer.validate_runtime_copy(PLUGIN_ROOT, runtime_root, "Codex")

            shutil.copy2(
                PLUGIN_ROOT / "skills/frontend-design/SKILL.md", missing
            )
            (runtime_root / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Codex.*unexpected"):
                renderer.validate_runtime_copy(PLUGIN_ROOT, runtime_root, "Codex")

    def test_cli_validates_codex_and_claude_runtime_roots_separately(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            codex_root = root / "codex"
            claude_root = root / "claude"
            shutil.copytree(PLUGIN_ROOT, codex_root)
            shutil.copytree(PLUGIN_ROOT, claude_root)
            result = subprocess.run(
                [
                    "python3",
                    "scripts/validate_frontend_design_stack.py",
                    "--repo-root",
                    str(REPO_ROOT),
                    "--codex-runtime-root",
                    str(codex_root),
                    "--claude-runtime-root",
                    str(claude_root),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Codex runtime", result.stdout)
        self.assertIn("Claude runtime", result.stdout)


if __name__ == "__main__":
    unittest.main()
