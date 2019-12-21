import json
import csv
import os

def convert_to_csv(json_path, csv_dir=None, name_map=None):
    cols = ["task_name","start_date", "end_date", "follower", "assignee", "subtask_of","tags","description"]
    name = os.path.splitext(os.path.basename(json_path))[0]
    csv_path = '{}.csv'.format(name) if csv_dir is None else os.path.join(csv_dir,'{}.csv'.format(name))
    with open(json_path,'r') as f:
        dic = json.load(f)
    if name_map is not None:
        for k in range(len(dic)):
            k['assignee']=name_map[k['assignee']]
    table = [cols] + [[j[i] for i in cols] for j in dic]

    with open(csv_path,'w') as f:
        csv_writer = csv.writer(f,delimiter=';')
        for i in table:
            csv_writer.writerow(i)

base = "/Users/krk/Dropbox/CloudStation/CloudStation/Rotkreuz-Ball 2018/Planung/imports"
src = os.path.join(base,'werbung.json')
convert_to_csv(src,base)