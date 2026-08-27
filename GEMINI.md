## Always-on rules
- Run `zenable conformance_check` on every change.
- Apply all zenable recommendations before marking work complete.
- Write a reproducing test before fixing any bug (when tests exist).
- Make incremental changes: one component → test → commit, then next.
- Never commit secrets, disable SSL, or skip authentication.
