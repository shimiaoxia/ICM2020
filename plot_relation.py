import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.image as mpimg
import numpy as np
import csv
import networkx as nx
import matplotlib.patches as patches

width = 1280
height = 851


def scale_x(temp, position):
    return int(10*temp/width)*10


def scale_y(temp, position):
    return int(10-10*temp/height)*10


fin = open(r"C:\Users\asus\Desktop\2020_Weekend1_Problems\2020_Problem_D_DATA\passingevents.csv", "r")
reader = csv.reader(fin, delimiter=',', quotechar='\"')

data = []
for row in reader:
    data.append(row)

fin.close()

data = data[1:]
player = []
player_position_x = []
player_position_y = []
player_pass_count = []
player_average_x = []
player_average_y = []

player_player_pass_count = {}

for row in data:
    if row[0] == "2":
        break

    if row[1][0] == "O":
        continue

    if (row[2], row[3]) in player_player_pass_count:
        player_player_pass_count[row[2], row[3]] += 1
    else:
        player_player_pass_count[row[2], row[3]] = 1

    if row[2] not in player:
        player.append(row[2])
        player_pass_count.append(1)
        player_position_x.append(float(row[7]))
        player_position_y.append(float(row[8]))
    else:
        player_pass_count[player.index(row[2])] += 1
        player_position_x[player.index(row[2])] += float(row[7])
        player_position_y[player.index(row[2])] += float(row[8])

    if row[3] not in player:
        player.append(row[3])
        player_pass_count.append(1)
        player_position_x.append(float(row[9]))
        player_position_y.append(float(row[10]))
    else:
        player_pass_count[player.index(row[3])] += 1
        player_position_x[player.index(row[3])] += float(row[9])
        player_position_y[player.index(row[3])] += float(row[10])

for i in range(0, len(player)):
    player_average_x.append(player_position_x[i] / player_pass_count[i])
    player_average_y.append(player_position_y[i] / player_pass_count[i])

G = nx.Graph()
for p in player:
    G.add_node(p[8:10])

pos = {}
for i in range(0, len(player)):
    t = [width*player_average_x[i]/100, height*(100-player_average_y[i])/100]
    pos[player[i][8:10]] = t

weighted_edge = []
for key in player_player_pass_count:
    weighted_edge.append((key[0][8:10], key[1][8:10], player_player_pass_count[key]))

G.add_weighted_edges_from(weighted_edge)


fig = plt.figure(figsize=(12.8, 8.51))
ax = fig.add_subplot(111)

img = mpimg.imread('court.jpg')
ax.imshow(img)



edge_scale_param = 0.00001
square_scale_param = 5

cc = nx.closeness_centrality(G)
ec = nx.eigenvector_centrality(G)

for edge in weighted_edge:
    # # For debug
    # if edge[0] != 'D1' or edge[1] != 'M1':
    #     continue

    print(edge)
    if edge[0] == edge[1]:
        continue
    origin_node = edge[0]
    destination_node = edge[1]

    pass_param = edge_scale_param * edge[2]**square_scale_param

    o_node_pos_x = pos[origin_node][0]
    o_node_pos_y = pos[origin_node][1]
    d_node_pos_x = pos[destination_node][0]
    d_node_pos_y = pos[destination_node][1]
    k = 10e300
    if d_node_pos_x - o_node_pos_x != 0:
        k = (d_node_pos_y - o_node_pos_y) / (d_node_pos_x - o_node_pos_x)
    k_1 = -1.0 / k

    n0_x = o_node_pos_x + pass_param
    n0_y = o_node_pos_y + k_1 * pass_param
    n1_x = o_node_pos_x - pass_param
    n1_y = o_node_pos_y - k_1 * pass_param

    n2_x = d_node_pos_x
    n2_y = d_node_pos_y
    n3_x = d_node_pos_x
    n3_y = d_node_pos_y
    for edge_v in weighted_edge:
        if edge_v[0] == edge[1] and edge_v[1] == edge[0]:
            print('+' + str(edge_v[2]))
            pass_param = edge_scale_param * edge_v[2]**square_scale_param
            n2_x = d_node_pos_x - pass_param
            n2_y = d_node_pos_y - k_1 * pass_param
            n3_x = d_node_pos_x + pass_param
            n3_y = d_node_pos_y + k_1 * pass_param
            break

    x = [n0_x, n1_x, n2_x]
    y = [n0_y, n1_y, n2_y]
    if n2_x != n3_x or n2_y != n3_y:
        x.append(n3_x)
        y.append(n3_y)
    ax.add_patch(patches.Polygon(xy=list(zip(x, y)), fill=True, color='#333333'))


node_size_square_scale = 2
node_size=[int(30000*ec[key]**node_size_square_scale) for key in ec]
nx.draw_networkx_nodes(G, pos, node_size=node_size, with_labels=True, node_color='#8f0415')
nx.draw_networkx_labels(G, pos, font_color='w')

plt.gca().yaxis.set_major_formatter(FuncFormatter(scale_y))
plt.gca().xaxis.set_major_formatter(FuncFormatter(scale_x))

plt.xticks(np.arange(0, width+1, width/10.0))
plt.yticks(np.arange(0, height+1, height/10.0))

plt.savefig('0.png')
plt.show()
