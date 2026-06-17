2. The script opens a real Chromium session via Browserless and navigates to the login URL.
3. The operator completes the login manually (via Browserless's live debugging view, or
   a VNC/remote viewer pointed at the Browserless session).
4. Once logged in, the operator presses Enter in the script's terminal.
5. The script captures `context.storage_state()` and POSTs it to the Session Manager,
   overwriting the expired session and resetting its status to `active`.

### Stage 3 — Resume
Once bootstrapped, the workflow can be re-run immediately with the same `profile_key`
and will use the freshly saved session.

## Security Notes
- Session files are never committed to GitHub; they live only in the `session_data`
  Docker volume on the server.
- Each profile is isolated — compromising one profile's session file does not expose
  others.
- Profile keys are sanitized (alphanumeric, underscore, hyphen only) before being used
  as filenames, preventing path traversal.

## Status Summary
- Per-account/per-platform storage: **implemented** (Session Manager API + volume)
- Refresh/bootstrap process for expired sessions: **implemented and documented** (this file + bootstrap-session.py)
- Workflow-level profile selection: **implemented** (profile_key passed from n8n)
