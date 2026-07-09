import copy
import io
import json
import shutil
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.frontend_design_test_support import (
    commit_all,
    init_git_repo,
    load_script_module,
    sha256_bytes,
    snapshot_tree,
    write_files,
    write_json,
    write_tar,
)


sync = load_script_module("sync_design_sources.py")


LICENSE = b"fixture license\n"
SKILL = b"---\nname: fixture\ndescription: Fixture skill.\n---\n\n# Fixture\n"
DESIGN = b"# Fixture design\n"
REVISION = "a" * 40
PREFIX = f"mengto-skills-{REVISION}"


def fixture_payloads(
    skill_content: bytes = SKILL,
    decision: str = "included",
) -> tuple[dict, dict, dict]:
    source = {
        "id": "mengto-skills",
        "repository": "https://example.invalid/source",
        "revision": REVISION,
        "authority": "procedural-guidance",
        "scope": ["skills/**"],
        "license": {
            "spdx": "MIT",
            "status": "verified",
            "notice_path": "LICENSE",
            "notice_sha256": sha256_bytes(LICENSE),
        },
        "role": "fixture",
        "update_method": "reviewed-local-tar",
        "distribution": "vendored",
        "destination": "design-stack/vendor/mengto-skills",
    }
    registry = {
        "schema_version": 1,
        "google_design_md_cli_version": "0.3.0",
        "sources": [source],
    }
    lock = {
        "schema_version": 1,
        "sources": [
            {
                "id": "mengto-skills",
                "revision": REVISION,
                "tree": "b" * 40,
                "files": [
                    {
                        "path": "LICENSE",
                        "size": len(LICENSE),
                        "mode": "0644",
                        "sha256": sha256_bytes(LICENSE),
                        "materialization": "vendored",
                    },
                    {
                        "path": "skills/fixture/SKILL.md",
                        "size": len(skill_content),
                        "mode": "0644",
                        "sha256": sha256_bytes(skill_content),
                        "materialization": "vendored",
                    },
                ],
            }
        ],
        "catalogs": {
            "mengto_skills": [
                {
                    "source_id": "mengto-skills",
                    "name": "fixture",
                    "description": "Fixture skill.",
                    "path": "skills/fixture/SKILL.md",
                    "sha256": sha256_bytes(skill_content),
                }
            ],
            "design_md": [],
        },
    }
    record = {
        "source_id": "mengto-skills",
        "upstream_path": "skills/fixture/SKILL.md",
        "revision": REVISION,
        "authority": "procedural-guidance",
        "catalog": "mengto_skills",
        "role": "fixture",
        "license": copy.deepcopy(source["license"]),
        "origin": {
            "repository": source["repository"],
            "path": "skills/fixture/SKILL.md",
            "revision": REVISION,
            "content_sha256": sha256_bytes(skill_content),
            "basis": "fixture",
            "introduced_revision": REVISION,
            "publisher": "Fixture",
        },
        "sha256": sha256_bytes(skill_content),
        "decision": decision,
    }
    if decision == "mapped-to-official":
        lock["sources"][0]["files"][1]["materialization"] = "metadata-only"
        record["reason"] = "Use a fixture official replacement."
        record["license"] = {
            "spdx": "Apache-2.0",
            "status": "verified",
            "notice_path": "skills/fixture/LICENSE.txt",
            "notice_sha256": "c" * 64,
        }
        record["official_mapping"] = {
            "repository": "https://example.invalid/official",
            "revision": "d" * 40,
            "tree": "e" * 40,
            "path": "skills/fixture/SKILL.md",
            "content_sha256": "f" * 64,
            "license_path": "skills/fixture/LICENSE.txt",
            "license_sha256": "c" * 64,
        }
    provenance = {
        "schema_version": 1,
        "records": [record],
    }
    return registry, lock, provenance


def write_sync_repo(
    repo_root: Path,
    *,
    locked_skill: bytes = SKILL,
    installed_skill: bytes = SKILL,
    branch: str = "codex/test",
    with_renderer: bool = True,
    decision: str = "included",
) -> None:
    init_git_repo(repo_root, branch=branch)
    registry, lock, provenance = fixture_payloads(locked_skill, decision=decision)
    write_json(repo_root / "design-stack/sources.json", registry)
    write_json(repo_root / "design-stack/sources.lock.json", lock)
    write_json(repo_root / "design-stack/provenance.json", provenance)
    vendor_files = {"LICENSE": LICENSE}
    if decision == "included":
        vendor_files["skills/fixture/SKILL.md"] = installed_skill
    write_files(repo_root / "design-stack/vendor/mengto-skills", vendor_files)
    write_files(
        repo_root / "plugins/frontend-design-pack",
        {"render.txt": b"old\n"},
    )
    if with_renderer:
        renderer = repo_root / "scripts/render_frontend_design_plugin.py"
        renderer.parent.mkdir(parents=True)
        renderer.write_text(
            """#!/usr/bin/env python3
import argparse
import json
import shutil
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--repo-root', required=True)
p.add_argument('--plugin-root', required=True)
a = p.parse_args()
root = Path(a.repo_root)
out = Path(a.plugin_root)
if out.exists():
    shutil.rmtree(out)
(out / '.codex-plugin').mkdir(parents=True)
(out / '.claude-plugin').mkdir(parents=True)
(out / 'skills/frontend-design').mkdir(parents=True)
manifest = {'name': 'frontend-design-pack', 'version': '1.0.0'}
(out / '.codex-plugin/plugin.json').write_text(json.dumps(manifest))
(out / '.claude-plugin/plugin.json').write_text(json.dumps(manifest))
(out / 'skills/frontend-design/SKILL.md').write_text(
    '---\\nname: frontend-design\\ndescription: Fixture router.\\n---\\n'
)
source_skill = root / 'design-stack/vendor/mengto-skills/skills/fixture/SKILL.md'
skill = source_skill.read_bytes() if source_skill.exists() else b'mapped-only'
(out / 'render.txt').write_bytes(b'rendered:' + skill)
""",
            encoding="utf-8",
        )
    commit_all(repo_root)


def standard_archive(path: Path, skill: bytes = SKILL, mode: int = 0o644) -> None:
    write_tar(
        path,
        PREFIX,
        {
            "LICENSE": LICENSE,
            "skills/fixture/SKILL.md": skill,
        },
        modes={"skills/fixture/SKILL.md": mode},
    )


def watched_snapshot(repo_root: Path) -> dict[str, bytes]:
    return snapshot_tree(repo_root / "design-stack") | snapshot_tree(
        repo_root / "plugins/frontend-design-pack"
    )


class FrontendDesignArchiveSafetyTests(unittest.TestCase):
    def test_extract_requires_explicit_existing_tar_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with self.assertRaisesRegex(ValueError, "archive does not exist"):
                sync.extract_reviewed_tar(
                    root / "missing.tar",
                    root / "out",
                    "mengto-skills",
                    REVISION,
                )

            archive = root / "source.zip"
            archive.write_bytes(b"PK\x03\x04not-a-tar")
            with self.assertRaisesRegex(ValueError, "tar archive"):
                sync.extract_reviewed_tar(
                    archive,
                    root / "out",
                    "mengto-skills",
                    REVISION,
                )

    def test_extract_requires_expected_revision_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive = root / "source.tar"
            write_tar(archive, "wrong-prefix", {"LICENSE": LICENSE})
            with self.assertRaisesRegex(ValueError, "revision|prefix"):
                sync.extract_reviewed_tar(
                    archive, root / "out", "mengto-skills", REVISION
                )

    def test_extract_rejects_unsafe_paths(self) -> None:
        unsafe_paths = (
            "../outside",
            "/absolute",
            f"{PREFIX}/../outside",
            f"{PREFIX}/./inside",
            f"{PREFIX}/inside//file",
            f"{PREFIX}/inside\\file",
        )
        for unsafe_path in unsafe_paths:
            with self.subTest(path=unsafe_path), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                archive = root / "source.tar"
                member = tarfile.TarInfo(unsafe_path)
                member.size = 6
                with tarfile.open(archive, "w") as tar:
                    tar.addfile(member, io.BytesIO(b"unsafe"))
                with self.assertRaisesRegex(ValueError, "path|prefix"):
                    sync.extract_reviewed_tar(
                        archive, root / "out", "mengto-skills", REVISION
                    )
                self.assertFalse((root / "outside").exists())

    def test_extract_rejects_links_devices_and_fifos(self) -> None:
        member_types = (
            tarfile.SYMTYPE,
            tarfile.LNKTYPE,
            tarfile.CHRTYPE,
            tarfile.BLKTYPE,
            tarfile.FIFOTYPE,
        )
        for member_type in member_types:
            with self.subTest(member_type=member_type), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                archive = root / "source.tar"
                member = tarfile.TarInfo(f"{PREFIX}/unsafe")
                member.type = member_type
                member.linkname = "target"
                write_tar(archive, PREFIX, {}, extra_members=[member])
                with self.assertRaisesRegex(ValueError, "regular|link|type"):
                    sync.extract_reviewed_tar(
                        archive, root / "out", "mengto-skills", REVISION
                    )

    def test_extract_rejects_duplicate_members(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive = root / "source.tar"
            first = tarfile.TarInfo(f"{PREFIX}/duplicate")
            second = tarfile.TarInfo(f"{PREFIX}/duplicate")
            write_tar(archive, PREFIX, {}, extra_members=[first, second])
            with self.assertRaisesRegex(ValueError, "duplicate"):
                sync.extract_reviewed_tar(
                    archive, root / "out", "mengto-skills", REVISION
                )

    def test_executable_members_are_copied_as_inert_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive = root / "source.tar"
            sentinel = root / "executed"
            script = f"#!/bin/sh\ntouch {sentinel}\n".encode()
            write_tar(
                archive,
                PREFIX,
                {"skills/fixture/scripts/unsafe.sh": script},
                modes={"skills/fixture/scripts/unsafe.sh": 0o755},
            )

            extracted = sync.extract_reviewed_tar(
                archive, root / "out", "mengto-skills", REVISION
            )

            copied = extracted / "skills/fixture/scripts/unsafe.sh"
            self.assertEqual(copied.read_bytes(), script)
            self.assertEqual(copied.stat().st_mode & 0o111, 0)
            self.assertFalse(sentinel.exists())


class FrontendDesignSyncTests(unittest.TestCase):
    def test_batch_sync_bootstraps_all_missing_vendored_sources(self) -> None:
        second_revision = "c" * 40
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            mengto_archive = root / "mengto.tar"
            design_archive = root / "design.tar"
            write_sync_repo(repo_root)
            registry_path = repo_root / "design-stack/sources.json"
            lock_path = repo_root / "design-stack/sources.lock.json"
            provenance_path = repo_root / "design-stack/provenance.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            second_source = {
                "id": "awesome-design-md",
                "repository": "https://example.invalid/design-source",
                "revision": second_revision,
                "authority": "third-party-analysis",
                "scope": ["design-md/*/DESIGN.md"],
                "license": {
                    "spdx": "MIT",
                    "status": "verified",
                    "notice_path": "LICENSE",
                    "notice_sha256": sha256_bytes(LICENSE),
                },
                "role": "fixture designs",
                "update_method": "reviewed-local-tar",
                "distribution": "vendored",
                "destination": "design-stack/vendor/awesome-design-md",
            }
            registry["sources"].append(second_source)
            lock["sources"].append(
                {
                    "id": "awesome-design-md",
                    "revision": second_revision,
                    "tree": "d" * 40,
                    "files": [
                        {
                            "path": "LICENSE",
                            "size": len(LICENSE),
                            "mode": "0644",
                            "sha256": sha256_bytes(LICENSE),
                            "materialization": "vendored",
                        },
                        {
                            "path": "design-md/fixture/DESIGN.md",
                            "size": len(DESIGN),
                            "mode": "0644",
                            "sha256": sha256_bytes(DESIGN),
                            "materialization": "vendored",
                        },
                    ],
                }
            )
            lock["catalogs"]["design_md"] = [
                {
                    "source_id": "awesome-design-md",
                    "name": "fixture",
                    "path": "design-md/fixture/DESIGN.md",
                    "sha256": sha256_bytes(DESIGN),
                    "authority": "third-party-analysis",
                }
            ]
            provenance["records"].append(
                {
                    "source_id": "awesome-design-md",
                    "upstream_path": "design-md/fixture/DESIGN.md",
                    "revision": second_revision,
                    "authority": "third-party-analysis",
                    "catalog": "design_md",
                    "role": "fixture design",
                    "license": copy.deepcopy(second_source["license"]),
                    "origin": {
                        "repository": second_source["repository"],
                        "path": "design-md/fixture/DESIGN.md",
                        "revision": second_revision,
                        "content_sha256": sha256_bytes(DESIGN),
                        "basis": "fixture",
                        "introduced_revision": second_revision,
                        "publisher": "Fixture",
                    },
                    "sha256": sha256_bytes(DESIGN),
                    "decision": "included",
                }
            )
            write_json(registry_path, registry)
            write_json(lock_path, lock)
            write_json(provenance_path, provenance)
            shutil.rmtree(repo_root / "design-stack/vendor")
            commit_all(repo_root, "add bootstrap metadata")
            standard_archive(mengto_archive)
            write_tar(
                design_archive,
                f"awesome-design-md-{second_revision}",
                {
                    "LICENSE": LICENSE,
                    "design-md/fixture/DESIGN.md": DESIGN,
                },
            )

            report = sync.sync_sources(
                repo_root,
                {
                    "mengto-skills": mengto_archive,
                    "awesome-design-md": design_archive,
                },
            )

            self.assertEqual(
                {
                    source_report["source_id"]
                    for source_report in report["sources"]
                },
                {"mengto-skills", "awesome-design-md"},
            )
            self.assertTrue(
                (
                    repo_root
                    / "design-stack/vendor/mengto-skills/skills/fixture/SKILL.md"
                ).is_file()
            )
            self.assertTrue(
                (
                    repo_root
                    / "design-stack/vendor/awesome-design-md/design-md/fixture/DESIGN.md"
                ).is_file()
            )

    def test_atomic_replacement_restores_every_target_on_late_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first_target = root / "first.txt"
            second_target = root / "second.txt"
            first_staged = root / "first.new"
            missing_staged = root / "missing.new"
            first_target.write_bytes(b"first old")
            second_target.write_bytes(b"second old")
            first_staged.write_bytes(b"first new")

            with self.assertRaises(FileNotFoundError):
                sync._replace_paths_atomically(
                    [
                        (first_staged, first_target),
                        (missing_staged, second_target),
                    ],
                    root / "transaction",
                    root,
                )

            self.assertEqual(first_target.read_bytes(), b"first old")
            self.assertEqual(second_target.read_bytes(), b"second old")

    def test_atomic_replacement_rolls_back_keyboard_interrupt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first_target = root / "first.txt"
            second_target = root / "second.txt"
            first_staged = root / "first.new"
            second_staged = root / "second.new"
            first_target.write_bytes(b"first old")
            second_target.write_bytes(b"second old")
            first_staged.write_bytes(b"first new")
            second_staged.write_bytes(b"second new")
            real_replace = sync.os.replace

            def interrupt_second_install(source: Path, target: Path) -> None:
                if Path(source) == second_staged:
                    raise KeyboardInterrupt()
                real_replace(source, target)

            with mock.patch.object(
                sync.os, "replace", side_effect=interrupt_second_install
            ), self.assertRaises(KeyboardInterrupt):
                sync._replace_paths_atomically(
                    [
                        (first_staged, first_target),
                        (second_staged, second_target),
                    ],
                    root / "transaction",
                    root,
                )

            self.assertEqual(first_target.read_bytes(), b"first old")
            self.assertEqual(second_target.read_bytes(), b"second old")
            self.assertFalse((root / "transaction").exists())

    def test_recovery_restores_an_interrupted_transaction_before_next_sync(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            transaction = root / "transaction"
            backup = transaction / "backups/0"
            target = root / "target.txt"
            backup.parent.mkdir(parents=True)
            backup.write_bytes(b"old")
            target.write_bytes(b"partially installed new")
            write_json(
                transaction / "journal.json",
                {
                    "schema_version": 1,
                    "targets": [
                        {
                            "target": "target.txt",
                            "backup": "backups/0",
                            "had_target": True,
                        }
                    ],
                },
            )

            sync._recover_incomplete_transaction(transaction, root)

            self.assertEqual(target.read_bytes(), b"old")
            self.assertFalse(transaction.exists())

    def test_sync_requires_clean_non_default_task_branch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            archive = root / "source.tar"
            write_sync_repo(repo_root, branch="main")
            standard_archive(archive)
            with self.assertRaisesRegex(ValueError, "task branch"):
                sync.sync_source(repo_root, "mengto-skills", archive)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            archive = root / "source.tar"
            write_sync_repo(repo_root)
            standard_archive(archive)
            (repo_root / "dirty.txt").write_text("dirty\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "clean"):
                sync.sync_source(repo_root, "mengto-skills", archive)

    def test_sync_rejects_invalid_or_duplicate_skill_frontmatter(self) -> None:
        invalid_skills = (
            b"# Missing frontmatter\n",
            b"---\nname: fixture\n---\n",
        )
        for skill in invalid_skills:
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                repo_root = root / "repo"
                archive = root / "source.tar"
                write_sync_repo(repo_root)
                standard_archive(archive, skill)
                with self.assertRaisesRegex(ValueError, "frontmatter|description"):
                    sync.sync_source(repo_root, "mengto-skills", archive)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            archive = root / "source.tar"
            write_sync_repo(repo_root)
            duplicate = SKILL.replace(b"Fixture skill.", b"Duplicate skill.")
            write_tar(
                archive,
                PREFIX,
                {
                    "LICENSE": LICENSE,
                    "skills/fixture/SKILL.md": SKILL,
                    "skills/duplicate/SKILL.md": duplicate,
                },
            )
            with self.assertRaisesRegex(ValueError, "duplicate skill"):
                sync.sync_source(repo_root, "mengto-skills", archive)

    def test_sync_rejects_missing_required_skill_and_changed_license(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            archive = root / "source.tar"
            write_sync_repo(repo_root)
            write_tar(archive, PREFIX, {"LICENSE": LICENSE})

            with self.assertRaisesRegex(ValueError, "missing required SKILL"):
                sync.sync_source(repo_root, "mengto-skills", archive)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            archive = root / "source.tar"
            write_sync_repo(repo_root)
            write_tar(
                archive,
                PREFIX,
                {
                    "LICENSE": b"changed license\n",
                    "skills/fixture/SKILL.md": SKILL,
                },
            )

            with self.assertRaisesRegex(ValueError, "license|notice|SHA-256|sha256"):
                sync.sync_source(repo_root, "mengto-skills", archive)

    def test_failed_late_validation_preserves_lock_tree_and_plugin(self) -> None:
        changed_skill = SKILL.replace(b"Fixture skill.", b"Changed skill.")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            archive = root / "source.tar"
            write_sync_repo(repo_root)
            standard_archive(archive, changed_skill)
            before = watched_snapshot(repo_root)

            with self.assertRaisesRegex(ValueError, "provenance|SHA-256|sha256"):
                sync.sync_source(repo_root, "mengto-skills", archive)

            self.assertEqual(watched_snapshot(repo_root), before)

    def test_sync_requires_renderer_and_post_render_safety_gates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            archive = root / "source.tar"
            write_sync_repo(repo_root, with_renderer=False)
            standard_archive(archive)
            before = watched_snapshot(repo_root)

            with self.assertRaisesRegex(ValueError, "renderer"):
                sync.sync_source(repo_root, "mengto-skills", archive)

            self.assertEqual(watched_snapshot(repo_root), before)

        private_path_marker = ("/" + "Users/example/private/project").encode()
        aws_key_marker = ("AKIA" + "ABCDEFGHIJKLMNOP").encode()
        dangerous_skill = (
            SKILL
            + b"\n"
            + private_path_marker
            + b"\nAWS access key: "
            + aws_key_marker
            + b"\n"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            archive = root / "source.tar"
            write_sync_repo(repo_root, locked_skill=dangerous_skill)
            standard_archive(archive, dangerous_skill)
            before = watched_snapshot(repo_root)

            with self.assertRaisesRegex(ValueError, "private|secret|safety"):
                sync.sync_source(repo_root, "mengto-skills", archive)

            self.assertEqual(watched_snapshot(repo_root), before)

    def test_success_replaces_tree_records_inventory_and_renders_when_available(self) -> None:
        changed_skill = SKILL.replace(b"# Fixture", b"# Reviewed fixture")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            archive = root / "source.tar"
            write_sync_repo(
                repo_root,
                locked_skill=changed_skill,
                installed_skill=SKILL,
                with_renderer=True,
            )
            standard_archive(archive, changed_skill, mode=0o755)

            report = sync.sync_source(repo_root, "mengto-skills", archive)

            installed = (
                repo_root
                / "design-stack/vendor/mengto-skills/skills/fixture/SKILL.md"
            )
            self.assertEqual(installed.read_bytes(), changed_skill)
            lock = json.loads(
                (repo_root / "design-stack/sources.lock.json").read_text(
                    encoding="utf-8"
                )
            )
            locked_skill = next(
                item
                for item in lock["sources"][0]["files"]
                if item["path"] == "skills/fixture/SKILL.md"
            )
            self.assertEqual(locked_skill["size"], len(changed_skill))
            self.assertEqual(locked_skill["mode"], "0755")
            self.assertEqual(locked_skill["sha256"], sha256_bytes(changed_skill))
            self.assertEqual(
                {item["path"] for item in lock["sources"][0]["files"]},
                {"LICENSE", "skills/fixture/SKILL.md"},
            )
            self.assertTrue(
                all(
                    {"path", "size", "mode", "sha256", "materialization"}
                    <= set(item)
                    for item in lock["sources"][0]["files"]
                )
            )
            rendered = (
                repo_root / "plugins/frontend-design-pack/render.txt"
            ).read_bytes()
            self.assertEqual(rendered, b"rendered:" + changed_skill)
            self.assertEqual(installed.stat().st_mode & 0o111, 0)
            self.assertTrue(report["plugin_rendered"])

    def test_sync_never_executes_executable_imported_script(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            archive = root / "source.tar"
            sentinel = root / "executed"
            write_sync_repo(repo_root)
            script = f"#!/bin/sh\ntouch {sentinel}\n".encode()
            write_tar(
                archive,
                PREFIX,
                {
                    "LICENSE": LICENSE,
                    "skills/fixture/SKILL.md": SKILL,
                    "skills/fixture/scripts/unsafe.sh": script,
                },
                modes={"skills/fixture/scripts/unsafe.sh": 0o755},
            )

            with self.assertRaisesRegex(ValueError, "provenance"):
                sync.sync_source(repo_root, "mengto-skills", archive)

            self.assertFalse(sentinel.exists())

    def test_mapped_source_file_remains_metadata_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            archive = root / "source.tar"
            write_sync_repo(repo_root, decision="mapped-to-official")
            standard_archive(archive)

            report = sync.sync_source(repo_root, "mengto-skills", archive)

            mapped_path = (
                repo_root
                / "design-stack/vendor/mengto-skills/skills/fixture/SKILL.md"
            )
            self.assertFalse(mapped_path.exists())
            lock = json.loads(
                (repo_root / "design-stack/sources.lock.json").read_text(
                    encoding="utf-8"
                )
            )
            locked_skill = next(
                item
                for item in lock["sources"][0]["files"]
                if item["path"] == "skills/fixture/SKILL.md"
            )
            self.assertEqual(locked_skill["materialization"], "metadata-only")
            self.assertTrue(report["plugin_rendered"])


if __name__ == "__main__":
    unittest.main()
