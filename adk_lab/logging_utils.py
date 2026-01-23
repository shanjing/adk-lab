import json
from typing import Any


def format_log_separator(
    title: str | None = None,
    *,
    meta: dict[str, Any] | None = None,
    width: int = 72,
    ch: str = "-",
) -> str:
    """A simple, readable separator line for logs.

    Examples:
      - "------------------------------------------------------------------------"
      - "------------------------------ AGENT FLOW ------------------------------"
      - "------------------------------ RUNNER ------------------------------"
        "ids: runner_id=0x..., session_id=..."
    """
    if width < 10:
        width = 10

    meta_str = ""
    if meta:
        # Keep it short and stable.
        def _short(v: Any, max_len: int = 48) -> str:
            s = str(v)
            return s if len(s) <= max_len else (s[: max_len - 3] + "...")

        parts: list[str] = []
        for k, v in meta.items():
            if v is None:
                continue
            parts.append(f"{k}={_short(v)}")
        if parts:
            meta_str = "ids: " + ", ".join(parts)

    if not title and not meta_str:
        return (ch * width) + "\n"
    if not title:
        title = ""

    title = f" {title.strip()} "
    if len(title) >= width - 2:
        sep_line = title[:width]
    else:
        remaining = width - len(title)
        left = remaining // 2
        right = remaining - left
        sep_line = (ch * left) + title + (ch * right)

    if meta_str:
        return sep_line + "\n" + meta_str + "\n"
    return sep_line + "\n"


def format_pydantic_model_for_log(obj: Any) -> str:
    """Pretty JSON for pydantic models (best-effort).

    Works well for ADK objects like Event, EventActions, etc.
    """
    try:
        payload = obj.model_dump()  # pydantic model -> plain python types
        return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(obj)


def format_event_for_log(event: Any) -> str:
    """Alias for readability when logging ADK events."""
    return format_pydantic_model_for_log(event)


def format_event_actions_for_log(actions: Any) -> str:
    """Pretty-print ADK EventActions with high-signal filtering (best-effort).

    Compared to dumping the raw model, this:
    - Drops empty/default fields (None, {}, [], set()) to reduce noise
    - Adds derived summaries like state_delta_keys / artifact_delta_keys
    """
    try:
        payload = actions.model_dump()
        if not isinstance(payload, dict):
            return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)

        # Derived summaries (keep only keys, not values).
        state_delta = payload.get("state_delta") if isinstance(payload.get("state_delta"), dict) else None
        artifact_delta = payload.get("artifact_delta") if isinstance(payload.get("artifact_delta"), dict) else None

        filtered: dict[str, Any] = {}
        for k, v in payload.items():
            if v is None:
                continue
            if v == {} or v == [] or v == set():
                continue
            filtered[k] = v

        if state_delta:
            filtered["state_delta_keys"] = sorted(list(state_delta.keys()))
        if artifact_delta:
            filtered["artifact_delta_keys"] = sorted(list(artifact_delta.keys()))

        return json.dumps(filtered, indent=2, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(actions)


def format_event_summary_for_log(event: Any) -> str:
    """Compact summary of an ADK Event (key attributes only).

    Intended for high-signal logging without dumping the full event payload.
    """
    # Basic identifiers
    invocation_id = getattr(event, "invocation_id", None)
    event_id = getattr(event, "id", None)
    author = getattr(event, "author", None)
    branch = getattr(event, "branch", None)
    timestamp = getattr(event, "timestamp", None)

    # Content
    content = getattr(event, "content", None)
    role = getattr(content, "role", None) if content else None
    parts = getattr(content, "parts", None) if content else None
    parts_len = len(parts) if parts else 0
    text_preview = ""
    if parts:
        texts = [getattr(p, "text", None) for p in parts if getattr(p, "text", None)]
        if texts:
            joined = "".join(texts)
            text_preview = joined[:180] + ("..." if len(joined) > 180 else "")

    # Actions (high-signal)
    actions = getattr(event, "actions", None)
    transfer_to_agent = getattr(actions, "transfer_to_agent", None) if actions else None
    state_delta = getattr(actions, "state_delta", None) if actions else None
    artifact_delta = getattr(actions, "artifact_delta", None) if actions else None
    skip_summarization = getattr(actions, "skip_summarization", None) if actions else None
    end_of_agent = getattr(actions, "end_of_agent", None) if actions else None

    state_keys = list(state_delta.keys()) if isinstance(state_delta, dict) else []
    artifact_keys = list(artifact_delta.keys()) if isinstance(artifact_delta, dict) else []

    final = None
    if hasattr(event, "is_final_response"):
        try:
            final = event.is_final_response()
        except Exception:
            final = None

    bits = [
        f"invocation_id={invocation_id}",
        f"id={event_id}",
        f"author={author}",
        f"branch={branch}",
        f"ts={timestamp}",
        f"final={final}",
        f"role={role}",
        f"parts={parts_len}",
    ]
    if transfer_to_agent:
        bits.append(f"transfer_to_agent={transfer_to_agent}")
    if state_keys:
        bits.append(f"state_delta_keys={state_keys}")
    if artifact_keys:
        bits.append(f"artifact_delta_keys={artifact_keys}")
    if skip_summarization:
        bits.append("skip_summarization=True")
    if end_of_agent:
        bits.append("end_of_agent=True")
    if text_preview:
        bits.append(f"text={text_preview!r}")

    return " | ".join(bits)


def format_session_for_log(session: Any) -> str:
    """Full log for an ADK session object."""
    if session is None:
        return "session=None"
    return format_pydantic_model_for_log(session)


def format_session_summary_for_log(session: Any) -> str:
    """Compact summary of an ADK session (key attributes only)."""
    if session is None:
        return "session=None"

    session_id = getattr(session, "session_id", None) or getattr(session, "id", None)
    user_id = getattr(session, "user_id", None)
    app_name = getattr(session, "app_name", None)
    state = getattr(session, "state", None)
    artifacts = getattr(session, "artifacts", None)

    bits = [
        f"app_name={app_name}",
        f"user_id={user_id}",
        f"session_id={session_id}",
    ]
    if isinstance(state, dict):
        bits.append(f"state_keys={list(state.keys())}")
    if isinstance(artifacts, dict):
        bits.append(f"artifact_keys={list(artifacts.keys())}")

    return " | ".join(bits)


def format_agent_flow_for_log(root_agent: Any) -> str:
    """ASCII flowchart of agent relationships.

    - Sequential flows use arrows: A -> B -> C
    - Parallel flows use a compact grouping: ParallelAgent(A || B || C)
    - Other agent trees fall back to a tree-ish inline form: Root{A, B, C}

    This is intended to be logged once per run (not per event).
    """

    def _name(agent: Any) -> str:
        return getattr(agent, "name", agent.__class__.__name__)

    def _sub_agents(agent: Any) -> list[Any]:
        subs = getattr(agent, "sub_agents", None)
        return list(subs) if subs else []

    def _kind(agent: Any) -> str:
        return agent.__class__.__name__

    def _fmt(agent: Any, *, top_level: bool) -> str:
        subs = _sub_agents(agent)
        kind = _kind(agent)

        if kind == "SequentialAgent":
            inner = " -> ".join(_fmt(a, top_level=False) for a in subs) if subs else ""
            if top_level:
                return f"{_name(agent)}: {inner}" if inner else _name(agent)
            return f"{_name(agent)}({inner})" if inner else _name(agent)

        if kind == "ParallelAgent":
            inner = " || ".join(_fmt(a, top_level=False) for a in subs) if subs else ""
            return f"{_name(agent)}({inner})" if inner else _name(agent)

        if subs:
            # Fallback: show children inline.
            inner = ", ".join(_fmt(a, top_level=False) for a in subs)
            return f"{_name(agent)}{{{inner}}}"

        return _name(agent)

    return _fmt(root_agent, top_level=True)

