from wLog import WLog
from wBasis import *
from collections import OrderedDict
import re
from pprint import pprint
import shutil
import math


class WLab:

    def __init__(self, lv_number, lab_name, verbose=True, clear=False):

        self.lv_number = lv_number
        self.lab_name = lab_name
        self.log = WLog(verbose, self)

        self.row_names = ['answer', 'correction', 'grading', 'points', 'comment']
        self.student_meta_header = ['matrnr', 'surname', 'name']

        self.re_answer_number = r"(?<=Gap\s)\d+(?=:)"
        self.re_answer_value = r"((?<=^Gap\s\d:\s').*(?='$)|(?<=^Gap\s\d\d:\s').*(?='$)|(?<=^Gap\s\d\d\d:\s').*(?='$))"
        self.re_student = r"(h\d{7}(?=\D)|h\d{8}(?=\D))?"
        self.re_file_type = {'pcap':r"\.pcap.*", 'pdml':r"\.pdml"}
        self.internal_sep = '|'
        self.internal_quote = '"'
        self.cell_sep = '|'
        self.error_margin = 0.015

        input_names = ['answer', 'capture', 'correction_sty', 'student_list', 'question_meta', 'question_meta_sty']
        process_names = ['answer', 'capture', 'pdml', 'correction', 'question_meta', 'report']

        self.base_processing_folder = 'temp'

        self.input_dic = OrderedDict([(i,[]) for i in input_names])
        self.process_dic = OrderedDict([(i,{}) for i in process_names])

        if clear is True:
            try:
                shutil.rmtree(self.base_processing_folder)
            except FileNotFoundError:
                pass

    def __processed(self, name, number):
        winput = WInput(self.input_dic[name][number].path, True)
        self.input_dic[name][number] = winput
        self.log.was_processed(name, number)

    def load_input(self, name, src_path):
        if src_path is None:
            self.input_dic[name] = []
        else:
            input_list = [WInput(i,False) for i in build_file_iter(src_path)]
            self.input_dic[name] = input_list
        self.log.display_input(name)

    def clear_temp(self):
        shutil.rmtree(self.base_processing_folder)

# ---------------------------- Extract student answers from learn-csv export ---------------------------- #

    def extract_answers(self, answer_nr, sep=';', escape_marker='"'):
        src_path = self.input_dic['answer'][int(answer_nr)].path
        dst_dir = os.path.join(self.base_processing_folder, 'answer', str(answer_nr))
        if make_dir_structure_in_path(dst_dir):
            data = equalise_table_shape(read_csv(src_path, sep, escape_marker))
            answer_dic = self.__build_answer_dic(data)

            self.__save_answers(dst_dir, answer_dic)
            self.__processed('answer', answer_nr)
        else:
            self.log.exist(src_path)

    def __build_answer_dic(self, answer_data):
        answer_dic = OrderedDict()
        for i in answer_data:
            row_dic = self.__read_answer_data_cell(i)
            answer_dic[i[0]] = OrderedDict([(i, row_dic.get(i, None)) for i in range(len(i)-2)])
        return answer_dic

    def __read_answer_data_cell(self, answer_row):
        row_dic = {}
        for i in answer_row:
            cell_string = str.strip(i)
            number = re.findall(self.re_answer_number,cell_string)
            value = re.findall(self.re_answer_value,cell_string)
            if any(number):
                row_dic[int(number[0])-1] = value[0] if any(value) else None
        return row_dic

    def __save_answers(self, dst_dir, answer_dic):
        for student, answers in answer_dic.items():
            data = transform_dic_to_table(answers, 'list')
            path = os.path.join(dst_dir, '.'.join(('h'+student, 'csv')))
            save_csv_from_list(path, data, self.internal_sep, self.internal_quote, ignore_header=True)
            self.log.file_created(path)


# ---------------------------- Extract captures and pdml from learn-zip export ---------------------------- #

    def extract_captures(self, capture_nr, force=False):
        src_path = self.input_dic['capture'][int(capture_nr)].path
        dst_dir = os.path.join(self.base_processing_folder, 'capture', str(capture_nr))
        if make_dir_structure_in_path(dst_dir) or force:
            unzip_folder(src_path, dst_dir, r"^(h(\d{7}|\d{8})?)_", r"\.pcap.*")
            self.log.file_extracted(src_path,os.path.join(dst_dir,'*'))
        else:
            self.log.exist(src_path)

    def extract_pdml(self, capture_nr, whitelist=None, wireshark_path='tshark', file_type='pdml', force=False):
        src_dir = os.path.join(self.base_processing_folder, 'capture', str(capture_nr))
        dst_dir = os.path.join(self.base_processing_folder, 'pdml', str(capture_nr))
        if make_dir_structure_in_path(dst_dir) or force:
            iter = build_file_iter(src_dir)
            for src_path in iter:
                student, filetype = separate_name_and_filetype(src_path, self.re_student, self.re_file_type['pcap'])
                if whitelist is None or student in whitelist:
                    dst_path = os.path.join(dst_dir, '.'.join((student,file_type)))
                    create_tshark_output(src_path, dst_path, wireshark_path, file_type)
                    self.log.file_converted(src_path, dst_path)
            self.__processed('capture', capture_nr)
        else:
            self.log.exist(self.input_dic['capture'][int(capture_nr)].path)


# ---------------------------- Extract correction from pdml ---------------------------- #

    def extract_correction(self, capture_nr, correction_sty_nr, xsl_parameter=None, whitelist=None, force=False):
        src_dir = os.path.join(self.base_processing_folder, 'pdml', str(capture_nr))
        dst_dir = os.path.join(self.base_processing_folder, 'correction', str(correction_sty_nr))
        if make_dir_structure_in_path(dst_dir) or force:
            sty_path = self.input_dic['correction_sty'][correction_sty_nr].path

            iter = build_file_iter(src_dir)
            for src_path in iter:
                student, file_type = separate_name_and_filetype(src_path, self.re_student, self.re_file_type['pdml'])
                if student is not None:
                    if whitelist is None or student in whitelist:
                        dst_path = os.path.join(dst_dir, student+'.csv')
                        values = xml_extraction(src_path, sty_path, xsl_parameter)
                        self.log.values_print(values, student)
                        data = [i.text for i in values]
                        save_csv_from_list(dst_path, data, self.internal_sep, self.internal_quote)

            self.__processed('correction_sty', correction_sty_nr)
        else:
            self.log.exist(self.input_dic['capture'][int(correction_sty_nr)].path)


# ---------------------------- Extract meta ---------------------------- #

    def extract_question_meta(self, question_meta_nr, question_meta_sty_nr, force=False):
        src_path = self.input_dic['question_meta'][question_meta_nr].path
        src_sty = self.input_dic['question_meta_sty'][question_meta_sty_nr].path
        dst_path = os.path.join(self.base_processing_folder, 'meta', 'question_meta_{n}.csv'.format(n=str(question_meta_nr)))
        if make_dir_structure_in_path(dst_path) or force:
            #dst_path = os.path.join(dst_path, 'question_meta_{n}.csv'.format(n=str(question_meta_nr)))
            values = xml_extraction(src_path, src_sty, None)
            self.log.values_print(values)
            data = self.__build_point_list(values, question_meta_nr)
            save_csv_from_list(dst_path, data, sep=self.internal_sep, quote=self.internal_quote)
        else:
            self.log.exist(self.input_dic['question_meta'][int(question_meta_nr)].path)

    def __build_point_list(self, values, answer_nr=0):
        f = lambda x: '0' + str(x) if len(str(x))<2 else str(x)
        q_a_name_list = []
        point_list = []
        for i in values:
            try:
                point = 0 if math.isnan(float(i.text)) else float(i.text)
            except Exception:
                point = 0
            q_id = i.get('q_id')
            a_id = i.get('a_id')
            q_a_name = f(answer_nr) + f(q_id) + f(a_id)

            q_a_name_list.append(q_a_name)
            point_list.append(point)
        return [q_a_name_list, point_list]

    def extract_student_meta(self, student_list_nr, sep=';', quote='"', force=False):
        src_path = self.input_dic['student_list'][student_list_nr].path
        dst_path = os.path.join(self.base_processing_folder, 'meta', 'student_meta.csv')
        if make_dir_structure_in_path(dst_path) or force:
            #dst_path = os.path.join(dst_path, 'student_meta.csv')
            data = read_csv(src_path, sep=sep, quote=quote)
            data.insert(0, self.student_meta_header)
            save_csv_from_list(dst_path, data, sep=self.internal_sep, quote=self.internal_quote)
        else:
            self.log.exist(self.input_dic['student_list'][int(student_list_nr)].path)


# ---------------------------- Create Lab Report ---------------------------- #

    def create_lab_report(self, answer_nr, correction_nr, question_meta_nr=None, force=False):
        src_answer_dir = os.path.join(self.base_processing_folder, 'answer', str(answer_nr))
        src_correction_dir = os.path.join(self.base_processing_folder, 'correction', str(answer_nr))
        src_question_meta = os.path.join(self.base_processing_folder, 'meta','question_meta_{n}.csv'.format(n=str(question_meta_nr)))
        src_student_list = os.path.join(self.base_processing_folder, 'meta', 'student_meta.csv')

        answer = build_file_list(src_answer_dir)
        correction = build_file_list(src_correction_dir)

        question_meta = self.__load_meta(src_question_meta)
        student_list = self.__load_meta(src_student_list)
        student_list = [i[:3] for i in student_list if any(i)]

        dst_file_name = '{lv}_{lab}_{nr}.csv'.format(lv=self.lv_number, lab=self.lab_name, nr=correction_nr)
        dst_path = os.path.join(self.base_processing_folder, 'report', dst_file_name)
        dst_path_individual = os.path.join(self.base_processing_folder, 'report', str(correction_nr))

        report_dic = self.__compile_report_dic(answer, correction, student_list)
        header = self.__create_header(question_meta, student_list)
        self.__save_individual_reports(dst_path_individual, report_dic, header, force)
        self.__save_report(dst_path, report_dic, header, force)


    def __load_meta(self, src_path):
        if os.path.exists(src_path):
            return read_csv(src_path, self.internal_sep, self.internal_quote)
        else:
            return None

    def __create_header(self, question_meta, student_list):
        if question_meta is not None and student_list is not None:
            return [['' for i in range(len(student_list[0])+1)] + question_meta[1], student_list[0] + ['type'] + question_meta[0]]
        elif student_list is None:
            return [['', '', question_meta[1]], [self.student_meta_header[0], 'type', question_meta[0]]]
        else:
            return [[], []]

    def __compile_report_dic(self, answer_files, correction_files, student_list=None):
        answer_dic = {separate_name_and_filetype(path, self.re_student): path for path in answer_files}
        student_dic = {i[0]: i for i in student_list} if student_list is not None else None
        report_dic = OrderedDict()
        for path in correction_files:
            student = separate_name_and_filetype(path, self.re_student)

            row_data_dic = self.__compile_row_data(student, path, answer_dic)
            table = self.__create_table_list(row_data_dic)
            if student_dic is not None:
                table = [student_dic[student] + i for i in table]

            report_dic[student] = table

        return report_dic

    def __compile_row_data(self, student, correction_path, answer_dic):
        row_dic = OrderedDict([(i, None) for i in self.row_names])
        correction = read_csv(correction_path, self.internal_sep, self.internal_quote)[0]
        row_dic['correction'] = ["'{0}".format(str(i)) for i in correction]
        empty_row = ['' for i in row_dic['correction']]

        a_path = answer_dic.get(student, None)
        if a_path is None:
            row_dic['answer'] = empty_row
        else:
            answer = read_csv(a_path, self.internal_sep, self.internal_quote)[0]
            row_dic['answer'] =["'{0}".format(str(i)) for i in answer]

        row_dic['grading'] = self.__create_grading_suggestion(row_dic['answer'], row_dic['correction'])
        row_dic['points'] = empty_row
        row_dic['comment'] = empty_row

        return row_dic

    def __create_table_list(self, row_data_dic):
        table = []
        for row_name, row in row_data_dic.items():
            table.append([row_name] + row)
        return table

    def __save_individual_reports(self, dst_dir, report_dic, header, force=False):
        for student, student_table in report_dic.items():
            dst_path = os.path.join(dst_dir, student+'.csv')
            table = header + student_table
            if make_dir_structure_in_path(dst_path) or force:
                save_csv_from_list(dst_path, table, self.internal_sep, self.internal_quote)

    def __save_report(self, dst_path, report_dic, header, force=False):
        table = header
        for student, student_table in report_dic.items():
            table = table + student_table
        if make_dir_structure_in_path(dst_path) or force:
            save_csv_from_list(dst_path, table, self.internal_sep, self.internal_quote)

    def __create_grading_suggestion(self, answer_list, correction_list):
        grade_sugg = []
        for i in range(len(correction_list)):
            try:
                answer = answer_list[i]
            except IndexError:
                answer = 'Error'
            correction = correction_list[i]
            code = self.__get_code(correction)
            answer = self.__clean_value(code, answer)
            correction = self.__clean_value(code, correction)
            matching = 0
            for c in correction:
                for a in answer:
                    if a is not None and a != '' and c is not None:
                        if code != 1:
                            if c == a:
                                matching += 1
                        else:
                            delta = min(a,c)*self.error_margin
                            if c-delta <= a and c+delta >= a:
                                matching += 1
            grade_sugg.append(min(matching/len(correction),1))
        return grade_sugg

    def __clean_value(self, code, value):

        if self.cell_sep not in value: ## Remove later !!!!!
            value = value.replace('|', self.cell_sep) ## Remove later !!!!!
        value = str.split(value, self.cell_sep)
        clean = []
        for v in value:
            if code == 0 or code == 1:
                try:
                    new_value = re.findall(r'(\d+[\.|,]\d+|\d+)',v)[0]
                    new_value = new_value.replace(',','.')
                    if code == 0:
                        try:
                            clean.append(int(new_value))
                        except ValueError:
                            clean.append(int(round(float(new_value),0)))
                    else:
                        clean.append(round(float(new_value),5))
                except IndexError:
                    clean.append(None)
            if code == 3:
                clean.append(v.strip())
        return clean


    def __get_code(self, correction_value):

        val = correction_value.split(self.cell_sep)[0]
        if val[0] == "'":
            val = val[1:]
        try:
            val = float(val)
            try:
                if val - int(val) == 0:
                    return 0
                else:
                    return 1
            except ValueError:
                return 1
        except ValueError:
            return 3






    # ---------------------------- Display ---------------------------- #

    def show_input(self):
        self.log.display_input(force=True)

    def show_output(self):
        self.log.display_output(force=True)