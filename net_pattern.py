import pymysql
import csv


def find_pattern(match_id=-1, team_start_char='H', match_period='1H', start_time=0.0, duration=3000):

    db = pymysql.connect("localhost", "root", "root", "msmicm")

    cursor = db.cursor()

    condition = "where team_id like 'H%'"
    if match_id > 0:
        condition = "where match_id = {0} and team_id like '{1}%' and event_time>{2} and event_time<{3} and match_period='{4}'".format(match_id, team_start_char, start_time, start_time + duration, match_period)

    print(condition)

    from_member = []
    cursor.execute("select distinct origin_player from full_event {0} order by origin_player".format(condition))
    raw_data = cursor.fetchall()
    for row in raw_data:
        from_member.append(row[0])

    to_member = []
    cursor.execute("select distinct destination_player from full_event {0} order by destination_player".format(condition)),
    raw_data = cursor.fetchall()
    for row in raw_data:
        if row[0] != '':
            to_member.append(row[0])

    all_member = from_member[:]
    for tm in to_member:
        if tm not in all_member:
            all_member.append(tm)

    passing_network = {}
    for fm in from_member:
        for tm in to_member:
            passing_network[fm, tm] = 0

    cursor.execute("select origin_player, destination_player, count(*) from passing_event {0} group by origin_player, destination_player".format(condition))
    raw_data = cursor.fetchall()

    data = []
    for row in raw_data:
        passing_network[row[0], row[1]] = row[2]

    total_pass_time = 0
    member_member_pass = 0
    for key in passing_network:
        if passing_network[key] != 0:
            total_pass_time += passing_network[key]
            member_member_pass += 1

    if member_member_pass != 0:
        average_passing_overall = float(total_pass_time) / member_member_pass

    strong_tie = {}
    for fm in from_member:
        strong_tie[fm] = []
        passing_count = 0
        degree = 0
        for tm in to_member:
            if passing_network[fm, tm] != 0:
                degree += 1
                passing_count += passing_network[fm, tm]
        average_passing = 100000
        if degree != 0:
            average_passing = passing_count / degree
        # print(fm + "'s average pass count = " + str(average_passing))
        for tm in to_member:
            if passing_network[fm, tm] > average_passing:
                strong_tie[fm].append(tm)


    double_sided_pair = []
    single_sided_pair = []
    d_or_s_strong_tie = {}

    for key in strong_tie:
        d_or_s_strong_tie[key] = strong_tie[key][:]

    for key in strong_tie:
        for p2 in strong_tie[key]:
            # Double-sided strong tie
            if key in strong_tie[p2]:
                if (key, p2) not in double_sided_pair and (p2, key) not in double_sided_pair:
                    double_sided_pair.append((key, p2))
            # Single-sided strong tie
            else:
                single_sided_pair.append((key, p2))
                d_or_s_strong_tie[p2].append(key)


    result = {}
    for pattern in [2, 8, 6, 9, 10]:
        result[pattern] = 0

    pattern_8_in_center = {}
    for am in all_member:
        pattern_8_in_center[am] = 0

    for am0 in all_member:
        for am1 in all_member:
            for am2 in all_member:
                if am0 == am1 or am0 == am2 or am1 == am2:
                    continue
                t = (am0, am1, am2)
                if (am1, am0) in single_sided_pair and (am2, am1) in single_sided_pair and (am0, am2) not in single_sided_pair and (am2, am0) not in single_sided_pair and (am0, am2) not in double_sided_pair and (am2, am0) not in double_sided_pair:
                    result[2] += 1
                elif ((am1, am0) in double_sided_pair or (am0, am1) in double_sided_pair) and ((am2, am1) in double_sided_pair or (am1, am2) in double_sided_pair) and (am0, am2) not in single_sided_pair and (am2, am0) not in single_sided_pair and (am0, am2) not in double_sided_pair and (am2, am0) not in double_sided_pair:
                    result[8] += 1
                    pattern_8_in_center[am1] += 1
                elif (am1, am0) in single_sided_pair and (am2, am0) in single_sided_pair and ((am1, am2) in double_sided_pair or (am2, am1) in double_sided_pair):
                    result[6] += 1
                elif (am0, am1) in single_sided_pair and (am1, am2) in single_sided_pair and (am2, am0) in single_sided_pair:
                    result[9] += 1
                elif ((am1, am0) in double_sided_pair or (am0, am1) in double_sided_pair) and (am1, am2) in single_sided_pair and (am2, am0) in single_sided_pair:
                    result[10] += 1

    max = 0
    leader = ''    
    for m in pattern_8_in_center:
        if pattern_8_in_center[m] > max:
            max = pattern_8_in_center[m]
            leader = m
    # print(leader, pattern_8_in_center[leader])

    return result


mid = 14
dt = 900

f = open('./net_pattern_in_{0}_{1}s.csv'.format(mid, dt), 'w', newline='')
writer = csv.writer(f, delimiter=',', quotechar='\"')
row0 = ['Match_period', 'Time', 'H2', 'H8', 'H6', 'H9', 'H10', 'O2', 'O8', 'O6', 'O9', 'O10']
writer.writerow(row0)

for mp in ['1H', '2H']:
    # start_time
    for st in range(0, 3000, 60):
        row_n = [mp, str(st)+'-'+str(st+dt)]
        for tc in ['H', 'O']:
            d = find_by_match_and_team(mid, tc, mp, st, dt)
            for pattern in [2, 8, 6, 9, 10]:
                row_n.append(d[pattern])
        print(row_n)
        writer.writerow(row_n)


f.close()
