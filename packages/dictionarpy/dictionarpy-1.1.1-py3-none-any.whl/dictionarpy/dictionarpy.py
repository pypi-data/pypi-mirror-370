import sqlite3
import pathlib
import os.path
import textwrap
import random
import shutil
from importlib import resources
from dictionarpy.box import Box
from dictionarpy.utils import AnsiWrapperGenerator


WIDTH = shutil.get_terminal_size().columns


class DictionarPy:
    def __init__(self, word: str, no_ansi: bool):
        self.no_ansi = no_ansi
        generator = AnsiWrapperGenerator(self.no_ansi)
        self.bold = generator.genwrapper('\u001b[1m', '\u001b[0m')
        self.underline = generator.genwrapper('\u001b[4m', '\u001b[24m')
        self.italic = generator.genwrapper('\u001b[3m', '\u001b[23m')

        self.word = word

        datadir = pathlib.Path.home() / '.local/share/dictionarpy'
        self.db = datadir / 'dictionary.db'
        if not self.db.is_file():
            datadir.mkdir(parents=True, exist_ok=True)
            with resources.path('dictionarpy.data', 'dictionary.db') as data:
                shutil.copy2(data, self.db)

        self.con = sqlite3.connect(self.db)
        self.cur = self.con.cursor()


    def show_definitions(self) -> None:
        defs_and_pos = self.get_definitions()
        ipa = self.get_ipa()

        box = Box(self.word, ipa, defs_and_pos, self.no_ansi)
        box.draw()


    def splash_display(self, title: str, items: str) -> None:
        print('─' * (WIDTH // 2 + 2))
        items = ' │ '.join(items)

        print(self.bold(title))
        for line in textwrap.wrap(items, width=(WIDTH // 2)):
            if line[-2:] == ' │':
                line = line[:-2]
            print('   ', line)


    def get_sim_words(self) -> set[str]:
        '''
        Print words in the database that contain the input string.
        This is used when a requested word is not found in the database.
        '''
        sim_words_res = self.cur.execute(
            'select word from words where word like ?', 
            (f'%{self.word.lower()}%',)).fetchall()

        return {} if not sim_words_res else {i[0] for i in sim_words_res}


    def get_word_id(self) -> int:
        word_id_res = self.cur.execute(
            'select id from words where word = ?', (self.word,)).fetchone()

        if not word_id_res:
            print('Cannot find word in working database.')
            self.splash_display('Similar:', self.get_sim_words())
            exit(1)

        word_id, = word_id_res
        return word_id


    def get_ipa(self) -> str:
        word_id = self.get_word_id()
        ipa_res = self.cur.execute(
            'select pronunciation from pronunciations where word_id = ?',
                (word_id,)).fetchone()

        if ipa_res is not None: 
            ipa, = ipa_res
            return ipa
        return None


    def get_definitions(self) -> list[tuple[str, str]]:
        '''
        Query database for definitions and parts of speech for a given word.

        E.g.

        word = happy
        returns
            [('enjoying or showing or marked by joy or pleasure', 'adjective'),
             ('marked by good fortune', 'adjective'), 
             ('eagerly disposed to act or to be of service', 'adjective'), 
             ('well expressed and to the point', 'adjective')]
        '''
        word_id = self.get_word_id()
        defs_and_pos = self.cur.execute(
            'select definition, pos from definitions where word_id = ?', 
            (word_id,)).fetchall()

        return defs_and_pos


    def remove_definition(self, index: int) -> None:
        '''
        Remove a definition as specified by its display index. If the last
        definition is removed, so is the word and its ipa transcription.
        '''
        word_id = self.get_word_id()
        index -= 1

        definition_id = self.cur.execute(
            'select id from definitions where word_id = ? limit 1 offset ?',
                (word_id, index)).fetchone()
        if not definition_id:
            print('There is no definition with this index')
            return

        definition_id, = definition_id
        self.cur.execute(
            'delete from definitions where id = ?', (definition_id,))

        # remove word if no definitions remain
        remaining_defs = self.cur.execute(
            'select definition from definitions where word_id = ?', 
            (word_id,)).fetchall()
        if not remaining_defs:
            self.cur.execute(
                'delete from words where id = ?', (word_id,))
            # don't want an orphan pronunciation
            self.cur.execute(
                'delete from pronunciations where word_id = ?', (word_id,))

        self.con.commit()


    def add_definition(self, addword: str, pos: str, definition: str) -> None:
        '''
        Create a word, pos, and definition if the word does not yet exist.
        Otherwise add a pos, definition pair to an existing word.
        '''
        self.cur.execute(
            'insert or ignore into words (word) values (?)', (addword,))
        addword_id, = self.cur.execute(
            'select id from words where word = ?', (addword,)).fetchone()

        self.cur.execute(
            'insert or ignore into definitions (word_id, definition, pos) \
                values (?, ?, ?)', (addword_id, definition, pos))
        self.con.commit()


    def add_ipa(self, addword: str, addipa: str) -> None:
        word_id, = self.cur.execute(
            'select id from words where word = ?', (addword,)).fetchone()

        self.cur.execute(
            'insert or replace into pronunciations (word_id, pronunciation) \
                values (?, ?)', (word_id, addipa))
        self.con.commit()


    def get_num_words(self) -> int:
        return self.cur.execute(
            'select count(*) from words').fetchone()[0]


    def get_num_defs(self, pos='*') -> int:
        '''
        Number of definitions in the dictionary. Optionally constrained to
        a specific part of speech
        '''
        return self.cur.execute(
            'select count(*) from definitions where pos glob ?', 
                (pos,)).fetchone()[0]


    def get_db_size(self) -> float:
        '''
        Size of dictionary db in MB
        '''
        return os.path.getsize(self.db) / (1024 ** 2) 


    def get_all_pos(self) -> set[str]:
        pos_res = self.cur.execute(
            'select distinct pos from definitions').fetchall()
        return {i[0] for i in pos_res}


    def get_ipa_transcriptions(self) -> int:
        return self.cur.execute(
            'select count(*) from pronunciations').fetchone()[0]


    def show_stats(self) -> None:
        '''
        Output a string containing database information
        '''
        words = self.get_num_words()
        definitions = self.get_num_defs()
        transcriptions = self.get_ipa_transcriptions()
        size = self.get_db_size()

        print(f"{self.bold('Words:')}               {words}")
        print(f"{self.bold('Definitions:')}         {definitions}")
        print(f"{self.bold('IPA Transcriptions:')}  {transcriptions}")
        print(f"{self.bold('Disk size:')}           {size:.2f}MB")

        self.splash_display('Parts of speech:', self.get_all_pos())


    def get_random(self, pos='any') -> str:
        if pos == 'any':
            ind = random.randint(0, self.get_num_words() - 1)        
            word, = self.cur.execute(
                'select word from words limit 1 offset ?', (ind,)).fetchone()

        elif pos in self.get_all_pos():
            ind = random.randint(0, self.get_num_defs(pos) - 1)
            word, = self.cur.execute('select w.word from words as w \
                             join definitions as d on w.id = d.word_id \
                             where d.pos = ? limit 1 offset ?', 
                             (pos, ind)).fetchone()
        else:
            print('Part of speech not found in working database')
            exit(1)

        return word


    def show_ipa_guide(self, key='all') -> None:
        u = self.underline
        guide = {
            'b':  [[u('b') + 'ook',
                   'tu' + u('b')]],
            'd':  [[u('d') + 'esk',
                   'sa' + u('d')]],
            'f':  [[u('f') + 'amily',
                   'lea' + u('f'),
                   'lau' + u('gh'),
                   u('ph') + 'one']],
            'g':  [[u('g') + 'irl',
                   'bi' + u('g')]],
            'h':  [[u('h') + 'ead',
                   u('h') + 'and']],
            'j':  [[u('y') + 'awn',
                   u('y') + 'ogurt']],
            'k':  [[u('k') + 'ing',
                   u('c') + 'a' + u('k') + 'e',
                   u('r') + 'ock',
                   's' + u('ch') + 'ool']],
            'l':  [[u('l') + 'ion',
                   'penci' + u('l')]],
            'm':  [[u('m') + 'oon',
                   'ar' + u('m'),
                   'cli' + u('mb')]],
            'n':  [[u('n') + 'est',
                   'lio' + u('n')]],
            'p':  [[u('p') + 'en',
                   'ma' + u('p')]],
            'ɹ':  [[u('r') + 'un',
                    u('r') + 'oom',
                    'sta' + u('r')]],
            's':  [[u('s') + 'un',
                   'rut' + u('s'),
                   'fa' + u('c') + 'e']],
            't':  [[u('t') + 'en',
                   'goa' + u('t'),
                   'bu' + u('tt') + 'er',
                   'ki' + u('tt') + 'en']],
            'ɾ':  [['bu' + u('tt') + 'er'], 'flap between sonorants'],
            'ʔ':  [['ki' + u('tt') + 'en'], 'glottal stop before nasal'],
            'v':  [[u('v') + 'an',
                   'lo' + u('ve')]],
            'w':  [[u('w') + 'ater',
                   u('wh') + 'ale']],
            'z':  [[u('z') + 'ebra',
                   'qui' + u('z'),
                   'bean' + u('s'),
                   'cookie' + u('s')]],
            'ŋ':  [['wi' + u('ng'),
                   'runni' + u('ng')]],
            'ʒ':  [['mea' + u('s') + 'ure']],
            'dʒ': [[u('g') + 'ym',
                   'hu' + u('ge'),
                   u('j') + 'et']],
            'ʃ':  [[u('sh') + 'oes',
                   'fi' + u('sh'),
                   'mo' + u('ti') + 'on']],
            'tʃ': [[u('ch') + 'eese',
                   'lun' + u('ch')]],
            'θ':  [[u('th') + 'ree',
                   'mou' + u('th'),
                   u('th') + 'igh']],
            'ð':  [[u('th') + 'is',
                   'mo' + u('th') + 'er',
                   u('th') + 'y']],
            'ɑ':  [[u('o') + 'n',
                   'm' + u('o') + 'm']],
            'æ':  [[u('a') + 'pple',
                   'b' + u('a') + 'g',
                   'b' + u('a') + 'n'], '[ɛə] b' + u('a') + 'n (pre-nasal vowel)'],
            'aɪ': [['b' + u('i') + 'ke',
                   'sk' + u('y'),
                   'p' + u('ie'),
                   'h' + u('igh')]],
            'aʊ': [['m' + u('ou') + 'th',
                    'c' + u('o') + 'w']],
            'ɛ':  [[u('e') + 'gg',
                   't' + u('e') + 'n',
                   'br' + u('ea') + 'd']],
            'eɪ': [['g' + u('a') + 'me',
                   'r' + u('ai') + 'n',
                   'pl' + u('ay')]],
            'ɪ':  [[u('i') + 'n',
                   'b' + u('i') + 'g',
                   'f' + u('i') + 'fty,']],
            'i':  [[u('ea') + 't',
                   'sl' + u('ee') + 'p',
                   'happ' + u('y')]],
            'oʊ': [['h' + u('o') + 'me',
                   'c' + u('o') + 'ld',
                   'r' + u('oa') + 'd',
                   'wind' + u('ow')]],
            'ɔ':  [['w' + u('a') + 'lk',
                   'y' + u('a') + 'wn',
                   u('Au') + 'gust']],
            'ɔɪ': [['c' + u('oi') + 'n',
                   'b' + u('oy')]],
            'ʊ':  [['b' + u('oo') + 'k',
                   'f' + u('oo') + 't',
                   'p' + u('u') + 't']],
            'u':  [['fl' + u('u') + 'te',
                   'bl' + u('ue'),
                   'fr' + u('ui') + 't',
                   'f' + u('oo') + 'd']],
            'ʌ':  [[u('u') + 'p',
                   'r' + u('u') + 'n',
                   'one']],
            'ɝ':  [['sh' + u('ir') + 't',
                   u('Ear') + 'th',
                   'n' + u('ur') + 'se',
                   'w' + u('or') + 'k']],
            'ə':  [['b' + u('a') + 'lloon',
                   'cam' + u('e') + 'l',
                   'pr' + u('o') + 'tect',
                   'min' + u('u') + 's'], '"shwa", an unstressed vowel'],
            'ɚ':  [['fath' + u('er'),
                   'bak' + u('er')], 'unstressed rhotic vowel']}

        if key == 'all':
            for k, v in guide.items():
                print(self.bold('/' + k + '/'), end='\t')
                print(' │ '.join(v[0]))
                if len(v) == 2: print('\t' + self.italic(v[1]))
        elif key in guide.keys():
            v = guide.get(key)
            print(' │ '.join(v[0]))
            if len(v) == 2: print('\t' + self.italic(v[1]))


    def __enter__(self):
        return self

    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()
