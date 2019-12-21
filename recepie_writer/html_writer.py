from pprint import pprint


style_path = 'style.css'
template_path = 'template.html'
local_script = 'script_local.js'
global_script = 'script_global.js'

temp_content='''
        <div class="main_container {version}">
            <div class="phase_container">
                {phases}
            </div>
            <div class="step_container">
                {steps}
            </div>
            <div class="ingredient_container">
                {table}
            </div>
        </div>
        '''


temp_version_button = '''
    <span class="tooltip_bottom">
    <span class="version_button_div">
        <button class="version_button" id="button_{id}" onclick="selectVersion('{id}')" style="vertical-align:middle"><span>{name}</span></button>
    </span>
    <span class="tooltiptext_bottom">{comment}</span></span>
    '''


temp_phase_button = '''
    <div class="phase_button_div">
        <button class="phase_button" id="button_{version}_{id}" onclick="selectInfo('{version}_{id}')" style="vertical-align:middle"><span>{name}</span></button>
    </div>
    '''

temp_step_field = '''
            <div class="step_field {version}_{id}">
                <h2>{name}:</h2>
                {steps}
            </div>
'''

temp_table_field = '''
            <div class="ingredient_list {version}_{id}">
                {table}
            </div>
'''


temp_step = '''
            <div class="step {version}_{id}">
                <h3>{name}:</h3>
                {text}
            </div>
            '''

temp_meta = {'ingredient': '<span class="ingredient {meta}">{text}</span>',
             'comment': '<span class="tooltip">{text}<span class="tooltiptext">{meta}</span></span>',
             'time': '<span class="time" value="{meta}">{text}</span>',
             'temperature':'<span class="temperature" value="{meta}">{text}</span>',
             'reference': '<span class="reference" value="{meta}">{text}</span>',
             'url': '<a target="_blank" href="{meta}">{text}</a>'}


def create_html(rws_dic):
    style = load(style_path)
    html_temp = load(template_path)
    script_g = load(global_script)
    script_l = load(local_script)
    versions = rws_dic['data']
    sub_dic = {'style':style,
               'start_version': versions[0]['id'],
               'title': rws_dic['title'],
               'comment':rws_dic['comment'],
               'version_buttons':'',
                'content':'',
               'script_local':script_l,
               'script_global':script_g}


    for version in versions:
        content_sub_dic={
               'phases':'',
               'steps':'',
               'table':''}

        sub_dic['version_buttons'] += temp_version_button.format(**version)
        pprint(version['id'])
        for phase in version['data']:
            pprint(phase['id'])
            content_sub_dic['phases'] += temp_phase_button.format(version=version['id'], **phase)
            table = create_table(phase['ingredient_in'])
            if table != '':
                content_sub_dic['table'] += temp_table_field.format(version=version['id'],table=table,
                                                        name=phase['name'], id=phase['id'])
            steps = ''
            for s in phase['steps']:
                print(s['id'])
                step = create_step(s,version['id'])
                steps+= step + '\n'
            content_sub_dic['steps'] += temp_step_field.format(version=version['id'], steps=steps, name=phase['name'], id=phase['id'])
        sub_dic['content'] += temp_content.format(version=version['id'], **content_sub_dic)


    return html_temp.format(**sub_dic)



def create_step(step,version):
    #print(step)
    text = step['text']
    for k,v in temp_meta.items():
        for i in step[k]:
            buff = v.format(**i)
            text = text.replace(i['replace'],buff)
    #print(temp_step.format(id=step['id'],name=step['name'],text=text))
    return temp_step.format(version=version,id=step['id'],name=step['name'],text=text)


def create_table(ingr):
    if not any(ingr):
        return ''
    table='<table><tr><th>Ingredients:</th><th></th><th></th></tr>\n{body}</table>'
    row = '<tr class="{meta}">' \
          '<td class="first_col" >{0}</td>' \
          '<td>{1}</td>' \
          '<td>{2}</td>' \
          '</tr>'
    body = ''
    for k,v in ingr.items():
        #print(v)
        body+=row.format(*[v[0].title().replace('_',' '),*v[1:]], meta=k) + '\n'
    table=table.format(body=body)
    #print(table)

    return table

def load(path):
    with open(path, 'r') as f:
        return f.read()