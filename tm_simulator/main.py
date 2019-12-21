import re


class TM:
    def __init__(self, program_path, input_values=None, break_at=100000, verbose=True):
        self.break_at=break_at
        self.verbose=verbose
        self.tests_dict = {'t':self.t}
        self.action_dict = {'R':self.R, 'L':self.L, 'd0':self.d0, 'd1':self.d1}

        self.tape = [0]
        self.head = 0
        self.step = 1
        self.stop = False

        if input_values is not None:
            self.write_input_values(input_values)
        self.program = self.compile_program(self.read_program(program_path))
        self.start_tm()

    def read_program(self, program_path):
        program = []
        with open(program_path, 'r') as f:
            for i in f.readlines():
                program.append(i)
        return program

    def compile_program(self, program):
        compiled_program = {0:(self.stop_tm,[])}
        number = 0
        for i in program:
            try:
                number = int(re.findall(r'^(\d+):\s*', i)[0])
            except:
                raise TypeError('Wrong command: number {0}'.format(number+1))

            if re.match(r'^\d+:\s*if\s*\w{1,2}\s*then\s*\d+\s*else\s*\d+', i):
                test = re.findall(r'^\d+:\s*if\s*(\w{1,2})\s*then\s*\d+\s*else\s*\d+', i)[0]
                step_true = int(re.findall(r'^\d+:\s*if\s*\w{1,2}\s*then\s*(\d+)\s*else\s*\d+', i)[0])
                step_false = int(re.findall(r'^\d+:\s*if\s*\w{1,2}\s*then\s*\d+\s*else\s*(\d+)', i)[0])
                test = self.tests_dict[test]
                compiled_program[number]=(self.if_then_else, [test, step_true, step_false])

            elif re.match(r'^\d+:\s*\w{1,2}\s*then\s*\d+', i):
                action = re.findall(r'^\d+:\s*(\w{1,2})\s*then\s*\d+', i)[0]
                step = int(re.findall(r'^\d+:\s*\w{1,2}\s*then\s*(\d+)', i)[0])
                action=self.action_dict[action]
                compiled_program[number]=(self.then,[action,step])

            else:
                raise TypeError('Wrong command: number {0}'.format(number))
        return compiled_program

    def if_then_else(self, test, step_true, step_false):
        if test():
            self.step=step_true
        else:
            self.step=step_false

    def then(self, action, step):
        action()
        self.step=step

    def start_tm(self):
        n = 0
        while not self.stop and n<=self.break_at:
            if self.verbose==True:
                print('Step: ',n, '  Command: ', self.step)
                self.print_tape()
            self.execute_command()
            n+=1

        if n > self.break_at:
            print('DIVERGE')

    def output_values(self):
        sum = 0
        values = []
        for i in self.tape:
            if i == 0:
                if sum > 0:
                    values.append(str(sum))
                sum = 0
            else:
                sum += 1
        if not any(values):
            values = ['0']
        print('Values:', ', '.join(values))

    def stop_tm(self):
        self.print_tape()
        self.output_values()
        self.stop = True

    def print_tape(self):
        print(''.join(['v' if i is self.head else ' ' for i in range(len(self.tape))]))
        print(''.join([str(i) for i in self.tape]))

    def execute_command(self):
        command = self.program[self.step]
        command[0](*command[1])

    def write_input_values(self, input_values):
        for i in input_values:
            self.tape = self.tape + [1 for j in range(i)] + [0]

    def d0(self):
        self.tape[self.head]=0

    def d1(self):
        self.tape[self.head]=1

    def R(self):
        self.head = self.head+1
        if self.head>=len(self.tape):
            self.tape.append(0)

    def L(self):
        if self.head == 0:
            self.tape = [0]+self.tape
        else:
            self.head = self.head-1

    def t(self):
        if self.tape[self.head] == 0:
            return True
        else:
            return False


tm = TM('program.txt', [3,1], break_at=1000)
