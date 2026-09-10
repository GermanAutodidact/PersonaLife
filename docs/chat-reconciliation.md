# Chat reconciliation

Call `start_chat_event` before advancing beyond the user's real session start. It advances ordinary life to that instant, pauses active work, then records the session. `advance_to` during an open session records chat time only. `end_chat_event` records the final interval, summary, story candidate and future schedule repairs in one command transaction.

`apply_chat_event` wraps start/end atomically for a known bounded interval. Retries use stable session IDs. Reusing an ID with a different start, end, metadata or summary is rejected. Concurrent independent conversations for the same persona are rejected; the host should coalesce turns into one session.

Reconciliation:

1. Preserve canonical executed segments and accumulated activity progress.
2. Resume an interrupted journey's remaining duration if already in transit.
3. Cancel obsolete future travel and replaceable free time.
4. Reserve outstanding hard obligations in order.
5. Place soft tasks around those obligations using explicit priorities.
6. Insert routes between actual locations and planned destinations.
7. Emit lateness and conflict reasons; retain original intended times for audit.

The default policy records the real chat, then permits lateness. `start_chat_event` returns upcoming hard-obligation warnings for a host that wants to shorten a chat. PersonaLife cannot force a user to stop talking and does not truncate a recorded real interval to fabricate punctuality.

A host crash leaves the session open. On reconnection, explicitly end the old session at a known last-active timestamp before advancing beyond it. If a heartbeat already committed later chat time, an earlier endpoint is rejected. Set a host-side inactivity policy appropriate to text or voice sessions; a single universal timeout is not assumed.

User-provided summaries are labeled data, not model instructions or proof of outside activities. They do not establish that shopping or work occurred while the conversation was active.
