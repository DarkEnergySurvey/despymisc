#!/usr/bin/env python

import xml.parsers.expat

class Xmlslurper:

    def __init__(self, filename, tablenames):
        self.data = {}
        

        ##################################################################
        def start_element(name, attrs, data = self.data):
            if "TABLE" == name:
                # skip if not one of the desired tables
                if not attrs['name'] in self.data['wanted_tables']:
                    return

                # initialize values for a new table
                data['curtable'] = attrs['name']
                data['fieldnames'] = []
                data['fieldtypes'] = []
                data['fieldarray'] = []
                data['tables'][data['curtable']] = []

            if "FIELD" == name and self.data['curtable']:
                # save description information
                data['fieldnames'].append(attrs['name'].lower())
                data['fieldtypes'].append(attrs['datatype'])
                data['fieldarray'].append(attrs.get('arraysize',None))

            if "TR" == name:
                # new row, inialize row values
                data['col'] = 0             # current column
                data['prevcol'] = 0         # previous column 
                data['prevtext'] = ''       # previous text parsed in case partial due to buffer
                data['currow'] = {}         # dictionary to store info from row

            if "TD" == name:
                # save state that are in a TD section
                data['in_TD'] = True


        ##################################################################
        def end_element(name, data = self.data):

            if "TD" == name:
                # if closed TD section, change TD state
                data['col'] += 1
                data['in_TD'] = False

            if "TR" == name and data['curtable']:
                # save current row dictionary to current table
                data['tables'][data['curtable']].append(data['currow'])

            if "TABLE" == name and data['curtable']:
                # empty table variables
                data['curtable'] = None
                del self.data['fieldnames'] 
                del self.data['fieldtypes']
                del self.data['fieldarray']


        ##################################################################
        def char_data(text, data = self.data):
            prevtext = text

            if data['in_TD'] and self.data['curtable']:
                # if still same column, need to join with previous data
                if data['prevcol'] == data['col']:
                    text = data['prevtext'] + text

                curarrsize = data['fieldarray'][data['col']]
                curtype = data['fieldtypes'][data['col']]
                curname = data['fieldnames'][data['col']]

                if curarrsize != None and curtype != 'char':
                    # data is for an array field
                    # assumes array cannot be of strings
                
                    # so split into separate values
                    vals = text.strip().split()

                    # convert values to right type
                    if curtype == 'int':
                        for i in range(0,len(vals)):
                            vals[i] = int(vals[i])
                    elif curtype == 'float':
                        for i in range(0,len(vals)):
                            vals[i] = float(vals[i])
                
                    # save data array to current row data
                    data['currow'][curname] = vals
                else:
                    # single value, convert to right type
                    if curtype == 'int':
                        val = int(text)
                    elif curtype == 'float':
                        val = float(text)
                    else:
                        val = text

                    # save data array to current row data
                    data['currow'][curname] = val

                # save state for next char_data call
                data['prevtext'] = prevtext
                data['prevcol'] = data['col']


        ##################################################################
        # actual code for __init__

        # initialize values
        # which tables we want values from
        self.data['wanted_tables'] = tablenames

        # name of table currently parsing
        self.data['curtable'] = None
        self.data['params'] = {}

        # dictionary of tables 
        #   tables are arrays of row dict
        self.data['tables'] = {}
        self.data['in_TD'] = False   # whether in TD section or not

        p = xml.parsers.expat.ParserCreate()
        #p.buffer_size=32768
        p.buffer_size=2048

        # assign functions to handler
        p.StartElementHandler = start_element
        p.EndElementHandler = end_element
        p.CharacterDataHandler = char_data

        f = open(filename,"r")
        p.ParseFile(f)
        f.close()

        #
        # clean out our bookkeeping
        #
        del self.data['curtable'] 
        del self.data['wanted_tables'] 
        del self.data['in_TD']


    ##################################################################
    def gettables(self):
        return self.data['tables']

    #
    # we look like our data member...
    #
    def __getattr__(self,blah):
        return getattr(self.data['tables'], blah)




if __name__ == "__main__":
    tablelist = (
            "Astrometric_Instruments",
            "FGroups",
            "Fields",
            "Photometric_Instruments",
            "PSF_Extensions",
            "PSF_Fields",
            "Warnings")
    import sys
    import glob
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    if len(sys.argv) > 1:
        pp.pprint(Xmlslurper(sys.argv[1],tablelist).gettables())
    else:
        for f in glob.glob('*.xml'):
            print "f: ", f
            pp.pprint(Xmlslurper(f,tablelist).gettables())
