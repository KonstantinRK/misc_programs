import re
import datetime
import pandas as pd
import json

def preprocessing(s):
    stream = s.split('\n')
    data_raw = {}
    key = 0
    name = 'No Name'
    for i in range(len(stream)):
        if stream[i].isnumeric() and len(stream[i]) <= 2:
            if stream[i + 1].split(' ')[0].split('-')[0].isalpha():
                key = stream[i].strip()
                name = stream[i + 1].strip()
                data_raw[key] = {'name': name, 'data': []}

        if stream[i] != key and stream[i] != name:
            data_raw[key]['data'].append(stream[i])
    return data_raw

def cleaning(data):
    new_data ={}
    for k,v in data.items():
        new_data[k]={}
        name = v['name']
        if name[-1]=='-':
            name = name[:-1]
            v['data'][0] = '-'+v['data'][0]
        text = name.split('(')
        try:
            new_data[k]['info'] = text[1].split(')')[0].strip()
            new_data[k]['name'] = text[0].strip()
        except IndexError:
            new_data[k]['name'] = text[0].strip()
            new_data[k]['info'] = ''
        data = [i.replace('V','').strip()  for i in v['data'] if i.replace('V','').strip()!='']
        new_data[k]['dates'] = clean_data(data)
    return new_data





def clean_dates(dates):
    date_list = []
    if ',' in dates:
        dates = [i.strip().split('-') for i in dates.split(',')]
        dates = [i+i if len(i)<2 else i for i in dates]
        keys = []
        for i, obj in enumerate(dates):
            for j, date in enumerate(obj):
                if any(re.findall('^\d{1,2}\.(\d{1,2}\.)',date)):
                    month = re.findall('^\d{1,2}\.(\d{1,2}\.)',date)[0]
                    keys.append([i,j,month])
        new_keys = {}
        for k in range(len(keys)):
            s = 0 if k==0 else keys[k-1][0]+1
            for j in range(s,keys[k][0]):
                new_keys[j, 0] = keys[k][2]
                new_keys[j, 1] = keys[k][2]
            k_s = 0 if k==0 else k-1
            if keys[k_s][0]==keys[k][0]:
                new_keys[keys[k][0],0] = ''
                new_keys[keys[k][0],1] = ''
            elif keys[k][1]==1:
                new_keys[keys[k][0], 0]= keys[k][2]
                new_keys[keys[k][0], 1] = ''
        keys = sorted(new_keys.keys())
        for k in keys:
            dates[k[0]][k[1]]=dates[k[0]][k[1]]+new_keys[k]
        date_list = [tuple(i+[False]) for i in dates]
    elif dates[0] == '-':
        date = min(datetime.datetime.strptime(dates[1:],'%d.%m.'), datetime.datetime.now())
        new_date = clean_date(date.strftime('%d.%m.') + dates)
        date_list.append((new_date[0],new_date[1],False))
    elif any(re.findall('[a-zA-Z]', dates)):
        date_list.append(('1.9.','4.11.',True))
    elif '-' in dates:
        date = clean_date(dates)
        date_list.append((date[0],date[1],False))
    else:
        pass
    for i in range(len(date_list)):
        date_list[i]=transform_date(date_list[i])
    return date_list

def transform_date(date):
    a=datetime.datetime.strptime(date[0], '%d.%m.').strftime('%d.%m.')
    b=datetime.datetime.strptime(date[1], '%d.%m.').strftime('%d.%m.')
    return (a,b,date[2])

def clean_date(date):
    start, end = date.split('-')
    if re.findall('^\d{1,2}\.$', start):
        start = start + re.findall('^\d{1,2}\.(\d{1,2}\.)$', end)[0]
    return (start, end)

def clean_data(data):
    new_data = []
    data_str = '|'.join(data)
    data_str = data_str.replace('-|-','-')
    data_str = data_str.replace('|.', '.')
    data_str = data_str.replace('-|', '-')
    data_str = re.sub('(?<=\d\.)(\s+)(?=\d)','|',data_str)
    data_str = re.sub('(?<=\d)\|(?=\d)', '', data_str)
    data = data_str.split('|')
    for i in data:
        new_data = new_data + clean_dates(i)
    return new_data

def consider_info(data):
    for k,v in data.items():
        sub_dic = {'Ruhetag':'Ruhetag','Ruhetage':'Ruhetag','Ruhet.':'Ruhetag'}
        sub_dates = {'Mo':0,'So':6,'Mi':2,'Di':1, '+Fei':'','Fr':4}
        info = v['info']
        for old,new in sub_dic.items():
            info = info.replace(old, str(new))
        A = False
        B = False
        for i in sub_dates.keys():
            if i in info:
                A = True
        if 'Ruhetag' in info:
            B = True

        if A:
            for old, new in sub_dates.items():
                info = info.replace(old, str(new))
            days = []
            if any(re.findall('\d\-\d',info)):
                s,e = re.findall('\d\-\d',info)[0].split('-')
                days = [i for i in range(int(s),int(e)+1)]
            elif any(re.findall('\d\+\d',info)):
                days = [int(i) for i in re.findall('\d\+\d',info)[0].split('+')]
            elif any(re.findall('\s*\d\s',info)):
                days = [int(i) for i in re.findall('\s*\d\s',info)]
            if not B:
                days = [i for i in range(7) if i not in days]
            data[k]['closed']=days
    return data




def allday(year):
    days = {i:[] for i in range(7)}
    d = datetime.date(year, 1, 1)
    while d.year == year:
        days[d.weekday()].append(d)
        d += datetime.timedelta(days = 1)
    return days

def get_allday(year, day):
   d = datetime.date(year, 1, 1)
   d += datetime.timedelta(days = 6 - d.weekday())
   d += datetime.timedelta(days = 1 + day)
   days = []
   while d.year == year:
      days.append(d)
      d += datetime.timedelta(days = 7)

def create_time_range(inp_dates, year):
    dates = []
    check = False
    for date in inp_dates:
        a = datetime.datetime.strptime(date[0]+str(year), '%d.%m.%Y').date()
        b = datetime.datetime.strptime(date[1]+str(year), '%d.%m.%Y').date()
        c = date[2]
        if c:
            check = True
        dates.append([a,b,c])

    date_range = []
    for date in dates:
        date_range= date_range + daterange(date[0],date[1])

    return date_range, check

def create_time_table(data,year, ball, loc_dict=None):
    if loc_dict is None:
        loc_dict = {}
    meta = {}
    year_range = daterange(datetime.date(year, 1, 1),datetime.date(year, 12, 31))
    df = pd.DataFrame()
    df['days']=year_range
    df = df.set_index('days')
    for k,v in data.items():
        dates = v['dates']
        data_range, check = create_time_range(dates, year)
        if check is False:
            df_buf = pd.DataFrame()
            df_buf['days'] = data_range
            df_buf = df_buf.set_index('days')
            df_buf[int(k)] = 1
            df = pd.concat([df, df_buf], join='outer', axis=1)


        meta[int(k)] = {'name': v['name'],'check':check, 'loc':loc_dict.get(int(k),'')}
    df = df.dropna(how='all')
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    df.index = pd.to_datetime(df.index)
    df = df.loc[str(date):ball]
    return df, meta

def daterange(date1, date2, skip=None):
    date_range = []
    skip = [] if skip is None else skip
    for n in range(int ((date2 - date1).days)+1):
        day = date1 + datetime.timedelta(n)
        if day.weekday() not in skip:
            date_range.append(day)
    return date_range


def save(data, meta, year):
    year = str(year)
    data.to_csv('{}_heurigen_data.csv'.format(year))

    with open('{}_heurigen_meta.json'.format(year),'w') as f:
        json.dump(meta,f)

    df = data.copy()
    df.columns = [meta[k]['name'] for k in data.columns]
    df.to_csv('{}_heurigen_table.csv'.format(year))
    df.transpose().to_csv('{}_heurigen_table_t.csv'.format(year))
    return {'data_file':'{}_heurigen_data.csv'.format(year), 'meta_file':'{}_heurigen_meta.json'.format(year)}

def create_loc_dic(meta):
    loc_list = []
    for i in meta:
        loc_list = loc_list + [(j,i[0]) for j in range(i[1],i[2])]
    return {i[0]:i[1] for i in loc_list}


def preprocess(pdf, meta, year, ball_date):
    with open(pdf, 'r') as f:
        s = f.read()
    loc_dic = create_loc_dic(meta)
    data_raw = preprocessing(s)
    data = cleaning(data_raw)
    data = consider_info(data)
    data, meta = create_time_table(data,year, ball_date,loc_dic)
    return save(data, meta,2018)
