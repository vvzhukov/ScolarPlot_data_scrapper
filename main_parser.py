import urllib.request
import nltk
import random
import numpy
from urllib.request import FancyURLopener
from urllib.parse import quote
from nameparser.parser import HumanName
from time import sleep

url1 = 'https://www.frenchanditalian.northwestern.edu/people/faculty/affiliated/' # Dept link
url2 = 'http://scholar.google.com/citations?view_op=search_authors&mauthors=' # Google scholar author search link
url3 = 'https://scholar.google.ru/citations?user=' # Google scholar user link
school_name = 'Northwestern'

filter = '/Button /a /button /i /p /strong /u Academic Academics Academy Action Active Active Adjunct Administrative ' \
         'Admission Advance Adviser Advisory Aesthetics African Algebraic Algoritm Algoritms Alumna Alumni America ' \
         'American Analysis Anixiety Anthropology Anxiety Applied Appointment Appointments Archaeological ' \
         'Architectural Architecture Archive Area Art Arts Assistant Astronomy Austin Award Award Awarded Awards ' \
         'Awards Bar Behaviour Biochemistry Biogeochemistry Biology Board Body Book Box Brain Britain CMS Calendar ' \
         'Campus Career Cascade Celeste Centennial Center Center Century Certification Certified Chair Chemistry Child ' \
         'City Civilization Climate Clinical Code Cognitive College Computing Conosortium Consulting Contact Content ' \
         'Coordinator Costume Council Course Courses Critic Critical Critics Crossing Crossings Curricular Curriculum ' \
         'Daily Dance Dane Data Deep Degree Demography Department Design Develop Development Development Directory ' \
         'Discovery Division Dynamic Dynamics Earth Ecology Econometrics Economic Economics Education Educator ' \
         'Electron Email Empire Employee Endowment Energy Engineering Environment Epistomology Ethics Ethics Evolution ' \
         'Explore FAQ FAQ FAQs Facilities Facility Faculty Fax Fellowship Festival Festivals Film Finance Form Form ' \
         'Forms Forms Fourth France Free Fund Future Gallery Game Gas Gases Gender Geometry Germany Get Gift Global ' \
         'Globals Google Grants Hall Head Health History Home Houston Human Humans I II Identity Image Images ' \
         'Inequality Information Informations Inorganic Institute Interdisciplinaria Investigator Involved Islam ' \
         'Jewish Job Jr Jury Lab Laboratory Labour Labs Language Languages Latin Lead Learn Learning Lecturer Lectures ' \
         'Lectures Lectureship Library Life Link LinksUH Load Main Major Make Management Manager Managers Map Maps ' \
         'Marine Math Mathematical Maths Matter Matters Mechanism Media Medium Method Methods Mexican Microscopy ' \
         'Mobile Model Modeling Molecular NYU Name Names Nanoscale Nature Network Networks Neuroscience Nuclear Number ' \
         'Numerical OD Occupationv Office Oh Online Operation Operations Opportunities Organic Organizations Page ' \
         'Pages Participation Past Pattern Patterns Pediator Performance PhD Philosophy Phone Photo Photostream ' \
         'Physics Plan Poor Post Postdoc Postdocs Power Principles Privacy Producer Professor Professor Professorship ' \
         'Program Program Programs Project Projects Promotion Psychology Public Race Race Rapoport Recognition ' \
         'Relationship Report Reporting Reports Republic Republics Research Research Researcher Resource Resources ' \
         'Result Results Robotic Robotics Room Safety Scholar School Science Sciences Scientific Secrets Security ' \
         'Seminar Senior Sensing Serious Sex Sociology Sound Sounds Specialist Specialists Spotlight Staff Startup ' \
         'Street Stress Student Students Studies Study Subserface Supervisor Supervisors Support Surface Survey Swap ' \
         'Switch Switches System Systems Table Tables Teaching Technology Telescope Test Tests Texas Theories Theory ' \
         'Therapy Thoughts Ties Tracks Training Trip Trips Tutorials US Unit University Up Urban Us View Views Visit ' \
         'Visual Visuals Volunteer Water Welcome Work Works Workshop Workshops Xray Year Organization Berlin Chicago' \
         'Group Geochemistry Imaging Seismic Major Majors Sequence Recruiting Prize Best English'

class AppURLOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) ' \
              'Chrome/33.0.1750.152 Safari/537.36'

def get_human_names(text):
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary = False)
    person_list = []
    person = []
    name = ""
    for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leaf in subtree.leaves():
            person.append(leaf[0])
        if len(person) > 1: # Avoid grabbing lone surnames
            for part in person:
                name += part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
            name = ''
        person = []

    return (person_list)

def sortedSentence(Sentence):
    words = Sentence.split(' ')
    words.sort()
    newSentence = ' '.join(words)
    return newSentence

def filterbyvalue(seq, value):  # NEED2 CORRECT EXCEPTION SECTION
    for el in seq[:]:
        for word in el.split():
            if word in value:
                try:
                    seq.pop(seq.index(el))

                except:
                    pass
        try:
            if (len(el.split()) == 1) or \
                    (sortedSentence(el) == sortedSentence(seq[seq.index(el)+1])):
                seq.pop(seq.index(el))  # Filtering Capital Letters in middle name and
                                        # doubles like a,b - b,a
        except:
           pass
    return seq

def body_parser(in_url1, in_url2, in_url3, in_filter, in_sch_name):     # NEED2 CORRECT EXCEPTION SECTION
    user_tag = '&amp;user='
    HTML = urllib.request.urlopen(in_url1)      # Getting Lab page content
    txt = HTML.read().decode('utf-8').replace(',', ' ').replace('>', ' ').replace('<', ' ').replace('.', '')

    # Code-block for conversion 'Name-Name Lastname' to 'Namename Lastname'.
    # Doesn't work on 'big' strings: Out-of-index.
    # dash_indexes = [m.start() for m in re.finditer('-', txt)]
    # for i in dash_indexes:
    #    txt = txt[:i] + txt[i+1].lower() + txt[i+2:]

    txt = ' '.join([w for w in txt.split() if len(w) > 1]).replace('-', '')

    names = get_human_names(txt)    # Names var contains all the names, scrapped from web url
    filterbyvalue(names, in_filter)

    print('FIRST LAST')
    i = 0   # Counter of publicised scientists
    m = 0   # Multi accounts
    k = 0   # Found by school
    n = str(len(names))     # Counter of scientists in the Lab
    output = {'FIRST LAST':'GS account link'}

    for name in names[:]:
        last_first = HumanName(name).last + ' ' + HumanName(name).first
        openurl = AppURLOpener().open

        try:
            sleep(1 + 2 * random.random())  # Timeout for google web pages, not robot :)
            cont = openurl(in_url2 + quote(last_first)).read().decode("utf-8") # Getting content GS page
        except:
            pass
            print(last_first + '; ' + '!!!Google Scholar web parse error!!!')
            output['last_first'] = '!!!Google Scholar web parse error!!!'
            continue
        pos1 = cont.find(user_tag)
        if pos1 < 0:        # No GS account found
            names.pop(names.index(name))

        else:
            if cont.count(user_tag) > 3:    # Multiply GS accounts validation; 3 user IDs ~ 1 user.
                m += 1
                ## print('More than one account found.')
                if cont.find(in_sch_name) > 0:  # Searching for school name
                    k += 1
                    pos1 = cont.find(user_tag, cont.find(in_sch_name) - 350)    # Getting the first ID after schl name
                                                                                # 350 symbols from the SchoolName
                                                                                # hardcode - bad
                    ## print('School found, account identified:')
                else:
                    ## print('School not found, picking first:')
                    names.pop(names.index(name))
            pos2 = cont.find('&amp;', pos1 + 1)
            if len(cont[pos1 + 10:pos2]) > 20:
                gslink = "!!!Parser error, too long gs link!!!"
            else:
                gslink = in_url3 + cont[pos1 + 10:pos2] # Concat GS url + ID value
            print(last_first + "; " + gslink)
            output['last_first'] = gslink
            i += 1

    print('-- Total people on dep page: ' + str(n))
    print('-- Total with G.S. profiles: ' + str(i) + ' (multi acc: ' + str(m) + '; school identified: ' + str(k) + ')')
    print('Check:', pos2-pos1)
    return output


# MAIN

body_parser(url1, url2, url3, filter, school_name)

exit()