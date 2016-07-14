class Ability:
    def __init__(self, name, texts=None):
        self._name = name
        self._texts = texts if texts is not None else []

    def get_name(self):
        return self._name

    def get_texts(self):
        return self._texts

    def __str__(self):
        return self.get_name()

def process_abilities(monster, ability_type):
    name = monster.find("name").string

    assert ability_type in ["reaction", "trait", "action", "legendary", "feature", "spell"]
    abilitiesInput = monster.find_all(ability_type)
    abilities = []
    for ability in list(abilitiesInput):
        abilities.append(process_ability(ability))
    return abilities

def process_ability(ability):
    name = ability.find("name").string
    texts = list(ability.find_all("text"))
    texts = map(lambda text: text.string, texts)
    texts = filter(lambda text: text is not None, texts)
    texts = map(lambda text: text.encode('ascii', errors='ignore').strip(), texts)
    return Ability(name, texts)
