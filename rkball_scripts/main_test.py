import numpy as np
import math
import re
import clipboard
'''
X=[[1,1,0,0,0], [1,1,1,1,0],[0,1,1,0,1],[0,1,0,1,0],[0,0,1,0,1]]

Y = [[0,1,0],[1,0,1],[0,1,0]]
arr = np.array(Y)
arr_n = arr
print(arr)
print(arr_n.transpose())


print(arr)
for i in range(20):
    arr_n =np.matrix.dot(arr_n, arr)
    print(arr_n)
#print(np.linalg.inv(arr))


#﻿A/B, B/C, B/D, C/E

'''

def calc(s):
    s = s.replace('\ufeff','')
    #print(re.findall(r'\\frac\{\d+\}\{(\d+|\d+\.\d+)\}',s))
    norm = float(re.findall(r'\\frac\{\d+\}\{(\d+|\d+\.\d+)\}',s)[0].strip())
    vals = re.findall(r'\s*(-{0,1}\s*\d+)\s* \\\\',s)
    print(norm)
    print(vals)
    s = []
    for i in vals:
        v = round(float(i.strip())/norm,5)
        s.append(str('{i} \\\\'.format(i=v)))
        print('{i} \\\\'.format(i=v))
    clipboard.copy(' \n'.join(s))

def deconstr_matrix(s):
    t = s.split('\\\\')
    matr = []
    for i in t:
        if any(re.findall(r'(-{0,1}\d+)',i)):
            #print(i)
            #print([re.findall(r'(-{0,1}\d+)',j.strip()) for j in i.split('&')])
            r = [int(re.findall(r'(-{0,1}\d+)',j.strip())[0]) for j in i.split('&')]
            matr.append(r)
    #print(matr)
    return matr


def matrix_mult(s):
    s_1, s_2 = s.split(r'\cdot')
    v_1 = deconstr_matrix(s_1)
    v_2 = deconstr_matrix(s_2)
    m_str = []
    m = []

    n1 = len(v_1)
    m1 = len(v_1[0])

    m2 = len(v_2)
    n2 = len(v_2[0])


    for i1 in range(n1):
        r_str = []
        r = []
        for i2 in range(n2):
            c_str = []
            c = []
            for j2 in range(m2):
                #print(i1,i2,j2)
                c_str.append('{0} \cdot {1}'.format(v_1[i1][j2], v_2[j2][i2]))
                c.append(v_1[i1][j2] * v_2[j2][i2])
            r_str.append(' + '.join(c_str))
            r.append(str(sum(c)))

        m_str.append(' & '.join(r_str))
        m.append(' & '.join(r))
    start = '\\begin{bmatrix} \n'
    end = '\\end{bmatrix} \n'

    step_m = start + ' \\\\ \n'.join(m_str) + ' \\\\ \n' + end
    fin_m = start + ' \\\\ \n'.join(m) + ' \\\\ \n' + end

    out = step_m + ' = \n' + fin_m

    check = np.matrix.dot(np.array(v_1),np.array(v_2))
    #print(step_m)
    #print(fin_m)
    print(out)
    print(check)
    clipboard.copy(out)


s = r'''
﻿\begin{bmatrix} 
16 & 12 & 8 \\ 
12 & 9 & 6 \\ 
8 & 6 & 4 \\ 
\end{bmatrix}  \cdot
\begin{bmatrix}
1 & 0 & 0 \\
0 & 1 & 0 \\
0 & 0 & 1 \\
\end{bmatrix} 
'''

matrix_mult(s)

A = np.array([[1,1],[1,1]])
B = np.array([[0,0],[0,1]])

print(np.matrix.dot(A,B))
print(np.matrix.dot(B,A))
s = r'''
﻿\begin{bmatrix} 
0 & 0 & -1 \\ 
\end{bmatrix} 
=
\begin{bmatrix} 
29 \\ 
13 \\ 
17 \\ 
\end{bmatrix} 
'''

'''
calc(s)



s = '﻿﻿4 + 5 + 2'
k = 11

print(sum([int(i.strip().replace('\ufeff','')) for i in str.split(s,'+')]))
print(math.sqrt(sum([int(i.strip().replace('\ufeff','')) for i in str.split(s,'+')])))
'''