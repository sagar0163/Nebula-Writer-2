# Issue #141: Run tests and fix failures

## Acceptance Criteria

- [x] Test session runs with zero failures (baseline: `collected 0 items`; current: 18 passed, 0 failed with DB; 12 passed, 6 skipped, 0 failed without)
- [x] All architectural inconsistencies revealed by test failures are documented and addressed
- [x] No new features added until test suite passes (no features added at all)

## State on handoff

Prior attempt concluded the suite already passed (12 passed, 6 skipped). The 6 "skipped" tests
were unconditionally `@pytest.mark.skip`'d, so the Supabase/PostgreSQL DB layer was never
actually exercised. The plan file's own subtask "Address skipped tests that should run" was
never completed. This attempt:

1. Spins up a local PostgreSQL 16 cluster and applies the repo's own `schema.sql`
   (minus the pgvector section, which is not installed and unused by these tests).
2. Makes the DB-integration tests RUN when `POSTGRES_CONNECTION_STRING` is set, and skip.
   gracefully (with a clear reason) when it is not - so CI without a DB stays green.
3. Runs them to reveal the real failures, then fixes them.

## Subtasks

- [x] Verify baseline suite green (12 passed, 6 skipped, 0 failed)
- [x] Create local PostgreSQL test cluster + apply repo schema (stripped of pgvector)
- [x] Un-skip DB tests via env-gated skip + per-test DB wipe (conftest.py helper + pytestmark)
- [x] Run DB tests against local Postgres; capture actual failures
- [x] Fix `supabase_db.py` `type`-vs-`entity_type` column mismatch (get_entities, get_entity, add_entity,
      get_relationships, get_stats, search) matching schema.sql ground truth
- [x] Add a conftest fixture that wipes tables between DB tests (isolation fix)
- [x] Re-run full suite with DB: all tests pass, 0 failures (18 passed)
- [x] Confirm suite still green WITHOUT POSTGRES_CONNECTION_STRING (CI mode: 12 passed, 6 skipped)
- [x] Document architectural inconsistency found (PROJECT_STATE.md entry)
- [ ] Delete WAR_ROOM_PLAN_141.md, final commit referencing #141
- [ ] Push branch to origin