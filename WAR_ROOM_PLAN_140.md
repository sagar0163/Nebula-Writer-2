# WAR_ROOM_PLAN_140: Fix broken frontend - remove placeholders

## Problem
The project references a non-existent `backend/` directory and `frontend/` in multiple places:
- Root `nebula-writer` CLI script imports from `backend/` (doesn't exist)
- Makefile `run` target does `cd backend/` (doesn't exist)
- ARCHITECTURE.md describes `frontend/` and `backend/` dirs that don't exist
- specs/BRD.md references Vue.js frontend features that don't exist
- The project is a backend-only API + CLI, but entry points are broken

## Checklist

- [x] Fix root `nebula-writer` CLI script - change `backend` import to `nebula_writer`
- [x] Fix Makefile `run` target to use correct uvicorn path
- [ ] Update ARCHITECTURE.md to reflect actual project structure
- [ ] Clean up specs/BRD.md frontend references (remove Vue.js references, mark as future)
- [ ] Verify CLI and Makefile work correctly
- [ ] Run tests to ensure nothing is broken
- [ ] Final commit and push
