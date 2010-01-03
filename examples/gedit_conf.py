from gpyconf import Configuration, fields

class GEditConfiguration(Configuration):
    autobreak = fields.BooleanField('Enable text wrapping', section='View', group='Text Wrapping')
    nowordsplit = fields.BooleanField('Do not split words over two lines', section='View', group='Text Wrapping')

    linenos = fields.BooleanField('Display line numbers', section='View', group='Line Numbers')

    highlight_line = fields.BooleanField('Highlight current line', section='View', group='Current Line')

    display_rightmargin = fields.BooleanField('Display right margin', section='View', group='Right Margin')
    rightmargin = fields.IntegerField('Right margin at column:', section='View', group='Right Margin', min=1, max=160)

    highlight_bracket = fields.BooleanField('Highlight matching bracked', section='View', group='Bracket Matching')


    tabwidth = fields.IntegerField('Tab width:', section='Editor', group='Tab Stops', default=8, min=1, max=24)
    use_spaces = fields.BooleanField('Inserted spaces instead of tabs', section='Editor', group='Tab Stops')

    autoindent = fields.BooleanField('Enable automatic indentation', section='Editor', group='Automatic Indentation')

    backup = fields.BooleanField('Create a backup copy of files before saving', section='Editor', group='File Saving')
    autosave = fields.IntegerField('Autosave every', label2='minutes', section='Editor', group='File Saving', default=8, min=1, max=100)

gedit = GEditConfiguration()
gedit.run_frontend()
