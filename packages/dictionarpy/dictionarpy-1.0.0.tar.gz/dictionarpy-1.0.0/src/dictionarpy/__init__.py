import argparse
from dictionarpy.dictionarpy import DictionarPy


def main():
    # TODO https://stackoverflow.com/questions/13310047/how-do-i-constrain-my-python-script-to-only-accepting-one-argument-argparse#13310109
    parser = argparse.ArgumentParser(description='Offline dictionarpy')
    parser.add_argument('word', nargs='?', help='Word to be defined') 
    parser.add_argument('-n', '--no-ansi', action='store_true', 
                        help="Don't make certain words bold")
    parser.add_argument('-s', '--stats', action='store_true', 
                        help='Show database statistics')
    parser.add_argument('-g', '--ipa-guide', const='all', metavar='IPA SYMBOL',
                        nargs='?', help='Show ipa guide (empty for all)')
    parser.add_argument('-z', '--random', const='any', nargs='?', 
                        metavar='PART OF SPEECH', help='Return a random word')
    parser.add_argument('-r', '--remove', type=int, metavar='INDEX',
        help='Remove a definition specified by its index')
    parser.add_argument('-a', '--add', action='store_true',
        help='Add new entry to the dictionarpy (must be used with -w -p -d or \
                        -w -i)')
    parser.add_argument('-w', '--addword', type=str, 
        help='Word to add/word to add to')
    parser.add_argument('-p', '--pos', type=str, help='Part of speech to add')
    parser.add_argument('-d', '--definition', type=str, 
        help='Definition to add')
    parser.add_argument('-i', '--ipa', type=str, help='Pronunciation to add')
    args = parser.parse_args()

    if args.stats:
        DictionarPy('', args.no_ansi).show_stats()
    elif args.ipa_guide:
        DictionarPy('', args.no_ansi).show_ipa_guide(args.ipa_guide)
    elif args.random:
        print(DictionarPy('', args.no_ansi).get_random(args.random))
    elif args.remove:
        if args.word is None:
            parser.error(
                'The -r/--remove flag requires a word to be specified.')
        with DictionarPy(args.word, args.no_ansi) as dictionarpy:
            dictionarpy.remove_definition(args.remove)
    elif args.add and args.addword and args.pos and args.definition:
        with DictionarPy('', args.no_ansi) as dictionarpy:
            dictionarpy.add_definition(args.addword, args.pos, args.definition)
    elif args.add and args.addword and args.ipa:
        with DictionarPy('', args.no_ansi) as dictionarpy:
            dictionarpy.add_ipa(args.addword, args.ipa)
    elif args.word is None:
        parser.print_help()
    else:
        with DictionarPy(args.word, args.no_ansi) as dictionarpy:
            dictionarpy.show_definitions()
