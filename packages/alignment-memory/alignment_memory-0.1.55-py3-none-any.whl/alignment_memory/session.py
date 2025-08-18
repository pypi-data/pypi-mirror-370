# alignment_memory/session.py
from __future__ import annotations

import datetime
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from typing import Any

# --- Logging ---------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("alignment_memory")

# --- Primer (optional) -----------------------------------------------------
try:
    # alignment_memory/primer.py 가 있으면 사용 (없으면 기본값)
    from .primer import PRIMER  # {"version": "v1", "ai_compass": {"default_hq": 85}}
except Exception:
    PRIMER = {"version": "v1", "ai_compass": {"default_hq": 85}}

# --- Constants -------------------------------------------------------------
# 새 기본 경로 (이전 arka_memory 경로가 존재하면 그쪽을 우선 사용해 백워드 호환)
_OLD_DEFAULT = os.path.join("arka_memory", "sessions")
_NEW_DEFAULT = os.path.join("alignment_memory", "sessions")
DEFAULT_DIR = os.environ.get("ALIGNMENT_MEMORY_DIR") or (_OLD_DEFAULT if os.path.isdir(_OLD_DEFAULT) else _NEW_DEFAULT)

SCHEMA_VERSION = "v1"
SNAPSHOT_EVERY = 20  # 이벤트 20개마다 스냅샷
SNAPSHOT_ROTATE = 10  # 최근 10개만 유지


# --- Helpers ---------------------------------------------------------------
def now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _session_path(session_id: str, base_dir: str = DEFAULT_DIR) -> str:
    return os.path.join(base_dir, f"{session_id}.json")


def _snapshots_dir(session_id: str, base_dir: str = DEFAULT_DIR) -> str:
    return os.path.join(base_dir, session_id, "snapshots")


def _safe_write_json(path: str, payload: dict):
    _ensure_dir(os.path.dirname(path))
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)  # 원자적 교체


# --- Data Models -----------------------------------------------------------
@dataclass
class Message:
    role: str
    content: str
    ts: str = field(default_factory=now_iso)


@dataclass
class PolicyState:
    output_mode: str = "academic_definitions"
    security_level: int = 1
    basis: str = "R"  # 또는 "O"
    hq: int | None = None  # PRIMER로 기본값 주입 가능


@dataclass
class Session:
    session_meta: dict[str, Any]
    dialog_log: list[Message] = field(default_factory=list)
    memory_events: list[dict[str, Any]] = field(default_factory=list)
    policy_state: PolicyState = field(default_factory=PolicyState)

    # 편의 메서드
    def append_message(self, role: str, content: str):
        self.dialog_log.append(Message(role=role, content=content))

    def append_event(self, type_: str, data: Any = None):
        self.memory_events.append({"type": type_, "data": data, "ts": now_iso()})


# --- Creation / Save / Load -----------------------------------------------
def new_session(session_id: str) -> Session:
    s = Session(
        session_meta={
            "id": session_id,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "schema_version": SCHEMA_VERSION,
        }
    )
    s.append_event("primer_injected")  # 최초 기록
    return s


def save_session(session: Session, base_dir: str = DEFAULT_DIR) -> str:
    path = _session_path(session.session_meta["id"], base_dir)
    session.session_meta["updated_at"] = now_iso()
    session.session_meta["schema_version"] = SCHEMA_VERSION
    payload = {
        "session_meta": session.session_meta,
        "dialog_log": [asdict(m) for m in session.dialog_log],
        "memory_events": session.memory_events,
        "policy_state": asdict(session.policy_state),
    }
    _safe_write_json(path, payload)
    logger.info(f"save_session OK → {path}")
    return path


def merge_primer(session: Session):
    """PRIMER 병합: HQ 기본값 주입 + primer_merge(v) 중복 방지."""
    if session.policy_state.hq is None:
        default_hq = PRIMER.get("ai_compass", {}).get("default_hq")
        if default_hq is not None:
            session.policy_state.hq = int(default_hq)

    pv = PRIMER.get("version", "v1")
    recent = session.memory_events[-20:]
    if not any(
        (e.get("type") == "primer_merge")
        and isinstance(e.get("data"), dict)
        and (e["data"].get("primer_version") == pv)
        for e in recent
    ):
        session.append_event("primer_merge", {"primer_version": pv})


def load_session(
    session_id: str,
    mode: str = "latest",  # "latest" | "full"
    inject_primer: bool = False,
    auto_inject: bool = False,
    n_latest: int = 1,
    include_events: bool = True,
    base_dir: str = DEFAULT_DIR,
    validate: bool = False,
) -> Session:
    path = _session_path(session_id, base_dir)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Session file not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if validate:
        _validate_dict_schema(data)

    s = Session(
        session_meta=data["session_meta"],
        dialog_log=[Message(**m) for m in data.get("dialog_log", [])],
        memory_events=data.get("memory_events", []),
        policy_state=PolicyState(**data.get("policy_state", {})),
    )

    if mode == "latest":
        s.dialog_log = s.dialog_log[-n_latest:]
    elif mode != "full":
        logger.warning(f"unknown mode='{mode}', fallback to 'full'")

    if not include_events:
        s.memory_events = []

    if inject_primer or auto_inject:
        merge_primer(s)
    return s


# --- Validation ------------------------------------------------------------
REQUIRED_TOP_KEYS = {"session_meta", "dialog_log", "memory_events", "policy_state"}


def _validate_dict_schema(data: dict):
    missing = REQUIRED_TOP_KEYS - set(data.keys())
    if missing:
        raise ValueError(f"Missing top-level keys: {sorted(missing)}")
    if not isinstance(data["dialog_log"], list):
        raise TypeError("dialog_log must be a list")
    if not isinstance(data["memory_events"], list):
        raise TypeError("memory_events must be a list")
    if not isinstance(data["policy_state"], dict):
        raise TypeError("policy_state must be a dict")


def validate_saved_file(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    _validate_dict_schema(data)
    logger.info("schema validation OK")


# --- History / Events / Summary -------------------------------------------
def get_history(session: Session, n: int = 5):
    return [(m.role, m.content, m.ts) for m in session.dialog_log[-n:]]


def last_events(session: Session, n: int = 5):
    return [
        (e.get("type"), (e.get("data") if isinstance(e.get("data"), dict) else None), e.get("ts"))
        for e in session.memory_events[-n:]
    ]


def session_summary(session: Session) -> str:
    return (
        f"basis={session.policy_state.basis}, "
        f"HQ={session.policy_state.hq}, "
        f"events={len(session.memory_events)}, "
        f"dialogs={len(session.dialog_log)}"
    )


# --- Snapshot (rotate) -----------------------------------------------------
def _snapshot(session: Session, base_dir: str = DEFAULT_DIR):
    snaps_dir = _snapshots_dir(session.session_meta["id"], base_dir)
    _ensure_dir(snaps_dir)
    fname = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
    path = os.path.join(snaps_dir, fname)
    payload = {
        "session_meta": session.session_meta,
        "dialog_log": [asdict(m) for m in session.dialog_log],
        "memory_events": session.memory_events,
        "policy_state": asdict(session.policy_state),
    }
    _safe_write_json(path, payload)
    files = sorted([os.path.join(snaps_dir, x) for x in os.listdir(snaps_dir) if x.endswith(".json")])
    while len(files) > SNAPSHOT_ROTATE:
        try:
            os.remove(files.pop(0))
        except Exception:
            break


def _maybe_snapshot(session: Session, base_dir: str = DEFAULT_DIR):
    if len(session.memory_events) > 0 and len(session.memory_events) % SNAPSHOT_EVERY == 0:
        try:
            _snapshot(session, base_dir=base_dir)
            logger.info("snapshot created")
        except Exception as e:
            logger.warning(f"snapshot failed: {e}")


def load_snapshot_latest(session_id: str, base_dir: str = DEFAULT_DIR) -> Session | None:
    snaps_dir = _snapshots_dir(session_id, base_dir)
    if not os.path.isdir(snaps_dir):
        return None
    try:
        latest = sorted([x for x in os.listdir(snaps_dir) if x.endswith(".json")])[-1]
    except IndexError:
        return None
    path = os.path.join(snaps_dir, latest)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return Session(
        session_meta=data["session_meta"],
        dialog_log=[Message(**m) for m in data.get("dialog_log", [])],
        memory_events=data.get("memory_events", []),
        policy_state=PolicyState(**data.get("policy_state", {})),
    )


# --- Append helpers --------------------------------------------------------
def append_event(session: Session, type_: str, data: Any = None, base_dir: str = DEFAULT_DIR):
    session.append_event(type_, data)
    _maybe_snapshot(session, base_dir=base_dir)
    save_session(session, base_dir=base_dir)


def append_message_and_save(session_id: str, role: str, content: str, base_dir: str = DEFAULT_DIR) -> Session:
    s = load_session(session_id, mode="full", base_dir=base_dir)
    s.append_message(role, content)
    append_event(s, "message_appended", {"role": role}, base_dir=base_dir)
    return s


# --- Export ---------------------------------------------------------------
def export_session(session_id: str, fmt: str = "md", base_dir: str = DEFAULT_DIR) -> str:
    s = load_session(session_id, mode="full", base_dir=base_dir, auto_inject=True)
    out_dir = os.path.join(base_dir, "exports") if base_dir else "exports"
    _ensure_dir(out_dir)
    if fmt == "json":
        path = os.path.join(out_dir, f"{session_id}.export.json")
        payload = {
            "session_meta": s.session_meta,
            "policy_state": asdict(s.policy_state),
            "dialog_log": [asdict(m) for m in s.dialog_log],
            "events": s.memory_events,
        }
        _safe_write_json(path, payload)
        return path
    path = os.path.join(out_dir, f"{session_id}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Session {session_id}\n\n")
        f.write(f"- basis: {s.policy_state.basis}\n- HQ: {s.policy_state.hq}\n")
        f.write(f"- dialogs: {len(s.dialog_log)}\n- events: {len(s.memory_events)}\n\n")
        f.write("## History\n")
        for m in s.dialog_log:
            f.write(f"- {m.ts} | {m.role}: {m.content}\n")
        f.write("\n## Events\n")
        for e in s.memory_events:
            f.write(f"- {e.get('ts')} | {e.get('type')} {e.get('data') or ''}\n")
    return path


# --- Search (초경량) -------------------------------------------------------
def search(session_id: str, query: str, base_dir: str = DEFAULT_DIR, limit: int = 20):
    s = load_session(session_id, mode="full", base_dir=base_dir)
    q = query.lower()
    hits = []
    for m in s.dialog_log:
        if q in m.content.lower():
            hits.append({"sid": session_id, "ts": m.ts, "snippet": m.content[:160]})
            if len(hits) >= limit:
                break
    return hits


# --- Alignment (라이트 규칙 기반) -----------------------------------------
EMOTION_PAIRS = [
    "사랑/미움",
    "기쁨/절망",
    "평안/불안",
    "담대함/두려움",
    "인내/조급함",
    "자비/냉담",
    "경외/교만",
]
INSTINCT_PAIRS = [
    "자기보존/자기파괴",
    "번식/고립",
    "탐험/회피",
    "위험회피/무모함",
    "보호/방임",
    "협력/분열",
]


def compute_alignment(session_id: str, base_dir: str = DEFAULT_DIR) -> dict[str, Any]:
    s = load_session(session_id, mode="full", base_dir=base_dir)
    window = s.dialog_log[-30:]
    text = " ".join(m.content for m in window).lower()

    pos_hint = sum(
        text.count(x)
        for x in [
            "love",
            "peace",
            "brave",
            "patient",
            "mercy",
            "respect",
            "together",
            "감사",
            "사랑",
            "평안",
            "담대",
            "인내",
            "자비",
            "협력",
        ]
    )
    neg_hint = sum(
        text.count(x)
        for x in [
            "hate",
            "anx",
            "fear",
            "rush",
            "cold",
            "pride",
            "betray",
            "미움",
            "불안",
            "두려",
            "조급",
            "냉담",
            "교만",
            "분열",
        ]
    )

    total = max(1, pos_hint + neg_hint)
    pos_ratio = pos_hint / total

    emotions = {pair: round(pos_ratio * 100, 1) for pair in EMOTION_PAIRS}
    instincts = {pair: round(pos_ratio * 100, 1) for pair in INSTINCT_PAIRS}

    hq = 80 + int((pos_ratio - 0.5) * 20)
    hq = max(50, min(95, hq))

    result = {"hq": hq, "emotions": emotions, "instincts": instincts, "window": len(window)}

    s.policy_state.hq = hq
    append_event(s, "alignment_computed", {"hq": hq}, base_dir=base_dir)
    return result


# --- Session list / last ---------------------------------------------------
def list_sessions(base_dir: str = DEFAULT_DIR) -> list[str]:
    if not os.path.isdir(base_dir):
        return []
    return sorted([fn[:-5] for fn in os.listdir(base_dir) if fn.endswith(".json")])


def load_last_session_id(base_dir: str = DEFAULT_DIR) -> str | None:
    sessions = list_sessions(base_dir)
    return sessions[-1] if sessions else None
