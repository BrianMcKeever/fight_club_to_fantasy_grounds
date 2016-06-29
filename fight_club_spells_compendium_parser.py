from bs4 import BeautifulSoup
import codecs
import string

f = codecs.open('Spells Compendium 1.1.2.xml', encoding='utf-8')
soup = BeautifulSoup(f.read(), "xml")
f.close()

f = codecs.open('spells' '.txt', 'w', encoding='utf-8')

class Spell:
    def __init__(self, name, level, school, casting_time, range, components, duration, description, source, classes):
        self.name = name
        self.level = level
        self.school = school
        self.casting_time = casting_time
        self.range = range
        self.components = components
        self.duration = duration
        self.description = description
        self.source = source
        self.classes = classes

spells = []
classes = Set()
for spell in soup.compendium.find_all('spell'):
    name = spell.find("name").string

    texts = list(spell.find_all("text"))
    texts = map(lambda text: text.string, texts)
    texts = filter(lambda text: text is not None, texts)

    description = string.join(texts, "\n")
    source = texts[-1]

    level = int(spell.level.string)
    school = spell.school.string
    casting_time = spell.time.string
    spell_range = spell.range.string
    components = spell.components.string
    duration = spell.duration.string
    spell_classes = spell.classes.string
    classes_list = spell_classes.split(",")
    classes_list = map(lambda x: x.strip(), classes_list)
    for spell_class in classes_list:
        classes.add(spell_class)

    spells.append(Spell(name, level, school, casting_time, spell_range, components, duration, description, source, classes_list))

orderDescriptor = {
    0: "0th",
    1: "1st",
    2: "2nd",
    3: "3rd",
    4: "4th",
    5: "5th",
    6: "6th",
    7: "7th",
    8: "8th",
    9: "9th",
}

def write_spell_index_for_level(class_spells, level):
    spells_of_that_level = filter(lambda x: x.level == level, class_spells)
    if len(spells_of_that_level) == 0: return
    if level == 0:
        f.write("Cantrips (0 Level)\n")
    else:
        f.write("%s Level\n"%orderDescriptor[level])

    for spell in spells_of_that_level:
        f.write("%s\n"%spell.name)
    f.write("\n")

f.write("#@;\n")
class_list = list(classes)
class_list.sort()
for spell_class in class_list:
    class_spells = filter(lambda x: spell_class in x.classes, spells)
    f.write("%s Spells\n"%spell_class)
    map(lambda x: write_spell_index_for_level(class_spells, x), range(0, 10))

spellSchool = {
    "A": "abjuration",
    "C": "conjuration",
    "D": "divination",
    "EN": "enchantment",
    "EV": "evocation",
    "N": "necromancy",
    "I": "illusion",
    "T": "transmutation",
}

f.write("##;\n")
for spell in spells:
    f.write("%s\n"%spell.name)
    f.write("%s-level %s\n"%(orderDescriptor[spell.level], spellSchool[spell.school]))
    f.write("Casting Time: %s\n"%spell.casting_time)
    f.write("Range: %s\n"%spell.range)
    f.write("Components: %s\n"%spell.components)
    f.write("Duration: %s\n"%spell.duration)
    f.write("%s\n"%spell.description)
    f.write("\n")

