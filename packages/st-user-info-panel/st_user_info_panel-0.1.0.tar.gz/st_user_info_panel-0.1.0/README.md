# st-user-info-panel

A polished **Streamlit custom component** for a floating **User Info Panel** anchored to the sidebar.  
Supports fixed float stick in sidebar, **collapsed chip** (avatar initials) when the sidebar is collapsed, and **usage stats** (messages, tokens, cost).

[![PyPI version](https://img.shields.io/pypi/v/st-user-info-panel.svg)](https://pypi.org/project/st-user-info-panel/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Repo:** https://github.com/agustyawan-arif/st-user-info-panel

---

## ✨ Features

- **Floating panel** that follows the sidebar width (portal) or **sticky** at the bottom of the sidebar (inside).
- **Collapsed chip**: when the sidebar collapses, a small circular chip with initials appears;
- **Stats**: **Messages**, **Tokens**, **Cost** with optional progress bars if monthly limits are set.
- **Compact mode** for tighter sidebars.
- **Optional fields**: Department, Work Location.
- **Uncontrolled** (default) or **Controlled** expansion state.
- Robust geometry handling for **scrollable sidebars** and **animated collapse/expand**.

---

## 📦 Install

```bash
pip install st-user-info-panel
```

Import name:

```python
from st_user_info_panel import st_user_info_panel
```

---

## 🚀 Quickstart

```python
import streamlit as st
from st_user_info_panel import st_user_info_panel

st.set_page_config(page_title="AI Chat Assistant Demo", layout="wide", initial_sidebar_state="expanded")

if "user_panel_expanded" not in st.session_state:
    st.session_state.user_panel_expanded = False

with st.sidebar:
    st.title("🤖 AI Assistant")
    st.subheader("Recent Conversations")
    for i in range(20):
        st.markdown(f"• Chat {i+1}")

    st.markdown("---")
    st.subheader("Settings")
    st.selectbox("Model", ["GPT-4", "Claude", "Gemini"])
    st.slider("Temperature", 0.0, 2.0, 0.7)

    result = st_user_info_panel(
        name="Sarah Johnson",
        job_title="Senior Data Scientist",
        email="sarah.johnson@techcorp.com",
        department="Data Platform",
        work_location="Jakarta",
        messages_count=340, monthly_messages_limit=500,
        tokens_this_month=3_200_000, monthly_tokens_limit=10_000_000,
        cost_usd=42.35, monthly_cost_limit=200.0,
        show_detailed_stats=True,
        compact=True,
        stats_style="rows",
        show_progress=False,
        side_padding_px=12,
        bottom_offset_px=16,
        controlled=False,
        expanded=st.session_state.user_panel_expanded,
        key="user-panel",
    )

    if result:
        evt = result.get("event")
        if evt == "toggle":
            st.session_state.user_panel_expanded = result["expanded"]
        elif evt == "logout":
            st.session_state.user_panel_expanded = False
            st.warning("Logout clicked")
        elif evt == "chip":
            pass
```

## ⚙️ API

### `st_user_info_panel(...) -> dict | None`

**Identity**

| Prop            | Type            |                  Default | Notes                 |
| --------------- | --------------- | -----------------------: | --------------------- |
| `name`          | `str`           |             `"John Doe"` | Used for initials     |
| `job_title`     | `str`           |       `"Data Scientist"` |                       |
| `email`         | `str`           | `"john.doe@company.com"` | Wraps for long values |
| `avatar_color`  | `str`           |              `"#FE5556"` | Any CSS color         |
| `department`    | `Optional[str]` |                   `None` | Optional              |
| `work_location` | `Optional[str]` |                   `None` | Optional              |

**Stats (neutral)**

| Prop                     | Type    | Default | Notes           |
| ------------------------ | ------- | ------: | --------------- |
| `messages_count`         | `int`   |     `0` |                 |
| `monthly_messages_limit` | `int`   |     `0` | `0` = unlimited |
| `tokens_this_month`      | `int`   |     `0` |                 |
| `monthly_tokens_limit`   | `int`   |     `0` | `0` = unlimited |
| `cost_usd`               | `float` |   `0.0` |                 |
| `monthly_cost_limit`     | `float` |   `0.0` | `0` = unlimited |
| `show_detailed_stats`    | `bool`  |  `True` |                 |
| `show_progress`          | `bool`  |  `True` |                 |

**Layout & Behavior**

| Prop               | Type                      |  Default | Notes             |
| ------------------ | ------------------------- | -------: | ----------------- |
| `side_padding_px`  | `int`                     |     `12` |                   |
| `bottom_offset_px` | `int`                     |     `16` |                   |
| `border_radius_px` | `int`                     |     `12` |                   |
| `compact`          | `bool`                    |  `False` |                   |
| `stats_style`      | `Literal["rows","cards"]` | `"rows"` | `rows` is compact |

**State control**

| Prop         | Type            | Default | Notes                              |
| ------------ | --------------- | ------: | ---------------------------------- |
| `controlled` | `bool`          | `False` | If `True`, follows `expanded` prop |
| `expanded`   | `bool`          | `False` |                                    |
| `key`        | `Optional[str]` |  `None` | Stable key recommended             |

**Return (events)**

```python
{
  "event": "toggle" | "logout" | "chip",
  "expanded": bool,
}
```
