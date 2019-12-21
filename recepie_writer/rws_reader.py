import re
from pprint import pprint

def extract_data(doc):
    title = re.findall(r"<(.*):.*?>",doc)[0]
    comment = re.findall(r"<.*:(.*?)>", doc)[0]
    data_dic = {'title':title, 'data':[], 'comment':comment}
    doc = re.sub(r"<(.*)>", '',doc)
    versions = extract_nesting(doc)
    for j in range(len(versions)):
        version = versions[j][0]
        doc = versions[j][1]
        version_dic = parse_version(version)
        version_dic['data']=[]
        phases = extract_nesting(doc)
        for i in range(len(phases)):
            phase = phases[i][0]
            content = extract_nesting(phases[i][1])
            phase_dic = parse_phase(phase)
            phase_dic['steps'] = []
            for step in content:
                step_dic = parse_step(step)
                for ing in step_dic['ingredient']:
                    my_ing = [*ing['meta']] if type(ing['meta'])==list else [ing['meta']]
                    for h in my_ing:
                        key = h.lower().strip().replace(' ','_')
                        if phase_dic['ingredient_in'].get(key,None) is None:
                            phase_dic['ingredient_in'][key]=[key,'-','-']
                phase_dic['steps'].append(step_dic)
            version_dic['data'].append(phase_dic)
        data_dic['data'].append(version_dic)
    return data_dic

def parse_version(version):
    name = re.findall(r'#(.*?)\[',version)[0].strip()
    comment = re.findall(r'#.*?\[(.*?)\]',version)[0].strip()
    return {'id':name.lower(), 'name':name, 'comment':comment}

def parse_phase(phase):

    re_name = r'#(.*?)\['
    re_ing = r'\((.*?)\)'
    phase = phase.replace('\n','')
    split_phase = phase.split('->')
    string_in = split_phase[0].strip()
    try:
        string_out = split_phase[1]
    except IndexError:
        string_out = ''

    name = re.findall(re_name, phase)[0]
    key = name.lower().replace(' ','_')
    ing_in = re.findall(re_ing, string_in)
    ing_out = re.findall(re_ing, string_out)

    ing_in = {i.split(',')[0].strip().lower().replace(' ','_'): [j.strip() for j in i.split(',')] for i in ing_in }
    ing_out = {i.split(',')[0].strip().lower().replace(' ','_'): [j.strip() for j in i.split(',')] for i in ing_out }
    return {'id':key,'name':name, 'ingredient_in':ing_in,'ingredient_out':ing_out}


def parse_step(step):
    f = lambda x,k: x.strip().lower().replace(' ','_') if k=='ingredient' else x.strip()
    step_dic = {}
    name = step[0][1:].strip()

    content = step[1]
    reg_dic = {'ingredient':r'\${.*?}\$','comment':r'!{.*?}!','time':r"'{.*?}'",'temperature':r"°{.*?}°",
               'reference':r'%{.*?}%','url':r'&{.*?}&'}

    step_dic['name']=name.strip()
    step_dic['id'] = name.lower().strip().replace(' ','_')
    step_dic['text'] = content
    for k,v in reg_dic.items():
        regex = re.compile(v, re.MULTILINE | re.DOTALL)
        data = re.findall(regex,content)
        #print(data)
        step_dic[k] = []
        for i in data:
            buffer = ' '.join([k.strip() for k in i.split('\n')])
            data_dic = {}
            data_dic['replace']=i
            data_dic['text'] = re.findall(r'{(.*?):.*?}',buffer)[0]
            data_dic['meta'] = re.findall(r'{.*?:(.*?)}', buffer)[0]
            l = re.findall(r'\[(.*?)\]',data_dic['meta'])
            if any(l):
                data_dic['meta'] = [f(j,k) for j in l[0].split(',')]
            else:
                data_dic['meta']= f(data_dic['meta'],k)
            step_dic[k].append(data_dic)
    return step_dic


def extract_nesting(doc):
    phases=[]
    block = [0,0,0]
    nesting = 0
    for i in range(len(doc)):
        if doc[i]=='#' and nesting==0:
            block[0]=i

        if doc[i]=='{':
            if nesting == 0:
                block[1] = i
            nesting+=1

        if doc[i]=='}':
            nesting+= -1
            if nesting == 0:
                block[2] = i
                phases.append([doc[block[0]:block[1]].strip(), doc[block[1] + 1:block[2]].strip()])
    return phases