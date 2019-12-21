import heurigen.preprocess as pre
import heurigen.analysis as ana
import pickle

pdf = 'raw2.txt'
meta = [['Klosterneuburg',0,20],['Kierling',20,30],['Kritzendorf',30,40],['Weidling',40,50]]
year = 2018
ball = '2018-11-03'

#files = pre.preprocess(pdf,meta,year,ball)
with open('names.pickle','rb') as f:
    files = pickle.load(f)
ana.compile_collect_dates(**files,start_day='2018-10-20',year=year)
#ana.compile_collect_dates(**files)