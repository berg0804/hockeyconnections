import streamlit as st
import pandas as pd
from unidecode import unidecode
import networkx as nx
df = pd.read_csv("teams_.csv")
df1 = df[["Player", "Team", "Season", "GP"]]
df1["Team2"] = df["Team"] + " " + df["Season"]

data = {
    "Player": list(df1["Player"]),
    "Team2": list(df1["Team2"])
}
df_new = pd.DataFrame(data)
df_new["Player"] = df_new["Player"].astype("string")


# Build the graph
G = nx.Graph()
for team, group in df_new.groupby("Team2"):
    players = group["Player"].tolist()
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            G.add_edge(players[i], players[j], team=team)

# Get sorted list of unique players



player_list = sorted(df_new["Player"].unique())

# Streamlit UI
st.title("Player Connection Finder")

player1 = st.selectbox("Choose Player A", player_list)
player2 = st.selectbox("Choose Player B", player_list, index=1)  # avoid default duplicate

if st.button("Find Connection"):
    if player1 == player2:
        st.warning("Please select two different players.")
    elif nx.has_path(G, player1, player2):
        path = nx.shortest_path(G, source=player1, target=player2)

# Build detailed path with teams
        detailed_path = []
        for i in range(len(path) - 1):
            p1 = path[i]
            p2 = path[i + 1]
            team = G[p1][p2]["team"]
            detailed_path.append(f"{p1} ({team})")
# Add the last player without a team
        detailed_path.append(path[-1])

        st.success(" → ".join(detailed_path))
        st.write("Degrees of separation:", len(path) - 1)

    else:
        st.warning("No connection found between the players.")


# immaculate search
teams = sorted(df["Team"].dropna().unique())

# Streamlit UI
st.title("Players Who Played for Both Teams")

team1 = st.selectbox("Select Team 1", teams)
team2 = st.selectbox("Select Team 2", teams, index=1)

if st.button("Find Players"):
    if team1 == team2:
        st.warning("Please select two different teams.")
    else:
        # Filter for each team
        df_team1 = df[df["Team"] == team1]
        df_team2 = df[df["Team"] == team2]

        # Players on both teams
        players1 = set(df_team1["Player"])
        players2 = set(df_team2["Player"])
        common_players = players1.intersection(players2)

        if common_players:
            # Filter just rows with those players and those 2 teams
            filtered_df = df[df["Player"].isin(common_players) & df["Team"].isin([team1, team2])]

            # Sum GP per player
            summary = (
                filtered_df.groupby("Player")["GP"]
                .sum()
                .reset_index()
                .rename(columns={"GP": "Total GP"})
                .sort_values(by="Total GP", ascending=True)
            )

            st.success(f"{len(summary)} players found who played for both teams:")
            st.dataframe(summary)
        else:
            st.warning("No players found who played on both teams.")

