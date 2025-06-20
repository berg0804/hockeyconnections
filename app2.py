import streamlit as st
import pandas as pd
from unidecode import unidecode
import networkx as nx
df = pd.read_csv("teams_.csv")
df1 = df[["Player", "Team", "Season", "GP"]]
df1["Team2"] = df["Team"] + " " + df["Season"]

data = {
    "Player": list(df1["Player"]),
    "Team2": list(df1["Team2"]),
    "GP": list(df1["GP"]),
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
df['Team'] = df['Team'].replace('ANA', 'DUCKS')
df['Team'] = df['Team'].replace('MDA', 'DUCKS')
df['Team'] = df['Team'].replace('ARI', 'COYOTES/JETS (DEFUNCT)')
df['Team'] = df['Team'].replace('WIN', 'COYOTES/JETS (DEFUNCT)')
df['Team'] = df['Team'].replace('PHX', 'COYOTES/JETS (DEFUNCT)')
df['Team'] = df['Team'].replace('ATF', 'FLAMES')
df['Team'] = df['Team'].replace('CGY', 'FLAMES')
df['Team'] = df['Team'].replace('ATL', 'JETS')
df['Team'] = df['Team'].replace('WPG', 'JETS')
df['Team'] = df['Team'].replace('BOS', 'BRUINS')
df['Team'] = df['Team'].replace('BRO', 'AMERICANS (DEFUNCT)')
df['Team'] = df['Team'].replace('NYA', 'AMERICANS (DEFUNCT)')
df['Team'] = df['Team'].replace('BUF', 'SABRES')
df['Team'] = df['Team'].replace('CAR', 'HURRICANES')
df['Team'] = df['Team'].replace('HAR', 'HURRICANES')
df['Team'] = df['Team'].replace('CBH', 'BLACKHAWKS')
df['Team'] = df['Team'].replace('CHI', 'BLACKHAWKS')
df['Team'] = df['Team'].replace('CBJ', 'BLUE JACKETS')
df['Team'] = df['Team'].replace('CGS', 'BARONS/GOLDEN SEALS/SEALS (DEFUNCT)')
df['Team'] = df['Team'].replace('OAK', 'BARONS/GOLDEN SEALS/SEALS (DEFUNCT)')
df['Team'] = df['Team'].replace('CLE', 'BARONS/GOLDEN SEALS/SEALS (DEFUNCT)')
df['Team'] = df['Team'].replace('CLR', 'DEVILS')
df['Team'] = df['Team'].replace('NJD', 'DEVILS')
df['Team'] = df['Team'].replace('KCS', 'DEVILS')
df['Team'] = df['Team'].replace('COL', 'AVALANCHE')
df['Team'] = df['Team'].replace('QUE', 'AVALANCHE')
df['Team'] = df['Team'].replace('DAL', 'STARS')
df['Team'] = df['Team'].replace('MNS', 'STARS')
df['Team'] = df['Team'].replace('DET', 'RED WINGS')
df['Team'] = df['Team'].replace('DTC', 'RED WINGS')
df['Team'] = df['Team'].replace('DTF', 'RED WINGS')
df['Team'] = df['Team'].replace('EDM', 'OILERS')
df['Team'] = df['Team'].replace('FLA', 'PANTHERS')
df['Team'] = df['Team'].replace('HAM', 'BULLDOGS/TIGERS (DEFUNCT)')
df['Team'] = df['Team'].replace('QBC', 'BULLDOGS/TIGERS (DEFUNCT)')
df['Team'] = df['Team'].replace('LAK', 'KINGS')
df['Team'] = df['Team'].replace('MIN', 'WILD')
df['Team'] = df['Team'].replace('MTL', 'CANADIENS')
df['Team'] = df['Team'].replace('MTM', 'MAROONS (DEFUNCT)')
df['Team'] = df['Team'].replace('MTW', 'WANDERERS (DEFUNCT)')
df['Team'] = df['Team'].replace('NSH', 'PREDATORS')
df['Team'] = df['Team'].replace('NYI', 'ISLANDERS')
df['Team'] = df['Team'].replace('NYR', 'RANGERS')
df['Team'] = df['Team'].replace('OTS', 'EAGLES/SENATORS (DEFUNCT)')
df['Team'] = df['Team'].replace('STE', 'EAGLES/SENATORS (DEFUNCT)')
df['Team'] = df['Team'].replace('OTT', 'SENATORS')
df['Team'] = df['Team'].replace('PHI', 'FLYERS')
df['Team'] = df['Team'].replace('PHQ', 'PIRATES/QUAKERS (DEFUNCT)')
df['Team'] = df['Team'].replace('PTP', 'PIRATES/QUAKERS (DEFUNCT)')
df['Team'] = df['Team'].replace('PIT', 'PENGUINS')
df['Team'] = df['Team'].replace('SEA', 'KRAKEN')
df['Team'] = df['Team'].replace('SJS', 'SHARKS')
df['Team'] = df['Team'].replace('STL', 'BLUES')
df['Team'] = df['Team'].replace('TBL', 'LIGHTNING')
df['Team'] = df['Team'].replace('TOR', 'MAPLE LEAFS')
df['Team'] = df['Team'].replace('TRA', 'MAPLE LEAFS')
df['Team'] = df['Team'].replace('TRS', 'MAPLE LEAFS')
df['Team'] = df['Team'].replace('UTA', 'MAMMOTH')
df['Team'] = df['Team'].replace('VAN', 'CANUCKS')
df['Team'] = df['Team'].replace('VEG', 'GOLDEN KNIGHTS')
df['Team'] = df['Team'].replace('WSH', 'CAPITALS')
teams = sorted(df["Team"].dropna().unique())



# Streamlit UI
st.title("Players Who Played for Both Teams")

teams = sorted(df["Team"].unique())
options = teams + ["GP > 50"]


# Two dropdowns with same choices
team1 = st.selectbox("Select Team 1 or GP Filter", options)
team2 = st.selectbox("Select Team 2 or GP Filter", options, index=1)

if st.button("Find Players"):
    if team1 == team2:
        st.warning("Please select two different options.")
    else:
        # Handle GP filter and team filtering
        df_team1 = df.copy()
        if team1 != "GP > 50":
            df_team1 = df[df["Team"] == team1]
        if team1 == "GP > 50":
            gp1_players = df.groupby("Player")["GP"].sum().reset_index()
            gp1_players = gp1_players[gp1_players["GP"] > 50]
            df_team1 = df[df["Player"].isin(gp1_players["Player"])]

        df_team2 = df.copy()
        if team2 != "GP > 50":
            df_team2 = df[df["Team"] == team2]
        if team2 == "GP > 50":
            gp2_players = df.groupby("Player")["GP"].sum().reset_index()
            gp2_players = gp2_players[gp2_players["GP"] > 50]
            df_team2 = df[df["Player"].isin(gp2_players["Player"])]

        # Find players that meet both criteria
        players1 = set(df_team1["Player"])
        players2 = set(df_team2["Player"])
        common_players = players1.intersection(players2)

        if common_players:
            # Filter full data for just those players
            filtered_df = df[df["Player"].isin(common_players)]

            # Show total GP for summary
            summary = (
                filtered_df.groupby("Player")["GP"]
                .sum()
                .reset_index()
                .rename(columns={"GP": "Total GP"})
                .sort_values(by="Total GP", ascending=True)
            )

            st.success(f"{len(summary)} players found who match both selections:")
            st.dataframe(summary)
        else:
            st.warning("No players found who match both selections.")