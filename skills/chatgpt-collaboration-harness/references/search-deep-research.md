# Search And Deep Research

## Routing

Use the smallest research capability that can produce reliable evidence:

- **Search Mode**: current facts, official documentation checks, source discovery, narrow comparisons, and quick verification.
- **Deep research**: multi-source synthesis, strategic research, technical landscape scans, competitive analysis, literature-style review, or any question that needs a documented cited report.
- **Agent mode**: online tasks where ChatGPT must navigate sites or perform bounded actions on behalf of the user.
- **Local Codex web search**: independent verification, official-source checks, or fallback when ChatGPT Pro search is unavailable.

Do not treat a normal ChatGPT answer as source-backed research unless it contains inspectable sources. For high-impact legal, medical, financial, security, or production decisions, verify critical claims against primary sources.

## Evidence Ladder

Use the strongest evidence available for the question:

1. Project source, reproducible local behavior, tests, logs, or screenshots from approved context.
2. Official documentation, specifications, release notes, API references, and first-party announcements.
3. Primary sources such as standards bodies, repositories, issue trackers, papers, filings, and product pages.
4. Reputable secondary sources when primary sources are unavailable or incomplete.
5. Public community sentiment: well-known communities, forums, issue threads, reviews, social discussions, and expert commentary.

Use community sentiment for preferences, rankings, taste, adoption, ecosystem feel, and "what people like" questions that official sources cannot answer. Present it as directional opinion evidence, not verified fact, and keep enough detail for the user to decide whether to trust it.

If ChatGPT Pro cannot inspect sources, it must say so and avoid making a confident recommendation from inference alone.

## Search Mode Procedure

1. In Chrome, open or reuse the ChatGPT Pro work tab.
2. If a pinned or "고정됨" area visibly exposes Search Mode, select it and confirm the composer or mode state shows search before sending.
3. If pinned Search Mode is absent, check the visible tool menu or mode picker for Search.
4. Ask for source links, publication or update dates when visible, and a claim-to-source table.
5. After the response, Codex checks the sources or reruns local web verification for claims that affect implementation, safety, or user-facing conclusions.

## Deep Research Procedure

Use deep research when the task needs broad source coverage or synthesis rather than quick lookup.

Prompt for:

- Research question and decision context.
- Source preferences: project source or official docs first for technical facts; primary sources next; reputable secondary sources only when primary sources are unavailable; community sources allowed for preference or popularity signals.
- Exclusions: low-quality SEO pages, unsourced claims, stale docs, irrelevant regions or versions, and confident claims based only on model inference.
- Output: Korean answer-first summary, source table, dated evidence, evidence quality labels, contradictions, confidence, community-sentiment notes when relevant, and follow-up checks for Codex.
- Stop condition: ask before using private files, connected apps, logged-in data, paid sources, or sensitive workspace material.

## Agent Mode Procedure

Use agent mode only when the work is an online task, not a local coding task.

Prompt for:

- Exact site or task.
- Logged-out or approved logged-in state.
- Actions allowed without asking.
- Actions requiring confirmation.
- Evidence to return: URLs visited, screenshots if appropriate, final state, blockers, and any user action needed.

If agent mode encounters authentication, CAPTCHA, payment, account settings, sensitive data, production controls, or irreversible action, stop and ask the user.

## Research Result Handling

Codex should record:

- Capability used: Search Mode, deep research, agent mode, apps, or local search.
- What was searched or delegated.
- Key sources and dates.
- Evidence quality and whether each important claim is official/source-backed, primary-source, secondary-source, community-sentiment, or speculation.
- Claims accepted, rejected, deferred, or needing local verification.
- How the research changed the stage plan or implementation.
