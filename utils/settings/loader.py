from collections import defaultdict
import json

def compare_nested_dicts(dictA, dictB, depth=1, changes=None, curr_key=''):
    '''
    compare dictB to dictA on keys (depth <= 3)
    '''
    if depth > 3:
        return changes
    if changes is None:
        changes = {'missing': {}, 'added': {}}

    keysA = set(dictA.keys())
    keysB = set(dictB.keys())

    # Check if the key of B completely contains the key of A
    if keysA != keysB:
        missing_keys = keysA - keysB
        added_keys = keysB - keysA
        if missing_keys:
            changes['missing'][curr_key] = missing_keys
        if added_keys:
            changes['added'][curr_key] = added_keys

    # Compare the values corresponding to each key
    for key in keysA.intersection(keysB):
        new_key = f'{curr_key}.{key}' if curr_key else key
        if isinstance(dictA[key], dict) and isinstance(dictB[key], dict):
            compare_nested_dicts(dictA[key], dictB[key], depth+1, changes, new_key)
        elif dictA[key] != dictB[key]:
            changes[curr_key] = (dictA[key], dictB[key])

    return changes

# a problem: Unable to use relative path of `example_conf_path`
class Settings:
    def __init__(
            self, conf_path: str="", example_conf_path = '/home/u2022101014/ZHEM/settings/example.json'
    ):
        self.settings = defaultdict(str)
        self.example_settings = defaultdict(str)
        self.load_settings(conf_path, example_conf_path)
        self._compare_settings()

    def load_settings(
            self, conf_path: str="", example_conf_path = '/home/u2022101014/ZHEM/settings/example.json'
    ) -> None:
        try:
            with open(conf_path, 'r') as fr:
                self.settings = json.load(fr)
            with open(example_conf_path, 'r') as fe:
                self.example_settings = json.load(fe)
        except Exception as ne:
            assert(f"[Error] Exception {ne} raised in settings.loader. Maybe the settings json file or example settings json file not exists!!")

    def _compare_settings(self) -> None:
        '''
        compare current settings to example settings and output the differences
        '''
        changes = compare_nested_dicts(self.example_settings, self.settings)
        if not changes['missing'] and not changes['added']:
            # if the two settings are the same, go on
            pass
        else:
            print("Differences between current settings to example settings.\nPlease align the current settings with the example settings.")
            if changes['missing']:
                print('Missing keys:')
                for key, missing_subkeys in changes['missing'].items():
                    for missing_subkey in missing_subkeys:
                        if key != '':
                            print(f'  {key}.{missing_subkey}')
                        else:
                            print(f'  {missing_subkey}')		
            if changes['added']:
                print('Redundant keys: ')
                for key, added_subkeys in changes['added'].items():
                    for added_subkey in added_subkeys:
                        if key != '':
                            print(f'  {key}.{added_subkey}')
                        else:
                            print(f'  {added_subkey}')	
            assert 0
    
    