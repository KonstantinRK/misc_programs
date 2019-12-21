import json
import pandas as pd
import datetime
from  matplotlib import pyplot as plt
import numpy as np
import cvxpy as cvx
import math
import csv
import pulp

def compile_collect_dates(data_file, meta_file, start_day=None, year=None):

    data = pd.DataFrame.from_csv(data_file)
    with open(meta_file, 'r') as f:
        meta = json.load(f)

    if start_day is None:
        start_day = datetime.datetime.now().strftime('%Y-%m-%d')

    o_data = data.loc[str(start_day):]

    #loc_df = pd.DataFrame([meta[k]['loc']for k in o_data], index=[k for k in o_data])
    #print(loc_df.values)
    #loc_list = sorted(list(set(list(loc_df.values.as_list()))))
    #print(loc_list)
    #print(loc_df)
    loc_dic = {}
    for i in o_data:
        loc = meta[i]['loc']
        if loc_dic.get(loc,None) is None:
            loc_dic[loc]=[]
        loc_dic[loc].append(i)

    #loc_list = sorted(list(set([meta[k]['loc']for k in o_data])))
    print('#',loc_dic)
    days = compute_dates(o_data)
    #for i in sorted(loc_dic.keys()):
    #    compute_dates([loc_dic[i]])

    table = [[k] + ['{} ({})'.format(meta[i]['name'],meta[i]['loc']) for i in days[k]] for k in sorted(days.keys())]

    if year is None:
        table_name = "heurigen_collect_days.csv"
    else:
        table_name = "{}_heurigen_collect_days.csv".format(str(year))

    with open(table_name, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile)
        max_len = max([len(i) for i in table])
        table = [i+['' for j in range(max_len-len(i))] for i in table]
        print(table)
        for i in range(max_len):
            row = [table[j][i] for j in range(len(table))]
            spamwriter.writerow(row)



def compute_dates(o_data):
    data = o_data.copy()
    # plot_dates(data, meta)
    date_mask = linear_int_programming(data, cost_foo_exp)
    data['key'] = date_mask
    data = data[data['key'] == 1].drop('key', axis=1)
    days = {}
    index = data.index
    for i in index:
        cols = data.loc[i].dropna().index
        days[i.strftime('%Y-%m-%d')] = list(cols)
        data = data.drop(cols, axis=1)
    for k, v in days.items():
        print(k)
        print(v)
        print(len(v))
    print('#' * 100)
    return days

def plot_dates(data, meta):
    data = data.copy()
    #for i in data.columns:
    #    data[i] = data[i]*int(i)

    X = pd.to_datetime(data.index)
    print(X)
    fig, ax = plt.subplots()
    c = 0
    map_dic={'Klosterneuburg':0,'Kritzendorf':1,'Kierling':2, 'Weidling':3}
    colors=['cornflowerblue','lightblue','steelblue','lightslategray']
    used = set()
    for i in data:
        color = colors[map_dic[meta[i]['loc']]]

        if color not in used:
            used.add(color)
            label = meta[i]['loc']
            ax.scatter(data[data[i] != 0][i].index, (data[data[i] != 0][i] * c).values, c=color, marker='s', s=100, label=label)
        else:
            ax.scatter(data[data[i] != 0][i].index, (data[data[i] != 0][i] * c).values, c=color, marker='s', s=100)
        #ax.scatter(X, [c] * len(X), c=data[i], marker='s', s=100)
        c+=1

    ax.yaxis.set_ticks(np.arange(0, c, 1))
    #ax.xaxis.set_ticks(X)
    ax.set_yticklabels(['{1}({0})'.format(str(data.columns[i]),meta[data.columns[i]]['name']) for i in range(c)])
    ax.yaxis.set_tick_params(labelsize=5)
    ax.xaxis.set_tick_params(labelsize=5)

    ax.set_xlim(X[0], X[-1])
    ax.xaxis.set_ticks(X)
    ax.set_xticklabels([i.strftime('%Y-%m-%d') for i in X])

    print([i.strftime('%Y-%m-%d') for i in X])
    #ax.xaxis.set_ticks(np.arange(X[0], X[-1], 1))


    #ax.xaxis_date()
    print([meta[data.columns[i]]['name'] for i in range(c)])
    plt.legend(loc=4,bbox_to_anchor = (1, 1),ncol=4)

    fig.autofmt_xdate()

    plt.show()

def cost_foo_lin(n):
    X = np.arange(1/n,1,1/(n+1))
    return X/np.sum(X)

def cost_foo_geo(n):
    X = np.geomspace(1,10**5,n)
    return X/np.sum(X)

def cost_foo_log(n):
    X = np.array([(((i-n/2)**3)+math.fabs(((1-n/2)**3))) for i in range(1,n+1)])
    return X/np.sum(X)

def cost_foo_quad(n):
    X = np.array([i**2*n for i in range(1,n+1)])
    return X/np.sum(X)

def cost_foo_exp(n):
    X = np.array([2**(i-n/10) for i in range(1,n+1)])
    return X/np.sum(X)

def linear_int_programming(data, cost_foo, loc=None):
    A = data.copy().dropna(axis=1,how='all').transpose().fillna(0).values
    n = len(A[0])
    c = cost_foo(n)
    x = cvx.Variable(n,boolean=True)
    objective = cvx.Minimize(cvx.sum(c*x))
    constraints = [1 <= x * i for i in A]
    if loc is not None:
        constraints = constraints + []
    prob = cvx.Problem(objective, constraints)
    prob.solve()
    return np.abs(np.round(x.value))


def linear_int_programming2(data, cost_foo, loc=None):
    A = data.copy().dropna(axis=1,how='all').transpose().fillna(0).values
    n = len(A[0])
    m = len(A)
    c = cost_foo(n)
    X = cvx.Variable((n,m),boolean=True)

    objective = cvx.Minimize(cvx.sum(c*X))
    constraints = [1 <= X[i] * A[i] for i in range(len(A))]
    if loc is not None:
        constraints = constraints + []
    prob = cvx.Problem(objective, constraints)
    print(prob.solve())
    #print(x)

    print(np.abs(np.round(X.value)))
    return np.abs(np.round(X.value))


def early_bird_algo(data, start_day, nr_dates):
    data = data.copy().fillna(0)
    h_df = pd.Series([0 for i in data.columns], index=[i for i in data.columns])
    #print(h_df)
    days = []
    s_delay = 0
    s_select = 0
    time = data.index
    for i in time:
        s_delay_1 =data.loc[:i].sum().sum()
        s_select_1 = data.loc[i].sum()
        print(s_delay_1, s_select_1)

        if s_select > s_select_1:
            s_select=0
            df = data.loc[i]==0
            df = df[df==True]
            data=data[df.index]
            days.append(i)
            print(s_delay, s_select)
            print(data.columns)
        else:
            s_select = s_select_1
        s_delay = s_delay_1




