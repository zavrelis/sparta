# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="General Player Impact Score (GPIS)",
    layout="wide"
)

# =================================================
# DATA LOADING
# =================================================
@st.cache_data
def load_data():
    players = pd.read_parquet("player_metrics.parquet")
    similarity = pd.read_parquet("similarity_matrix.parquet")
    return players, similarity

df, similarity_df = load_data()

# =================================================
# SESSION STATE INIT
# =================================================
if "player_main" not in st.session_state:
    st.session_state.player_main = df.index[0]

if "player_top" not in st.session_state:
    st.session_state.player_top = st.session_state.player_main

if "player_similarity" not in st.session_state:
    st.session_state.player_similarity = st.session_state.player_main

# =================================================
# HELPERS
# =================================================
def section_divider(space="3rem"):
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"<div style='height:{space}'></div>", unsafe_allow_html=True)


def best_match_for(player: str) -> str:
    return (
        similarity_df[player]
        .drop(player)
        .sort_values(ascending=False)
        .index[0]
    )


def find_similar_players(player, top_n=10):
    sims = (
        similarity_df[player]
        .drop(player)
        .sort_values(ascending=False)
        .head(top_n)
    )
    return sims.to_frame("Similarity").join(df[["GPIS", "minutes_played"]])


def radar_chart(p1, p2, features, labels):
    v1 = df.loc[p1, features].tolist()
    v2 = df.loc[p2, features].tolist()

    v1 += [v1[0]]
    v2 += [v2[0]]
    labels = labels + [labels[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=v1,
        theta=labels,
        fill="toself",
        name=p1,
        line=dict(color="#1f77b4", width=3),
        fillcolor="rgba(31,119,180,0.35)"
    ))

    fig.add_trace(go.Scatterpolar(
        r=v2,
        theta=labels,
        fill="toself",
        name=p2,
        line=dict(color="#d62728", width=3),
        fillcolor="rgba(214,39,40,0.35)"
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(range=[-2.5, 2.5])),
        margin=dict(l=30, r=30, t=60, b=30),
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center")
    )

    return fig


def gpis_quality(percentile):
    if percentile >= 85:
        return "Elite impact", "#2ecc71"
    elif percentile >= 60:
        return "Above average", "#3498db"
    elif percentile >= 40:
        return "League average", "#f1c40f"
    else:
        return "Below average", "#e74c3c"


# =================================================
# FEATURES
# =================================================
style_features = [
    "progression_raw_per90_z",
    "xg_per90_z",
    "shot_assists_per90_z",
    "goal_assists_per90_z",
    "defensive_raw_per90_z"
]

style_labels = [
    "Progression",
    "Threat (xG)",
    "Shot Assists",
    "Goal Assists",
    "Defensive Impact"
]

# =================================================
# CALLBACKS (sync two selects into one truth)
# =================================================
def sync_from_top():
    st.session_state.player_main = st.session_state.player_top
    st.session_state.player_similarity = st.session_state.player_top


def sync_from_similarity():
    st.session_state.player_main = st.session_state.player_similarity
    st.session_state.player_top = st.session_state.player_similarity


# =================================================
# HERO SECTION (LOGO + AUTHOR)
# =================================================

col_logo, col_text = st.columns([1, 4])

with col_logo:
    st.image(
        "sparta.png", 
        width=120
    )

with col_text:
    st.markdown("""
    ### General Player Impact Score (GPIS)
    **Technical assignment – player metric & similarity system**

    *Author:* **Ivan Zavřel**  
    *Focus:* custom football analytics metric, player rating & similarity  
    """)

section_divider("2rem")



# =================================================
# INTRO / PROJECT EXPLANATION (place before metrics)
# =================================================
st.markdown("""
### What this project does (challenge deliverables)

This app was built to meet the following requirements:

- **Create at least 1 new metric** → **GPIS (General Player Impact Score)**

- **Build a rating or similarity system** → player rating via GPIS + a style-based similarity system
            
- **Visualise the results** → league-wide distribution + radar style comparison
            
- **Document the approach** → this section summarises the metric and the system directly in the app
""")

with st.expander("Method summary (metric + similarity system)", expanded=False):
    st.markdown("""
#### 1) The metric: General Player Impact Score (GPIS)

**GPIS** is a composite impact metric intended to describe how much a player contributes to overall play,
not just goals or assists.

It combines multiple contribution dimensions (per 90 minutes), such as:
- **Ball progression**
- **Attacking threat (xG)**
- **Creativity** (assists / shot assists)
- **Defensive involvement**

The underlying inputs are **standardised (z-scores)** to make players comparable across metrics.
The final GPIS value should be interpreted as a **balanced impact signal**, not a pure attacking or defensive stat.

#### 2) Rating vs. similarity

- **Rating:** GPIS can be used as a league-wide rating number (with percentile context).
- **Similarity:** the similarity system compares players by their **contribution profile / style** using the
  underlying standardised feature vector (not by name, team, or popularity).

This distinction matters because two players can be highly similar in style even if:
- one has much higher GPIS,
- or they play in different teams/contexts.

#### 3) How to read this app

- **GPIS value + percentile** → overall impact relative to the league
- **League-wide GPIS distribution** → where the player sits among all players
- **Similarity table** → closest stylistic matches
- **Radar chart** → visual style comparison across key dimensions

> Note: GPIS and similarity are decision-support tools and should not be treated as absolute truth.
""")

st.markdown("""
**Libraries used in this app:** pandas, plotly, streamlit, sklearn, missingno, matplotlib
(Feature engineering and matrix preparation were done in the notebook workflow.)
""")

section_divider("2.5rem")



# =================================================
# HERO
# =================================================
st.title("General Player Impact Score (GPIS)")
st.markdown("""
**GPIS** measures how much a player contributes to their team's overall performance.

It is **not a rating or ranking**, but an impact metric combining:
- progression
- attacking threat
- creativity
- defensive involvement

The similarity system compares **playing styles**, not performance level.
""")

# =================================================
# PLAYER SELECTION (PRIMARY)
# =================================================
st.markdown("### Select player")

col_sel, _ = st.columns([3, 7])
with col_sel:
    st.selectbox(
        "",
        df.index,
        key="player_top",
        on_change=sync_from_top,
        label_visibility="collapsed"
    )

player = st.session_state.player_main
player_row = df.loc[player]

# =================================================
# PLAYER OVERVIEW
# =================================================
st.subheader("Player Overview")

gpis = player_row["GPIS"]
percentile = df["GPIS"].rank(pct=True).loc[player] * 100
label, color = gpis_quality(percentile)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div style="
            font-size: 3rem;
            font-weight: 700;
            color: {color};
            line-height: 1.1;
        ">
            {gpis:.2f}
        </div>
        <div style="margin-top:0.25rem; font-size:0.95rem;">
            <b>{label}</b> · Percentile {percentile:.1f}
            <span style="color:#6c757d;">
                (Top {100-percentile:.0f}%)
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.write(f"**Matches:** {int(player_row.get('matches_played', 0))}")
    st.write(f"**Minutes:** {int(player_row['minutes_played'])}")

# =================================================
# DISTRIBUTION
# =================================================
st.markdown("### League-wide GPIS distribution")
st.caption("Sorted GPIS values with highlighted selected player.")

dist_df = df.reset_index().sort_values("GPIS")

fig_dist = go.Figure()

fig_dist.add_bar(
    x=dist_df["player"],
    y=dist_df["GPIS"],
    name="All players",
    marker=dict(color="#3498db", opacity=0.3)
)

fig_dist.add_bar(
    x=[player],
    y=[df.loc[player, "GPIS"]],
    name="Selected player",
    marker=dict(color="#e74c3c")
)

fig_dist.update_layout(
    height=320,
    barmode="overlay",
    xaxis=dict(showticklabels=False)
)

st.plotly_chart(fig_dist, use_container_width=True)

section_divider()

# =================================================
# SIMILARITY SYSTEM
# =================================================
st.header("Similarity system")
st.markdown("""
The similarity system identifies players with **comparable contribution profiles**.

Two players can be highly similar even if:
- one has much higher GPIS
- they play in different teams
""")


col_vs1, col_vs2, col_vs3 = st.columns([3, 1, 3])

with col_vs1:
    st.selectbox(
        "Player A",
        df.index,
        key="player_similarity",
        on_change=sync_from_similarity
    )

with col_vs2:
    st.markdown("<h3 style='text-align:center;'>vs.</h3>", unsafe_allow_html=True)

similar_options = find_similar_players(player).index.tolist()

default_b = best_match_for(player)
default_index = similar_options.index(default_b)

with col_vs3:
    player_b = st.selectbox(
        "Player B",
        similar_options,
        index=default_index
    )


# =================================================
# OUTPUT
# =================================================
similar_df = (
    find_similar_players(player)
    .reset_index()
    .rename(columns={
        "index": "Player",
        "Similarity": "Similarity (%)",
        "GPIS": "GPIS",
        "minutes_played": "Minutes Played"
    })
)

# převod similarity na %
similar_df["Similarity (%)"] = similar_df["Similarity (%)"] * 100


def highlight_best(row):
    player_name = row.iloc[0]  # první sloupec = Player
    if player_name == player_b:
        return ["background-color: rgba(214,39,40,0.15)"] * len(row)
    return [""] * len(row)


col_left, col_right = st.columns([3, 4])

with col_left:
    st.markdown("**Most similar players**")
    st.dataframe(
    similar_df.style
    .apply(highlight_best, axis=1)
    .format({
        "Similarity (%)": "{:.1f}",
        "GPIS": "{:.2f}",
        "Minutes Played": "{:.0f}"
    }),
    use_container_width=True
)


with col_right:
    st.markdown("**Style comparison**")
    fig = radar_chart(
        player,
        player_b,
        style_features,
        style_labels.copy()
    )
    st.plotly_chart(fig, use_container_width=True)

# =================================================
# FOOTER
# =================================================
st.caption(
    "GPIS and similarity metrics are intended as decision-support tools, "
    "not absolute performance rankings."
)
