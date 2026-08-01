# Director operating guide — HELM (`trade`)

The foundation is authored. This is your control panel: the decisions only you can make, the spawn order,
and the human-only steps. Governance scaffolding is identical whether you confirm the defaults or override
them — **but no wave dispatches, no spend, and no remote push happens until you act.**

## 1 · Open decisions (present, then WAIT — LL-38)
Everything below is scaffolded against the Lead's recommended default and marked DIRECTOR-PENDING; confirm
or override. Two are **LOCKS** needing an explicit "yes."

| # | Decision | Recommended default | Kind |
|---|---|---|---|
| 1 | 🔴 **What does HELM do?** (`canonical-design <1.1>`) | EDGAR + market-data → AI-assisted trading signals | blocker for W1+ design |
| 2 | 🔒 **Cost model** (D-TRADE-004) | **BILLED PER-USE** → arm FinOps + B4 chokepoint | LOCK |
| 3 | 🔒 **Roster** (D-TRADE-005) | **14 seats** (core spine + AI/ML·AIQ·FinOps·Legal·Data-Eng) | LOCK |
| 4 | 🟡 **External providers** (`<2.1>`) | SEC EDGAR + Polygon.io (SecOps ToS-taint first) | pending |
| 5 | 🟡 **Run B9 Gauntlet?** (D-TRADE-009) | **RUN** before any design/build; needs `<1.1>` | pending |
| 6 | 🟡 **B7 (CX-heavy)?** | off unless CX-heavy | pending |
| 7 | 🟡 **Python data/ML lane?** (D-TRADE-003) | Node/TS only unless quant-heavy; reopen before W1 | pending |
| 8 | 🟡 **Product name** (rebrand `HELM`) | parked codename → one find-replace | any time |
| 9 | 🟡 **Isolation rule** | kit crosses / product content doesn't (LL-4) | confirm or add a specific rule |

## 2 · Human-only steps (Prohibited / permission-required for the agent — you do these)
1. **Place the session defaults:** copy `docs/foundation/settings.json.template` → repo-root
   `.claude/settings.json` (the harness blocks an agent from authoring an active permissions file —
   appropriately, since you hold the root of trust). §10.5 low-friction defaults; full-auto stays per-seat.
2. **Create the remote** (gh was unavailable this session — the foundation is committed **locally only**):
   ```bash
   gh repo create ShupeCapital/trade --private --source="Trade - Lead" --remote=origin --push
   ```
   (or create it in the GitHub UI and `git remote add origin … && git push -u origin main` from
   `Trade - Lead`). Confirm `.gitignore` excludes secrets before the first push — it does.
3. **Spawn each role session** in its own clone dir with the block from `role-bootstrap-scripts.md`, at the
   §2-locked model/effort. **You are the only one who spawns sessions and approves spend.**
4. **Confirm the locks** (cost model, roster) and give the **product paragraph** — then the Lead unblocks
   W1 planning.
5. **Approve each Wave-Entry GO** (the Lead authors the plan; oversight reviews; you say GO — the Lead
   never self-dispatches).

## 3 · Spawn order — *for reference; NO build role is spawned yet (D-TRADE-010)*
We are **not building any code yet**, so no build/oversight seat needs a session at this point. This is
the order for *when* work exists for a seat:
1. **DevOps** (W0 scaffold) → **BE-API · BE-Data · FE-Web · Data-Eng** (code lanes) — only after a build-GO.
2. **QA · GA · SecOps · FinOps · AIQ · Legal** (oversight — independent, → you).
3. **Architect** on-demand (W1 spine ADR). **AI/ML** when the engine surface opens (post-design).
4. **Gauntlet cluster** — the *first* seats that could be spawned, and only **if you run B9** (needs the
   product paragraph). SecOps' provider ToS-taint check is the other pre-build task.

**Building unblocks only after:** product defined (`<1.1>`) → B9 viability/blueprint (if run) → your
explicit build-GO. Until then nothing is dispatched.

## 4 · What's where
`PROJECT-CONFIG.md` (config of record) · `../AGENT-COORDINATION.md` (charter) · `../decisions-log.md`
(D-TRADE-001…009) · `../app-design/{canonical-design,working-log,stage-plan}.md` · `../gate/{gate-spec,
oracle-boundary}.md` · `../roles/<role>/PROFILE.md` · `role-bootstrap-scripts.md` · `../dev-lessons-learned.md`
· `kit/` (the improved v2.3.0 kit copy — see STEP 6).
