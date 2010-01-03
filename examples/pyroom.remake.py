from gpyconf import Configuration
from gpyconf.fields import IntegerField, BooleanField, MultiOptionField
from gpyconf.fields import ColorField, FontField
from gpyconf.backends.python import PythonModuleBackend

themes = [(theme, theme.title()) for theme in (
    'amber', 'c64', 'darkgreen', 'locontrast', 'banker', 'cupid', 'green',
    'website', 'blue', 'custom', 'grey')]

class PyRoomConfiguration(Configuration):
    filename = 'pyroom.conf'

    autosave = IntegerField('Autosave every', default=2, label2='minutes', group='Autosave')

    line_numbering = BooleanField('Use line numbering', group='Line Numbering')
    show_border = BooleanField('Show border', default=True, group='Line Numbering')

    line_spacing = BooleanField('Line spacing', default=2, group='Line Spacing')

    preset = MultiOptionField('Presets:', options=themes,
        section='Theme', default='c64')

    font = FontField('Font:', section='Theme')
    background_color = ColorField('Background color', section='Theme')
    border_color = ColorField('Border color', section='Theme')
    text_color = ColorField('Text color', section='Theme')
    text_background_color = ColorField('Text background color', section='Theme')

    height = IntegerField('Height in %:', default=5, section='Theme')
    width = IntegerField('Width in %:', default=5, section='Theme')
    padding = IntegerField('Padding', section='Theme')


pyroom_config = PyRoomConfiguration()
pyroom_config.run_frontend()
