import streamlit as st
import pandas as pd
import altair as alt
import os

FILE_PATH = "ultimate_stats.csv"

def load_data():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH)
    return pd.DataFrame(columns=[
        "Player", "Game", "Your Score", "Opponent Score", "Goals", "Assists",
        "Drops", "Throwaways", "Stall Downs", "Total Pulls", "OB Pulls", "Pull Success %",
        "Ds", "Turnovers", "+/-"
    ])

def save_data(df):
    df.to_csv(FILE_PATH, index=False)

def show():
    st.title("🥏 Ultimate Stats Tracker")
    st.write("Track your game-by-game Ultimate Frisbee stats — with trends, filters, and CSV export.")

    df = load_data()

    with st.form("log_form"):
        st.subheader("📋 Log a Stat")

        col0a, col0b = st.columns(2)
        my_score = col0a.number_input("Your Team Score", min_value=0, value=0)
        opp_score = col0b.number_input("Opponent Score", min_value=0, value=0)

        col1, col2 = st.columns(2)
        player = col1.text_input("Player Name")
        game = col2.text_input("Game / Date")

        col3, col4 = st.columns(2)
        goals = col3.number_input("Goals", min_value=0, value=0)
        assists = col4.number_input("Assists", min_value=0, value=0)

        col5, col6 = st.columns(2)
        drops = col5.number_input("Drops", min_value=0, value=0)
        throwaways = col6.number_input("Throwaways", min_value=0, value=0)

        col7, col8 = st.columns(2)
        stalls = col7.number_input("Stall Downs", min_value=0, value=0)
        ds = col8.number_input("Ds (Defensive Blocks)", min_value=0, value=0)

        col9, col10 = st.columns(2)
        total_pulls = col9.number_input("Total Pulls", min_value=0, value=0)
        ob_pulls = col10.number_input("OB Pulls", min_value=0, value=0)

        submit = st.form_submit_button("✅ Add Stat")

        if submit and player and game:
            turnovers = drops + throwaways + stalls
            plus_minus = (goals + assists + ds) - turnovers
            in_bounds_pulls = max(total_pulls - ob_pulls, 0)
            pull_success = (in_bounds_pulls / total_pulls * 100) if total_pulls > 0 else None

            new_entry = pd.DataFrame([{
                "Player": player,
                "Game": game,
                "Your Score": my_score,
                "Opponent Score": opp_score,
                "Goals": goals,
                "Assists": assists,
                "Drops": drops,
                "Throwaways": throwaways,
                "Stall Downs": stalls,
                "Total Pulls": total_pulls,
                "OB Pulls": ob_pulls,
                "Pull Success %": pull_success,
                "Ds": ds,
                "Turnovers": turnovers,
                "+/-": plus_minus
            }])

            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df)
            st.success("Stat added successfully!")

    if df.empty:
        st.info("No stats logged yet.")
        return

    # Filters
    st.subheader("🔍 Filter Stats")
    players = ["All"] + sorted(df["Player"].dropna().unique())
    games = ["All"] + sorted(df["Game"].dropna().unique())

    col1, col2 = st.columns(2)
    selected_player = col1.selectbox("Filter by Player", players)
    selected_game = col2.selectbox("Filter by Game", games)

    filtered_df = df.copy()
    if selected_player != "All":
        filtered_df = filtered_df[filtered_df["Player"] == selected_player]
    if selected_game != "All":
        filtered_df = filtered_df[filtered_df["Game"] == selected_game]

    st.subheader("📄 Game Log")
    st.dataframe(filtered_df)

    # Chart
    st.subheader("📈 Stat Trend")
    stat_to_chart = st.selectbox(
        "Select Stat to Chart",
        ["Goals", "Assists", "Drops", "Throwaways", "Stall Downs", "OB Pulls",
         "Total Pulls", "Pull Success %", "Turnovers", "Ds", "+/-"]
    )

    if not filtered_df.empty and stat_to_chart in filtered_df.columns:
        chart = alt.Chart(filtered_df).mark_line(point=True).encode(
            x="Game:N",
            y=stat_to_chart,
            color="Player:N",
            tooltip=["Player", "Game", stat_to_chart]
        ).properties(title=f"{stat_to_chart} Over Games")
        st.altair_chart(chart, use_container_width=True)

    # CSV Export
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Filtered CSV", csv, "ultimate_stats_filtered.csv", "text/csv")

# 👇 This runs the app when deployed directly on Streamlit Cloud
if __name__ == "__main__":
    show()
