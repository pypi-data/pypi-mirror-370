"""Define the default boring things

You modify the class' __get__ descriptor to effect changes!
"""
import re

def patternify(class_) -> re.Pattern:
    """Decorate a class to turn it into a regex pattern

    Note that we don't check whether it's a class nor if it has a __call__ method that returns an
    actual pattern.  So expect the usual exceptions if you maltreat the decoratee.

    We make an instance of the class and then call this.
    """
    return class_()()


@patternify
class DEFAULT_THINGS_CONSIDERED_BORING:

    def __init__(self): pass

    class ProtecedRegex:

        def __set__(self, instance, value):
            raise AttributeError(f'cannot modify readonly content of {self.__class__.__name__!r}')


        def __delete__(self, instance):
            raise AttributeError(f'cannot delete readonly content of {self.__class__.__name__!r}')


        def __get__(self, instance, owner):
            return re.compile(r'''
                (?:b(ed)?h(anger)?\svdr:)
                |
                (?:(dovecot)|(log)(\[\d+\])?:\simap)
                |
                (?:b(ed)?h(anger)?\sfirefox(\.desktop)?(\[\d+\])?:)
                |
                (?:b(ed)?h(anger)?\smp3fs(\[\d+\])?:)
                |
                (?:b(ed)?h(anger)?\scron.*:)
                |
                (?:failed\sto\scoldplug\sunifying.*:)
                |
                (?:b(ed)?h(anger)?\ssmartd.*:.*SMART\sUsage\sAttribute:\s194\sTemperature_Celsius\schanged\sfrom)
                |
                (?:EMITTING\sCHANGED\sfor)
                |
                (?:helper\(pid\s+\d+\):\scompleted\swith\sexit\scode\s0)
                |
                (?:helper\(pid\s+\d+\):\slaunched\sjob\sudisks-helper-ata-smart-collect\son)
                |
                (?:Refreshing\sATA\sSMART\sdata\sfor)
                |
                (?:dvb_frontend_get_frequency_limits)
                |
                (?:systemd\[1\]:\sCondition\scheck\sresulted\sin\s.+\sbeing\sskipped\.)
                |
                (?:gdm-x-session\[\d+\]:\s>\sWarning:\s+Could\snot\sresolve\skeysym\s\S+)
            ''', re.VERBOSE)

    regex = ProtecedRegex()


    def __call__(self) -> re.Pattern:
        return self.regex


    def __str__(self):
        return self.regex.pattern


    def __setattr__(self, name, value):
        if not hasattr(self, name):
            raise AttributeError(f'{self.__class__.__name__!r} may not be augmented')
        else:
            super().__setattr__(name, value)

    def __delattr__(self, name):
        if not hasattr(self, name):
            raise AttributeError(f'{self.__class__.__name__!r} has no attribute {name!r}')
        else:
            super().__delattr__(name)
