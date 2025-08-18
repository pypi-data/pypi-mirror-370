from __future__ import annotations

from alignment_memory.session import new_session, save_session, session_summary

SID = "20250814-TEST"
s = new_session(SID)
save_session(s)
print("NEW:", session_summary(s))
