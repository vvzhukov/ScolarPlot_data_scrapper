import urllib.request
import nltk
import random
from urllib.request import FancyURLopener
from urllib.parse import quote
from nameparser.parser import HumanName
from time import sleep


url = 'https://cm.utexas.edu/component/cobalt/category-items/1-directory/12-chemistry?Itemid=1252' #lab link
url2 = 'https://scholar.google.com/citations?view_op=search_authors&mauthors=' #google scholar author search link
url3 = 'https://scholar.google.ru/citations?user=' #google scholar user link

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
         'Future Table Tables Information Safety Informations Facility Facilities Nuclear Xray'
url_dict = {}

class AppURLOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'

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
        if len(person) > 1: #avoid grabbing lone surnames
            for part in person:
                name += part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
            name = ''
        person = []

    return (person_list)


def sortedSentence(Sentence):
    words = Sentence.split(" ")
    words.sort()
    newSentence = " ".join(words)
    return newSentence

def filterbyvalue(seq, value):
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


HTML = urllib.request.urlopen(url)
txt = HTML.read().decode('utf-8').replace(',', ' ').replace('>', ' ').replace('<', ' ').replace('.','')

## Code-block for conversion 'Name-Name Lastname' to 'Namename Lastname'.
## Doesn't work on 'big' strings: Out-of-index.
## dash_indexes = [m.start() for m in re.finditer('-', txt)]
## for i in dash_indexes:
##    txt = txt[:i] + txt[i+1].lower() + txt[i+2:]

txt= ' '.join( [w for w in txt.split() if len(w)>1] ).replace('-', '')

names = get_human_names(txt) # Names var contains all the names, scrapped from web url
filterbyvalue(names, filter)

print("FIRST LAST")
i = 0 # Counter of publicated scientists
n = str(len(names)) # Counter of scientists in the Lab

for name in names[:]:
    last_first = HumanName(name).last + ' ' + HumanName(name).first
    query = last_first

    openurl = AppURLOpener().open
    try:
        sleep(1+2*random.random())    # Timeout for google web pages, not robot :)
        cont = openurl(url2 + quote(query)).read().decode("utf-8")
    except:
        pass
        print(last_first + "; " + "!!!Google Scholar web parse error!!!")
        continue
    pos1 = cont.find("&amp;user=")
    if pos1 < 0:
        names.pop(names.index(name))
    else:
        pos2 = cont.find("&amp;", pos1 + 1)
        gslink = url3 + cont[pos1 + 10:pos2]
        print(last_first + "; " + gslink)
        i += 1

print('-- Total people on lab page: ' + str(n))
print('-- Total with G.S. profiles: ' + str(i))
