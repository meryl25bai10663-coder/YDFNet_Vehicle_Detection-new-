"""
EmergeRoute - Dashboard

Streamlit app tying the whole pipeline together: shows real network state,
the ranked candidate policies, the recommended top pick, and a plain-language
explanation, matching the brief's dashboard requirement.

Run with:
    streamlit run dashboard.py
"""
from __future__ import annotations
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from policy_generator import probe_network, generate_candidate_policies
from scoring_engine import rank_policies
from traffic_prediction import train_predictor, predict_congestion_level, N_LAGS
from detection_panel import render_detection_section
from video_upload import render_video_upload
from map_section import render_map_section
from background import render_background
from splash import render_splash
from smooth import render_smooth_scroll

# Set these before launch. "#" keeps the links inert until then.
LANDING_URL = "#"
PRIVACY_URL = "privacy"
TERMS_URL = "terms"

FAVICON = Path("assets/favicon.png")
st.set_page_config(
    page_title="EmergeRoute dashboard",
    page_icon=str(FAVICON) if FAVICON.exists() else None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_splash()

UPLOADED_CFG = "simulation_uploaded.sumocfg"
SCENARIO_NAMES = {
    "simulation.sumocfg": "Light traffic",
    "simulation_heavy_stable.sumocfg": "Heavy congestion",
    "simulation_realistic.sumocfg": "Realistic (varying) traffic",
    "simulation_heavy.sumocfg": "Gridlock (worst-case)",
    UPLOADED_CFG: "Uploaded video",
}

# ---------------------------------------------------------------------------
# Theme. Warm black ground, one amber accent, rectangular controls.
# No scroll animation, no gradients, no JS.
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@300;400;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
        --ground: #0c0b09;
        --surface: #15130f;
        --line: #2a261d;
        --text: #ece7dc;
        --muted: #9a9283;
        --accent: #d6a24a;
        --jam: #c8553d;
        --good: #8fb582;
        --sans: "Red Hat Display", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
        --mono: "IBM Plex Mono", ui-monospace, Consolas, monospace;
    }

    html, body, .stApp { font-family: var(--sans); }
    /* Keep Streamlit's icon font: icon spans must not get the text font, or their names print as words */
    [class*="st-"]:not([data-testid="stIconMaterial"]):not([class*="material"]):not([class*="Material"]) { font-family: var(--sans); }
    .stApp { background-color: var(--ground); color: var(--text); font-weight: 300; }
    .block-container { padding-top: 1.5rem; max-width: 1280px; }
    /* No sidebar: hide it and its open/close arrows */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
    [data-testid="stExpandSidebarButton"], [data-testid="collapsedControl"] { display: none !important; }

    /* Hide Streamlit chrome */
    #MainMenu, footer, .stDeployButton, [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    h1, h2, h3 { font-family: var(--sans); font-weight: 300; letter-spacing: -0.01em; color: var(--text); }
    h1 { font-size: clamp(1.9rem, 3.6vw, 2.8rem); }
    h2 { font-size: clamp(1.4rem, 2.4vw, 1.9rem); padding-top: 1.5rem; }
    h3 { font-weight: 600; font-size: 1.2rem; }
    p, li, label, [data-testid="stMarkdownContainer"] { color: var(--text); }
    [data-testid="stCaptionContainer"], .stCaption { color: var(--muted); }
    hr { border-color: var(--line); }
    a { color: var(--accent); text-underline-offset: 3px; }

    .appbar {
        display: flex; justify-content: space-between; align-items: center;
        border-bottom: 1px solid var(--line); padding: 0 0 0.9rem 0; margin-bottom: 1.6rem;
    }
    .appbar .mark { font-weight: 600; letter-spacing: 0.06em; color: var(--text); text-decoration: none; }
    .appbar .nav a { color: var(--muted); text-decoration: none; font-size: 0.92rem; margin-left: 1.5rem; }
    .appbar .nav a:hover { color: var(--text); }

    /* Buttons: rectangular, 2px radius */
    .stButton > button, button[data-testid="stBaseButton-secondary"], button[data-testid="stBaseButton-primary"] {
        border-radius: 2px; font-family: var(--sans); font-weight: 600;
    }
    button[data-testid="stBaseButton-secondary"], .stButton > button[kind="secondary"] {
        background: transparent; color: var(--text); border: 1px solid var(--line);
    }
    button[data-testid="stBaseButton-secondary"]:hover, .stButton > button[kind="secondary"]:hover {
        border-color: var(--accent); color: var(--accent);
    }
    button[data-testid="stBaseButton-primary"], .stButton > button[kind="primary"] {
        background: var(--accent); color: #14100a; border: 1px solid var(--accent);
    }
    button[data-testid="stBaseButton-primary"]:hover, .stButton > button[kind="primary"]:hover {
        background: var(--text); border-color: var(--text); color: #14100a;
    }
    button:focus-visible, a:focus-visible, input:focus-visible { outline: 2px solid var(--accent) !important; outline-offset: 2px; }

    /* Inputs */
    [data-baseweb="select"] > div, [data-baseweb="input"] > div, .stTextInput input {
        background-color: var(--surface); border-color: var(--line); border-radius: 2px;
    }
    [data-testid="stFileUploaderDropzone"] { background-color: var(--surface); border: 1px dashed var(--line); border-radius: 2px; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--line); border-radius: 2px; background: var(--surface); }

    /* Cards and panels */
    .card {
        background-color: var(--surface); border: 1px solid var(--line);
        border-radius: 2px; padding: 1.1rem 1.3rem; margin-bottom: 0.9rem;
    }
    .card-label { font-size: 0.85rem; color: var(--muted); margin-bottom: 0.3rem; }
    .card-value { font-family: var(--mono); font-size: 1.55rem; font-weight: 500; color: var(--text); }

    .stat-bar { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-bottom: 1.1rem; }
    .stat-pill {
        background-color: var(--surface); border: 1px solid var(--line);
        border-radius: 2px; padding: 0.5rem 0.85rem; font-size: 0.88rem; color: var(--muted);
    }
    .stat-pill b { color: var(--text); font-family: var(--mono); font-weight: 500; }

    .status-banner {
        background-color: var(--surface); border-left: 3px solid var(--accent);
        border-radius: 2px; padding: 0.8rem 1.1rem; margin-bottom: 0.7rem; font-size: 0.97rem;
    }
    .status-banner.ok { border-left-color: var(--good); }

    .pareto-tag {
        display: inline-block; background-color: transparent; color: var(--good);
        border: 1px solid var(--good); font-size: 0.8rem; font-weight: 600;
        padding: 0.1rem 0.5rem; border-radius: 2px; margin-bottom: 0.5rem;
    }

    .zone-card {
        background-color: var(--surface); border: 1px solid var(--line);
        border-radius: 2px; padding: 0.9rem 1.1rem; margin-bottom: 0.7rem;
    }
    .zone-id { font-family: var(--mono); font-size: 0.92rem; color: var(--text); }
    .zone-queue { font-family: var(--mono); font-size: 1.5rem; font-weight: 500; margin-top: 0.2rem; }
    .zone-label { font-size: 0.82rem; color: var(--muted); }

    .event-row {
        border-left: 3px solid var(--accent); background-color: var(--surface);
        border-radius: 2px; padding: 0.55rem 0.9rem; margin-bottom: 0.4rem;
        font-size: 0.9rem; color: var(--text);
    }
    .event-row b { color: var(--accent); font-weight: 600; }

    .car-grid { display: grid; grid-template-columns: 1fr 1fr 1.6fr; gap: 0.8rem; margin-bottom: 1rem; }
    @media (max-width: 900px) { .car-grid { grid-template-columns: 1fr; } }
    .car-card { background-color: var(--surface); border: 1px solid var(--line); border-radius: 2px; padding: 1rem 1.2rem; }
    .car-body { font-size: 0.97rem; color: var(--text); line-height: 1.55; }
    .src-tag {
        display: inline-block; font-family: var(--mono); font-size: 0.72rem;
        color: var(--muted); border: 1px solid var(--line); border-radius: 2px;
        padding: 0.05rem 0.4rem; margin-left: 0.5rem;
    }

    .delta-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; margin: 0.4rem 0 1rem 0; }
    .delta-table th { text-align: left; font-weight: 400; font-size: 0.85rem; color: var(--muted);
                      padding: 0.5rem 0.8rem; border-bottom: 1px solid var(--line); }
    .delta-table td { padding: 0.55rem 0.8rem; border-bottom: 1px solid var(--line); color: var(--text); font-family: var(--mono); }
    .delta-table td:first-child { font-family: var(--sans); }
    .delta-good { color: var(--good) !important; font-weight: 500; }
    .delta-bad { color: var(--jam) !important; font-weight: 500; }
    .delta-flat { color: var(--muted) !important; }

    div[data-testid="stExpander"] { background-color: var(--surface); border: 1px solid var(--line); border-radius: 2px; }


    /* ---- Layout pass: ruled sections instead of identical boxes ---- */
    .block-container { padding-top: 1.2rem; }
    h2 { padding-top: 3rem; margin-bottom: 0.4rem; }
    .hero-lead { font-size: 1.15rem; color: var(--text); max-width: 44rem; margin: 0.4rem 0 1.4rem 0; line-height: 1.55; }
    .start { margin: 0 0 1.4rem 0; padding: 0; list-style: none; max-width: 44rem; counter-reset: s; }
    .start li { counter-increment: s; border-top: 1px solid var(--line); padding: 0.7rem 0 0.7rem 2.2rem; position: relative; color: var(--muted); font-size: 0.97rem; line-height: 1.5; }
    .start li::before { content: counter(s); position: absolute; left: 0; top: 0.7rem; font-family: var(--mono); color: var(--accent); }
    .start li b { color: var(--text); font-weight: 600; }
    .index { font-size: 0.92rem; margin-bottom: 1rem; }
    .index a { color: var(--muted); text-decoration: none; margin-right: 1.4rem; border-bottom: 1px solid var(--line); }
    .index a:hover { color: var(--text); border-bottom-color: var(--accent); }

    .step { border-top: 1px solid var(--line); padding: 0.9rem 0.4rem 1rem 0; margin-bottom: 0.6rem; }

    .card { background-color: transparent; border: none; border-top: 1px solid var(--line); border-radius: 0; padding: 0.9rem 0.4rem 0.5rem 0; margin-bottom: 0.4rem; }
    .card-value { font-size: 2rem; }
    .zone-card { background-color: transparent; border: none; border-top: 1px solid var(--line); border-radius: 0; padding: 0.9rem 0.4rem 0.6rem 0; }
    .car-card { background-color: transparent; border: none; border-top: 2px solid var(--accent); border-radius: 0; padding: 0.9rem 0.6rem 0.6rem 0; }

    .site-footer {
        border-top: 1px solid var(--line); margin-top: 3rem; padding-top: 1.2rem;
        display: flex; flex-wrap: wrap; justify-content: space-between; gap: 1rem;
        color: var(--muted); font-size: 0.9rem;
    }
    .site-footer a { color: var(--muted); text-decoration: none; margin-left: 1.5rem; }
    .site-footer a:hover { color: var(--text); }
</style>
""", unsafe_allow_html=True)

render_background()
render_smooth_scroll()

st.markdown(
    f'<div class="appbar"><a class="mark" href="{LANDING_URL}" target="_self">EmergeRoute</a>'
    f'<span class="nav"><a href="{LANDING_URL}" target="_self">Overview</a></span></div>',
    unsafe_allow_html=True,
)
with st.container():
    st.title("Traffic policy dashboard")
    st.markdown(
        '<p class="hero-lead">Test a signal change in simulation before anyone touches a real signal. '
        'Generate candidate policies and compare each one against doing nothing.</p>'
        '<ol class="start">'
        '<li><b>Run a scenario.</b> Pick a traffic scenario and generate policies.</li>'
        '<li><b>Try a real area.</b> Search a place on the map and simulate its street layout.</li>'
        '<li><b>Use your own video.</b> Upload a clip to set the traffic demand.</li>'
        '</ol>'
        '<div class="index">'
        '<a href="#real-area-traffic-map" target="_self">Real-area map</a>'
        '<a href="#how-it-works" target="_self">How it works</a>'
        '<a href="#run-a-scenario" target="_self">Run a scenario</a>'
        '<a href="#analyze-your-own-traffic-video" target="_self">Video analysis</a>'
        '</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Real-Area Traffic Map -- first thing on the page, ahead of the synthetic
# scenario pipeline below, since it's the entry point for a real place.
# ---------------------------------------------------------------------------
render_map_section()

st.divider()

# ---------------------------------------------------------------------------
# How it works -- explains the synthetic-scenario pipeline before its
# controls appear right below.
# ---------------------------------------------------------------------------
st.header("How it works")
steps = [
    ("01", "Probe the network", "A short SUMO simulation measures queue lengths at every traffic-light intersection, so the busiest ones are measured, not guessed."),
    ("02", "Predict (optional)", "XGBoost, trained on your own logged simulation history, forecasts near-future congestion so the system can act ahead of a jam instead of only reacting."),
    ("03", "Generate candidates", "A rule-based policy generator proposes several explainable traffic-control actions: signal timing extensions, network-wide adjustments, emergency corridors."),
    ("04", "Simulate every candidate", "Each candidate policy runs end to end in a full SUMO simulation. The results are measured, not estimated."),
    ("05", "Score with NSGA-II", "Every candidate is ranked across six objectives at once: congestion, travel time, safety, emergency delay, emissions, and fairness."),
    ("06", "Recommend, with reasons", "The top policy is surfaced with a plain-language explanation of why it was chosen over the alternatives."),
]
step_cols = st.columns(3)
for i, (num, title, desc) in enumerate(steps):
    with step_cols[i % 3]:
        st.markdown(f"""
        <div class="step">
            <div class="card-label" style="font-family:var(--mono); color:var(--accent);">Step {num}</div>
            <div style="font-size:1.08rem; font-weight:600; color:var(--text); margin-bottom:0.4rem;">{title}</div>
            <div style="font-size:0.9rem; color:var(--muted); line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Policy generation -- the synthetic-scenario control bar, now positioned
# under "How it works" rather than above it.
# ---------------------------------------------------------------------------
scenario_options = [
    "simulation.sumocfg",
    "simulation_heavy_stable.sumocfg",
    "simulation_realistic.sumocfg",
    "simulation_heavy.sumocfg",
]
if Path(UPLOADED_CFG).exists():
    scenario_options.append(UPLOADED_CFG)

st.header("Run a scenario")
with st.container(border=True):
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        sumocfg = st.selectbox(
            "Traffic scenario",
            options=scenario_options,
            format_func=lambda x: SCENARIO_NAMES.get(x, "Uploaded video"),
        )
    with c2:
        if sumocfg == UPLOADED_CFG:
            # The XGBoost model is trained on the other scenarios' logs, so it
            # would not say anything real about an uploaded video.
            st.caption("AI prediction is off for uploaded videos (the model was trained on other scenarios). Set the level below.")
            use_prediction = False
        else:
            use_prediction = st.checkbox(
                "Use AI prediction (XGBoost) to set congestion level",
                value=True,
                help="Predicts near-future congestion from recent traffic history, instead of setting it manually.",
            )
        if not use_prediction:
            congestion_level = st.select_slider(
                "Congestion level",
                options=["low", "moderate", "high"],
                value="high",
            )
        else:
            congestion_level = None
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        run_button = st.button("Generate & Test Policies", type="primary", use_container_width=True)


def metric_card(label: str, value: str):
    st.markdown(f'<div class="card"><div class="card-label">{label}</div><div class="card-value">{value}</div></div>', unsafe_allow_html=True)


def render_metric_cards(m):
    """Eight metric cards in two rows of four."""
    rows = [
        [("Congestion delay", f"{m['avg_time_loss_s']:.0f}s"),
         ("Avg travel time", f"{m['avg_travel_time_s']:.0f}s"),
         ("Worst-case wait", f"{m['max_waiting_time_s']:.0f}s"),
         ("CO2 emitted", f"{m['co2_kg']:.1f}kg")],
        [("Fairness gap", f"{m['fairness_gap_s']:.0f}s"),
         ("Trips completed", str(m["completed_trips"])),
         ("Safety events", str(m.get("safety_events", 0))),
         ("Emergency delay", f"{m.get('emergency_delay_s', 0):.0f}s")],
    ]
    for row in rows:
        for col, (label, value) in zip(st.columns(4), row):
            with col:
                metric_card(label, value)
    if m.get("emergency_vehicles_measured", 1) == 0:
        st.caption("No emergency vehicle was measured in this run, so emergency delay shows 0 for every policy.")


def stat_pill(label: str, value):
    return f'<div class="stat-pill">{label}: <b>{value}</b></div>'


def render_video_sections():
    """Video upload + detection output. Shown in both the landing and results views."""
    render_video_upload()
    render_detection_section()


PLOTLY_DARK = dict(
    paper_bgcolor="#15130f",
    plot_bgcolor="#15130f",
    font_color="#ece7dc",
    font_family="Red Hat Display, system-ui, sans-serif",
    colorway=["#d6a24a", "#9a9283", "#c8553d", "#8fb582", "#b98a4a", "#6d6657", "#e3c78f"],
    margin=dict(l=10, r=10, t=40, b=10),
)

if run_button:
    if use_prediction:
        traffic_log_map = {
            "simulation.sumocfg": "traffic_log.csv",
            "simulation_heavy.sumocfg": "traffic_log_long.csv",
            "simulation_realistic.sumocfg": "traffic_log_realistic.csv",
            "simulation_heavy_stable.sumocfg": "traffic_log_heavy.csv",
        }
        log_path = traffic_log_map.get(sumocfg, "traffic_log_realistic.csv")
        with st.spinner("Training prediction model on recent traffic history..."):
            model, feature_cols = train_predictor(log_path)
            df = pd.read_csv(log_path).sort_values("time_s").reset_index(drop=True)
            recent = df.tail(N_LAGS + 1)
            congestion_level = predict_congestion_level(model, feature_cols, recent)

    with st.spinner("Probing network conditions..."):
        probe = probe_network(sumocfg=sumocfg)

    busiest_tls = probe["ranked_tls"]
    candidates = generate_candidate_policies(busiest_tls, congestion_level=congestion_level)

    with st.spinner(f"Testing {len(candidates)} candidate policies in SUMO simulation. This may take a few minutes..."):
        ranked = rank_policies(candidates, sumocfg=sumocfg)

    scenario_label = SCENARIO_NAMES.get(sumocfg, "Uploaded video")
    pareto_count = sum(1 for e in ranked if e["pareto_optimal"])

    st.markdown(
        '<div class="stat-bar">'
        + stat_pill("Scenario", scenario_label)
        + stat_pill("Intersections monitored", len(busiest_tls))
        + stat_pill("Peak vehicles (probe)", probe["peak_vehicles"])
        + stat_pill("Jam events detected", len(probe["events"]))
        + stat_pill("Policies tested", len(candidates))
        + stat_pill("Pareto-optimal", pareto_count)
        + '</div>',
        unsafe_allow_html=True,
    )
    if use_prediction:
        st.markdown(f'<div class="status-banner ok">Predicted near-future congestion level: <b>{congestion_level.upper()}</b> (based on recent traffic trend, via XGBoost)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-banner ok">Busiest intersections (by measured queue length): {", ".join(busiest_tls[:3])}</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # Zone cards
    # -----------------------------------------------------------------
    st.header("Monitored Intersections")
    top_zones = busiest_tls[:6]
    zone_cols = st.columns(3)
    max_q = max(probe["queue_totals"].values()) if probe["queue_totals"] else 1
    for i, tid in enumerate(top_zones):
        q = probe["queue_totals"][tid]
        severity = "SEVERE" if q > 0.66 * max_q else ("BUSY" if q > 0.33 * max_q else "NORMAL")
        color = "#c8553d" if severity == "SEVERE" else ("#d6a24a" if severity == "BUSY" else "#8fb582")
        with zone_cols[i % 3]:
            st.markdown(f"""
            <div class="zone-card">
                <div class="zone-id">{tid}</div>
                <div class="zone-queue" style="color:{color};">{q}</div>
                <div class="zone-label">accumulated queue, {severity.lower()}</div>
            </div>
            """, unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # Event feed
    # -----------------------------------------------------------------
    st.header("Traffic Events (probe window)")
    if probe["events"]:
        for ev in probe["events"][:10]:
            st.markdown(
                f'<div class="event-row"><b>Jam:</b> vehicle <b>{ev["vehicle_id"]}</b> '
                f'teleported after waiting too long, at t={ev["time_s"]}s</div>',
                unsafe_allow_html=True,
            )
        if len(probe["events"]) > 10:
            st.caption(f"+ {len(probe['events']) - 10} more events in the full probe window.")
    else:
        st.markdown('<div class="event-row" style="border-left-color:#8fb582;">No jam events detected in the probe window. Traffic flowed without major stalling.</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # Recommended policy
    # -----------------------------------------------------------------
    st.header("Recommended Policy")
    top = ranked[0]
    baseline = next((e for e in ranked if e["policy_name"].lower().startswith("baseline")), None)
    st.markdown(f"### {top['policy_name']}")

    # Condition / Action / Reason, all taken from this run's results
    cond_queues = ", ".join(f"{t} ({probe['queue_totals'][t]})" for t in busiest_tls[:3])
    if use_prediction:
        level_txt = f"predicted near-future congestion <b>{congestion_level.upper()}</b>"
        cond_tag = "Simulated, predicted"
    else:
        level_txt = f"congestion level set to <b>{congestion_level.upper()}</b>"
        cond_tag = "Simulated"
    st.markdown(f"""
    <div class="car-grid">
      <div class="car-card">
        <div class="card-label">Condition<span class="src-tag">{cond_tag}</span></div>
        <div class="car-body">Longest measured queues at {cond_queues}; {level_txt}.</div>
      </div>
      <div class="car-card">
        <div class="card-label">Action<span class="src-tag">Derived</span></div>
        <div class="car-body"><b>{top['policy_name']}</b></div>
      </div>
      <div class="car-card">
        <div class="card-label">Reason<span class="src-tag">Derived</span></div>
        <div class="car-body">{top['explanation']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    m = top["metrics"]
    render_metric_cards(m)

    # Change against the do-nothing baseline
    if baseline is not None and baseline is top:
        st.markdown('<div class="status-banner">No tested change beat the baseline in this run, so the recommendation is to leave the signals as they are.</div>', unsafe_allow_html=True)
    elif baseline is not None:
        bm = baseline["metrics"]
        delta_rows = [
            ("Congestion delay", "avg_time_loss_s", "s", True, 0),
            ("Avg travel time", "avg_travel_time_s", "s", True, 0),
            ("Worst-case wait", "max_waiting_time_s", "s", True, 0),
            ("CO2 emitted", "co2_kg", "kg", True, 1),
            ("Fairness gap", "fairness_gap_s", "s", True, 0),
            ("Trips completed", "completed_trips", "", False, 0),
            ("Safety events", "safety_events", "", True, 0),
            ("Emergency delay", "emergency_delay_s", "s", True, 0),
        ]
        body = ""
        for label, key, unit, lower_better, dec in delta_rows:
            b, r = bm.get(key, 0), m.get(key, 0)
            d = r - b
            pct = (d / b * 100) if b else 0.0
            if abs(pct) < 0.5:
                cls = "delta-flat"
            else:
                improved = (d < 0) if lower_better else (d > 0)
                cls = "delta-good" if improved else "delta-bad"
            body += (
                f"<tr><td>{label}</td><td>{b:.{dec}f}{unit}</td><td>{r:.{dec}f}{unit}</td>"
                f'<td class="{cls}">{d:+.{dec}f}{unit} ({pct:+.1f}%)</td></tr>'
            )
        st.markdown(
            '<div class="card-label" style="margin-top:0.8rem;">Change vs baseline (no changes)<span class="src-tag">Derived</span></div>'
            '<table class="delta-table"><tr><th>Metric</th><th>Baseline</th><th>Recommended</th><th>Change</th></tr>'
            + body + '</table>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="status-banner">Scope: values come from SUMO simulation runs. Recommendations are decision support and are not applied to real traffic signals.</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # Charts -- Plotly, explicit rank order (fixes the alphabetical-sort
    # bug st.bar_chart had), plus two real donut charts.
    # -----------------------------------------------------------------
    st.header("Policy Comparison")

    policy_order = [f"#{e['rank']} {e['policy_name']}" for e in ranked]
    comp_df = pd.DataFrame([
        {
            "Policy": f"#{e['rank']} {e['policy_name']}",
            "Congestion delay (s)": e["metrics"]["avg_time_loss_s"],
            "Avg travel time (s)": e["metrics"]["avg_travel_time_s"],
            "CO2 (kg)": e["metrics"]["co2_kg"],
        }
        for e in ranked
    ])
    comp_melted = comp_df.melt(id_vars="Policy", var_name="Metric", value_name="Value")
    fig_bar = px.bar(
        comp_melted, x="Policy", y="Value", color="Metric", barmode="group",
        category_orders={"Policy": policy_order},
    )
    fig_bar.update_layout(**PLOTLY_DARK, legend=dict(orientation="h", y=1.15))
    st.plotly_chart(fig_bar, use_container_width=True)

    d1, d2 = st.columns(2)
    with d1:
        st.caption("Share of total CO2 across tested policies")
        fig_donut1 = go.Figure(data=[go.Pie(
            labels=comp_df["Policy"], values=comp_df["CO2 (kg)"], hole=0.6,
            marker=dict(line=dict(color="#0c0b09", width=2)),
        )])
        fig_donut1.update_layout(**PLOTLY_DARK, showlegend=True, legend=dict(font=dict(size=10)))
        st.plotly_chart(fig_donut1, use_container_width=True)
    with d2:
        st.caption("Share of total congestion delay across tested policies")
        fig_donut2 = go.Figure(data=[go.Pie(
            labels=comp_df["Policy"], values=comp_df["Congestion delay (s)"], hole=0.6,
            marker=dict(line=dict(color="#0c0b09", width=2)),
        )])
        fig_donut2.update_layout(**PLOTLY_DARK, showlegend=True, legend=dict(font=dict(size=10)))
        st.plotly_chart(fig_donut2, use_container_width=True)

    fair_df = pd.DataFrame([
        {
            "Policy": f"#{e['rank']} {e['policy_name']}",
            "Fairness gap (s)": e["metrics"]["fairness_gap_s"],
            "Trips completed": e["metrics"]["completed_trips"],
        }
        for e in ranked
    ])
    f1, f2 = st.columns(2)
    with f1:
        fig_fair = px.bar(fair_df, x="Policy", y="Fairness gap (s)", category_orders={"Policy": policy_order})
        fig_fair.update_traces(marker_color="#d6a24a")
        fig_fair.update_layout(**PLOTLY_DARK)
        st.plotly_chart(fig_fair, use_container_width=True)
    with f2:
        fig_trips = px.bar(fair_df, x="Policy", y="Trips completed", category_orders={"Policy": policy_order})
        fig_trips.update_traces(marker_color="#8fb582")
        fig_trips.update_layout(**PLOTLY_DARK)
        st.plotly_chart(fig_trips, use_container_width=True)

    # -----------------------------------------------------------------
    # All candidates
    # -----------------------------------------------------------------
    st.header("All Candidate Policies (ranked)")
    for entry in ranked:
        with st.expander(f"#{entry['rank']}: {entry['policy_name']}"):
            if entry["pareto_optimal"]:
                st.markdown('<span class="pareto-tag">Pareto-optimal</span>', unsafe_allow_html=True)
            st.write(entry["explanation"])
            m = entry["metrics"]
            render_metric_cards(m)

    # -----------------------------------------------------------------
    # Video upload + vehicle detection (also shown in the landing view)
    # -----------------------------------------------------------------
    render_video_sections()

    st.caption(
        "Policies are tested in SUMO simulation runs, not estimated, and ranked "
        "using NSGA-II multi-objective optimization across congestion, travel time, safety, "
        "emergency delay, environmental impact, and fairness. Pareto-optimal policies "
        "represent genuine trade-offs: no other tested policy strictly beats them on every objective. "
        "Zone cards, events, and all stats above come directly from simulation probes. Nothing shown is placeholder or fabricated."
    )

else:
    st.markdown("""
    <div class="status-banner ok" style="font-size:1rem;">
        Configure a scenario above and click <b>Generate & Test Policies</b> to run the full pipeline on a SUMO simulation.
    </div>
    """, unsafe_allow_html=True)

    # Video upload + vehicle detection
    render_video_sections()

    st.header("Built on")
    stack = ["SUMO", "Python", "pymoo (NSGA-II)", "XGBoost", "Streamlit", "Plotly", "Folium"]
    st.markdown(
        '<div class="stat-bar">' + "".join(f'<div class="stat-pill">{s}</div>' for s in stack) + '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div class="status-banner">
        Every number this dashboard shows after you run a scenario (queue lengths, predicted congestion, policy scores) comes directly from a SUMO simulation or a model trained on your own logged data. Nothing is placeholder.
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    f'<div class="site-footer"><span>EmergeRoute. Simulation-based decision support.</span>'
    f'<span><a href="{PRIVACY_URL}" target="_self">Privacy policy</a>'
    f'<a href="{TERMS_URL}" target="_self">Terms and conditions</a></span></div>',
    unsafe_allow_html=True,
)
