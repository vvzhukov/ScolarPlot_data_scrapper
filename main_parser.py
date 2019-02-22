import urllib.request
import nltk
import random
import numpy
from urllib.request import FancyURLopener
from urllib.parse import quote
from nameparser.parser import HumanName
from time import sleep

url1 = 'https://www.chemistry.northwestern.edu/people/research-faculty/' # Dept link
url2 = 'http://scholar.google.com/citations?view_op=search_authors&mauthors=' # Google scholar author search link
url3 = 'https://scholar.google.ru/citations?user=' # Google scholar user link
school_name = 'Northwestern'

filter = 'Google Online Clinical Seminar Science Program University Course Calendar ' \
         'Phone Plan FAQ Research Professor Award Bar Name Names Cognitive Neuroscience Campus ' \
         'Support Archive Awards Career Alumni Fellowship Page Pages Map Maps Contact Advance' \
         'Medium Up Health School Endowment City Unit Link LinksUH Media Body Content Head Degree ' \
         'Certification Dynamic Dynamics Network Networks Study Fund Student Students organization' \
         'Organizations Post Research Researcher System Systems Management Operation Operations' \
         'Report Reports Reporting Privacy Security Spotlight Faculty Houston Texas Austin Directory /' \
         'Button Academy Physics Human Humans Resource Resources Gender Sex Load Mechanism CMS Cascade' \
         '/a /p /u /i /strong Ties Sociology Economic Economics History Power Image Images Main Demography Lab Labs' \
         'Urban Rapoport Centennial America Latin Race Inequality Analysis Jury Method Methods Race' \
         'Make Gift Work Works Occupationv Program Programs View Views Switch Switches /button Professor' \
         'Professorship Ecology Evolution Coordinator Forms Form Active Learn Learning Education' \
         'Educator Curriculum Active Form Forms Chair Biology Molecular Swap Employee Jr Telescope' \
         'Future Table Tables Information Safety Informations Facility Facilities Nuclear Xray' \
         'Specialist Specialists Project Projects Art Arts Visual Visuals Crossing Crossings' \
         'Sound Sounds Oh Film Critic Critics Republic Republics Producer Festival Festivals' \
         'Chemistry Organic Inorganic Major Global Globals Award Awards Awarded Welcome' \
         'Alumna Electron Microscopy Matter Matters Nanoscale PhD Lecturer Postdoc Postdocs ' \
         'NYU Math Maths Architectural Architecture Earth Supervisor Supervisors Surface ' \
         'Subserface Deep Climate Water Trip Trips Workshop Workshops Lectures Public Home' \
         'Staff Academic Academics Assistant Scientific Scholar Administrative Manager Managers' \
         'Finance Biochemistry Marine Fax Number Biogeochemistry Appointment Appointments Geometry' \
         'Algebraic Applied Mathematical Lectureship Code Computing Mobile Startup Robotics Robotic' \
         'Engineering Explore Conosortium Get Involved Advisory Council Training Consulting Free ' \
         'Tutorials FAQ FAQs Sciences Data Discovery Pattern Patterns Recognition Email Development' \
         'Principles Gas Gases Model Modeling Develop Development Language Languages Algoritm Algoritms' \
         'Numerical Game Serious France Germany Center Anixiety Therapy Theories Relationship Certified' \
         'Board Thoughts Child Center Stress Laboratory Daily Promotion Psychology Room Anxiety Institute' \
         'Econometrics Empire Energy Mexican Environment Courses Past Philosophy Ethics Aesthetics' \
         'College Library Epistomology Ethics Hall Visit OD Us US I II Investigator Pediator Sensing' \
         'Grants Result Results Test Tests Department Studies Anthropology Job Opportunities Nature' \
         'Technology Islam Civilization Jewish Senior Behaviour Brain Adviser Lead Dane Admission Gallery' \
         'Photo Volunteer Photostream Division Dance Area Performance Design Box Office Costume Theory' \
         'Critical Participation Astronomy Interdisciplinaria Year Fourth Lectures Adjunct Tracks Curricular' \
         'Celeste Survey Archaeological African American Teaching Secrets Identity Action Book Life Street Poor' \
         'Labour Century Britain'

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
            if pos2-pos1 > 20:
                gslink = "!!!Parser error, too long gs link!!!"
            else:
                gslink = in_url3 + cont[pos1 + 10:pos2] # Concat GS url + ID value
            print(last_first + "; " + gslink)
            output['last_first'] = gslink
            i += 1

    print('-- Total people on dep page: ' + str(n))
    print('-- Total with G.S. profiles: ' + str(i) + ' (multi acc: ' + str(m) + '; school identified: ' + str(k) + ')')

    return output


# MAIN

body_parser(url1, url2, url3, filter, school_name)

exit()