from bs4 import BeautifulSoup
import codecs
from shared import process_abilities
f = codecs.open('Bestiary Compendium 1.2.1.xml', encoding='utf-8')
soup = BeautifulSoup(f.read(), "xml")
f.close()

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


def write_monster(f, monster):
    f.write(monster["name"] + "\n")
    f.write("%s %s, %s\n"%(monster["size"], monster["type"], monster["alignment"]))
    f.write("Armor Class %s\n"%monster["ac"])
    f.write("Hit Points %s\n"%monster["hp"])
    f.write("Speed %s\n"%monster["speed"])
    f.write("STR DEX CON INT WIS CHA\n")
    f.write("%s %s %s %s %s %s\n"%(monster["strength"], monster["dexterity"],
        monster["constitution"],
        monster["intelligence"], monster["wisdom"], monster["charisma"]))
    if monster["saves"] is not None:
        f.write("Saving Throws %s\n"%monster["saves"])
    if monster["skill"] is not None:
        f.write("Skills %s\n"%monster["skill"])
    if monster["vulnerabilities"] is not None:
        f.write("Damage Vulnerabilities %s\n"%monster["vulnerabilities"])
    if monster["resists"] is not None:
        f.write("Damage Resistances %s\n"%monster["resists"])
    if monster["immunities"] is not None:
        f.write("Damage Immunities %s\n"%monster["immunities"])
    if monster["condition_immunities"] is not None:
        f.write("Condition Immunities %s\n"%monster["condition_immunities"])
    if monster["senses"] is None:
        f.write("Senses passive Perception %s\n"%monster["passive"])
    else:
        f.write("Senses %s, passive Perception %s\n"%(monster["senses"],
        monster["passive"]))
    f.write("Languages %s\n"%monster["languages"])

    if monster["cr"] == "00":
        monster["cr"] = "0"
    f.write("Challenge %s\n"%monster["cr"])

    for trait in monster["traits"]:
        trait_name = trait.get_name()
        if trait_name == "Spellcasting" or trait_name == "Innate Spellcasting":
            texts = trait.get_texts()
            f.write("%s. %s"%(trait.get_name(), texts[0]))
            for text in texts[1:]:
                text = text.encode('ascii', errors='ignore')
                text = text.strip()
                f.write("\\r%s"%text)
            f.write("\n")
            continue
        f.write("%s. "%trait.get_name())
        output_texts_on_one_line(f, trait.get_texts())

    f.write("ACTIONS\n")
    for action in monster["actions"]:
        f.write("%s. "%action.get_name())
        texts = action.get_texts()
        output_texts_on_one_line(f, texts)

    if len(monster["reactions"]) > 0:
        f.write("REACTIONS\n")
        for reaction in monster["reactions"]:
            f.write("%s. "%reaction.get_name())
            texts = reaction.get_texts()
            output_texts_on_one_line(f, texts)

    if len(monster["legendary_actions"]) > 0:
        f.write("LEGENDARY ACTIONS\n")
        for legendary in monster["legendary_actions"]:
            f.write("%s. "%legendary.get_name())
            texts = legendary.get_texts()
            output_texts_on_one_line(f, texts)

    f.write("##;\n")
    f.write("Source: %s\n"%monster["source"])
    f.write("\n")

monsters = []

for monster in soup.compendium.find_all('monster'):
    name = monster.find("name").string
    size = process_size(monster.size.string)
    type, source = process_type(monster.type.string)
    alignment = monster.alignment.string
    ac = monster.ac.string
    hp = process_hp(monster)
    speed = process_speed(monster)
    strength = process_attribute(monster.str.string)
    dexterity = process_attribute(monster.dex.string)
    constitution = process_attribute(monster.con.string)
    intelligence = process_attribute(monster.int.string)
    wisdom = process_attribute(monster.wis.string)
    charisma = process_attribute(monster.cha.string)
    skill = monster.skill.string if monster.skill else None
    saves = monster.save.string if monster.save else None
    resists = monster.resist.string if monster.resist else None
    immunities = monster.immune.string if monster.immune else None
    condition_immunities = monster.conditionImmune.string if monster.conditionImmune else None
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

    monster = {}
    monster["name"] = name
    monster["size"] = size
    monster["type"] = type
    monster["source"] = source
    monster["alignment"] = alignment
    monster["ac"] = ac
    monster["hp"] = hp
    monster["speed"] = speed
    monster["strength"] = strength
    monster["dexterity"] = dexterity
    monster["constitution"] = constitution
    monster["intelligence"] = intelligence
    monster["wisdom"] = wisdom
    monster["charisma"] = charisma
    monster["skill"] = skill
    monster["saves"] = saves
    monster["resists"] = resists
    monster["immunities"] = immunities
    monster["condition_immunities"] = condition_immunities
    monster["vulnerabilities"] = vulnerabilities
    monster["senses"] = senses
    monster["passive"] = passive
    monster["languages"] = languages
    monster["cr"] = cr
    monster["traits"] = traits
    monster["actions"] = actions
    monster["reactions"] = reactions
    monster["legendary_actions"] = legendary_actions
    monster["spells"] = spells
    monsters.append(monster)

f = codecs.open('npcs.txt', 'w', encoding='utf-8')
for monster in monsters:
    write_monster(f, monster)
f.close()

f = codecs.open('shapeshift_npcs.txt', 'w', encoding='utf-8')
beasts = filter(lambda x: x["type"] == "beast", monsters[:])
for beast in beasts:
    print(beast["name"])
    write_monster(f, beast)
f.close()

