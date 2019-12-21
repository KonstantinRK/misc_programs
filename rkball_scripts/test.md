
# Code of Conduct

## Check List

**Everytime** you have to hand in an assignment, go through this check list and make sure you have accounted for **every case**:

1. Did I adhere to the naming convention?
2. Did I structure my files propperly?
3. Did I include all my data?
4. Did I ensure that the code can be executed externally?

## Naming conventions and file structure (for this course)

The name of a file should convey a certain meaning. That is, we want to be able to deduce
- **when** the file was created (i.e. which LV),
- **why** was the file created (i.e. which Homework),
- to **whom** the file belongs (i.e. which Student) and
- **what** is the file about (i.e. Data, Notebook, a.o.).

Moreover, you will work with data. When you hand in your notebook, the code within this notebook will require this data for propper execution.
That is,
- without the data, your code will not execute properly;
- if your code does not execute, you will get a failing grade;
- you dont want a failing grade;
- we dont want to give you a failing grade;
- **SO HAND IN YOUR DATA!!!**

Hence, we propose (a *code word* for **require** btw.) the following conventions:

1. When you start your assignment create a directory with the name

       [lv-nr]_asgnm-[assignment-nr.]_[matr.-nr.]


2. Within this directory create your notebook(s) with the name

        notebook-[notebook-nr.].ipynb

   with `notebook-nr.` referencing the order in which the notebooks shall be assessed (starting with 1).
   **Preferably, only submit one notebook.**


3. Within this directory create another directory with the name

        data

   This data directory will contain all your data files.


4. Name the data files as follows

        data_notebook-[notebook-nr.]_[name].[file extension]

   with `notebook-nr.` referencing where this data file is used. Moreover, you are free to choose `name`, however, make it **descriptive**.

*Note: `[...]` indicates a variable.*

#### Example:
We assume a student with the following properties:

    Name:= Karla
    Surname:= Lama
    Matr.Nr.:= 03579864

who wants to hand in the fifth homework for the LV 1020.
She used two notebooks. The first one pre-processes, cleanes the three data files

    stars.json
    planets.csv
    solar_systems.xml

and compiled them into a single data file

    milkyway.json

which was used by the second notebook.

Hence, obtaining `1020_asgnm-2_03579864.zip`, which if extracted results in

    1020_asgnm-5_03579864
    |---- notebook-1.ipynb
    |---- notebook-2.ipynb
    |---- data
    |     |---- data_notebook-1_stars.json
    |     |---- data_notebook-1_planets.csv
    |     |---- data_notebook-1_solar_system.xml
    |     |---- data_notebook-2_milkyway.json





## Working with data files

As already mentioned it is of vital importance that you **hand in your data with your notebooks**.
However, there are some additional remarks to be made.

**You want that your code requests data from a website or an API?**

Make sure that you immediately persist your data, because your data should be our data. Therefore,
- append the percistance process at the beginning of your notebook;
- isolate the percistance process for each data file in a single cell;
- after the data is downloaded and stored in a data file, comment the cell out.
- every subsequent cell must reference the persisted data, i.e. before processing further you have to load the data from your file (do not rely on the download).


**Always provide the original data**
- do not clean the data by hand;
- all cleaning ought to be done within the notebook.



## Does my code execute?

This is a somewhat misleading framing. Because it does not matter whether your code executes on your machine.
The **only** thing that matters is that the code executes on **our** machines.

### How can I ensure that my code executes for grading?
We use the python version provided on the server. Hence,

1. Setup the test:
    - if you work locally on your machine, upload the files (as presented above) to the server;
    - if you work on the server, structure your files as presented above.
2. Press `Cell -> Run All`:
    - if there is no exception, you should be fine;
    - if there is an exception, try to fix it and/or seek help.
3. Do not change the structure of predefined notebooks:
    - do **not** delete cells;
    - do **not** add cells.

## Seeking help

We want to help you. So please ask questions. However, be aware of the following.


### When to seek help
As soon as possible. However, do **not** expect any support close to the deadline or on **weekends**. That is, **one day before the deadline we will not answer questions**.

For example, If there is a **deadline on Tuesday**, then the last possible date for questions is **Friday**.
- Monday is the day before the deadline.
- Sunday is part of the weekend.
- Saturday is part of the weekend.
- Firday is fine.


### How to seek help

#### Methods

1. Is your question/problem a generic question/problem (i.e. the question itself does not provide the solution for a homework problem)
    - use the forum
2. Do you have very specific question/problem
    - write us an email (konstantin.kueffner@wu.ac.at)
3. If none of the above works, or you have some fundamental issues
    - make an appointment with us

#### Structure

In order to help, we need to know your problem. It is important that you boil down your issues and questions to their essence. Therefore, adhere to the [following](https://stackoverflow.com/help/mcve) rules.

**Your code should be ...**

- ... **Minimal** – Use as little code as possible that still produces the same problem.
    - However, still readable.
- ... **Complete** – Provide all parts needed to reproduce the problem.
    - Yes, this includes data (if required).
- ... **Verifiable** – Test the code you're about to provide to make sure it reproduces the problem.

##### Example


```python
a=3
b=10.5
c= True
d=[0,1,5,6]
e='s'


print(a+b)
print(b+c)
print(d+e)
```

    13.5
    11.5



    ---------------------------------------------------------------------------

    TypeError                                 Traceback (most recent call last)

    <ipython-input-6-7fa43b2ba800> in <module>()
          8 print(a+b)
          9 print(b+c)
    ---> 10 print(d+e)


    TypeError: can only concatenate list (not "str") to list


**Minimal: Don't**
```python
a=3
b=10.5
c= True
d=[0,1,5,6]
e='s'

print(a+b)
print(b+c)
print(d+e)
```

**Complete: Don't**
```python
print(d+e)
```
or

```python
d=[0,1,5,6]
e='s'
```

**Verifiable: Don't**
```python
d="[0,1,5,6]"
e='s'

print(d+e)
```

or

```python
d=[0,1,5,6]
e=['s']

print(d+e)
```

**Do**
```python
d=[0,1,5,6]
e='s'

print(d+e)
```
