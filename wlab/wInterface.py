from wBasis import *
from wLog import WLog
from wLab import WLab


class WInterface:

    def __init__(self, lv_number, lab_name, verbose=True, clear=False):

        self.lab = WLab(lv_number, lab_name, verbose, clear)


# ---------------------------- Load Input ---------------------------- #

    def load_answers(self, src_path):
        self.lab.load_input('answer', src_path)

    def load_captures(self, src_path):
        self.lab.load_input('capture', src_path)

    def load_correction_sty(self, src_path):
        self.lab.load_input('correction_sty', src_path)

    def load_question_meta(self, src_path):
        self.lab.load_input('question_meta', src_path)

    def load_question_meta_sty(self, src_path):
        self.lab.load_input('question_meta_sty', src_path)

    def load_students(self, src_path):
        self.lab.load_input('student_list', src_path)

    def load_input(self, src_answer, src_capture, src_correction_sty, src_students=None, src_question_meta=None, src_question_meta_sty=None):
        self.load_answers(src_answer)
        self.load_captures(src_capture)
        self.load_correction_sty(src_correction_sty)
        self.load_students(src_students)
        self.load_question_meta(src_question_meta)
        self.load_question_meta_sty(src_question_meta_sty)
        if self.lab.log.verbose is False:
            self.show_input()


# ---------------------------- Process Input ---------------------------- #

    def process_lab(self, answer, capture, correction_sty, question_meta=None, question_meta_sty=None, student_list=None):
        self.extract_lab_files(answer, capture)

        self.extract_lab_correction(capture, correction_sty, force=True)

        self.lab.extract_question_meta(question_meta, question_meta_sty, force=True)
        self.lab.extract_student_meta(student_list)

        self.lab.create_lab_report(answer, correction_sty, question_meta, force=True)


    def extract_meta(self,question_meta, question_meta_sty, student_list, force=False):
        self.lab.extract_question_meta(question_meta, question_meta_sty, force=force)
        self.lab.extract_student_meta(student_list, force=force)

    def create_lab_report(self, answer, correction_sty, question_meta, force=False):
        self.lab.create_lab_report(answer, correction_sty, question_meta, force=force)

    def extract_lab_files(self, answer, capture):
        self.lab.extract_answers(answer, ';', '"')
        self.lab.extract_captures(capture)
        self.lab.extract_pdml(capture)

    def extract_lab_correction(self, capture, correction_sty, force=False):
        self.lab.extract_correction(capture, correction_sty, force=force)

    def extract_lab(self, answer, capture, correction_sty=None, question_meta=None, question_meta_sty=None, student_list=None):
        self.extract_lab_files(answer, capture)
        self.extract_lab_correction(capture, correction_sty)
        self.lab.extract_question_meta(question_meta, question_meta_sty, force=True)
        self.lab.extract_student_meta(student_list)

# ---------------------------- Print Functions ---------------------------- #

    def show_input(self):
        self.lab.show_input()

    def clean(self):

        self.lab.clear_temp()