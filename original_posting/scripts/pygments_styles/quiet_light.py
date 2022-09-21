from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Text, \
     Number, Operator, Generic, Whitespace, Punctuation, Other, Literal

BACKGROUND = "#f9f9f9"
FOREGROUND = "#383a42"
COMMENT = "#a0a1a7"
KEYWORD = "#0098dd"
FUNCTION = "#23974a"
PROPERTY = "#a05a48"
STRING = "#c5a332"
NUMBER = "#ce33c0"
CONSTANT = "#823ff1"
CLASS = "#d52753"
OPERATOR = "#7a82da"
PUNCTUATION = "#275fe4"
RED = "#e92d46"
SELECTION = "#a8aaaa"
AQUA = "#00b5b0"
ESCAPE = "#f92672"


class quiet_light(Style):

    default_style = ''

    background_color = BACKGROUND
    highlight_color = SELECTION

    background_color = BACKGROUND
    highlight_color = SELECTION

    styles = {
        # No corresponding class for the following:
        Text:                      FOREGROUND,  # class:  ''
        Whitespace:                "",          # class: 'w'
        Error:                     RED,         # class: 'err'
        Other:                     "",          # class 'x'

        Comment:                   COMMENT,   # class: 'c'
        Comment.Multiline:         "",        # class: 'cm'
        Comment.Preproc:           "",        # class: 'cp'
        Comment.Single:            "",        # class: 'c1'
        Comment.Special:           "",        # class: 'cs'

        Keyword:                   KEYWORD,    # class: 'k'
        Keyword.Constant:          CONSTANT,   # class: 'kc'
        Keyword.Declaration:       CLASS,      # class: 'kd'
        Keyword.Namespace:         CLASS,      # class: 'kn'
        Keyword.Pseudo:            "",         # class: 'kp'
        Keyword.Reserved:          "",         # class: 'kr'
        Keyword.Type:              CLASS,      # class: 'kt'

        Operator:                  OPERATOR,  # class: 'o'
        Operator.Word:             "",        # class: 'ow' - like keywords

        Punctuation:               PUNCTUATION, # class: 'p'

        Name:                      FOREGROUND,  # class: 'n'
        Name.Attribute:            PROPERTY,    # class: 'na' - to be revised
        Name.Builtin:              CONSTANT,    # class: 'nb'
        Name.Builtin.Pseudo:       "",          # class: 'bp'
        Name.Class:                CLASS,       # class: 'nc' - to be revised
        Name.Constant:             CONSTANT,    # class: 'no' - to be revised
        Name.Decorator:            KEYWORD,     # class: 'nd' - to be revised
        Name.Entity:               "",          # class: 'ni'
        Name.Exception:            RED,         # class: 'ne'
        Name.Function:             FUNCTION,    # class: 'nf'
        Name.Property:             "",          # class: 'py'
        Name.Label:                "",          # class: 'nl'
        Name.Namespace:            CLASS,       # class: 'nn' - to be revised
        Name.Other:                FOREGROUND,  # class: 'nx'
        Name.Tag:                  AQUA,        # class: 'nt' - like a keyword
        Name.Variable:             RED,         # class: 'nv' - to be revised
        Name.Variable.Class:       "",          # class: 'vc' - to be revised
        Name.Variable.Global:      "",          # class: 'vg' - to be revised
        Name.Variable.Instance:    "",          # class: 'vi' - to be revised

        Number:                    NUMBER,    # class: 'm'
        Number.Float:              "",        # class: 'mf'
        Number.Hex:                "",        # class: 'mh'
        Number.Integer:            "",        # class: 'mi'
        Number.Integer.Long:       "",        # class: 'il'
        Number.Oct:                "",        # class: 'mo'

        Literal:                   STRING,     # class: 'l'
        Literal.Date:              STRING,     # class: 'ld'

        String:                    STRING,       # class: 's'
        String.Backtick:           "",          # class: 'sb'
        String.Char:               FOREGROUND,  # class: 'sc'
        String.Doc:                COMMENT,     # class: 'sd' - like a comment
        String.Double:             "",          # class: 's2'
        String.Escape:             ESCAPE,      # class: 'se'
        String.Heredoc:            "",          # class: 'sh'
        String.Interpol:           AQUA,        # class: 'si'
        String.Other:              "",          # class: 'sx'
        String.Regex:              "",          # class: 'sr'
        String.Single:             "",          # class: 's1'
        String.Symbol:             "",          # class: 'ss'

        Generic:                   "",                    # class: 'g'
        Generic.Deleted:           RED,                   # class: 'gd',
        Generic.Emph:              "italic",              # class: 'ge'
        Generic.Error:             "",                    # class: 'gr'
        Generic.Heading:           "bold " + FOREGROUND,  # class: 'gh'
        Generic.Inserted:          FUNCTION,              # class: 'gi'
        Generic.Output:            "",                    # class: 'go'
        Generic.Prompt:            "bold " + COMMENT,     # class: 'gp'
        Generic.Strong:            "bold",                # class: 'gs'
        Generic.Subheading:        "bold " + AQUA,        # class: 'gu'
        Generic.Traceback:         "",                    # class: 'gt'
    }