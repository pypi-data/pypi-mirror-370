class AnsiWrapperGenerator:
    def __init__(self, no_ansi: bool):
        self.no_ansi = no_ansi
        

    def genwrapper(self, start_code: str, end_code: str):
        if self.no_ansi:
            return lambda string: string
        return lambda string: start_code + string + end_code
