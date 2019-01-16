import urllib.request
import nltk
from nameparser.parser import HumanName

url = "http://www.uh.edu/nsm/physics/people/research/"
filter = 'Google Online Clinical Seminar Science Program University Course Calendar ' \
         'Phone Plan FAQ Research Professor Award Bar Name Names Cognitive Neuroscience Campus ' \
         'Support Archive Awards Career Alumni Fellowship Page Pages Map Maps Contact Advance' \
         'Medium Up Health School Endowment City Unit Link Links Media Body Content Head Degree ' \
         'Certification Dynamic Dynamics Network Networks Study Fund Student Students organization' \
         'Organizations Post Research Researcher System Systems Management Operation Operations' \
         'Report Reports Reporting Privacy Security Spotlight Faculty Houston Texas Austin Directory /' \
         'Button /a Academy Physics'

# Install notes (in terminal)
# import nltk
# nltk.download()

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


def filterbyvalue(seq, value):
    for el in seq[:]:
        for word in el.split():
            if word.lower() in value.lower():
                try:
                    seq.pop(seq.index(el))
                except:
                    pass
        if len(el.split()) == 1:
            seq.pop(seq.index(el))
    return (seq)


HTML = urllib.request.urlopen(url)
txt = HTML.read().decode('utf-8').replace(',', ' ').replace('>', ' ').replace('<', ' ')
names = get_human_names(txt) #names var contains all the names, scrapped from web url

filterbyvalue(names, filter)
print('Total: ' + str(len(names)))
print("FIRST LAST")
for name in names:
    last_first = HumanName(name).last + ' ' + HumanName(name).first
    print(last_first)