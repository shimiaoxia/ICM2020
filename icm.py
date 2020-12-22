import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 16})
import operator
import math



def myKmeans(X, k):
    X['ATR'] = X['FG'] / X['FGA']
    X['PS/G'] = X['attack_duel_with_loose_duel'] 

    #X['ATR'] = X['FG'] / X['FGA']
    #X['PS/G'] = X['Passatt'] 
    #plt.xlabel('Shot success rate')
    #plt.ylabel('Pass attack count')
    #plt.xlim(-0.5, 1.5) 
    #plt.ylim(-0.5, 1.5)  
    #plt.title('Select Wing Forward')

    #X['ATR'] = X['PassA'] 
    #['PS/G'] = X['defend_duel_with_loose_duel'] 
    #plt.xlabel('Pass count')
    #plt.ylabel('Defend action count')
    #plt.xlim(-0.5, 1.5)  
    #plt.ylim(-0.5, 1.5)  
    #plt.title('Select Side Back')

    #X['ATR'] = X['FG'] / X['FGA']
    #X['PS/G'] = X['Passsuc'] 
    #plt.xlabel('Shot success rate')
    #plt.ylabel('Pass success count')
    #plt.xlim(-0.5, 1.5)
    #plt.ylim(-0.5, 1.5)  
    #plt.title('Select Side Mid-Fielder')

    #X['ATR'] = X['defend_duel_with_loose_duel'] 
    #X['PS/G'] = X['attack_duel_with_loose_duel'] 
    #plt.xlabel('Defend action count')
    #plt.ylabel('Attack action count')
    #plt.xlim(-0.5, 1.5)  
    #plt.ylim(-0.5, 1.5)  
    #plt.title('Select Center Back')

     #X['ATR'] = X['defend_duel_with_loose_duel'] 
    #X['PS/G'] = X['attack_duel_with_loose_duel'] 
    #plt.xlabel('Defend action count')
    #plt.ylabel('Attack action count')
    #plt.xlim(-0.5, 1.5)  
    #plt.ylim(-0.5, 1.5)  
    #plt.title('Select Center Middle Field')

    fig = plt.figure(num=None, figsize=(10, 6), edgecolor='k')
    ax = fig.add_subplot(1, 1, 1, facecolor="1.0")
    ax.scatter(X['PS/G'], X['ATR'], alpha=0.5, c='y', edgecolors='g', s=150)
    plt.xlabel('Shot success rate')
    plt.ylabel('Attack action count')
    plt.xlim(-0.5, 1.5)  
    plt.ylim(-0.5, 1.5)  
    plt.title('Select Center Forward')
    plt.show()

    random_initial_pts = np.random.choice(X.index, size=k)

    centroids = X.loc[random_initial_pts]

    def centroids_data(centroids):
        dictionary = dict()
        # iterating counter, need this to generate cluster_id
        counter = 0

        # traversing the data frame using iterrows
        for index, row in centroids.iterrows():
            coordinates = [row['PS/G'], row['ATR']]
            dictionary[counter] = coordinates
            counter += 1

        return dictionary

    centroids_dict = centroids_data(centroids)

    # Calculating Eucledian distance (like pythagoras thm) between centroids and players
    def calc_dist(centroid, player_nos):
        root_distance = 0

        for x in range(0, len(centroid)):
            diff = centroid[x] - player_nos[x]
            sq_diff = diff ** 2
            root_distance += sq_diff

        euc_dis = math.sqrt(root_distance)
        return euc_dis

    #we know the distances now we'll determine which point belongs to which cluster
    def assign_clust(row):
        player_vals = [row['PS/G'], row['ATR']]
        dist_prev = -1
        cluster_id = None

        for centroid_id, centroid_vals in centroids_dict.items():
            dist = calc_dist(centroid_vals, player_vals)
            if dist_prev == -1:
                cluster_id = centroid_id
                dist_prev = dist
            elif dist < dist_prev:
                cluster_id = centroid_id
                dist_prev = dist
        return cluster_id

    # Apply to each row in normalised players
    X['cluster'] = X.apply(lambda row: assign_clust(row), axis=1)

    def recalculate_centroids(df):
        new_centroids_dict = dict()
        for cluster_id in range(0, k):
            df_cluster_id = df[df['cluster'] == cluster_id]

            xmean = df_cluster_id['PS/G'].mean()
            ymean = df_cluster_id['ATR'].mean()
            new_centroids_dict[cluster_id] = [xmean, ymean]

            # Finish the logic
        return new_centroids_dict

    centroids_dict = recalculate_centroids(X)

    def vis_clust(df, num_clusters, iteration):
        colors = ['b', 'y', 'r', 'c', 'y', 'm']
        fig = plt.figure(num=None, figsize=(10, 6), edgecolor='k')
        ax = fig.add_subplot(1, 1, 1, facecolor="1.0")
        for n in range(num_clusters):
            clustered_df = df[df['cluster'] == n]
            ax.scatter(clustered_df['PS/G'], clustered_df['ATR'], c=colors[n - 1], edgecolors='g', alpha=0.5, s=150)
            plt.xlabel('Shot success rate')
            plt.ylabel('Attack action count')
            plt.xlim(-0.5, 1.5)  
            plt.ylim(-0.5, 1.5)  
            plt.title('Select Center Forward')
        plt.show()

    iteration = 0
    vis_clust(X, 5, iteration)

    #3 Iterations for each k, to find the right cluster density
    # Iteration 1

    centroids_dict = recalculate_centroids(X)
    X['cluster'] = X.apply(lambda row: assign_clust(row), axis=1)
    vis_clust(X, k, 1)

    # Iteration 2

    centroids_dict = recalculate_centroids(X)
    X['cluster'] = X.apply(lambda row: assign_clust(row), axis=1)
    vis_clust(X, k, 2)

    # Iteration 3

    centroids_dict = recalculate_centroids(X)
    X['cluster'] = X.apply(lambda row: assign_clust(row), axis=1)
    vis_clust(X, k, 3)

def euclDistance(x, xi):
    d = 0.0
    for i in range(len(x)-1):
        d += pow((float(x[i])-float(xi[i])),2)  #euclidean distance
    d = math.sqrt(d)
    return d

def myKNN(test_data, train_data, k_value):
    for i in test_data:
        eu_Distance =[]
        knn = []
        good = 0
        bad = 0
        for j in train_data:
            eu_dist = euclDistance(i, j)
            #print(eu_dist)
            eu_Distance.append((j[5], eu_dist))
            eu_Distance.sort(key=operator.itemgetter(1))
            knn = eu_Distance[:k_value]
            #print(knn)
            for k in knn:
                #print(k[0])
                if k[0] =='g':
                    good += 1
                else:
                    bad +=1
        if good > bad:
            i.append('g')
        elif good < bad:
            i.append('b')
        else:
            i.append('NaN')

#Accuracy calculation function
def accuracy(test_data):
    correct = 0
    for i in test_data:
        if i[5] == i[6]:
            correct += 1
    accuracy = float(correct)/len(test_data) *100  #accuracy
    return accuracy

def main():
    #reading CSV inputs
    nbaff = pd.read_csv("playerstats.csv")

    #dropping columns with strings
    nbaff_numeric = nbaff.drop(columns=['Player','POS'])
    #standardizing data
    data_normalised = (nbaff_numeric - nbaff_numeric.mean()) / (nbaff_numeric.max() - nbaff_numeric.min())

    #K Means for 3 clusters
    nclusters = 3
    myKmeans(data_normalised , nclusters)



if __name__ == '__main__':
    main()