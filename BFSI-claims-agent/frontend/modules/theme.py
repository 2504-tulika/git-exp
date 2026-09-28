INK_NAVY = "#1B2A4A"
PAPER = "#FAFAF8"
SLATE = "#5B6B85"
SEAL_GREEN = "#2F6D5C"      # approve
SIGNAL_AMBER = "#B8863B"    # needs_more_info
SIGNAL_RUST = "#A13D2E"     # deny

STATUS_COLORS = {
    "approve": SEAL_GREEN,
    "deny": SIGNAL_RUST,
    "needs_more_info": SIGNAL_AMBER,
}

GLOBAL_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
}}

h1, h2, h3 {{
    font-family: 'Fraunces', serif;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: {INK_NAVY};
}}

.stApp {{
    background-color: {PAPER};
}}

[data-testid="stSidebar"] {{
    background-color: {INK_NAVY};
}}
[data-testid="stSidebar"] * {{
    color: {PAPER} !important;
}}

.stButton>button {{
    background-color: {INK_NAVY};
    color: {PAPER};
    border-radius: 6px;
    border: none;
    font-weight: 500;
    padding: 0.5rem 1.25rem;
}}
.stButton>button:hover {{
    background-color: {SLATE};
    color: {PAPER};
}}

.stTabs [data-baseweb="tab"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 500;
    color: {INK_NAVY};
}}

[data-testid="stMetricValue"] {{
    font-family: 'Fraunces', serif;
    color: {INK_NAVY};
}}
[data-testid="stMetricLabel"] {{
    color: {SLATE};
}}

[data-testid="stForm"] {{
    border: 1px solid {INK_NAVY}22;
    border-radius: 8px;
    padding: 1.5rem;
    background: white;
}}
</style>
"""


def accent_bar(color):
    """A 4px colored rule -- the top-accent device used at the head of every card, colored by what that card represents."""
    return f'<div style="height:4px;background:{color};border-radius:2px;margin-bottom:0.85rem;"></div>'


def recommendation_block(recommendation, rationale):
    """
    The agent's recommendation, always inside a clearly-labeled advisory
    frame -- the one deliberately custom-built element in this app,
    rather than a reskinned st.success/error/warning, so it carries this
    app's own signal palette instead of Streamlit's default red/green/
    yellow alert colors.

    recommendation/rationale are None for the 30 seeded historical claims
    (they predate the agent entirely -- there was nothing to recommend
    before this project existed), which is an expected, common case for
    any real customer's claim history, not a rare edge case to ignore.
    """
    if recommendation is None:
        html = f"""
        <div style="border:1px solid {SLATE}33;border-left:4px solid {SLATE};border-radius:6px;padding:1rem 1.25rem;background:{PAPER};">
            <div style="font-size:0.85rem;color:{SLATE};">No AI recommendation on file -- this claim predates automated review.</div>
        </div>
        """
        return html

    color = STATUS_COLORS.get(recommendation, SLATE)
    label = recommendation.replace("_", " ").title()
    rationale_html = (
        f'<p style="margin-top:0.5rem;color:{INK_NAVY};line-height:1.5;">{rationale}</p>'
        if rationale else ""
    )
    html = f"""
    <div style="border:1px solid {color}33;border-left:4px solid {color};border-radius:6px;padding:1rem 1.25rem;background:{PAPER};">
        <div style="font-size:0.8rem;color:{SLATE};margin-bottom:0.35rem;">AI recommendation -- pending human review, not a final decision</div>
        <div style="font-family:'Fraunces',serif;font-size:1.15rem;font-weight:600;color:{color};">{label}</div>
        {rationale_html}
    </div>
    """
    return html

