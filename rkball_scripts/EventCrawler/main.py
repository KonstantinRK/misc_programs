import pandas as pd
from bs4 import BeautifulSoup
import requests
import datetime
from pprint import pprint
import numpy as np

def get_event_tables(url, *args, **kwargs):
    table = pd.read_html(url,*args,**kwargs)
    return table


def get_next_url(soup, url,  match):
    next_url = soup.find('a',match)
    next_url = next_url.get('href')
    return url + next_url



def little_spider(url, base_url, column_order, max_date, df = None, pages=1):
    if df is None:
        df = pd.DataFrame(columns=column_order)

    raw = requests.get(url)
    soup = BeautifulSoup(raw.text, "lxml")
    table = build_table(soup,{'summary':'Veranstaltungen'}, base_url)
    table = fill_time(table, {'class': 'verticaltable'})
    new_df = pd.DataFrame.from_dict(table)
    new_df = new_df[column_order]
    new_df = create_new_df(new_df)
    df = df.append(new_df)
    if df['datum'].max() < max_date or pages > 1:
        next_url = get_next_url(soup,base_url,{'rel':'Next'})
        final_df = little_spider(next_url,base_url,column_order,max_date,df,pages=pages-1)
    else:
        final_df = df
        final_df.sort_values(by='datum', inplace=True)
        final_df.reset_index(drop=True, inplace=True)

    return final_df


def fill_time(table, match):
    time_col = []
    for url in table['url']:
        time = None
        print(url)
        soup = BeautifulSoup(requests.get(url).text,'lxml')
        for data in soup.findAll('table',match):
            for row in data.findAll('tr'):
                if 'Zeit' in str.strip(row.find('th').text):
                    time = row.find('td').text
        time_col.append(time)
    table['zeit'] = time_col
    return table


def build_table(soup, match, base_url):
    table_soup = soup.find('table',match)
    columns = [str.lower(i.text) for i in table_soup.findAll('th')]
    table = [[] for i in columns]
    urls = []
    for row in table_soup.findAll('tr'):
        count = 0
        for cell in row.findAll('td'):
            table[count].append(cell.text)
            if columns[count] == 'veranstaltung':
                urls.append(base_url + cell.find('a').get('href'))
            count += 1
    header_table = {columns[i]:table[i] for i in range(len(columns))}
    header_table['url'] = urls
    return header_table



def add_remaining_values(new_df, old_df, from_column):
    index = list(old_df.index)[from_column:]
    for i in index:
        new_df[i] = old_df[i]
    return new_df


def convert_to_date(date_str, index = 0):
    pattern_list = ['%d.%m.%Y','%d.%m.%y']
    try:
        return datetime.datetime.strptime(str.strip(date_str),pattern_list[index]).date()
    except ValueError:
        return convert_to_date(date_str, index+1)


def add_line(old_df):
    datum = old_df['datum']
    new_df = pd.DataFrame()
    if '-' in datum:
        datum = str.split(datum,'-')
        datum_start = convert_to_date(datum[0])
        datum_end =  convert_to_date(datum[1])
        days = (datum_end-datum_start).days +1
        new_df['datum'] = pd.date_range(datum_start, periods=days)

    else:
        datum = convert_to_date(datum)
        new_df['datum'] = [datum]

    new_df['datum'] = pd.to_datetime(new_df['datum'])
    new_df = add_remaining_values(new_df, old_df, 1)
    return new_df

def create_new_df(old_df):
    new_df = pd.DataFrame(columns=list(old_df.columns))
    for i in old_df.iterrows():
        new_line = add_line(i[1])
        #print(new_line)
        new_df = new_df.append(new_line)

    new_df.sort_values(by='datum', inplace=True)
    new_df.reset_index(drop=True, inplace=True)
    return new_df


def create_html(df):
    body_string = '<ul>{elements}</ul>'
    elements = ''
    for i in df.groupby('veranstaltung'):
        event = '<li><details><summary>{title}</summary><div class="info">{table}</div></details>'
        title = i[0]
        body = i[1]
        body = body[['datum', 'zeit', 'ort']]
        #print(body.style.render())
        table = body.to_html(border=0, index = False, bold_rows=False)
        #table = body.style.render()
        new_event = event.format(title=title,table = table)
        elements = ''.join((elements,new_event))
    body_string = body_string.format(elements=elements)
    with open('html_template.html','r') as file:
        html_string = file.read()
    html_string = str(html_string)
    html_string = html_string.format(body = body_string)
    with open('event_overview.html','w') as file:
        file.write(html_string)


def google_cal_export(df):
    df['datum'] = pd.to_datetime(df['datum'])
    df['datum'] = df['datum'].dt.strftime('%m/%d/%Y')
    df['zeit'] = df['zeit'].str.replace(r'[a-zA-Z]','')
    df['zeit'] = df['zeit'].str.strip()
    df['zeit'] = df['zeit'].fillna('00:01-23:59')
    df[['start_zeit','end_zeit']] = df['zeit'].str.split('-',expand=True)

    new_df = pd.DataFrame()
    new_df['Subject'] = df['veranstaltung']
    new_df['Start Date'] = df['datum']
    new_df['End Date'] = df['datum']
    new_df['Start Time'] = df['start_zeit']
    new_df['End Time'] =  df['end_zeit']
    new_df['Location'] = df['ort']
    new_df['Description'] = df['url']

    return new_df

max_date = datetime.datetime(2018,11,4)



column_order = ['datum','veranstaltung','zeit','ort', 'url']

#df = little_spider('https://www.klosterneuburg.at/de/Kultur_und_Bildung/Veranstaltungen','http://www.klosterneuburg.at',column_order,max_date,pages=4)
#print(df)
#df.to_csv('test.csv',sep=';')
df = pd.DataFrame.from_csv('test.csv',sep=';')
df['datum'] = pd.to_datetime(df['datum'])
df = df[df['datum']<max_date]
df.reset_index(drop=True,inplace=True)
df.sort_values(by='datum', inplace=True)
df.to_csv('event_list.csv',sep=';')
'''
'''

df = pd.DataFrame.from_csv('event_list.csv', sep=';')
df_g = google_cal_export(df)
df_g.to_csv('google_cal.csv', index=False)
create_html(df)



