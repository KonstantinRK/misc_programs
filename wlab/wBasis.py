import os
from collections import namedtuple
import csv
import zipfile
import re
from subprocess import call
from lxml import etree

# ---------------------------- File System ---------------------------- #

def beep(x):
    for i in range(x):
        os.system("afplay /System/Library/Sounds/Glass.aiff;")

# returns content of dir as list or wraps path in list
def build_file_list(src_path):
    if not os.path.exists(src_path):
        raise FileNotFoundError
    if os.path.isdir(src_path):
        file_list = []
        for i in os.listdir(src_path):
            file_list.append(os.path.join(src_path,i))
    else:
        file_list = [src_path]

    return file_list


# returns content of dir as iter or wraps path in iter
def build_file_iter(src_path):
    if not os.path.exists(src_path):
        raise FileNotFoundError(src_path)
    if os.path.isdir(src_path):
        for i in os.listdir(src_path):
            yield os.path.join(src_path,i)
    else:
            yield src_path


def make_dir_structure_in_path(path):
    if os.path.exists(path):
        return False
    else:
        if os.path.splitext(path)[1] != '':
            path = os.path.dirname(path)
        try:
            os.makedirs(path)
            return True
        except FileExistsError:
            return True


def separate_name_and_filetype(path, new_name_regex_pattern, regex_pattern_file=None):
    try:
        path = os.path.basename(path)
        name = re.findall(new_name_regex_pattern, path)[0]
        if regex_pattern_file is None:
            return name
        else:
            file_type = re.findall(regex_pattern_file, path)[0]
            return name, file_type
    except IndexError:
        return None, None

# ---------------------------- CSV Processing ---------------------------- #


def read_csv(src_path, sep, quote='"', encoding='utf-8'):
    with open(src_path,'r',encoding=encoding) as f:
        data = list(csv.reader(f, delimiter=sep, quotechar=quote, quoting=csv.QUOTE_ALL, skipinitialspace=True))
    return data


def equalise_table_shape(data):
    max_row_len = 0
    for row in data:
        max_row_len = max_row_len if len(row)<max_row_len else len(row)
    for row_nr in range(len(data)):
        data[row_nr] = data[row_nr] + ['' for i in range(len(data[row_nr]),max_row_len)]
    return data

def save_csv_from_list(dst_path, data, sep, quote, ignore_header=False, encoding='utf-8'):
    __save_csv_from_list(dst_path, data, sep, quote, ignore_header, encoding)
    if not test_csv(dst_path, data, sep, quote, ignore_header, encoding):
        __save_csv_from_list(dst_path, data, sep, quote, ignore_header, encoding, True)

def __save_csv_from_list(dst_path, data, sep, quote, ignore_header=False, encoding='utf-8', line_break=False):
    kwargs = {'encoding':encoding} if line_break else {'encoding':encoding, 'newline':''}
    if not isinstance(data[0], list):
        data = [data]
    with open(dst_path,'w',**kwargs) as f:
        writer = csv.writer(f, delimiter=sep, quotechar=quote)
        for i in data:
            if ignore_header is True:
                ignore_header = False
            else:
                writer.writerow(i)
    return data

def test_csv(path,data,sep,quote,ignore_header=False,encoding='utf-8'):
    csv = read_csv(path,sep,quote,encoding)
    k = 1 if ignore_header else 0
    if len(data)-k==len(csv):
        return True
    else:
        return False



def save_csv_from_dic(dst_path, data, sep, quote, ignore_header=False, encoding='utf-8'):
    header = list(data[0].keys())
    with open(dst_path,'w',encoding=encoding) as f:
        writer = csv.DictWriter(f, delimiter=sep, quotechar=quote, fieldnames=header)
        if ignore_header is False:
            writer.writeheader()
        for i in data:
            writer.writerow(i)
    return data


def __transform_dic_to_table_list(data_dic, max_data):
    header = list(data_dic.keys())
    table_list = [header]
    for row_nr in range(max_data):
        row = []
        for k in header:
            try:
                row.append(data_dic[k][row_nr])
            except IndexError:
                row.append(None)
        table_list.append(row)
    return table_list


def __transform_dic_to_table_dic(data_dic, max_data):
    header = list(data_dic.keys())
    table_list = []
    for row_nr in range(max_data):
        row = {}
        for k in header:
            try:
                row[k] = data_dic[k][row_nr]
            except IndexError:
                row[k] = None
        table_list.append(row)
    return table_list


def transform_dic_to_table(data_dic, kind='list'):
    data_dic, max_data = __clean_and_count_dic(data_dic)
    table = None
    if kind == 'list':
        table = __transform_dic_to_table_list(data_dic, max_data)
    elif kind == 'dict':
        table = __transform_dic_to_table_dic(data_dic,max_data)
    return table


def __clean_and_count_dic(data_dic):
    max_data = 0
    for k, data in data_dic.items():
        if not isinstance(data, list):
            data = [data]
            data_dic[k] = data
        max_data = max_data if len(data) < max_data else len(data)
    return data_dic, max_data


# ---------------------------- Misc ---------------------------- #


def unzip_folder(src_zip, dst_dir, new_name_regex_pattern, regex_pattern_file):
    archive = zipfile.ZipFile(src_zip)
    for file_name in archive.namelist():
        if file_name[0:2] != '__':
            name = re.findall(new_name_regex_pattern, file_name)[0][0]
            file_type = re.findall(regex_pattern_file, file_name)[0]
            dst_path = os.path.join(dst_dir, name+file_type)
            archive.extract(file_name, dst_dir)
            os.rename(os.path.join(dst_dir, file_name), dst_path)


def create_tshark_output(src_path, dst_path, wireshark_path, output_type):
    value = call('{tshark} -r {path_from} -T {output_type} > {path_to}'.format(tshark=wireshark_path,
                                                                                   path_from=src_path,
                                                                                   path_to=dst_path,
                                                                                   output_type=output_type), shell=True)
    return value


def xml_extraction(path, sty_path, xsl_parameter, encoding='iso-8859-1'):

    if xsl_parameter is None:
        xsl_parameter = {}
    xslt = etree.parse(sty_path)
    transform = etree.XSLT(xslt)
    parser = etree.XMLParser(recover=True, encoding=encoding)
    xml = etree.parse(path, parser)
    newdom = transform(xml, **xsl_parameter)
    results = newdom.xpath('/Q')
    return results


# ---------------------------- Clear String ---------------------------- #

def get_string_clean_foo(base_string, change_string):
    print(base_string, change_string)
    return change_string


# ---------------------------- Data Structures ---------------------------- #

class WInput(namedtuple('WInput', ('path', 'processed'))):
    __slots__ = ()

    def __str__(self):
        '''
        r_string = '{name}: \n\t| Path:  {path}\n\t| Processed:  {processed}'.format(name=os.path.basename(self.path),
                                                                                     path=self.path, processed=self.processed)
        '''
        r_string = '{name}  ->  Processed: {processed}  (Path:{path})'.format(name=os.path.basename(self.path),
                                                                                     path=self.path, processed=self.processed)
        return r_string




