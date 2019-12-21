import rws_reader
import html_writer
import os
from pprint import pprint

def convert_to_html(path):
    with open(path, 'r') as f:
        doc = f.read()
    dic = rws_reader.extract_data(doc)

    html = html_writer.create_html(dic)
    name = os.path.splitext(path)[0]
    with open('{name}.html'.format(name=name),'w') as f:
        f.write(html)
    return dic


convert_to_html("rk_ball_2018_cookies.rws")