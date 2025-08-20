import textwrap
import shutil
from dictionarpy.utils import AnsiWrapperGenerator

class Box:
    def __init__(self, word: str, pronunciation: str|None, 
                defs_and_pos: list[tuple[str, str]], no_ansi: bool):
        self.bold = AnsiWrapperGenerator(
            no_ansi).genwrapper('\u001b[1m', '\u001b[0m')

        self.word = word
        self.pronunciation = pronunciation
        self.defs_and_pos = defs_and_pos

        def_widths, pos_widths = zip(*[[len(i), len(j)] 
            for i, j in self.defs_and_pos])

        self.word_width = len(self.word)
        self.pronunciation_width = len(self.pronunciation) \
            if self.pronunciation else 0

        # width in columns
        self.inner_width = max(max(def_widths), 
                               max(pos_widths), 
                               self.word_width,
                               self.pronunciation_width) + 5

        # box would be bigger than terminal
        self.cols = shutil.get_terminal_size().columns
        if self.inner_width > self.cols - 2:
            self.inner_width = self.cols - 2


    def _get_padding(self, text) -> tuple[int, int]:
        '''
        Get the left and right spacing given the length of input text such that
        it is centered
        '''
        leftpad = (self.inner_width - text) // 2
        rightpad = self.inner_width - text - leftpad
        return leftpad, rightpad


    def _draw_header(self) -> None:
        leftpad, rightpad = self._get_padding(self.word_width)

        print('│', leftpad * ' ', 
                  self.bold(self.word), rightpad * ' ', '│', sep='')

        if self.pronunciation:
            leftpad, rightpad = self._get_padding(self.pronunciation_width)
            print('│', leftpad * ' ', self.pronunciation, rightpad * ' ',
                  '│', sep='')


    def _draw_hr(self, first, last) -> None:
        print(first, '─' * self.inner_width, last, sep='')


    def _draw_defs_and_pos(self) -> None:
        total_items = len(self.defs_and_pos)
        for i, (definition, pos) in enumerate(self.defs_and_pos, start=1):
            rightpad = (self.inner_width - len(pos) - 3 - len(str(i)))
            print('│ ', i, '. ', self.bold(pos), rightpad * ' ', '│', 
                  sep='')
            definition = textwrap.wrap(definition, width=self.inner_width - 6)

            for line in definition:
                leftpad = len(str(i)) + 3
                rightpad = self.inner_width - len(line) - leftpad
                print('│', leftpad * ' ', line, rightpad * ' ', '│', sep='')

            if i < total_items:
                print('│', self.inner_width * ' ', '│', sep='')

    
    def draw(self):
        self._draw_hr('┌', '┐')
        self._draw_header()
        self._draw_hr('├', '┤')
        self._draw_defs_and_pos()
        self._draw_hr('└', '┘')
