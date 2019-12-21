import pandas as pd
#import nltk
import re
import jellyfish
from pprint import pprint

def compute_similarity(names1,names2):
    data = []
    hist = {}
    mapping_list = []
    for i, n in enumerate(names1):
        row = []
        n_1 = clean_name(n)
        min_obj = (None,0,0)
        for j, m in enumerate(names2):
            n_2 = clean_name(m)
            score = jellyfish.damerau_levenshtein_distance(n_1,n_2)
            row.append(score)
            if min_obj[0] is None or min_obj[0]>=score:
                min_obj=(score,i,j)

        if min_obj[0] <= 1:
            mapping_list.append(min_obj)
            '''
            print('#' * 100)
            print(min_obj[0])
            print(names1[min_obj[1]])
            print(names2[min_obj[2]])
            print('')
            print(clean_name(names1[min_obj[1]]))
            print(clean_name(names2[min_obj[2]]))
            print('')
            print('')
            '''
        if hist.get(min_obj[0],None) is None:
            hist[min_obj[0]]=0
        hist[min_obj[0]]+=1
        data.append(row)
    #pprint(hist)
    return mapping_list





def clean_name(n):
    n = re.sub('\w+\.','',n)
    n = n.replace('MBA','')
    n = n.replace('OA', '')
    n = re.sub('[^a-zA-Z0-9\s]', '',n)
    n = str.lower(n).strip()
    l = n.split(' ')
    l.sort()
    l.sort(key=len, reverse=True)
    l = [i for i in l if len(i)>3]
    n = ' '.join(l)
    return n

def generate_new_list(df, mapping_list):
    df = df.reset_index()
    for i in mapping_list:
        df = df.drop(i[2])
    return df


df1 = pd.DataFrame.from_csv('stefan.csv', sep=';',header=None, index_col=None)
df2 = pd.DataFrame.from_csv('tapp_dump.csv', sep=',',header=None)

names1 = df1[0].values
names2 = df2[1].values
mapping_list = compute_similarity(names1,names2)
df = generate_new_list(df2,mapping_list)
df = df[[1,5,3,4,10,11,2]]

f = lambda x: x.replace(',',', ').replace('"','').replace('[','').replace(']','')
g =lambda x: x.replace('\\u00c4','Ä').replace('\\u00e4','ä').replace('\\u00fc','ü')
df[2] = df[2].apply(f)
df[2] = df[2].apply(g)
df[11] = df[11].apply(f)
df[10] = df[10].apply(f)
print(df.head())
df.to_csv('aerzteliste_tapp_dump.csv', sep=';', index=False, header=False)