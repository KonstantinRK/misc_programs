# ---------------------------- Print Functions ---------------------------- #


def structure_print(structure, tab=0, number=0):
        r_string = ''
        if isinstance(structure, dict):
            for k, v in structure.items():
                v_string = structure_print(v,tab=tab+1)
                r_string = '{o}{t}{k} :\n{v}\n'.format(o=r_string, t='\t'*tab, k=k, v=v_string)
                r_string = r_string + '\n'
            return r_string
        elif isinstance(structure, list):
            for i in range(len(structure)):
                v_string = structure_print(structure[i], tab=tab, number=i)
                r_string = '{o}{v}\n'.format(o=r_string, n=i, v=v_string)
            return r_string
        else:
            if len(str(number))<2:
                number='0'+str(number)
            return '{t}{n}| {v}'.format(n=number, t='\t'*tab, v=str(structure))


class WLog:

    def __init__(self, verbose, lab):
        self.verbose = verbose
        self.lab = lab

    def display_input(self, name=None, force=False):
        if force is False:
            if self.verbose is True:
                self.__display_input(name)
        else:
            self.__display_input(name)

    def display_output(self, name=None, force=False):
        if force is False:
            if self.verbose is True:
                self.__display_processing(name)
        else:
            self.__display_processing(name)

    def __display_input(self, name=None):
        if name is None:
            s = structure_print(self.lab.input_dic)
        else:
            print(name,':')
            s = structure_print(self.lab.input_dic.get(name,''), 1)
        print(s)

    def __display_processing(self, name=None):
        if name is None:
            s = structure_print(self.lab.process_dic)
        else:
            print(name,':')
            s = structure_print(self.lab.process_dic.get(name,''), 1)
        print(s)

    def file_created(self, path):
        if self.verbose is True:
            print('\tFile: "{path}" was created'.format(path=path))

    def file_extracted(self, src_path, dst_path):
        if self.verbose is True:
            print('\tFile: "{dst_path}" was extracted from "{src_path}"\n'.format(src_path=src_path, dst_path=dst_path))

    def file_converted(self, src_path, dst_path):
        if self.verbose is True:
            print('\tFile: "{dst_path}" was converted from "{src_path}"'.format(src_path=src_path, dst_path=dst_path))

    def was_processed(self, name, number):
        path = self.lab.input_dic[name][number].path
        s = '\nFile: "{path}" was processed (Name: "{name}", Number: "{number}")\n'
        if self.verbose is True:
            print('')
            print('#'*100)
        print(s.format(path=path, name=name, number=number))
        print('#'*100)
        print('')

    def values_print(self, values, student=None):
        if self.verbose is True:
            print('\t', '-' * 90)
            print('\t|', student, ': ') if student is not None else print('\t|')
            print('\t', '-' * 90)
            for i in values:
                print('\t|', i.get('q_id'), i.get('a_id'), ' :      ', i.text)
            print('\t', '-' * 90)
            print('')
            print('')

    def exist(self, path):
        print('\tFile: "{path}" was already processed. Please set "cear=True" to reprocess this File again!'.format(path=path))


