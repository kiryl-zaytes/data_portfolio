import pandas as pd
import sqlite3 as sql
from sqlite3 import Error
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from soccer.global_var.query import SQLpatterns, REGEXpatterns


def connect(data_base):
    try:
        conn = sql.connect(data_base)
        return conn
    except Error as e:
        print(e)
    return None


def get_goals_scored(id_data, distribution):
    """

    :param id_data: extracted players id's and goals
    :param distribution: left, right distributions groups
    Lookup values from distribution within extracted data.

    """
    goals = []
    for k in distribution.keys():
        data = distribution[k]
        val_data = data['player_api_id'].get_values()
        for x in val_data:
            try:
                goal = id_data[str(x)]
                goals.append(goal)
            except KeyError:
                # remove key as not existed or never scored
                distribution[k] = distribution[k][distribution[k].player_api_id != x]
        res = np.array(goals)
        # attach to initial distribution
        distribution[k] = distribution[k].assign(goals_scored=res)
        del goals[:]  # clean buffer


def get_goals_scored_impr(id_data, distribution):
    """
    :param id_data: extracted players id's and goals
    :param distribution: left, right distributions groups
    Lookup values from distribution within extracted data.

    """
    goals = []
    val_data = distribution['player_api_id'].get_values()
    for x in val_data:
        try:
            goal = id_data[str(x)]
            goals.append(goal)
        except KeyError:
            # remove key as not existed or never scored
            distribution = distribution[distribution.player_api_id != x]
    res = np.array(goals)
    # attach to initial distribution
    return distribution.assign(goals_scored=res)


def leveloff_distribution(dist1, dist2):
    for k in dist1.keys():
        d1_l = len(dist1[k])
        d2_l = len(dist2[k])
        m = min(d1_l, d2_l)
        if m == d1_l:
            dist2[k] = dist2[k].sample(d1_l)
        else:
            dist1[k] = dist1.sample(d2_l)
    showcase_dist(dist1, dist2)


def get_players_impr(player_ratings_df, match_df):
    """
    :param player_ratings_df: player ratings
    :param match_df: available Match data

    Filters player rating based on parameters coming in lambda function. Unpacking and substituting corresponding place
    holders in search query.
    Creates two distribution lists for left and right footed players. Lists in their turn aggregate data on 3 levels:
    low, medium and high.
    For each distribution group applies 'goal' column search against regExp that includes player id.
    Appends data to existed distribution.
    To select Match data for these 3 level tiers distribution get_goals_scored subroutines is used. It finds and adds
    amount of goals scored by each player in each distribution group.

    """
    f = lambda x: player_ratings_df.query('preferred_foot == "{}" and avr_sp > {} and avr_sp < {}'.format(*x))
    stats = player_ratings_df['avr_sp'].describe()
    match_filtered = match_df[match_df['goal'].notnull()]
    extract_id_data = match_filtered['goal'].str.extractall(REGEXpatterns.player_ids)['id'].value_counts()
    p = f(('left', stats['25%'], stats['50%']))
    p1 = f(('left', stats['50%'], stats['75%']))
    p2 = f(('left', stats['75%'], 100))

    a, a1, a2 = np.empty(len(p), dtype='U3'),\
                np.empty(len(p1), dtype='U3'),\
                np.empty(len(p2), dtype='U3')

    a.fill('50%')
    a1.fill('75%')
    a2.fill('max')
    d = p.assign(distr=a)
    d1 =p1.assign(distr=a1)
    d2 =p2.assign(distr=a2)
    x = pd.concat([d,d1,d2])

    p = f(('right', stats['25%'], stats['50%']))
    p1 = f(('right', stats['50%'], stats['75%']))
    p2 = f(('right', stats['75%'], 100))

    a, a1, a2 = np.empty(len(p), dtype='U3'),\
                np.empty(len(p1), dtype='U3'),\
                np.empty(len(p2), dtype='U3')

    a.fill('50%')
    a1.fill('75%')
    a2.fill('max')
    d = p.assign(distr=a)
    d1 = p1.assign(distr=a1)
    d2 = p2.assign(distr=a2)
    x1 = pd.concat([d,d1,d2])
    res = pd.concat([x, x1])
    res = get_goals_scored_impr(extract_id_data, res)

    sns.lmplot(x="avr_sp", y="goals_scored", hue="preferred_foot",
               truncate=True, size=10, aspect=1.7, data=res)
    plt.title('Left/Right goal distribution')
    sns.lmplot(x="avr_sp", y="goals_scored", hue="distr",
               truncate=True, size=10, aspect=1.7, data=res)
    plt.title('Groups goal distribution')


def get_players(player_ratings_df, match_df):
    """
    :param player_ratings_df: player ratings
    :param match_df: available Match data

    Filters player rating based on parameters coming in lambda function. Unpacking and substituting corresponding place
    holders in search query.
    Creates two distribution lists for left and right footed players. Lists in their turn aggregate data on 3 levels:
    low, medium and high.
    For each distribution group applies 'goal' column search against regExp that includes player id.
    Appends data to existed distribution.
    To select Match data for these 3 level tiers distribution get_goals_scored subroutines is used. It finds and adds
    amount of goals scored by each player in each distribution group.

    """
    f = lambda x: player_ratings_df.query('preferred_foot == "{}" and avr_sp > {} and avr_sp < {}'.format(*x))
    distribution_left = {}
    distribution_right = {}
    stats = player_ratings_df['avr_sp'].describe()
    match_filtered = match_df[match_df['goal'].notnull()]
    extract_id_data = match_filtered['goal'].str.extractall(REGEXpatterns.player_ids)['id'].value_counts()

    distribution_left["50%"] = f(('left', stats['25%'], stats['50%']))
    distribution_left["75%"] = f(('left', stats['50%'], stats['75%']))
    distribution_left["max"] = f(('left', stats['75%'], 100))

    distribution_right["50%"] = f(('right', stats['25%'], stats['50%']))
    distribution_right["75%"] = f(('right', stats['50%'], stats['75%']))
    distribution_right["max"] = f(('right', stats['75%'], 100))

    get_goals_scored(extract_id_data, distribution_left)
    get_goals_scored(extract_id_data, distribution_right)
    showcase_dist(distribution_left, distribution_right)
    leveloff_distribution(distribution_left, distribution_right)


def showcase_dist(distribution_left, distribution_right):
    left_goals, left_power = zip(
        *[(distribution_left[d]['goals_scored'].mean(), distribution_left[d]['avr_sp'].mean()) for d in
          distribution_left])
    right_goals, right_power = zip(
        *[(distribution_right[d]['goals_scored'].mean(), distribution_right[d]['avr_sp'].mean()) for d in
          distribution_right])

    sns.set_style("darkgrid")
    sns.axes_style()
    plt.yticks([0, 3.5, 6, 12, 16])
    plt.ylabel('Goals scored (mean)')
    plt.xlabel('Power of shot (mean)')
    plt.title('Proportion by Shot Power and Goals')

    bp = sns.barplot(x=right_power, y=right_goals, color="salmon", label="Right footed players")
    sns.barplot(x=left_power, y=left_goals, color="purple", label="Left footed players")
    bp.set_xticklabels(('Low power (0-50%)', 'Average (50-75%)', 'Strong (above 75%)'))
    plt.legend()
    plt.show()


def top_teams_ever(team_df):
    """

    :param team_df: team data set
    :return:
    Calculates k as sum of attributes and building relative differences between each row(season) in group row as delta column
    """
    k = team_df.apply(lambda x: x['average'] / 100 +
                                (x['won'] / (x['won'] + x['lose'] + x['draw'])) +
                                (x['scored'] / (x['won'] + x['lose'] + x['draw'])),
                      axis=1)
    team_df['k'] = k
    team_df['season'] = pd.to_numeric(team_df['season'])
    gr = team_df.groupby('id')
    team_df['delta'] = gr['k'].apply(lambda x: x - x.shift())
    team_df['delta'].fillna(0, inplace=True)
    top50ever = team_df.nlargest(50, 'k')

    g = sns.PairGrid(top50ever,
                     x_vars=top50ever.columns[2:8], y_vars=["team_short_name"],
                     size=10, aspect=.25)
    g.map(sns.stripplot, size=10, orient="h",
          palette="Reds_r", edgecolor="gray")

    for ax in g.axes.flat:
        ax.xaxis.grid(False)
        ax.yaxis.grid(True)


def most_improved(team_df):
    top10impr = team_df.nlargest(10, 'delta')
    top10degr = team_df.nsmallest(10, 'delta')
    id_season = top10impr[['id', 'season']].values
    frames = []
    frm = lambda x: team_df.query('id == {} and season== {}'.format(r[0], r[1] - x))
    for r in id_season:
        i = 1
        size = frm(i).size
        while size == 0:
            i += 1
            size = frm(i).size
        else:
            frames.append(frm(i))
    origin = pd.concat(frames)
    melted_df_impr = pd.melt(top10impr, id_vars=['team_short_name'], value_vars=['scored', 'won', 'lose', 'k'])
    melted_df_orig = pd.melt(origin, id_vars=['team_short_name'], value_vars=['scored', 'won', 'lose', 'k'])

    sns.set_style("darkgrid")
    fig, (ax1, ax2) = plt.subplots(ncols=2, sharey=True, figsize=(15, 10))
    fig.yyb('Most improved teams over 1 season', fontsize=20)
    b1 = sns.barplot(x='variable', y='value', hue='team_short_name', data=melted_df_orig, ax=ax1)
    b2 = sns.barplot(x='variable', y='value', hue='team_short_name', data=melted_df_impr, ax=ax2)
    b1.legend(title='short name')
    b2.legend(title='short name')
    ax1.set_xlabel("the teams's attr before best year")
    ax2.set_xlabel("Best year ever")
    plt.legend()

    top10impr['status'] = 'improved'
    origin['status'] = 'old'
    comboset = pd.concat([top10impr, origin])
    g = sns.factorplot(data=comboset, x='team_short_name', y='k', hue='status', kind='bar', size=15)
    g.despine(left=True)
    plt.title('Ration of old k and improved k over one season ')
    team_attr_df = pd.read_sql_query(SQLpatterns.select_team_attr_score, cn)
    top_teams_ever(team_attr_df)
    most_improved(team_attr_df)


player_ratings()
