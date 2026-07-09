import fnmatch
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DESIGN_STACK = REPO_ROOT / "design-stack"
ROUTING_PATH = DESIGN_STACK / "routing.json"
ROUTING_CASES_PATH = DESIGN_STACK / "evals/routing-cases.json"
TRIGGER_CASES_PATH = DESIGN_STACK / "evals/trigger-cases.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class FrontendDesignRouterContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.routing = load_json(ROUTING_PATH)
        cls.routing_cases = load_json(ROUTING_CASES_PATH)
        cls.trigger_cases = load_json(TRIGGER_CASES_PATH)
        cls.lock = load_json(DESIGN_STACK / "sources.lock.json")
        cls.provenance = load_json(DESIGN_STACK / "provenance.json")

    def test_router_exposes_one_native_skill_and_six_modes(self) -> None:
        self.assertEqual(self.routing["schema_version"], 1)
        self.assertEqual(self.routing["native_skills"], ["frontend-design"])
        self.assertEqual(
            set(self.routing["modes"]),
            {"shape", "explore", "implement", "review", "copy", "harden"},
        )
        self.assertFalse((REPO_ROOT / "skills/frontend-design").exists())

    def test_every_mode_reports_route_and_uses_small_reference_sets(self) -> None:
        available = set(self.routing["references"])
        report_fields = {"mode", "target_surface", "loaded_references"}
        for name, mode in self.routing["modes"].items():
            with self.subTest(mode=name):
                self.assertTrue(mode["description"])
                self.assertTrue(report_fields <= set(mode["required_outputs"]))
                references = mode["default_reference_keys"]
                self.assertEqual(len(references), len(set(references)))
                self.assertLessEqual(
                    len(references),
                    self.routing["selection_policy"]["max_default_references"],
                )
                self.assertTrue(set(references) <= available)

    def test_pressure_cases_cover_each_mode_and_are_not_trigger_fixtures(self) -> None:
        cases = self.routing_cases["cases"]
        available = set(self.routing["references"])
        self.assertEqual(
            {case["expected_mode"] for case in cases}, set(self.routing["modes"])
        )
        self.assertNotEqual(ROUTING_CASES_PATH, TRIGGER_CASES_PATH)
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["target_surface"])
                self.assertTrue(case["loaded_reference_keys"])
                self.assertLessEqual(
                    len(case["loaded_reference_keys"]),
                    self.routing["selection_policy"]["max_loaded_references"],
                )
                self.assertTrue(set(case["loaded_reference_keys"]) <= available)
                self.assertLessEqual(
                    len(case["inspiration_sources"]),
                    self.routing["selection_policy"]["max_inspiration_sources"],
                )
                for source in case["inspiration_sources"]:
                    self.assertTrue(source["label"])
                    self.assertIn(
                        source["authority"],
                        {"official", "procedural-guidance", "third-party-analysis"},
                    )

    def test_trigger_cases_include_positive_and_negative_boundaries(self) -> None:
        cases = self.trigger_cases["cases"]
        outcomes = {case["should_trigger"] for case in cases}
        self.assertEqual(outcomes, {True, False})
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["request"])
                if case["should_trigger"]:
                    self.assertIn(case["expected_mode"], self.routing["modes"])
                else:
                    self.assertIsNone(case["expected_mode"])

    def test_source_precedence_is_explicit_and_project_first(self) -> None:
        self.assertEqual(
            self.routing["source_precedence"],
            [
                "current-user-instruction-and-approved-scope",
                "verified-project-behavior-and-product-evidence",
                "project-components-tokens-figma-and-design-md",
                "accessibility-legal-compliance-and-brand-requirements",
                "vercel-official-guidance",
                "mengto-procedural-and-visual-guidance",
                "third-party-design-md-inspiration",
                "router-defaults",
            ],
        )

    def test_mode_and_source_safety_policies_are_machine_readable(self) -> None:
        modes = self.routing["modes"]
        self.assertEqual(modes["shape"]["edit_policy"], "read-only-unless-explicit")
        self.assertEqual(modes["review"]["edit_policy"], "read-only-unless-explicit")
        self.assertTrue(modes["implement"]["requires_tdd"])
        self.assertEqual(
            modes["copy"]["allowed_change_scope"],
            ["copy", "accessible-names", "directly-required-markup"],
        )
        policy = self.routing["selection_policy"]
        self.assertEqual(policy["external_side_effect_material"], "explicit-use-only")
        self.assertEqual(policy["open_design"], "explicit-demand-only")
        self.assertEqual(policy["max_inspiration_sources"], 3)
        self.assertTrue(policy["require_authority_labels"])

    def test_design_md_validation_contract_is_pinned_in_repo_and_plugin(self) -> None:
        package = load_json(
            DESIGN_STACK / "vendor/google-design-md/packages/cli/package.json"
        )
        packaged_routing = load_json(
            REPO_ROOT
            / "plugins/frontend-design-pack/skills/frontend-design/references/routing.json"
        )
        for label, routing in (
            ("repository", self.routing),
            ("packaged plugin", packaged_routing),
        ):
            with self.subTest(location=label):
                contract = routing["design_md_validation"]
                self.assertEqual(contract["package_spec"], "@google/design.md@0.3.0")
                self.assertEqual(contract["binary"], "designmd")
                self.assertEqual(contract["arguments"], ["lint", "DESIGN.md"])
                self.assertEqual(
                    contract["fallback_command"],
                    [
                        "npx",
                        "--package=@google/design.md@0.3.0",
                        "designmd",
                        "lint",
                        "DESIGN.md",
                    ],
                )
                self.assertEqual(
                    contract["authority_order"],
                    [
                        "user-approved-project-pinned-contract",
                        "project-committed-pinned-contract",
                        "frontend-design-pack-pinned-fallback",
                        "versionless-imported-examples-non-authoritative",
                    ],
                )
                self.assertEqual(
                    contract["unavailable_policy"],
                    "report-unverified-never-substitute-unpinned",
                )

        self.assertEqual(package["name"], "@google/design.md")
        self.assertEqual(package["version"], "0.3.0")
        self.assertEqual(package["bin"]["designmd"], "./dist/index.js")

    def test_authored_guidance_overrides_unpinned_imported_design_md_commands(self) -> None:
        quality = (
            DESIGN_STACK / self.routing["references"]["quality-gates"]
        ).read_text(encoding="utf-8")
        precedence = (
            DESIGN_STACK / self.routing["references"]["source-precedence"]
        ).read_text(encoding="utf-8")
        self.assertIn(
            'npx --package="@google/design.md@0.3.0" designmd lint DESIGN.md',
            quality,
        )
        self.assertIn("Ask before downloading or executing", quality)
        self.assertIn("versionless commands in imported DESIGN.md", precedence)
        self.assertIn("non-authoritative", precedence)

    def test_vercel_runtime_skills_are_selected_only_for_applicable_gates(self) -> None:
        contract = load_json(DESIGN_STACK / "vercel-runtime-skills.json")
        quality = (
            DESIGN_STACK / self.routing["references"]["quality-gates"]
        ).read_text(encoding="utf-8")
        router_skill = (DESIGN_STACK / "router/SKILL.md").read_text(encoding="utf-8")

        self.assertEqual(
            [skill["gate"] for skill in contract["skills"]],
            [
                "react-performance",
                "component-composition",
                "react-view-transitions",
            ],
        )
        for skill in contract["skills"]:
            requirement = skill["external_runtime_requirement"]
            self.assertEqual(requirement["capability"], f"skill:{skill['name']}")
            self.assertEqual(requirement["resolution"], "discover-installed-skill")
            self.assertTrue(skill["use_condition"].startswith("Use only"))
        for marker in (
            "applicable gate only",
            "Status: unavailable",
            "Result: not applied",
            "never claim that unavailable guidance was applied",
        ):
            self.assertIn(marker, quality)
        self.assertIn("vercel_runtime_skills", router_skill)
        self.assertIn("exact installed skill name", router_skill)

    def test_open_design_requires_explicit_demand_and_package_selection(self) -> None:
        cases = load_json(DESIGN_STACK / "evals/open-design-cases.json")["cases"]
        by_id = {case["id"]: case for case in cases}

        self.assertEqual(
            by_id["generic-best-references"]["expected_action"],
            "ignore-open-design",
        )
        self.assertEqual(
            by_id["cached-without-explicit-demand"]["expected_action"],
            "ignore-open-design",
        )
        self.assertEqual(
            by_id["named-without-selection"]["expected_action"],
            "list-up-to-three-and-confirm-slug",
        )
        self.assertEqual(
            by_id["explicit-slug"]["expected_action"],
            "fetch-selected-package",
        )
        self.assertEqual(
            by_id["delegated-selection"]["expected_action"],
            "select-report-and-fetch-one",
        )
        self.assertTrue(
            all(
                case["explicit_demand"]
                for case in cases
                if case["expected_action"] != "ignore-open-design"
            )
        )

        self.assertEqual(
            self.routing["references"]["open-design"],
            "router/references/open-design.md",
        )
        router_skill = (DESIGN_STACK / "router/SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "references/open-design.md",
            "exact slug",
            "selection authority",
            "cache presence never counts as demand",
        ):
            self.assertIn(marker, router_skill)

    def test_every_approved_mengto_entry_resolves_without_native_skill_sprawl(self) -> None:
        decisions = {
            (record["source_id"], record["upstream_path"]): record["decision"]
            for record in self.provenance["records"]
        }
        rules = self.routing["mengto_resolution_rules"]
        approved = [
            entry
            for entry in self.lock["catalogs"]["mengto_skills"]
            if decisions[(entry["source_id"], entry["path"])]
            in {"included", "mapped-to-official"}
        ]
        self.assertEqual(len(approved), 95)
        for entry in approved:
            matching = [
                rule
                for rule in rules
                if fnmatch.fnmatchcase(entry["path"], rule["path_pattern"])
            ]
            with self.subTest(path=entry["path"]):
                self.assertTrue(matching, "approved catalog entry has no router resolution")
                selected = matching[0]
                self.assertIn(
                    selected["delivery"],
                    {"reference-corpus", "official-mapping", "explicit-use-only"},
                )
                if decisions[(entry["source_id"], entry["path"])] == "mapped-to-official":
                    self.assertEqual(selected["delivery"], "official-mapping")

        risky_names = {
            "elevenlabs-tts",
            "netlify-deploy",
            "x-bookmark-quote-posts",
            "aura-asset-images",
            "unsplash-asset-images",
        }
        for entry in approved:
            if entry["name"] not in risky_names:
                continue
            selected = next(
                rule
                for rule in rules
                if fnmatch.fnmatchcase(entry["path"], rule["path_pattern"])
            )
            self.assertEqual(selected["delivery"], "explicit-use-only")

    def test_router_skill_is_concise_safe_and_explains_runtime_contract(self) -> None:
        skill_path = DESIGN_STACK / "router/SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        self.assertLessEqual(len(text.splitlines()), 120)
        for phrase in (
            "Classify the request",
            "primary project evidence",
            "smallest sufficient",
            "authority and scope",
            "Mode:",
            "Target surface:",
            "Loaded references:",
            "Verification actually run:",
        ):
            self.assertIn(phrase, text)
        for forbidden in ("git clone", "curl |", "plugin install", "npm install -g"):
            self.assertNotIn(forbidden, text)

    def test_authored_references_and_templates_cover_quality_contract(self) -> None:
        for relative_path in self.routing["references"].values():
            self.assertTrue((DESIGN_STACK / relative_path).is_file(), relative_path)

        precedence = (DESIGN_STACK / self.routing["references"]["source-precedence"]).read_text(
            encoding="utf-8"
        )
        quality = (DESIGN_STACK / self.routing["references"]["quality-gates"]).read_text(
            encoding="utf-8"
        )
        for marker in ("Current user instruction", "Project-owned", "Third-party"):
            self.assertIn(marker, precedence)
        for marker in (
            "reachable states",
            "keyboard",
            "reduced motion",
            "compact",
            "localization",
            "successful build is not visual verification",
            "React",
            "DESIGN.md",
        ):
            self.assertIn(marker, quality)

        templates = {
            "DESIGN.md.template": ("User", "Outcome", "States", "Decisions"),
            "product-brief.md": ("User", "Job", "Success signal", "Non-goals"),
            "design-decision.md": ("Decision", "Alternatives", "Evidence", "Risks"),
        }
        for filename, fields in templates.items():
            text = (DESIGN_STACK / "templates" / filename).read_text(encoding="utf-8")
            for field in fields:
                self.assertIn(field, text)


if __name__ == "__main__":
    unittest.main()
