from lib import HasThread


class Input(HasThread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
