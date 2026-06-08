# agent-bootstrap

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

## 마스터 프롬프트

아래를 Codex, Claude Code, OpenCode 또는 다른 코딩 에이전트에게 그대로 붙여넣습니다. 에이전트는 이 레포를 clone한 위치에서 시작해야 합니다.

```text
이 레포를 기준으로 agent-bootstrap을 처음부터 끝까지 세팅해줘.

먼저 AGENTS.md, README.md, docs/agent-setup-playbook.md, docs/global-guardrail-setup.md, docs/vibe-coding-guardrails.md, docs/agent-bootstrap-structure.md, docs/local-project-knowledge-template.md를 읽어라. 명령어, 패키지 이름, 설정 옵션, API 세부사항을 지어내지 마라.

파일을 바꾸기 전에 git status --short --branch를 실행해라. 커밋되지 않은 변경이나 untracked 파일이 있으면 멈추고 어떻게 처리할지 물어봐라. 현재 하네스가 Codex, Claude Code, OpenCode, 기타 중 무엇인지 확인하고 내가 요청한 범위를 확인해라.

가장 작은 유효 범위를 선택해라:
- 이미 Codex, Claude Code, OpenCode 안에 있다면 내가 명시적으로 다른 하네스를 요구하지 않는 한 현재 하네스만 세팅해라.
- 하네스가 불명확하면 shared-core-only를 적용해라.
- 애플리케이션 레포라면 project guardrail을 적용하고 project-local knowledge guidance를 만들어라.
- 언급됐다는 이유만으로 선택 도구를 설치하지 마십시오.

선택한 범위를 처음부터 끝까지 세팅해라:
- 이 레포에 문서화된 명령으로 shared core를 설치하거나 렌더링해라.
- Superpowers는 이 레포에 문서화된 경로로만 업데이트해라.
- shared prompt나 metadata가 바뀌었다면 Claude plugin output을 재생성해라.
- Obsidian, Lumin Repo Lens, dependency lint, strict type checks, cycle detection, complexity limits 같은 선택 도구를 inventory하고 required, recommended, optional, skipped 중 하나로 분류해라. 어떤 것도 설치 전에는 반드시 물어봐라.
- private path, credential, MCP endpoint, auth state, browser profile, machine-specific trust setting을 tracked file에 넣지 마라.
- 테스트와 scripts/audit_agent_stack.py를 포함해 이 레포의 실제 검증 명령을 실행해라.
- duplicate helper, hidden coupling, swallowed error, fallback drift, unmanaged re-export, fan-in/fan-out hotspot, weak test, generated-output drift, private path leakage를 post-write review로 확인해라.
- 적절하다면 작은 단위로 커밋하고, 무엇을 바꿨는지, 무엇을 설치했는지, 실행한 명령, 검증 결과, 남은 리스크를 요약해라.
```

Codex, Claude Code, OpenCode를 위한 프로세스 중심 AI 코딩 환경 부트스트랩입니다.

`agent-bootstrap`은 최신 AI 코딩 도구에 공통으로 적용할 수 있는 `superpowers` 워크플로우, 역할 기반 서브에이전트, 토큰 효율적인 실행 방식, 다국어 설치 문서를 제공합니다.

> 이 문서는 `README.md`의 한국어 번역본입니다. 기준 문서는 영어판입니다.

## 왜 agent-bootstrap을 써야 하나?

- Codex, Claude Code, OpenCode 각각에 따로 프롬프트 스택을 유지하지 않고, 하나의 `superpowers` 기반 워크플로우를 공유할 수 있습니다.
- 계획, 구현, 리뷰, 검증, 릴리스 역할을 서브에이전트와 공통 프롬프트 코퍼스로 분리해 일관된 협업 흐름을 유지할 수 있습니다.
- 범위가 명확한 작업, 짧은 handoff, 재사용 가능한 skill 중심으로 흐르게 해 토큰 낭비를 줄이는 process-first 실행 모델을 제공합니다.
- 하나의 범용 installer 억지 적용이 아니라 각 하네스의 네이티브 방식에 맞춘 어댑터를 제공합니다.
  - Codex는 managed `.codex` 설정과 latest `superpowers`
  - Claude Code는 marketplace entry와 generated agent plugin package
  - OpenCode는 generated agents와 native plugin wiring
- credential, private MCP endpoint, 개인 경로, 머신별 trust state를 public baseline에 넣지 않도록 설계되어 있습니다.
- 영어, 한국어, 일본어, 중국어 간체 문서를 같이 제공해 동일한 레포에서 온보딩할 수 있습니다.

## 에이전트에게 맡길 수 있는 일

이 레포는 단순 installer가 아니라 에이전트 운영 가이드로 쓰는 것이 핵심입니다.

- 전역 기본값 설치: [docs/global-guardrail-setup.md](docs/global-guardrail-setup.md)를 사용해 Codex, Claude Code, OpenCode의 user-level defaults에 공통 guardrail을 설치합니다.
- 프로젝트에 guardrail 적용: 대상 레포 안에서 [prompts/apply-vibe-coding-guardrails.md](prompts/apply-vibe-coding-guardrails.md)를 에이전트에게 붙여넣습니다.
- guardrail이 있는 프로젝트에서 기능 작업 시작: 기능 추가, 버그 수정, 리팩터링 전에 [prompts/start-with-vibe-coding-guardrails.md](prompts/start-with-vibe-coding-guardrails.md)를 붙여넣습니다.
- 이 bootstrap 업데이트/재점검: 새 변경을 pull한 뒤 또는 이 레포 자체를 다시 점검하고 싶을 때 [prompts/update-agent-bootstrap.md](prompts/update-agent-bootstrap.md)를 사용합니다.
- 이 레포 자체의 구조 설명: shared prompt, installer, generated plugin output, setup docs를 수정하기 전에 [docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md)를 읽습니다.

선택 도구는 판단 후 사용합니다. Obsidian, Lumin Repo Lens, dependency lint, cycle detection, strict type checks, complexity limits는 대상 레포와 사용자 승인으로 필요성이 확인될 때만 추천하거나 설치합니다.

## 빠른 시작

먼저 범위를 고릅니다. 에이전트 세팅 실패는 보통 한 번에 너무 많이 하려 할 때 생깁니다. 새 하네스, 새 플러그인, 새 provider, 레포 워크플로우를 동시에 바꾸지 말고, 가장 작은 유효 범위를 먼저 적용하고 검증한 뒤 넓힙니다.

1. 이 머신의 앞으로 열릴 Codex, Claude Code, OpenCode 세션에 기본 규칙을 넣고 싶다면 [docs/global-guardrail-setup.md](docs/global-guardrail-setup.md)를 따릅니다.
2. 다른 애플리케이션 레포에 같은 규칙을 적용하고 싶다면 그 레포에서 [prompts/apply-vibe-coding-guardrails.md](prompts/apply-vibe-coding-guardrails.md)를 붙여넣습니다.
3. 이미 guardrail이 있는 레포에서 기능 추가, 버그 수정, 리팩터링을 시작하려면 [prompts/start-with-vibe-coding-guardrails.md](prompts/start-with-vibe-coding-guardrails.md)를 사용합니다.
4. 이 bootstrap 레포가 바뀌어서 다시 적용, 점검, 고도화를 맡기려면 [prompts/update-agent-bootstrap.md](prompts/update-agent-bootstrap.md)를 사용합니다.

## 프롬프트별 사용 시점

- `prompts/setup-codex-current-harness.md`: Codex 안에서 현재 Codex 하네스에 shared core만 적용할 때 사용합니다.
- `prompts/setup-claude-current-harness.md`: Claude Code 안에서 Claude plugin과 공통 역할 프롬프트를 세팅할 때 사용합니다.
- `prompts/setup-opencode-current-harness.md`: OpenCode 안에서 generated agents와 native plugin wiring을 적용할 때 사용합니다.
- `prompts/setup-shared-core.md`: 대상 환경이 애매하고 shared prompt/skills 레이어만 적용하는 것이 가장 안전할 때 사용합니다.
- `prompts/apply-vibe-coding-guardrails.md`: 애플리케이션 레포에 구조 지도, edge-case-first 테스트, 의존 경계 점검, project-local knowledge를 넣을 때 사용합니다.
- `prompts/start-with-vibe-coding-guardrails.md`: 이미 프로젝트 지도와 guardrail workflow가 있는 레포에서 일상적인 기능/버그/리팩터링 작업을 시작할 때 사용합니다.
- `prompts/update-agent-bootstrap.md`: 이 레포 자체의 새 변경을 pull, render, install, audit, 문서화, 리뷰할 때 사용합니다.

## Guardrail이 강제하는 것

이 guardrail의 목적은 에이전트 코딩이 매 세션 기억을 잃고 구조를 망가뜨리는 문제를 줄이는 것입니다.

- Pre-write lens: 수정 전 module boundary, dependency direction, public API, helper, type, shape, re-export, test, error boundary, hotspot을 확인합니다.
- TDD write gate: 빈 입력, null/missing, 경계값, 실패 경로, side effect, 동시성 같은 edge case 테스트를 먼저 쓰고 실패를 확인한 뒤 구현합니다.
- 결합도 제어: 숨은 import, 초기화 순서 계약, 중복 shape, 방치된 barrel/re-export, fan-in/fan-out hotspot을 피합니다.
- 에러 규율: 에러를 조용히 삼키지 않고, 문서화된 요구사항이 아닌 fallback을 추가하지 않으며, 에러 처리는 명시적 경계에 둡니다.
- 테스트 규율: 문자열이나 함수 이름이 아니라 행동과 side effect를 검증하고, mock은 외부 경계에만 둡니다.
- 개인정보 경계: 개인 vault 경로, private project path, credential, MCP endpoint, auth state, browser profile, machine-specific trust setting은 커밋하지 않습니다.

## 선택 도구와 설치 정책

선택 도구는 workflow를 돕는 보조 수단이지 workflow 자체가 아닙니다.

- Obsidian은 레포 구조가 커서 매번 다시 파악하는 비용이 클 때 private project wiki로 유용합니다.
- Lumin Repo Lens는 TS/JS 레포에서 AST 기반 증거로 duplicate helper, hidden coupling, re-export drift, fan-in/fan-out hotspot을 찾을 때 유용합니다.
- Dependency lint, cycle detection, strict type checks, complexity limits, file/function size limits는 강력하지만 실제 tooling 변경입니다.

언급됐다는 이유만으로 선택 도구를 설치하지 않습니다. 먼저 현재 환경을 inventory하고, 해당 도구가 required/recommended/optional/skipped 중 무엇인지 설명하고, 설치 전 승인을 받고, package name 또는 official source를 검증하고, 레포에는 project-safe usage guidance만 남깁니다.

## 이 레포 유지보수

이 bootstrap을 바꾸기 전에는 [docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md)를 repo-local map으로 읽습니다.

- 공통 행동 규칙은 `AGENTS.md`와 `agents/*.md`에서 바꿉니다.
- 역할 metadata는 `shared/agent-metadata.json`에서 바꿉니다.
- Codex 설치 동작은 `.codex/install.py`에서 바꿉니다.
- OpenCode 설치 동작은 `.opencode/install.py`에서 바꿉니다.
- Claude plugin render 동작은 `scripts/render_claude_plugin.py`에서 바꿉니다.
- shared prompt나 metadata를 바꾸면 `python3 scripts/render_claude_plugin.py --partner-name "<Name>"`로 Claude plugin output을 재생성합니다.
- `python3 -m unittest discover -s tests -p 'test_*.py'`와 `python3 scripts/audit_agent_stack.py`로 검증합니다.

## 이 레포가 하는 일

이 레포는 특정 도구 하나에 묶이지 않고, 여러 코딩 하네스에 설치할 수 있는 공통 운영체계의 source of truth입니다.

대상 하네스:

- Codex
- Claude Code
- OpenCode

OpenClaw 연동 방법도 문서화하지만, OpenClaw는 first-class bootstrap target이 아니라 integration layer로 취급합니다.

## 기본 세팅 범위

사용자가 "이 레포 보고 세팅해줘"라고만 말하고 특정 하네스를 지정하지 않았다면 기본값은 `shared-core-only`입니다.

`shared-core-only`의 의미:

- 현재 도구가 지원하면 `superpowers` 설치 또는 업데이트
- shared constitution과 agent/subagent prompt만 현재 도구의 네이티브 형식으로 적용
- 사용자가 명시적으로 요구하지 않는 한 새 하네스, ACP backend, gateway, provider stack을 고르지 않음

특히 OpenClaw 요청에서는 `Codex-first`가 기본값이 아니고, shared prompt와 skills 레이어만 먼저 맞추는 것이 기본값입니다.

## 기본 범위 매트릭스

- Codex: `current-harness-only`
- Claude Code: `current-harness-only`
- OpenCode: `current-harness-only`
- OpenClaw: `shared-core-only`

`current-harness-only`의 의미는, 이미 Codex나 Claude Code나 OpenCode 안에 있다면 기본적으로 그 현재 하네스만 세팅하고 다른 하네스는 사용자가 명시적으로 요구할 때만 건드린다는 뜻입니다.

## 세팅 프롬프트

다른 에이전트에 바로 붙여넣기 좋은 프롬프트:

- Codex 현재 하네스 전용: [prompts/setup-codex-current-harness.md](prompts/setup-codex-current-harness.md)
- Claude Code 현재 하네스 전용: [prompts/setup-claude-current-harness.md](prompts/setup-claude-current-harness.md)
- OpenCode 현재 하네스 전용: [prompts/setup-opencode-current-harness.md](prompts/setup-opencode-current-harness.md)
- 공통 shared core 세팅: [prompts/setup-shared-core.md](prompts/setup-shared-core.md)
- OpenClaw shared core 전용: [prompts/setup-openclaw-shared-core.md](prompts/setup-openclaw-shared-core.md)
- OpenClaw ACP 연동: [prompts/setup-openclaw-acp.md](prompts/setup-openclaw-acp.md)
- 이 bootstrap 업데이트/재점검: [prompts/update-agent-bootstrap.md](prompts/update-agent-bootstrap.md)

Codex 세션 시작용 위임 허용 문구:

```text
이번 세션에서는 독립적으로 분리 가능한 작업이 있을 때, 효율이 분명히 좋아진다고 판단되면 서브에이전트나 병렬 에이전트를 사용해도 된다. 이건 허용이지 의무가 아니므로, 작업이 작거나 서로 강하게 얽혀 있거나 즉시 막히는 성격이거나 위임 오버헤드가 더 크면 로컬에서 처리해라.
```

## 설치 가이드

- Codex: [docs/README.codex.md](docs/README.codex.md)
- Claude Code: [docs/README.claude.md](docs/README.claude.md)
- OpenCode: [docs/README.opencode.md](docs/README.opencode.md)
- OpenClaw integration: [docs/README.openclaw.md](docs/README.openclaw.md)

## 아키텍처

레포는 두 계층으로 나뉩니다.

- shared core
  - `AGENTS.md`
  - `agents/*.md`
  - `shared/agent-metadata.json`
  - 공통 process-first 헌법과 역할 프롬프트 본문
- harness adapters
  - `.codex/`
  - `.claude-plugin/`
  - `.opencode/`

shared core는 운영 모델을 한 번만 정의하고, 각 adapter가 이를 대상 하네스의 네이티브 형식으로 변환합니다.

자세한 프로젝트 구조 지도, 업데이트 흐름, source-of-truth 경계, 생성물 정책은 [docs/agent-bootstrap-structure.md](docs/agent-bootstrap-structure.md)를 참고합니다.

## Superpowers 연동

이 bootstrap은 `obra/superpowers`를 중심으로 설계되어 있습니다.

- Codex는 `~/.agents/skills/superpowers` symlink 패턴을 사용합니다.
- OpenCode는 `superpowers@git+https://github.com/obra/superpowers.git` plugin line을 사용합니다.
- Claude Code는 두 층으로 나뉩니다.
  - upstream 공식 `superpowers` skill library
  - 이 레포가 생성하는 Claude agent plugin package

Codex App의 curated Superpowers plugin과 수동 `~/.codex/superpowers` fallback을 함께 켜면 중복 skill 항목이 보일 수 있으므로, 의도한 경우가 아니면 한 discovery path만 사용합니다.

목표는 `superpowers` skill library를 이 레포에 복사하지 않고 upstream을 그대로 재사용하는 것입니다.

## 레포 구조

- `AGENTS.md`
  - 공통 헌법 템플릿
- `agents/`
  - 공통 역할 프롬프트 본문
- `shared/agent-metadata.json`
  - 공유 설명과 OpenCode capability metadata
- `.codex/`
  - Codex installer, template, install guide
- `.opencode/`
  - OpenCode installer, template, install guide
- `.claude-plugin/marketplace.json`
  - 레포 수준의 Claude marketplace entry
- `plugins/process-first-agents/`
  - 생성된 Claude plugin package
- `scripts/render_claude_plugin.py`
  - shared prompt corpus로부터 Claude plugin package를 다시 생성
- `docs/`
  - 하네스별 가이드, repo metadata 가이드, OpenClaw 문서
- `tests/`
  - installer, plugin metadata, README 기대사항 검증

## 검색성과 발견성

GitHub 레포의 발견성은 일반 웹 SEO보다 repository metadata 영향을 더 많이 받습니다.

이 레포는 다음 방식으로 발견성을 개선합니다.

- 키워드가 잘 들어간 canonical README
- 다국어 README
- GitHub repository description과 topics
- [docs/repo-metadata.md](docs/repo-metadata.md)에 정리된 social preview 가이드

## 제약

이 레포에는 public하게 공유해도 안전한 baseline만 들어가야 합니다.

넣지 말아야 할 것:

- private MCP endpoint
- 개인 프로젝트 경로
- 조직 전용 secret
- 머신별 trust configuration
- credential, token, auth state

## 업데이트

- Codex와 OpenCode: pull 후 각 installer를 다시 실행
- Claude Code: pull 후 `python3 scripts/render_claude_plugin.py --partner-name "<Name>"`를 다시 실행하고 plugin을 갱신

## 에이전트 스택 점검

업데이트 전후에 로컬 Codex, Claude Code, OpenCode, Superpowers 상태를 확인하려면 다음을 실행합니다.

```bash
python3 scripts/audit_agent_stack.py
```

기본 점검은 offline/read-only입니다. npm과 원격 git 기준 최신 drift까지 확인하려면 `--online`을 붙이고, OpenCode 같은 optional tool 누락도 실패로 처리하려면 `--strict`를 붙입니다.

## 레거시 파일

이전 Codex-only bootstrap 시절의 파일 일부가 아직 남아 있습니다.

- `codex-home/`
- `scripts/install.py`
- `scripts/install.sh`
- `prompts/fresh-install.md`

이들은 호환성 entrypoint이며, 장기적인 멀티 하네스 구조의 중심은 아닙니다.

## 테스트

installer와 metadata 테스트는 Python `unittest`를 사용합니다.

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
