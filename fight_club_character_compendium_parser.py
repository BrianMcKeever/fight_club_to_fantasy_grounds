from bs4 import BeautifulSoup
import codecs
from shared import process_abilities, Ability, process_ability

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
    if skills is None and name == "Haunted One":
        skills = abilityHead(lambda x: x.get_name() == "Skill Proficincies", abilities)
    tools = abilityHead(lambda x: x.get_name() == "Tool Proficiencies", abilities)
    feature = head(lambda x: x.get_name()[:8] == "Feature:", abilities)
    if feature is None and name == "Haunted One":
        feature = head(lambda x: x.get_name() == "Heart of Darkness", abilities)
        feature = Ability("Feature: " + feature.get_name(), feature.get_texts())

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
f.close()

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
f.close()


def convert_ability_to_fg_format(ability):
    name, value = ability.split(" ")
    if name == "Cha":
        stat_name = "Charisma"
    elif name == "Con":
        stat_name = "Constitution"
    elif name == "Dex":
        stat_name = "Dexterity"
    elif name == "Int":
        stat_name = "Intelligence"
    elif name == "Str":
        stat_name = "Strength"
    elif name == "Wis":
        stat_name = "Wisdom"
    else:
        raise Exception("unknown stat")
    return "#!;Ability Score Increase. Your %s score increases by %s.\n"%(stat_name, value)


def process_stats(race_node):
    if race_node.ability is None:
        return []
    stats = race_node.ability.string
    stats = stats.split(",")
    stats = map(lambda s: s.strip(), stats)
    stats = map(convert_ability_to_fg_format, stats)
    return stats


f = codecs.open('races' '.txt', 'w', encoding='utf-8')
for race in soup.compendium.find_all('race'):
    race_name = race.find("name").string
    race_name = race_name.replace("(", "")
    race_name = race_name.replace(")", "")
    size = race.size.string
    speed = race.speed.string
    stats = process_stats(race)
    traits = process_abilities(race, "trait")

    f.write("##; %s\n"%race_name)
    f.write("%s Traits\n"%race_name)
    for line in stats:
        f.write(line)
    for trait in traits:
        f.write("#!; %s. "%(trait.get_name()))
        for text in trait.get_texts():
            f.write("%s\n"%text)
f.close()


f = codecs.open('feats' '.txt', 'w', encoding='utf-8')
for feat in soup.compendium.find_all('feat'):
    ability = process_ability(feat)

    f.write("##; %s\n"%ability.get_name())
    for line in ability.get_texts():
        f.write("%s\n"%line)
    f.write("\n")
f.close()
