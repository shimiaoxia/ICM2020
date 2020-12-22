import pymysql
import csv
import networkx as nx

selfchar = 'H'
oppchar = 'O'

db = pymysql.connect("localhost", "root", "root", "msmicm")
cursor = db.cursor()
cursor.execute("select distinct origin_player from full_event where team_id like 'H%' order by origin_player")
raw_data = cursor.fetchall()

all_member = []
for row in raw_data:
    all_member.append(row[0])

cursor.execute("select * from full_event")
raw_data = cursor.fetchall()

e_type = 7
e_subtype = 8
o_player = 3
d_player = 4
t_id = 2
m_id = 1

# For next event of passing event
good_event = ['Shot', 'Free Kick', 'Duel']
bad_event = ['Foul']


d = {}
for m in all_member:
    # Indicators for each member

    dd = {}

    dd["duel_count"] = 0
    dd["duel_bunch"] = 0
    dd["attack_duel_bunch"] = 0
    dd["defend_duel_bunch"] = 0

    dd["attack_duel_simple"] = 0
    dd["attack_duel_with_loose_duel"] = 0
    dd["attack_duel_shot"] = 0
    dd["attack_duel_lose_ball"] = 0
    dd["attack_duel_cause_opp_foul"] = 0

    dd["defend_duel_simple"] = 0
    dd["defend_duel_with_loose_duel"] = 0
    dd["defend_duel_cause_opp_foul"] = 0
    dd["defend_duel_suc"] = 0
    dd["defend_duel_gain_ball"] = 0
    dd["defend_duel_fail"] = 0
    dd["clearance_count"] = 0

    dd["pass_count"] = 0
    dd["pass_suc"] = 0
    dd["pass_cause_attack_duel"] = 0
    dd["pass_cause_defense_duel"] = 0
    dd["pass_lose"] = 0

    i = 0
    while i < len(raw_data) - 1:
        if raw_data[i][o_player] == m:
            if raw_data[i][e_type] == 'Pass':
                dd["pass_count"] += 1
                if raw_data[i+1][e_type] == 'Duel' and raw_data[i+1][o_player][0] == selfchar:
                    dd["pass_suc"] += 1
                    dd["pass_cause_attack_duel"] += 1
                elif raw_data[i+1][e_type] == 'Duel' and raw_data[i+1][o_player][0] == oppchar:
                    dd["pass_lose"] += 1
                    dd["pass_cause_defense_duel"] += 1
                elif (raw_data[i+1][e_type] in good_event and raw_data[i+1][o_player][0] == selfchar) or (raw_data[i+1][e_type] in bad_event and raw_data[i+1][o_player][0] == oppchar):
                    dd["pass_suc"] += 1
                elif raw_data[i + 1][e_type] not in bad_event and raw_data[i + 1][o_player][0] == oppchar:
                    dd["pass_lose"] += 1
        i += 1

    i = 0
    while i < len(raw_data) - 1:
        if raw_data[i][o_player] == m:
            if raw_data[i][e_type] == 'Duel':
                dd["attack_duel_bunch"] += 1
                dd["duel_bunch"] += 1
                duel_type = 'loose'
                duel_self_count = 0
                duel_self_attack_count = 0
                while raw_data[i][e_type] == 'Duel':
                    if raw_data[i][e_subtype] == 'Ground attacking duel' or raw_data[i][e_subtype] == 'Ground defending duel':
                        duel_type = 'attack'
                    if raw_data[i][o_player][0] == selfchar:
                        duel_self_count += 1
                        if raw_data[i][e_subtype] == 'Ground attacking duel':
                            duel_self_attack_count += 1
                    i += 1

                dd["duel_count"] += duel_self_count
                dd["attack_duel_simple"] += duel_self_attack_count
                if duel_type == 'attack':
                    dd["attack_duel_with_loose_duel"] += duel_self_count

                if i < len(raw_data):
                    if raw_data[i][e_type] == 'Shot' and raw_data[i][o_player][0] == selfchar:
                        dd["attack_duel_shot"] += 1
                    if raw_data[i][e_type] == 'Foul' and raw_data[i][o_player][0] == oppchar:
                        dd["attack_duel_cause_opp_foul"] += 1
                    if raw_data[i][e_type] not in bad_event and raw_data[i][o_player][0] == oppchar:
                        dd["attack_duel_lose_ball"] += 1
        i += 1

    # Count detail for defend data
    i = 0
    while i < len(raw_data) - 1:
        # opponent's duel
        if raw_data[i][e_type] == 'Duel' and raw_data[i][o_player][0] == oppchar:
            appear_m = False
            duel_type = 'loose'
            duel_m_count = 0
            duel_m_defend_count = 0
            while raw_data[i][e_type] == 'Duel':
                if raw_data[i][e_subtype] == 'Ground attacking duel' or raw_data[i][e_subtype] == 'Ground defending duel':
                    duel_type = 'defend'
                if raw_data[i][o_player] == m:
                    appear_m = True
                    duel_m_count += 1
                    if raw_data[i][e_subtype] == 'Ground defending duel':
                        duel_m_defend_count += 1
                i += 1

            if appear_m:
                dd["defend_duel_bunch"] += 1
                dd["duel_bunch"] += 1
                dd["duel_count"] += duel_m_count
                dd["defend_duel_simple"] += duel_m_defend_count
                if duel_type == 'defend':
                    dd["defend_duel_with_loose_duel"] += duel_m_count

                if i < len(raw_data):
                    if raw_data[i][e_type] == 'Shot' and raw_data[i][o_player][0] == oppchar:
                        dd["defend_duel_fail"] += 1
                    if raw_data[i][e_type] == 'Foul' and raw_data[i][o_player][0] == oppchar:
                        dd["defend_duel_cause_opp_foul"] += 1
                    if raw_data[i][e_type] not in bad_event and raw_data[i][o_player] == m:
                        dd["defend_duel_gain_ball"] += 1
                        dd["defend_duel_suc"] += 1
                    if raw_data[i][e_type] not in good_event and raw_data[i][o_player][0] == oppchar:
                        dd["defend_duel_suc"] += 1
        i += 1

    # Count clearance
    i = 0
    while i < len(raw_data):
        if raw_data[i][e_subtype] == 'Clearance' and raw_data[i][o_player] == m:
            dd["clearance_count"] += 1
        i += 1

    d[m] = dd


f = open("./sub_indicator_1.csv", 'w', newline='')
writer = csv.writer(f)
row0 = ['']
for m in d:
    for indicator_name in d[m]:
        row0.append(indicator_name)
    break
writer.writerow(row0)

for m in d:
    row_n = [m]
    for c in d[m]:
        row_n.append(d[m][c])
    writer.writerow(row_n)

f.close()

