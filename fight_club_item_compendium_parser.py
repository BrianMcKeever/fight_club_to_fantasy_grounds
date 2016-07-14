from bs4 import BeautifulSoup
import codecs
import string
from shared import process_abilities, Ability, process_ability

f = codecs.open('Items Compendium 1.3.0.xml', encoding='utf-8')
soup = BeautifulSoup(f.read(), "xml")
f.close()


def process_type(item):
    type = item.type.string
    if type == "P":
        type = "Potion"
    elif type == "W":
        type = "Wondrous Item"
    elif type == "MA":
        type = "Medium Armor"
    elif type == "HA":
        type = "Heavy Armor"
    elif type == "LA":
        type = "Light Armor"
    elif type == "G":
        type = "Adventuring Gear"
    elif type == "M":
        type = "Melee Weapon"
    elif type == "$":
        type = "Currency"
    elif type == "A":
        type = "Ammunition"
    elif type == "R":
        type = "Ranged Weapon"
    elif type == "SC":
        type = "Scroll"
    elif type == "S":
        type = "Shield"
    elif type == "WD":
        type = "Wand"
    elif type == "ST":
        type = "Staff"
    elif type == "RD":
        type = "Rod"
    elif type == "RG":
        type = "Ring"
    else:
        print "unknown item type %s"%type
    return type


damage_types = {
    "B":"bludgeoning",
    "P":"piercing",
    "S":"slashing",
}

weapon_properties_dictionary = {
    "L":"light",
    "F":"finesse",
    "T":"thrown",
    "2H":"two-handed",
    "V":"versatile",
    "H":"heavy",
    "R":"reach",
    "LD":"loading",
    "S":"special",
    "A":"ammunition",
}


def process_weapon_properties(weapon_properties, weapon_range = None, damage2 = None):
    result_list = []
    weapon_properties = weapon_properties.split(",")
    weapon_properties = map(lambda x: x.strip(), weapon_properties)
    for weapon_property in weapon_properties:
        weapon_property = weapon_properties_dictionary[weapon_property]
        if weapon_property == "thrown" or weapon_property == "ammunition":
            if weapon_range is None:
                weapon_range = ""
                print("Ranged weapon without range")
            result_list.append("%s (%s)"%(weapon_property, weapon_range))
        elif weapon_property == "versatile":
            assert(damage2 is not None);
            result_list.append("%s (%s)"%(weapon_property, damage2))
        else:
            result_list.append(weapon_property)
    result = ", ".join(result_list)
    return result


class Item:
    def __str__(self):
        return self.name

    def __init__(self, name, type, texts, damage2, weight, ac, weapon_range, damage_type, damage1, properties, cost, strength, stealth):
        self.name = name
        self.type = type
        self.weight = weight
        self.ac = ac
        self.weapon_range = weapon_range
        self.damage_type = damage_type
        self.damage1 = damage1
        self.properties = properties
        self.damage2 = damage2
        self.cost = cost
        self.texts = texts
        self.strength = strength
        self.stealth = stealth
        self.rarity = None
        self.requires_attunement = None
        for text in texts:
            if text[:8] == "Requires":
                self.requires_attunement = text
            if text[:7] == "Rarity:":
                self.rarity = string.split(text, " ", 1)[1]
        self.texts = filter(lambda t: t[:7] != "Rarity:", self.texts)
        self.texts = filter(lambda t: t[:8] != "Requires", self.texts)

types = []
items = []
for item in soup.compendium.find_all('item'):
    ability = process_ability(item)

    weight = "0.1"
    if item.weight:
        weight = item.weight.string

    damage2 = None
    if item.dmg2:
        damage2 = item.dmg2.string

    ac = None
    if item.ac:
        ac = item.ac.string

    weapon_range = None
    if item.range:
        weapon_range = item.range.string

    damage_type = None
    if item.dmgType:
        damage_type = damage_types[item.dmgType.string]

    damage1 = None
    if item.dmg1:
        damage1 = item.dmg1.string

    properties = "--"
    if item.property:
        properties = process_weapon_properties(item.property.string, weapon_range, damage2)

    strength = "-"
    if item.strength:
        strength = item.strength.string

    stealth = "NO"
    if item.stealth:
        stealth = item.stealth.string
    cost = "1"
    item_type = process_type(item)
    types.append(item_type)
    items.append(Item(ability.get_name(), item_type, ability.get_texts(), damage2, weight, ac, weapon_range, damage_type, damage1, properties, cost, strength, stealth))
types.sort()
non_magic_gear = filter(lambda i: i.rarity is None, items)

f = codecs.open('equipment' '.txt', 'w', encoding='utf-8')
adventuring_gear = filter(lambda i: i.type == "Adventuring Gear", non_magic_gear)
f.write("#@;ADVENTURING GEAR\n")
f.write("#th;Name;Cost;Weight\n")

f.write("#st;Ammunition\n")
ammunition = filter(lambda i: i.type == "Ammunition", non_magic_gear)
for item in ammunition:
    f.write("%s;%s gp;%s lb.\n"%(item.name, item.cost, item.weight))

f.write("#st;Random\n")
for item in adventuring_gear:
    f.write("%s;%s gp;%s lb.\n"%(item.name, item.cost, item.weight))

f.write("#@;ARMOR\n")
f.write("#th;Armor;Cost;Armor Class (AC);Strength;Stealth;Weight\n")

f.write("#st;Light Armor\n")
for item in filter(lambda i: i.type == "Light Armor", non_magic_gear):
    f.write("%s;%s gp;%s;%s;%s;%s lb.\n"%(item.name, item.cost, item.ac, item.strength, item.stealth, item.weight))

f.write("#st;Medium Armor\n")
for item in filter(lambda i: i.type == "Medium Armor", non_magic_gear):
    f.write("%s;%s gp;%s;%s;%s;%s lb.\n"%(item.name, item.cost, item.ac, item.strength, item.stealth, item.weight))

f.write("#st;Heavy Armor\n")
for item in filter(lambda i: i.type == "Heavy Armor", non_magic_gear):
    f.write("%s;%s gp;%s;%s;%s;%s lb.\n"%(item.name, item.cost, item.ac, item.strength, item.stealth, item.weight))

f.write("#@;WEAPON\n")
f.write("#th;Name;Cost;Damage;Weight;Properties\n")

f.write("#st;Melee\n")
for item in filter(lambda i: i.type == "Melee Weapon", non_magic_gear):
    f.write("%s;%s gp;%s %s;%s lb.;%s\n"%(item.name, item.cost, item.damage1, item.damage_type, item.weight, item.properties))

f.write("#st;Ranged\n")
for item in filter(lambda i: i.type == "Ranged Weapon", non_magic_gear):
    f.write("%s;%s gp;%s %s;%s lb.;%s\n"%(item.name, item.cost, item.damage1, item.damage_type, item.weight, item.properties))

f.write("\n")
for item in non_magic_gear:
    texts = r" ".join(item.texts)
    f.write("%s. %s\n"%(item.name, texts))
f.close()

f = codecs.open('magicitems' '.txt', 'w', encoding='utf-8')
magic_items = filter(lambda i: i.rarity is not None, items)

magic_item_types = {
    "Wondrous Item": "Wondrous item",
    "Potion": "Potion",
    "Light Armor": "Armor (light)",
    "Medium Armor": "Armor (medium)",
    "Heavy Armor": "Armor (heavy)",
    "Shield": "Armor (shield)",
    "Ammunition": "Weapon (ammunition)",
    "Ranged Weapon": "Weapon (ranged weapon)",
    "Melee Weapon": "Weapon (melee weapon)",
    "Scroll": "Scroll",
    "Staff": "Staff",
    "Rod": "Rod",
    "Ring": "Ring",
    "Wand": "Wand",
}

for item in magic_items:
    f.write("%s\n"%item.name)
    if item.rarity:
        if item.requires_attunement:
            if len(item.requires_attunement) > 19:
                f.write("%s, %s (Requires Attunement)\n"%(magic_item_types[item.type], item.rarity))
                f.write("%s\n"%item.requires_attunement)
            else:
                f.write("%s, %s (%s)\n"%(magic_item_types[item.type], item.rarity, item.requires_attunement))
        else:
            f.write("%s, %s\n"%(magic_item_types[item.type], item.rarity))
    else:
        f.write("%s\n"%(magic_item_types[item.type]))
    for text in item.texts:
        f.write("%s\n"%text)
    f.write("\n")
f.close()
