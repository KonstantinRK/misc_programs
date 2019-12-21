import networkx as nx
import networkx.algorithms as nx_algo
import pandas as pd
import numpy as np
import scipy.spatial as sci_space
import math
import csv
import graphviz
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
import os
import shutil
import datetime
import re

def euclid(e1,e2):
    x1 = e1['latitude']
    y1 = e1['longitude']
    x2 = e2['latitude']
    y2 = e2['longitude']
    return math.sqrt((x1-x2)**2+(y1-y2)**2)

def build_node_list(df, columns=None):
    if columns is not None:
        df = df[[*columns]]
    data_list = []
    count = 0
    for row in df.iterrows():
        data = count,row[1].to_dict()
        data_list.append(data)
        count = count+1
    return data_list


def build_weight_matrix(df, x_name, y_name):
    x = np.asarray(df[[x_name, y_name]])
    #y = np.asarray(df[y_name])[..., np.newaxis]
    w = sci_space.distance.pdist(x, metric= 'euclidean')
    w = np.asarray(sci_space.distance.squareform(w))

    w = w*10**10
    np.fill_diagonal(w, np.inf)
    #df = pd.DataFrame(w)
    #df.to_csv('test.csv', sep=';')
    return w

def build_graph(V, w_foo, tour=None):
    G = nx.Graph()
    for v in V:
        G.add_node(v[0],attr_dict=v[1])
    if tour is None:
        for i in range(len(V)):
            for j in range(len(V)):
                G.add_edge(i,j,weight=w_foo[i][j])
    else:
        for i in tour:
            G.add_edge(i[0],i[1],weight=w_foo[i[0]][i[1]])
    return G

def draw_network(G, x='longitude', y='latitude', e=True, l=False, save=None):
    pos = {}
    label = {}
    for i in G.nodes():
        pos[i] = float(G.node[i]['attr_dict'][x]),float(G.node[i]['attr_dict'][y])
        try:
            label[i] = str(G.node[i]['attr_dict']['company'])
        except KeyError:
            label[i] = str(G.node[i]['attr_dict']['name'])
    my_dpi = 150
    fig = plt.figure(figsize=(1200/my_dpi, 600/my_dpi), dpi=my_dpi)

    ax =  plt.subplot()
    nx.draw_networkx_nodes(G, pos, node_size=4, ax=ax)
    if l is True:
        nx.draw_networkx_labels(G, pos, node_size=2, labels=label, font_size=6, ax=ax)
    if e is True:
        nx.draw_networkx_edges(G, pos, ax=ax)

    plt.draw()
    plt.tight_layout()
    if save is not None:
        plt.savefig(save, dpi=my_dpi)
    else:
        plt.show()


def create_start_tour(w):
    tour = []
    length = w.shape[0]
    start_node = 0
    current_node = start_node
    while len(tour)<length:
        next_node = np.argmin(w[current_node])
        tour.append((current_node,next_node))
        current_node = next_node
    print(tour)


def clean_df(df):
    df.columns = [i.strip() for i in df.columns]
    city_map = {'Klosterneuburg':'Klosterneuburg',
                'Kritzendorf':'Kritzendorf',
                'St. Andrä-Wördern':'Wördern',
                'Wördern':'Wördern',
                'Klosterneuburg-Weidling':'Weidling',
                'Weidling':'Weidling',
                'St. Andrä Wördern':'Wördern',
                'Sankt Andrä-Wördern':'Wördern',
                'Hintersdorf':'Kierling',
                'Wien':'Wien',
                'Klosterneuburg/ Maria Gugging':'Kierling',
                'Kierling':'Kierling',
                'Klosterneuburg/Kierling': 'Kierling',
                'Klosterneuburg-Kierling': 'Kierling',
                'Greifenstein': 'Kritzendorf',
                'Höflein':'Kritzendorf',
                'Zeiselmauer':'Wördern'}

    group = []
    for i in range(len(df)):
        #print(city_map[df.iloc[i]['city']])
        group.append(city_map[df.iloc[i]['city']])
    df['group']=group
    return df


def build_euler_graph(G, w):
    MST = nx.minimum_spanning_tree(G, 'weight')
    T = nx.MultiGraph()

    T.add_nodes_from(MST.nodes(data=True))
    T.add_weighted_edges_from(MST.edges(data=True))
    T.add_weighted_edges_from(MST.edges(data=True))
    tour = nx_algo.eulerian_circuit(T,0)
    ET = nx.Graph()
    ET.add_nodes_from(MST.nodes(data=True))
    visited = np.zeros(w.shape[0])
    current_node = 0
    for edge in tour:
        next_node = edge[1]
        if visited[next_node]==0:
            print(current_node, next_node)
            ET.add_edge(current_node,next_node,weight=w[current_node][next_node])
            visited[next_node] = 1
            current_node = next_node
    ET.add_edge(current_node, 0, weight=w[current_node][0])
    return ET

def build_euler_tour(G, w):
    MST = nx.minimum_spanning_tree(G, 'weight')
    T = nx.MultiGraph()
    T.add_nodes_from(MST.nodes(data=True))
    T.add_weighted_edges_from(MST.edges(data=True))
    T.add_weighted_edges_from(MST.edges(data=True))
    tour = nx_algo.eulerian_circuit(T, 0)
    ET = []
    visited = np.zeros(w.shape[0])
    current_node = 0
    for edge in tour:
        next_node = edge[1]
        if visited[next_node] == 0:
            ET.append((current_node, next_node))
            visited[current_node] = 1
            current_node = next_node
    ET.append((current_node, 0))
    #draw_network(ET, 'longitude', 'latitude', l=True)
    return ET


def build_tour(tour, start=0):
    adj_list = [None for i in range(len(tour))]
    for i in tour:
        adj_list[i[0]]=i[1]
    node = start
    tour = [node]
    print(adj_list)
    for i in range(len(adj_list)):
        tour.append(adj_list[node])
        node = adj_list[node]
    return tour


def get_N(T):
    N = []
    tour = list(nx_algo.eulerian_circuit(T,0))
    for p in range(len(tour)):
        for q in range(p+2,len(tour)-1):
            #N.append(((p,p+1),(q,q+1)))
            N.append((tour[p],tour[q]))
    return N

def calculate_tour_sum(tour,w):
    cost = 0
    for i in tour:
        cost += w[i[0],i[1]]
    return cost

def opt_heuristic(tour, w):
    stop=False
    T = nx.Graph(tour)
    tour_sum = calculate_tour_sum(tour,w)
    counter = 0
    while stop is False and counter<=10000:
        counter +=1
        old_sum = tour_sum

        N=get_N(T)
        for n in N:
            node_p1 = n[0][0]
            node_p2 = n[0][1]
            node_q1 = n[1][0]
            node_q2 = n[1][1]
            s1 = w[node_p1][node_p2]+w[node_q1][node_q2]
            s2 = w[node_p1][node_q1]+w[node_p2][node_q2]

            if s1>s2:
                if old_sum <= tour_sum+s2-s1:
                    stop = True
                else:
                    T.remove_edge(node_p1, node_p2)
                    T.remove_edge(node_q1, node_q2)
                    T.add_edge(node_p1, node_q1)
                    T.add_edge(node_p2, node_q2)
                    tour_sum = tour_sum+s2-s1
                break

        if old_sum <= tour_sum:
            stop=True
    return T


def solve_tsp(df):
    my_df = pd.DataFrame(df)
    w = build_weight_matrix(my_df, 'latitude', 'longitude')
    try:
        V = build_node_list(my_df, list(my_df.columns))
    except KeyError:
        V = build_node_list(my_df, ['name', 'city', 'street', 'latitude', 'longitude'])
    G = build_graph(V, w)
    if len(V) > 1:
        tour = build_euler_tour(G, w)
        if len(V)>2:
            T = opt_heuristic(tour, w)
            tour = list(nx_algo.eulerian_circuit(T, 0))
        T = build_graph(V, w, tour)
    else:
        T = G
    return T

data = []

def get_df(path):
    with open(path,'r') as f:
        raw_data = csv.reader(f,delimiter='\t')
        for i in raw_data:
            if i[-1]=='':
                data.append(i[:-1])
            else:
                data.append(i)
    df = pd.DataFrame(data[1:], columns=data[0])
    df = clean_df(df)
    return df


def clustering(df, c=2, sub_cluster=None, max_subcluster=4):
    try:
        df['cluster']
    except:
        df['cluster']=0

    sub_cluster = [0] if sub_cluster is None else sub_cluster
    for i in sub_cluster:
        b_df = df[df['cluster']==i]
        X = np.asarray(b_df[['longitude','latitude']])
        kmeans = KMeans(n_clusters=c)
        kmeans.fit(X)
        #centroids = kmeans.cluster_centers_
        labels = kmeans.labels_
        buffer_df= df[df['cluster']==i]['cluster']+labels
        df.loc[df['cluster'] == i,'cluster']= buffer_df
        #df[df['cluster'] == i]['cluster']=df[df['cluster']==i]['cluster']+1
    new_iter = []
    df['cluster'] = df['cluster'] + 1

    cluster_count =  math.ceil(math.log(df['cluster'].max()))
    for i in df.groupby('cluster'):
        if len(i[1])>20:
            new_iter.append(i[0]*10)
    #if cluster_count <= max_subcluster:
    if any(new_iter):
        df['cluster']=df['cluster']*10
        df = clustering(df,c,new_iter)

    return df


def start_save_tsp(df, groupby=None):
    graphs = {}
    folder = 'trips'
    try:
        shutil.rmtree(folder)
    except Exception as e:
        print(e)
        pass
    os.makedirs(folder)

    if groupby is not None:
        for i in df.groupby(groupby):
            graphs[i[0]] = solve_tsp(i[1])
    else:
        graphs['all']=solve_tsp(df)

    for z, g in graphs.items():
        print(z)
        if len(g.nodes())>2:
            path = list(nx_algo.eulerian_circuit(g))
        else:
            path = [(i,i) for i in g.nodes()]
        data = []
        for i in path:
            data.append(g.node[i[0]]['attr_dict'])
        print(data)
        df = pd.DataFrame(data)
        print(df.head())
        try:
            df = df[['company', 'city', 'street','data','message']]
        except KeyError:
            df = df[['name', 'city', 'street','data','message']]

        os.makedirs(os.path.join(folder,str(z)))

        df.to_csv(os.path.join(folder,str(z),'{0}.csv'.format(str(z))),sep=';')
        draw_network(g, 'longitude', 'latitude', l=True, save=os.path.join(folder, str(z),'{0}'.format(str(z))))
        #draw_network(g, 'longitude', 'latitude', l=True)

def get_message_dic(df):
    message_dic={'data':{}, 'message':{}}

    for i in df.iterrows():
        date = datetime.datetime.strptime(i[1]['created_when'].split(' ')[0],'%Y-%m-%d')
        for k in message_dic.keys():
            if message_dic.get(i[0], None) is None:
                message_dic[k][i[0]] = []
            s = i[1][k]

            if str(s).strip()!= 'nan':
                if k=='data':
                    if type(s) == str:
                        s = ', '.join(re.findall(r'\["(.+)\"]',s))
                    else:
                        s = ''
                s = "{s} ({y})".format(s=s, y=date.strftime('%Y'))
                s = str(s).encode('latin').decode('unicode-escape').strip()

            else:
                s = ''
            message_dic[k][i[0]].append(s)

    return message_dic

#df = get_df('tapp_companylog.csv')

#columns = ['id', 'name',  	created_when 	id 	name 	id 	company 	city 	zip 	street 	latitude 	longitude]
df = clean_df(pd.DataFrame.from_csv('tapp_companylog.csv'))
message_dic = get_message_dic(df)
#df = df.drop(['created_when', ])
df = df[~df.index.duplicated(keep='first')]
df = clustering(df,3)


df[['data','message']] = ''
for k in ['data','message']:
    df[k]=[', '.join(message_dic[k][i]) for i in df.index]


start_save_tsp(df, 'cluster')











#draw_network(T,'longitude', 'latitude', l=False)
'''
for i in range(w.shape[0]):
    x = euclid(df.iloc[i],df.iloc[np.argmin(w[i])])*10**10
    y = np.min(w[i])*10**10

    print(x, y, x-y)
    print(i,':',np.argmin(w[i]))
'''