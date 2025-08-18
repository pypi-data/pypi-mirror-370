from __future__ import annotations
from pathlib import Path
from typing import Optional, Literal, TypedDict, Any
import streamlit as st
import streamlit.components.v1 as components

# Point to frontend (index.html, main.js, etc.)
_frontend_dir = (Path(__file__).parent / "frontend").absolute()
_component_func = components.declare_component("st-user-info-panel", path=str(_frontend_dir))

class PanelResult(TypedDict, total=False):
    event: Optional[Literal["toggle", "view_profile", "logout"]]
    expanded: bool

def st_user_info_panel(
    *,
    # Identity
    name: str = "John Doe",
    job_title: str = "Data Scientist",
    email: str = "john.doe@company.com",
    avatar_color: str = "#FE5556",
    department: Optional[str] = None,
    work_location: Optional[str] = None,
    # Stats
    messages_count: int = 0,
    monthly_messages_limit: int = 0,
    tokens_this_month: int = 0,
    monthly_tokens_limit: int = 0,
    cost_usd: float = 0.0,
    monthly_cost_limit: float = 0.0,
    show_detailed_stats: bool = True,
    # Behavior
    expanded: bool = False,
    controlled: bool = False,
    # Layout
    bottom_offset_px: int = 16,
    side_padding_px: int = 8,
    border_radius_px: int = 12,
    dense: bool = False,
    compact: bool = False,
    stats_style: str = "cards",
    show_progress: bool = True,
    attach_mode: str = "portal",
    # IMPORTANT: Streamlit component key
    key: Optional[str] = None,
):
    """Floating user panel anchored to Streamlit sidebar."""
    # NEW: stable instance key used by frontend to cleanup orphaned portals
    instance_key = key or "st_user_info_panel_default"

    payload: Any = _component_func(
        key=key,
        # identity
        name=name, job_title=job_title, email=email, avatar_color=avatar_color,
        department=department or "", work_location=work_location or "",
        # stats
        messages_count=int(messages_count), monthly_messages_limit=int(monthly_messages_limit),
        tokens_this_month=int(tokens_this_month), monthly_tokens_limit=int(monthly_tokens_limit),
        cost_usd=float(cost_usd), monthly_cost_limit=float(monthly_cost_limit),
        show_detailed_stats=bool(show_detailed_stats),
        # behavior
        expanded=bool(expanded), controlled=bool(controlled),
        # layout
        bottom_offset_px=int(bottom_offset_px), side_padding_px=int(side_padding_px),
        border_radius_px=int(border_radius_px), dense=bool(dense),
        compact=bool(compact), stats_style=stats_style, show_progress=bool(show_progress),
        attach_mode=attach_mode,
        # NEW: pass stable instance id to JS
        instance_key=instance_key,
    )
    if payload is None:
        return {"event": None, "expanded": expanded}
    return payload