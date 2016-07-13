from bs4 import BeautifulSoup
import codecs
from shared import process_abilities

f = codecs.open('Character Compendium 1.3.3.xml', encoding='utf-8')
soup = BeautifulSoup(f.read(), "xml")
f.close()

f = codecs.open('backgrounds' '.txt', 'w', encoding='utf-8')

def get_background_field(name):
    field = filter(lambda x: x.get_name() == "name", abilities)
    if len(languages)> 0:
        field = languages[0].get_texts()[0]
    else:
        field = None
    return field


def head(predicate, iterable):
    for item in iterable:
        if predicate(item):
            return item
    return None


def abilityHead(predicate, iterable):
    result = abilityHeads(predicate, iterable)
    if result is None:
        return None
    return result[0]

def abilityHeads(predicate, iterable):
    item = head(predicate, iterable)
    if item is None:
        return None
    return item.get_texts()

for background in soup.compendium.find_all('background'):
    name = background.find("name").string
    proficiency = background.proficiency
    abilities = process_abilities(background, "trait")
    skills = abilityHead(lambda x: x.get_name() == "Skill Proficiencies", abilities)
    tools = abilityHead(lambda x: x.get_name() == "Tool Proficiencies", abilities)
    feature = head(lambda x: x.get_name()[:8] == "Feature:", abilities)
    languages = abilityHead(lambda x: x.get_name() == "Languages", abilities)
    equipment = abilityHead(lambda x: x.get_name() == "Equipment", abilities)

    f.write("##; %s\n"%name)
    if skills is not None:
        f.write("Skill Proficiencies: %s\n"%skills)
    if tools is not None:
        f.write("Tool Proficiencies: %s\n"%tools)
    if languages is not None:
        f.write("Languages: %s\n"%languages)
    if equipment is not None:
        f.write("Equipment: %s\n"%equipment)
    if feature is not None:
        f.write("%s\n"%feature.get_name())
        f.write("%s\n"%feature.get_texts()[0])
    else:
        f.write("Feature: -\n")
    f.write("Suggested Characteristics\n")
    f.write("d0 Personality Trait\n")
    f.write("\n")

f = codecs.open('class' '.txt', 'w', encoding='utf-8')

for player_class in soup.compendium.find_all('class'):
    name = player_class.find("name").string
    hd = int(player_class.hd.string)
    hp_at_first_level = "%s + your constitution modifier"%hd
    average_hp_per_level = hd/2 + 1
    saving_throws = player_class.proficiency.string #not a typo
    features = process_abilities(player_class, "feature")
    starting_proficiencies = abilityHeads(lambda x: x.get_name() == "Starting Proficiencies", features)
    armor_proficiencies = head(lambda x: x[:6] == "Armor:", starting_proficiencies)
    weapon_proficiencies = head(lambda x: x[:8] == "Weapons:", starting_proficiencies)
    tool_proficiencies = head(lambda x: x[6] == "Tools:", starting_proficiencies)
    skill_proficiencies = head(lambda x: x[:7] == "Skills:", starting_proficiencies)
    starting_equipment = abilityHeads(lambda x: x.get_name() == "Starting Equipment", features)

    f.write("##; %s\n"%name)
    f.write("Hit Dice: 1d%s\n"%hd)
    f.write("Hit Points at 1st Level: %s\n"%hp_at_first_level)
    f.write("Hit Points at Higher Levels: %s (or %s)\n"%(hd, average_hp_per_level))
    f.write("Proficiencies\n")
    f.write("%s\n"%armor_proficiencies)
    f.write("%s\n"%weapon_proficiencies)
    if tool_proficiencies is None:
        f.write("Tools: none\n")
    else:
        f.write("%s\n"%tool_proficiencies)
    f.write("Saving Throws: %s\n"%saving_throws)
    f.write("%s\n"%skill_proficiencies)
    for line in starting_equipment:
        f.write("%s\n"%line)
    f.write("\n")

