import urllib.request
import nltk
import random
from urllib.request import FancyURLopener
from urllib.parse import quote
from nameparser.parser import HumanName
from time import sleep

url1 = 'https://www.cs.utexas.edu/faculty' # Dept link
url2 = 'http://scholar.google.com/citations?view_op=search_authors&mauthors=' # Google scholar author search link
url3 = 'https://scholar.google.ru/citations?user=' # Google scholar user link
school_name = 'University of Texas at Austin'

filter = 'Google Online Clinical Seminar Science Program University Course Calendar ' \
         'Phone Plan FAQ Research Professor Award Bar Name Names Cognitive Neuroscience Campus ' \
         'Support Archive Awards Career Alumni Fellowship Page Pages Map Maps Contact Advance' \
         'Medium Up Health School Endowment City Unit Link Links Media Body Content Head Degree ' \
         'Certification Dynamic Dynamics Network Networks Study Fund Student Students organization' \
         'Organizations Post Research Researcher System Systems Management Operation Operations' \
         'Report Reports Reporting Privacy Security Spotlight Faculty Houston Texas Austin Directory /' \
         'Button Academy Physics Human Humans Resource Resources Gender Sex Load Mechanism CMS Cascade' \
         '/a /p  /strong Ties Sociology Economic Economics History Power Image Images Main Demography Lab Labs' \
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
         'Subserface Deep Climate Water'

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
'''
No more than 3800 per hour! Limitation from Google. Thanks to Mohammed's emperical testing.
Test Results
1. school_name = 'University of Texas at Austin'

1.1. Physics: https://ph.utexas.edu/component/cobalt/category-items/1-directory/18-physics?Itemid=1264
-- Total people on dep page: 54
-- Total with G.S. profiles: 19 (multi acc: 8; school identified: 1)
In ScholarPlot: 12 profiles

1.2. Mathematics: https://www.ma.utexas.edu/component/cobalt/category-items/1-directory/15-mathematics?Itemid=1334
-- Total people on dep page: 63
-- Total with G.S. profiles: 19 (multi acc: 12; school identified: 2)
In ScholarPlot: 20 profiles

1.3. Neuroscience: https://neuroscience.utexas.edu/component/cobalt/category-items/1-directory/17-neuroscience?Itemid=1225
-- Total people on dep page: 59
-- Total with G.S. profiles: 23 (multi acc: 8; school identified: 1)
In ScholarPlot: 13 profiles

2. school_name = 'New York University'
2.1 Biology: http://as.nyu.edu/biology/people/faculty.html
-- Total people on dep page: 85
-- Total with G.S. profiles: 43 (multi acc: 12; school identified: 4)
In ScholarPlot: 34

2.2 Chemistry: http://as.nyu.edu/chemistry/people/faculty.html
-- Total people on dep page: 96
-- Total with G.S. profiles: 30 (multi acc: 16; school identified: 3)
In ScholarPlot: 19

2.3 Mathematics: https://www.math.nyu.edu/dynamic/people/faculty/


In ScholarPlot: 30

3. school_name = 'Columbia University'
3.1 Film: https://arts.columbia.edu/film/faculty


In ScholarPlot: 0 profiles

3.2 Visual Arts: https://arts.columbia.edu/visual-arts/faculty

In ScholarPlot: 0 profiles


3.3 Writing: https://arts.columbia.edu/writing/faculty


In ScholarPlot: 0 profiles

'''