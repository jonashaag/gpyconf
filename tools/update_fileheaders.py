FILE_HEADER = """
Copyright (c) 2008-2009 Jonas Haag.
This file is part of gpyconf.
For conditions of distribution and use,
see the accompanying LICENSE file.
"""
FILE_HEADER = '# ' + '\n# '.join(FILE_HEADER.strip('\n').split('\n'))

if __name__ == '__main__':
    import os
    for _, _, files in os.walk('../src'):
        for file in files:
            with open(file) as fobj:
                content = fobj.read()
            with open(file, 'w') as fobj:
                fobj.write(content.replace('# %FILEHEADER%', FILE_HEADER))
            print "Updated license header in %s" % file
