#import libraries needed

import xmlrpclib  # allows to import to odoo
import csv        # allows to read csv files
import random     # allows to choice randomly

# declare the user name, password and the name of the database

username = "admin"
pwd = "admin"
dbname = "demo"

# get the common socket to connect to the server
sock_common = xmlrpclib.ServerProxy("http://localhost:8069/xmlrpc/common")

# log in to database
uid = sock_common.login(dbname, username, pwd)

# get an object socket to execute our commands later
sock = xmlrpclib.ServerProxy("http://localhost:8069/xmlrpc/object")

# read the csv file containing ids of the survey
survey_ids = csv.reader(open('survey_ids.csv','rb'))

# read the csv file containing the names of the survey, pages, questions, answer choices
pages = csv.reader(open('pages.csv','rb'))

# define a function that will read each line of the "pages" csv file and extract names
def extract_name(file):
    survey=[]
    page=[]
    quest=[]
    label=[]
    for row in file:
        conc = concatenate(row)
        list = conc.split(";")
        if list == [''] or list[0]=="External ID":
            continue
        if list[1] != "" and (list[1] not in survey):
            survey.append(list[1])
            page.append([])
        if list[2] != "" and (list[2] not in page[-1]):
            page[-1].append(list[2])
            quest.append([])
            label.append([])
        if list[3] != "" and (list[3] not in quest[-1]):
            quest[-1].append([list[3],list[4],list[5],list[6],list[7]])
            label[-1].append([])
        label[-1][-1].append([list[8],list[9]])
        quest[-1][-1].append([list[8], list[9]])
    return [survey,page,quest,label]

# define a function that will read each line of the "survey_ids" csv file and extract ids
def extract_id(file):
    survey_name_id = []
    page_name_id = []
    question_name_id = []
    label_name_id = []
    for row in file:
        # print row[0]
        conc = concatenate(row)
        list = conc.split(";")
        if list == [''] or list[0]=="External ID":
            continue
        if list[1] != "" and (list[1] not in survey_name_id):
            survey_name_id.append(list[1])
            page_name_id.append([])
        if list[2] != "" and (list[2] not in page_name_id[-1]):
            page_name_id[-1].append(list[2])
            question_name_id.append([])
            label_name_id.append([])
        if list[3] != "" and (list[3] not in question_name_id[-1]):
            question_name_id[-1].append(list[3])
            label_name_id[-1].append([])
        label_name_id[-1][-1].append(list[4])
    return [survey_name_id, page_name_id, question_name_id, label_name_id]

# define a function that choose randomly questions from the list of question names
def quest_random(quest,n):
    k = []
    for i in range(0,n):
        m=random.choice(quest)
        while (m in k):
            m = random.choice(quest)
        k.append(m)
    return k

# this function correct the problem of commas in the line of the survey file
def concatenate(list):
    conc = ''
    for l in list:
        if list.index(l) == len(list)-1 :
            conc = conc +l
            break
        conc = conc + l + ','
    return conc

# extracting and saving names from the file "pages"
s= extract_name(pages)
survey_name=s[0]
page_name=s[1]
question_name=s[2]
label_name=s[3]

#extracting and saving ids from the file "survey_ids"
s_id=extract_id(survey_ids)
survey_name_id=s_id[0]
page_name_id=s_id[1]
question_name_id=s_id[2]
label_name_id=s_id[3]

### importing data to odoo

s1 =0 # the index of each survey

# select surveys in survey list
for s_name in survey_name:

    p1 = 0 # the index of each page or bloc

    s=survey_name_id[s1] # id of the survey

    
    # affect the values of each attribute of the survey in odoo's database
    survey_survey = {
        'id': s,                    # id of the survey
        'title': survey_name[s1],   # name of the survey
        'quizz_mode': True,         # Quizz mode
        'users_can_go_back': True,  # ability to go back
        'auth_required': True       # login is required
    }

    # executing the import process for the survey
    sock.execute(dbname, uid, pwd, 'survey.survey', 'write', int(s), survey_survey)


    # select pages in survey's pages list
    for p_name in page_name[s1]:

        p = page_name_id[s1][p1] # id of the page

        question_name_random= quest_random(question_name[p1],5) # select 5 questions randomly from question list of each page



        # affect the values of each attribute of the page in odoo's database
        survey_page = {
            'survey_id': s,             # id of the survey
            'title': page_name[s1][p1]  # name of the page
        }

        # executing the import process for the page
        sock.execute(dbname, uid, pwd, 'survey.page', 'write', int(p), survey_page)

        q1 = 0   # the index of each question for the current page


        # select questions in the random question list
        for q_name in question_name_random:



            q = question_name_id[p1][q1]    # id of the question


            # affect the values of each attribute of the question in odoo's database
            survey_question = {
                'page_id': p,                                   # id
                'question': question_name_random[q1][0],        # name of the page
                'type': question_name_random[q1][1],            # type of the question ( simple or multiple choice, ...)
                'display_mode': question_name_random[q1][2],    # display mode ( radio or checkbox button, ...)
                'constr_mandatory': False,                      # this field must be fulled ( True or False)
                'validation_email': False                       # the input must be an email
            }

            # executing the import process for the question
            sock.execute(dbname, uid, pwd, 'survey.question', 'write', int(q), survey_question)

            l1 = 0      # the index of each answer choice for the current question



            # collect the list of answer choices of the current question
            label_name_random = question_name_random[q1][5::]




            # select answer choices in the answer choices list
            for l_name in label_name_random:

                l = label_name_id[p1][q1][l1]       # id of the answer choice

                #print "l----------------------", l

                # affect the values of each attribute of the answer choice in odoo's database
                survey_label = {
                    'id': l,                                    # id of the answer choice
                    'question_id': q,                           # id of the question
                    'value': label_name_random[l1][0],          # name of the choice
                    'quizz_mark': label_name_random[l1][1]      # score of the choice
                }

                # executing the update process for the answer choice
                sock.execute(dbname, uid, pwd, 'survey.label', 'write', int(l), survey_label)

                print j
                j+=1

                l1 += 1     # increase the index of the choice to go to the next one

            q1 += 1         # increase the index of the question to go to the next one
       
        
        p1 += 1             # increase the index of the page to go to the next one
    s1 += 1                 # increase the index of the survey to go to the next one

# indicate the finish of the compilation
print "\n\n\n-----------DONE-----------"