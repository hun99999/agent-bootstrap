# agent-bootstrap

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

## 마스터 프롬프트

아래를 Codex 또는 Claude Code에 그대로 붙여넣습니다. 에이전트는 이 레포를 clone한 위치에서 시작해야 합니다.

```text
이 레포에서 agent-bootstrap을 끝까지 세팅해줘.

먼저 AGENTS.md, README.md, docs/agent-setup-playbook.md, docs/global-guardrail-setup.md, docs/vibe-coding-guardrails.md, docs/agent-bootstrap-structure.md, docs/local-project-knowledge-template.md를 읽어라. 명령어, 패키지명, 설정 옵션, API 세부사항을 모르면 지어내지 말고 확인하거나 모른다고 말해라.

파일을 바꾸기 전에 git status --short --branch를 실행해라. 커밋되지 않은 변경이나 untracked 파일이 있으면 멈추고 어떻게 처리할지 물어봐라. 현재 하네스가 Codex인지 Claude Code인지 확인하고 내가 요청한 범위를 확인해라.

로컬 설정을 렌더링하기 전에 에이전트가 나를 어떤 이름으로 부를지 물어봐라. 현재 Codex와 Claude runtime이 실제로 지원하는 모델과 reasoning level을 확인하고, 최신 모델명이나 유료 플랜을 가정해 고정하지 말고 사용 가능한 선택을 상속해라. 선택한 이름은 로컬에만 둬라. 선택한 이름이나 그 이름이 들어간 렌더 결과는 커밋하지 마라.

docs/frontend-design-stack.md를 읽어라. tracked frontend-design-pack을 검증하고, Figma 인증 없이 사용 가능 여부만 보고하며, runtime plugin copy를 설치하거나 교체하기 전에 물어봐라. 설치가 승인되면 installed root를 별도로 검증하고 fresh task/session에서 discovery를 확인해라.

가장 작은 유효 범위를 골라라:
- 이미 Codex 안에 있다면 내가 Claude Code까지 명시적으로 요구하지 않는 한 Codex만 세팅해라.
- 이미 Claude Code 안에 있다면 내가 Codex까지 명시적으로 요구하지 않는 한 Claude Code만 세팅해라.
- 지원되는 하네스가 분명하지 않다면 어떤 하네스를 세팅할지 물어봐라.
- 애플리케이션 레포라면 프로젝트 guardrail을 적용하고 project-local knowledge guidance를 만들어라.
- 언급됐다는 이유만으로 선택 도구를 설치하지 마십시오.

선택한 범위를 끝까지 세팅해라:
- 이 레포에 문서화된 명령으로 shared core를 설치하거나 렌더링해라
- 현재 하네스의 문서화된 경로로만 upstream superpowers를 설치해라
- shared prompt나 metadata가 바뀌었다면 Claude plugin output을 다시 생성해라
- public default base skill은 karpathy-guidelines로 둬라
- hun-engineering-loop은 내가 명시적으로 승인하지 않는 한 Hun의 로컬 runtime wrapper로만 둬라
- chatgpt-collaboration-harness는 Claude Code에 설치하지 마라
- Obsidian, Lumin Repo Lens, dependency lint, strict type checks, cycle detection, complexity limits 같은 optional tool inventory를 읽기 전용으로 확인하고 required, recommended, optional, skipped로 분류한 뒤 설치 전에는 반드시 물어봐라
- private path, credential, MCP endpoint, auth state, browser profile, machine-specific trust setting을 tracked file에 넣지 마라
- tests와 scripts/audit_agent_stack.py를 포함해 이 레포의 실제 검증 명령을 실행해라
- duplicate helpers, hidden coupling, swallowed errors, fallback drift, unmanaged re-exports, fan-in/fan-out hotspots, weak tests, generated-output drift, private path leakage에 대해 post-write review를 실행해라
- 적절하면 작은 단위로 커밋하고, 변경 사항, 설치 내용, 실행한 명령, 검증 결과, 남은 리스크를 요약해라
```

Codex와 Claude Code를 위한 프로세스 중심 AI 코딩 환경 부트스트랩입니다.

`agent-bootstrap`은 새로 clone한 사용자가 `superpowers` workflow, role-based subagents, token-efficient 실행 습관, 자세한 설치 문서, `karpathy-guidelines` 기반 public-safe skill 모델을 함께 적용할 수 있게 해줍니다.

## 현재 지원 표면

Codex와 Claude Code만 first-class setup target입니다.

OpenCode와 OpenClaw는 legacy/reference material이며 active service target이 아닙니다. 예전 사용자의 감사나 마이그레이션을 위해 관련 파일이 git에 남아 있을 수는 있지만, 새 README, setup guide, 기본 audit은 그것들을 일반 설치 경로처럼 보여주면 안 됩니다.

이 범위는 공개 레포를 이해하기 쉽게 유지하기 위한 결정입니다.

- Codex는 `.codex` template, Codex installer, Codex 문서, optional Codex skill catalog guide를 사용합니다.
- Claude Code는 generated plugin bundle과 optional public-safe skill sync guide를 사용합니다.
- 공통 role prompt는 `AGENTS.md`, `agents/*.md`, `shared/agent-metadata.json`에 남깁니다.
- 프로젝트별/private workflow 지식은 공개해도 안전한 경우가 아니면 이 public repo 밖에 둡니다.

## Private Project Skills

auto-eva 같은 private project skill은 이 public repository에 커밋하지 않습니다. 실제 프로젝트별 skill은 Codex용 `~/.codex/skills`와 Claude Code용 `~/.claude/skills` 같은 local runtime home에 둡니다. 이 레포에는 templates and public-safe process guidance만 남기고, private access path, credential, auth state, browser profile, customer data, machine-specific trust setting은 넣지 않습니다.

## 핵심 모델

공개 기본값은 얇게 유지합니다.

- `karpathy-guidelines`가 public default base skill입니다. 에이전트가 가정을 숨기지 않고, 단순하게 구현하고, 넓은 diff를 피하고, 성공 기준을 검증 가능하게 만들도록 잡아줍니다.
- `superpowers`는 brainstorming, planning, TDD, debugging, verification, review에 쓰는 reusable workflow library입니다.
- `hun-engineering-loop`은 `karpathy-guidelines` 위에 Hun 로컬 운영 방식을 얹은 wrapper입니다. memory preflight, source-of-truth ordering, high-risk approval boundary, artifact-first execution, QA evidence contract를 추가합니다. Hun의 로컬 runtime에서는 유용하지만 public default install set에는 포함하지 않습니다.
- `chatgpt-collaboration-harness`는 Codex 쪽에서 ChatGPT Pro와 협업할 때 쓰는 선택 skill입니다. Claude Code에는 기본 설치하지 않습니다.

Memory와 이전 요약은 recall layer일 뿐 source of truth가 아닙니다. 충돌하면 현재 사용자 지시, repo docs, scripts, tests, `AGENTS.md`, 실제 runtime output이 이깁니다.

넓은 filesystem/tool access는 작업 능력이지 포괄 승인이 아닙니다. 데이터 삭제, credential 회전, 권한 변경, production, billing, external account, private material 공유, history rewrite, hook 우회, browser profile 변경, test 비활성화 전에는 멈추고 물어봐야 합니다.

## 빠른 시작

먼저 범위를 고릅니다. 실패하는 세팅 작업은 보통 한 번에 너무 많은 것을 건드릴 때 생깁니다. 두 번째 하네스, plugin stack, optional tool, project rule을 한 번에 바꾸지 말고, 가장 작은 유효 범위부터 검증합니다.

1. 레포를 clone하거나 pull합니다.

   ```bash
   git clone https://github.com/hun99999/agent-bootstrap.git
   cd agent-bootstrap
   git status --short --branch
   ```

2. 설치나 편집 전에 공통 규칙을 읽습니다.

   ```bash
   sed -n '1,220p' AGENTS.md
   sed -n '1,220p' docs/agent-setup-playbook.md
   ```

3. 현재 지원 하네스를 고릅니다.

   - Codex: [docs/README.codex.md](docs/README.codex.md)를 따릅니다.
   - Claude Code: [docs/README.claude.md](docs/README.claude.md)를 따릅니다.

4. 변경 전후로 검증합니다.

   ```bash
   python3 -m unittest discover -s tests -p 'test_*.py'
   python3 scripts/audit_agent_stack.py
   ```

5. 기존 clone을 업데이트한다면 먼저 fast-forward pull을 하고, 필요한 generated artifact를 다시 만든 뒤 같은 검증을 돌립니다.

   ```bash
   git pull --ff-only
   python3 scripts/render_claude_plugin.py --partner-name "<Name>"
   python3 -m unittest discover -s tests -p 'test_*.py'
   python3 scripts/audit_agent_stack.py
   ```

## 에이전트에게 맡길 수 있는 일

이 레포는 installer만이 아니라 운영 가이드입니다.

- 전역 기본값 설치: [docs/global-guardrail-setup.md](docs/global-guardrail-setup.md)를 사용해 Codex 또는 Claude Code user-level defaults에 공통 guardrail을 설치합니다.
- 프로젝트에 guardrail 적용: 대상 레포 안의 agent session에 [prompts/apply-vibe-coding-guardrails.md](prompts/apply-vibe-coding-guardrails.md)를 붙여넣습니다.
- guardrail이 있는 프로젝트에서 기능 작업 시작: feature, bugfix, refactor 전에 [prompts/start-with-vibe-coding-guardrails.md](prompts/start-with-vibe-coding-guardrails.md)를 붙여넣습니다.
- optional Codex skill 검토: [skills/README.md](skills/README.md)와 [docs/codex-skills.md](docs/codex-skills.md)를 읽고, 승인된 skill만 비교/설치하려면 [prompts/setup-codex-skills.md](prompts/setup-codex-skills.md)를 사용합니다.
- optional Claude Code skill 검토: [docs/claude-skills.md](docs/claude-skills.md)를 읽고 승인된 public-safe skill만 설치합니다.
- 이 bootstrap 업데이트/재점검: 새 변경을 pull한 뒤 또는 이 레포를 다시 audit하고 싶을 때 [prompts/update-agent-bootstrap.md](prompts/update-agent-bootstrap.md)를 붙여넣습니다.
- 이 레포 구조 이해: shared prompt, installer, generated plugin output, setup docs를 바꾸기 전에 [docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md)를 읽습니다.

선택 도구는 판단 후 사용합니다. Obsidian, Lumin Repo Lens, dependency lint, cycle detection, strict type checks, complexity limits는 대상 레포와 사용자 승인이 정당화할 때만 recommended 또는 installed가 됩니다.

## 대상 프로젝트용 Claude Code 프롬프트

Claude Code를 대상 프로젝트 레포 안에서 연 뒤 아래 프롬프트를 그대로 붙여넣습니다. 공개 URL을 참조하므로 개인 로컬 경로에 의존하지 않습니다.

```text
이 프로젝트에 agent-bootstrap 기반 vibe-coding guardrails를 적용해줘.

참조 레포:
- https://github.com/hun99999/agent-bootstrap

먼저 이 프로젝트에서 git status --short --branch를 실행해라. 커밋되지 않은 변경이나 untracked 파일이 있으면 멈추고 어떻게 처리할지 물어봐라. 승인 없이 stash, delete, overwrite, git add를 하지 마라.

그다음 이 프로젝트를 확인해라:
- AGENTS.md, CLAUDE.md, README.md, 기존 docs
- package.json, pyproject.toml, Cargo.toml, go.mod 또는 다른 language/tooling signal
- 실제 test, lint, type-check, build command
- source-of-truth helpers, types, schemas, public APIs, module boundaries, dependency direction, error boundaries, re-export/barrel policy, known hotspots

위 참조 레포의 docs를 URL에서 읽어라. 필요하면 이 프로젝트 밖에 read-only로 clone해라. 아래 파일을 source로 사용해라:
- docs/agent-setup-playbook.md
- docs/vibe-coding-guardrails.md
- docs/global-guardrail-setup.md
- docs/local-project-knowledge-template.md
- prompts/apply-vibe-coding-guardrails.md
- prompts/start-with-vibe-coding-guardrails.md

optional tool inventory는 가능하면 read-only evidence로만 실행해라. 참조 레포를 clone했다면 이 프로젝트 root를 대상으로 실행해라:
- python3 <agent-bootstrap-clone>/scripts/inventory_optional_tools.py --repo-root .
- python3 <agent-bootstrap-clone>/scripts/inventory_optional_tools.py --repo-root . --json

그 스크립트를 쓸 수 없다면 정확히 한계를 설명하고 직접 조사로 계속해라. 선택 도구를 자동 설치하지 마라. Do not install optional tools automatically. Obsidian, Lumin Repo Lens, dependency lint, strict type checks, cycle detection, complexity limits를 required, recommended, optional, skipped로 분류하고 설치 승인 전에는 묻는다.

이 프로젝트에 필요한 가장 작은 guardrail만 적용해라:
- 이 프로젝트가 이미 사용하는 agent guidance를 추가하거나 업데이트한다
- docs/local-project-knowledge-template.md를 바탕으로 project structure index를 만든다
- source-of-truth helpers, types, schemas, public APIs, module boundaries, dependency direction, error boundaries, re-export policy, test strategy, known hotspots, decisions를 기록한다
- local evidence artifact가 생길 수 있을 때만 .audit/을 .gitignore에 추가한다
- personal vault path, private path, credential, MCP endpoint, auth state, browser profile, machine-specific trust setting을 커밋하지 않는다

TS/JS-heavy project이고 내가 Lumin Repo Lens를 승인하면 evidence tool로만 사용해라:
- structural claim에는 evidence가 필요하다
- absence claim에는 scan range가 필요하다
- evidence가 부분적이면 "not observed in this scan range"라고 말한다
- pre-write intent는 names, shapes, files, dependencies, plannedTypeEscapes를 사용한다
- post-write machine evidence는 type escapes, unexpected files, scan range, confidence changes로 제한된다
- duplicate helpers, dependency drift, public API drift, re-export drift는 direct evidence가 필요한 manual review claim이다

behavior change에는 TDD를 사용해라. 변경 후 이 프로젝트의 실제 verification command와 post-write review를 실행해라. 변경 파일, 실행한 명령, 검증 결과, optional tool skipped/recommended, 남은 리스크를 보고해라.
```

## 프롬프트별 사용 시점

- `prompts/setup-codex-current-harness.md`: Codex 안에서 현재 Codex harness에 shared core를 적용할 때 사용합니다.
- `prompts/setup-claude-current-harness.md`: Claude Code 안에서 Claude plugin과 shared role prompt를 세팅할 때 사용합니다.
- `prompts/setup-shared-core.md`: 대상 환경이 불분명하고 설치 없이 shared prompt guidance만 확인하는 것이 안전할 때 사용합니다.
- `prompts/setup-codex-skills.md`: optional Codex skill catalog를 확인하고 `~/.codex/skills`와 비교한 뒤 승인된 skill만 설치할 때 사용합니다.
- `prompts/apply-vibe-coding-guardrails.md`: structure map, edge-case-first tests, dependency-boundary checks, local project knowledge가 필요한 애플리케이션 레포에서 사용합니다.
- `prompts/start-with-vibe-coding-guardrails.md`: 프로젝트에 이미 guardrail이 있고 일반 feature, bugfix, refactor를 시작할 때 사용합니다.
- `prompts/update-agent-bootstrap.md`: 이 레포의 새 변경을 pull, render, install, audit, document, review해야 할 때 사용합니다.

예전 OpenCode/OpenClaw 실험용 prompt가 git에 남아 있을 수 있지만 현재 지원 setup path에는 포함하지 않습니다.

## Guardrail이 강제하는 것

Guardrail은 agent coding이 망각과 구조적 난잡함으로 흐르지 않게 하기 위한 것입니다.

- Pre-write lens: 편집 전에 module boundaries, dependency direction, public APIs, helpers, types, shapes, re-exports, tests, error boundaries, known hotspots를 확인합니다.
- TDD write gate: edge case와 failure path test를 먼저 쓰고 기대한 실패를 확인한 뒤 가장 작은 구현 변경을 합니다.
- Coupling control: hidden imports, initialization-order contracts, duplicate shapes, unreviewed barrels, fan-in/fan-out hotspots를 피합니다.
- Error discipline: 에러를 조용히 삼키지 않고, 문서화된 요구가 아니면 fallback behavior를 추가하지 않으며, error handling은 명시적 boundary에 둡니다.
- Test discipline: behavior와 side effect를 검증하고, mock은 external boundary에만 둡니다.
- Privacy discipline: personal vault path, private project path, credential, MCP endpoint, auth state, browser profile, machine-specific trust setting을 커밋하지 않습니다.
- Skill discipline: skill을 단순 prose가 아니라 tested process code로 취급합니다.

## 선택 도구와 설치 정책

Optional tool은 workflow를 보조해야지 workflow 자체가 되면 안 됩니다.

- Obsidian은 레포 구조가 커서 반복 재탐색 비용이 클 때 private project wiki로 유용합니다.
- Lumin Repo Lens는 TS/JS 레포에서 AST-backed evidence로 duplicate helpers, hidden coupling, re-export drift, fan-in/fan-out hotspots를 찾을 때 유용합니다.
- Dependency lint, cycle detection, strict type checks, complexity limits, file/function size limits는 강력하지만 실제 tooling change입니다.

언급됐다는 이유만으로 선택 도구를 설치하지 않습니다. 먼저 현재 환경을 조사하고, required/recommended/optional/skipped를 설명하고, 설치 전 승인받고, package name이나 official source를 확인하고, 레포에는 project-safe usage guidance만 남깁니다.

## 설치 가이드

- Codex: [docs/README.codex.md](docs/README.codex.md)
- Claude Code: [docs/README.claude.md](docs/README.claude.md)
- Codex·Claude Code 프론트엔드 디자인 팩: [docs/frontend-design-stack.md](docs/frontend-design-stack.md)
- Codex skills: [docs/codex-skills.md](docs/codex-skills.md)
- Claude Code skills: [docs/claude-skills.md](docs/claude-skills.md)

## 아키텍처

레포는 네 층으로 나뉩니다.

- shared core
  - `AGENTS.md`
  - `agents/*.md`
  - `shared/agent-metadata.json`
  - common process-first constitution and role prompt bodies
- reviewed frontend design source
  - `design-stack/`
  - source registry, immutable lock, provenance, router contract, reviewed vendored material
- first-class harness adapters
  - `.codex/`
  - `.claude-plugin/`
  - `plugins/process-first-agents/`
  - `plugins/frontend-design-pack/`
- reusable public-safe skills
  - `skills/karpathy-guidelines/`
  - `skills/chatgpt-collaboration-harness/`
  - `skills/hun-engineering-loop/`
  - `skills/_template/`

shared core는 operating model을 한 번만 정의합니다. Codex와 Claude Code adapter는 그 core를 각 runtime의 native format으로 변환합니다. 자세한 project-local structure map, update flow, source-of-truth boundary, generated-artifact policy는 [docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md)를 읽습니다.

## Superpowers 통합

이 bootstrap은 upstream `obra/superpowers`를 중심으로 둡니다.

- Codex는 Codex App curated Superpowers plugin을 사용할 수 있습니다.
- Codex installer는 local skill discovery가 필요한 환경을 위해 manual ~/.codex/superpowers fallback도 지원합니다.
- Claude Code는 Anthropic official plugin marketplace에서 upstream `superpowers`를 설치하고, 이 레포의 generated `process-first-agents` plugin을 설치합니다.

Codex App curated Superpowers plugin과 manual fallback을 동시에 켜면 중복 skill 항목이 생길 수 있습니다. 의도한 게 아니라면 discovery path는 하나만 사용합니다.

## 이 레포 유지보수

이 bootstrap을 바꾸기 전에는 [docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md)를 repo-local map으로 사용합니다.

- Shared behavior는 `AGENTS.md`와 `agents/*.md`에서 바꿉니다.
- Role metadata는 `shared/agent-metadata.json`에서 바꿉니다.
- Codex 설치 동작은 `.codex/install.py`에서 바꿉니다.
- Claude plugin rendering은 `scripts/render_claude_plugin.py`에서 바꿉니다.
- reviewed frontend design source와 routing은 `design-stack/`에서 바꿉니다.
- frontend design plugin은 `scripts/render_frontend_design_plugin.py`로 생성하며
  `plugins/frontend-design-pack/`을 손으로 편집하지 않습니다.
- Shared prompt나 metadata가 바뀌면 `python3 scripts/render_claude_plugin.py --partner-name "<Name>"`로 Claude plugin output을 다시 만듭니다.
- 디자인 변경은 전체 테스트와 audit에 더해
  `python3 scripts/validate_frontend_design_stack.py --repo-root .`로 검증합니다.
- Generated Claude plugin output은 항상 sync합니다. Generated Claude plugin agent를 손으로 편집하지 않습니다.

## Pull And Update Workflow

기존 clone에서는 다음 순서로 업데이트합니다.

```bash
git status --short --branch
git pull --ff-only
python3 scripts/render_claude_plugin.py --partner-name "<Name>"
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/audit_agent_stack.py
```

업데이트가 `design-stack/`이나 `plugins/frontend-design-pack/`을 건드리면
[docs/frontend-design-stack.md](docs/frontend-design-stack.md)와
[prompts/update-agent-bootstrap.md](prompts/update-agent-bootstrap.md)의 조건부 절차를 따릅니다.
pull 후에는 live runtime root를 확인하고 검증합니다. local Codex marketplace라면 tracked
plugin root일 수 있지만 cached install은 별도 위치일 수 있습니다. cached install 교체는
별도 승인을 받은 뒤 진행하고, 확인한 root를 검증한 다음 fresh task 또는 session에서
discovery를 확인합니다.

`git status --short --branch`가 깨끗하지 않다면 pull 전에 local work를 commit할지, WIP branch로 옮길지, 그대로 둘지 결정해야 합니다. 사용자 작업을 자동으로 stash하거나 overwrite하지 않습니다.

## Agent Stack Audit

업데이트 전후에 로컬 Codex, Claude Code, Superpowers state, generated Claude plugin bundle을 확인하려면 다음을 실행합니다.

```bash
python3 scripts/audit_agent_stack.py
```

기본 audit은 offline/read-only입니다. npm과 원격 git 기준 최신 drift까지 확인하려면 `--online`을 붙입니다. OpenCode는 더 이상 기본 지원 표면으로 audit하지 않습니다.

## Compatibility Notes

예전 OpenCode/OpenClaw 관련 docs나 prompt가 history와 migration review 목적으로 남아 있을 수 있습니다. 현재 public setup path가 아닙니다. 사용자가 명시적으로 support 복원을 요청하지 않는 한 확장하지 않습니다.

## 테스트

Installer, metadata, README expectation, skill catalog expectation, generated plugin output은 Python `unittest`로 검증합니다.

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

README, skills, prompts, docs, generated plugin output, setup script를 바꿨다면 publish 전에 `python3 scripts/check_private_paths.py`도 실행합니다.
