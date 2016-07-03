from bs4 import BeautifulSoup
import codecs
from shared import process_abilities
f = codecs.open('Bestiary Compendium 1.2.0.xml', encoding='utf-8')
soup = BeautifulSoup(f.read(), "xml")
f.close()

f = codecs.open('npcs.txt', 'w', encoding='utf-8')


sizes = {
    "G": "Gargantuan",
    "H": "Huge",
    "L": "Large",
    "M": "Medium",
    "S": "Small",
    "T": "Tiny",
}


def process_size(size_input):
    return sizes[size_input]


def process_type(type_input):
    type, source = type_input.rsplit(", ", 1)
    return type, source


def process_attribute(attr):
    mod = (int(attr) - 10)/ 2
    if mod >= 0:
        mod = "+%s"%mod
    return "%s (%s)"%(attr, mod)

cr_xp = {
    "00": "0 XP",
    "0": "10 XP",
    "1/8": "25 XP",
    "1/4": "50 XP",
    "1/2": "100 XP",
    "1": "200 XP",
    "2": "450 XP",
    "3": "700 XP",
    "4": "1,100 XP",
    "5": "1,800 XP",
    "6": "2,300 XP",
    "7": "2,900 XP",
    "8": "3,900 XP",
    "9": "5,000 XP",
    "10": "5,900 XP",
    "11": "7,200 XP",
    "12": "8,400 XP",
    "13": "10,000 XP",
    "14": "11,500 XP",
    "15": "13,000 XP",
    "16": "15,000 XP",
    "17": "18,000 XP",
    "18": "20,000 XP",
    "19": "22,000 XP",
    "20": "25,000 XP",
    "21": "33,000 XP",
    "22": "41,000 XP",
    "23": "50,000 XP",
    "24": "62,000 XP",
    "25": "75,000 XP",
    "26": "90,000 XP",
    "27": "105,000 XP",
    "28": "120,000 XP",
    "29": "135,000 XP",
    "30": "155,000 XP",
}


def process_cr(cr_input):
    return "%s (%s)"%(cr_input, cr_xp[cr_input])


def process_speed(monster):
    speed = monster.speed.string
    speed = speed.replace("ft, ", "ft., ")
    speed = speed.replace("swim", "0 ft., swim")
    speed = speed.replace("fly", "0 ft., fly")
    speed = speed.replace("climb", "0 ft., climb")
    return speed


def process_hp(monster):
    hp = monster.hp.string
    if hp == "0":
        hp = "1"

    if hp[-1] != ")":
        hp += " (1d1)"
    return hp

def output_texts_on_one_line(file, texts):
    past_first = False

    for text in texts:
        if past_first:
            file.write("\\r")
        else:
            past_first = True
        file.write(text)
    else:
        file.write("\n")

for monster in soup.compendium.find_all('monster'):
    name = monster.find("name").string
    size = process_size(monster.size.string)
    type, source = process_type(monster.type.string)
    alignment = monster.alignment.string
    ac = monster.ac.string
    hp = process_hp(monster)
    speed = process_speed(monster)
    strength = process_attribute(monster.str.string)
    dex = process_attribute(monster.dex.string)
    con = process_attribute(monster.con.string)
    intelligence = process_attribute(monster.int.string)
    wis = process_attribute(monster.wis.string)
    cha = process_attribute(monster.cha.string)
    skill = monster.skill.string if monster.skill else None
    saves = monster.save.string if monster.save else None
    resists = monster.resist.string if monster.resist else None
    immunities = monster.immune.string if monster.immune else None
    conditionImmunities = monster.conditionImmune.string if monster.conditionImmune else None
    vulnerabilities = monster.vulnerable.string if monster.vulnerable else None
    senses = monster.senses.string if monster.senses else None
    passive = monster.passive.string
    languages = monster.languages.string if monster.languages else None
    languages = "--" if languages is None else languages
    cr = process_cr(monster.cr.string)
    traits = process_abilities(monster, "trait")
    actions = process_abilities(monster, "action")
    reactions = process_abilities(monster, "reaction")
    legendary_actions = process_abilities(monster, "legendary")
    spells = monster.spells.string if monster.spells else None

    f.write(name + "\n")
    f.write("%s %s, %s\n"%(size, type, alignment))
    f.write("Armor Class %s\n"%ac)
    f.write("Hit Points %s\n"%hp)
    f.write("Speed %s\n"%speed)
    f.write("STR DEX CON INT WIS CHA\n")
    f.write("%s %s %s %s %s %s\n"%(strength, dex, con, intelligence, wis, cha))
    if saves is not None:
        f.write("Saving Throws %s\n"%saves)
    if skill is not None:
        f.write("Skills %s\n"%skill)
    if vulnerabilities is not None:
        f.write("Damage Vulnerabilities %s\n"%vulnerabilities)
    if resists is not None:
        f.write("Damage Resistances %s\n"%resists)
    if immunities is not None:
        f.write("Damage Immunities %s\n"%immunities)
    if conditionImmunities is not None:
        f.write("Condition Immunities %s\n"%conditionImmunities)
    if senses is None:
        f.write("Senses passive Perception %s\n"%passive)
    else:
        f.write("Senses %s, passive Perception %s\n"%(senses, passive))
    f.write("Languages %s\n"%languages)

    if cr == "00":
        cr = "0"
    f.write("Challenge %s\n"%cr)

    for trait in traits:
        trait_name = trait.get_name()
        if trait_name == "Spellcasting" or trait_name == "Innate Spellcasting":
            texts = trait.get_texts()
            f.write("%s. %s"%(trait.get_name(), texts[0]))
            for text in texts[1:]:
                text = text.encode('ascii', errors='ignore')
                text = text.strip()
                f.write("\\r%s"%text)
            #f.write("%s\n"%spells)
            f.write("\n")
            continue
        f.write("%s. "%trait.get_name())
        output_texts_on_one_line(f, trait.get_texts())

    f.write("ACTIONS\n")
    for action in actions:
        f.write("%s. "%action.get_name())
        texts = action.get_texts()
        output_texts_on_one_line(f, texts)

    if len(reactions) > 0:
        f.write("REACTIONS\n")
        for reaction in reactions:
            f.write("%s. "%reaction.get_name())
            texts = reaction.get_texts()
            output_texts_on_one_line(f, texts)

    if len(legendary_actions) > 0:
        f.write("LEGENDARY ACTIONS\n")
        for legendary in legendary_actions:
            f.write("%s. "%legendary.get_name())
            texts = legendary.get_texts()
            output_texts_on_one_line(f, texts)

    f.write("##;\n")
    f.write("Source: %s\n"%source)
    f.write("\n")
