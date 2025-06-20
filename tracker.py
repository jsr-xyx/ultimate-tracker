import streamlit as st
import pandas as pd
import altair as alt
import os

DATA_FILE = "ultimate_stats.csv"

STAT_COLUMNS = [
    "Player", "Game", "Team Score", "Opponent Score",
    "Goals", "Assists", "Drops", "Throwaways", "Stall Downs",
    "Total Pulls", "Out-of-Bounds Pulls", "Pull Success %",
    "Defensive Blocks", "Turnovers", "Plus/Minus"
]

# Load existing data
def load_stats():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=STAT_COLUMNS)

# Save updated data
def save_stats(df):
    df.to_csv(DATA_FILE, index=False)

# Logging form
def log_stat_form(df):
    with st.form("log_form"):
        st.subheader("Log Game Stats")

        col1, col2 = st.columns(2)
        team_score = col1.number_input("Team Score", 0)
        opponent_score = col2.number_input("Opponent Score", 0)

        col3, col4 = st.columns(2)
        player = col3.text_input("Player Name")
        game = col4.text_input("Game / Date")

        col5, col6 = st.columns(2)
        goals = col5.number_input("Goals", 0)
        assists = col6.number_input("Assists", 0)

        col7, col8 = st.columns(2)
        drops = col7.number_input("Drops", 0)
        throwaways = col8.number_input("Throwaways", 0)

        col9, col10 = st.columns(2)
        stalls = col9.number_input("Stall Downs", 0)
        blocks = col10.number_input("Defensive Blocks", 0)

        col11, col12 = st.columns(2)
        pulls = col11.number_input("Total Pulls", 0)
        ob_pulls = col12.number_input("Out-of-Bounds Pulls", 0)

        submitted = st.form_submit_button("+ Add Stat")

        if submitted and player and game:
            turnovers = drops + throwaways + stalls
            plus_minus = (goals + assists + blocks) - turnovers
            in_bounds = max(pulls - ob_pulls, 0)
            pull_success = (in_bounds / pulls * 100) if pulls > 0 else None

            new_row = pd.DataFrame([{
                "Player": player,
                "Game": game,
                "Team Score": team_score,
                "Opponent Score": opponent_score,
                "Goals": goals,
                "Assists": assists,
                "Drops": drops,
                "Throwaways": throwaways,
                "Stall Downs": stalls,
                "Total Pulls": pulls,
                "Out-of-Bounds Pulls": ob_pulls,
                "Pull Success %": pull_success,
                "Defensive Blocks": blocks,
                "Turnovers": turnovers,
                "Plus/Minus": plus_minus
            }])

            df = pd.concat([df, new_row], ignore_index=True)
            save_stats(df)
            st.success("Game stats added!")

    return df

# Filtering
def show_filtered_table(df):
    st.subheader("Filter Stats")

    players = ["All"] + sorted(df["Player"].dropna().unique())
    games = ["All"] + sorted(df["Game"].dropna().unique())

    col1, col2 = st.columns(2)
    selected_player = col1.selectbox("Player", players)
    selected_game = col2.selectbox("Game", games)

    filtered = df.copy()
    if selected_player != "All":
        filtered = filtered[filtered["Player"] == selected_player]
    if selected_game != "All":
        filtered = filtered[filtered["Game"] == selected_game]

    st.subheader("Game Log")
    st.dataframe(filtered)

    return filtered

# Chart
def show_trend_chart(filtered_df):
    st.subheader("Stat Trend")

    stat = st.selectbox(
        "Choose stat to chart",
        ["Goals", "Assists", "Drops", "Throwaways", "Stall Downs",
         "Out-of-Bounds Pulls", "Total Pulls", "Pull Success %",
         "Turnovers", "Defensive Blocks", "Plus/Minus"]
    )

    if not filtered_df.empty:
        chart = alt.Chart(filtered_df).mark_line(point=True).encode(
            x="Game:N",
            y=stat,
            color="Player:N",
            tooltip=["Player", "Game", stat]
        ).properties(title=f"{stat} Over Games")
        st.altair_chart(chart, use_container_width=True)

# Export + Delete
def export_and_reset(df):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "filtered_stats.csv", "text/csv")

    st.subheader("Delete All Stats")
    if st.button("Delete All"):
        df = df.iloc[0:0]
        save_stats(df)
        st.success("All stats deleted.")
        st.rerun()

# Main App
def show():
    st.title("Ultimate Stats Tracker")
    st.caption("Track, filter, and visualize your Ultimate game stats.")

    stats_df = load_stats()
    stats_df = log_stat_form(stats_df)

    if stats_df.empty:
        st.info("No stats to display yet.")
        return

    filtered_df = show_filtered_table(stats_df)
    show_trend_chart(filtered_df)
    export_and_reset(filtered_df)

if __name__ == "__main__":
    show()
