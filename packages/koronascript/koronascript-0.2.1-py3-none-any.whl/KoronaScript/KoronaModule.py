from .Configuration import modules_spec

global_spec = {
    # 'ModuleConfiguration' : None, # cds file name, attrib 'ref' points to...what?
    #   <parameter name="ModuleConfiguration" ref="CfsDirectory">CW.cds</parameter>
    # The following are None, or point to xml files (contents unknown)
    'Categorization' : None,
    'HorizontalTransducerOffsets' : None,
    'VerticalTransducerOffsets' : None,
    'TransducerRanges' : None,
    'Plankton' : None,
    'BroadbandNotchFilters' : None,
    'PulseCompressionFilters' : None,
    'BroadbandSplitterBands' : None,
    'Towfish' : None,
}

class KoronaModule():
    '''Baseclass for modules'''

    def __init__(self, name, **parameters):
        '''initialize with parameter definitions'''
        # check that the module exists
        if name not in modules_spec:
            print(f'Unknown Korona module "{name}" - aborting')
            exit(-1)
        self._name = name
        self._config = {}
        # Add defaults
        for k, v in modules_spec[name].items():
            self._config[k] = v

        for k in parameters:
            if k != 'Active' and k not in modules_spec[name]:
                print(f'Parameter "{k}" not valid for Korona module "{name}" - aborting')
                exit(-1)
            self._config[k] = parameters[k]

    def to_xml(self):
        '''Generate XML output'''
        res = ''
        myname = self._name + 'Module'
        res += (f'  <module name="{myname}">\n')
        res += ('    <parameters>\n')
        for k in self._config:
            if self._config[k] is None:
                res += f'      <parameter name="{k}"/>\n'
            elif isinstance(self._config[k], list):
                res += f'      <parameter name="{k}">'
                for v in self._config[k]:
                    res += str(v) + ','
                res = res[:-1]  # remove last comma
                res += '</parameter>\n'
            elif isinstance(self._config[k], dict):
                res += f'      <parameter name="{k}">\n'
                # Should maybe call recursively?  Can they be lists or dicts?
                for key, val in self._config[k].items():
                    res += f'       <parameter name="{key}">{val}</parameter>\n'
                res += '      </parameter>\n'
            else:
                res += (f'      <parameter name="{k}">{self._config[k]}</parameter>\n')
        res += ('    </parameters>\n')
        res += ('  </module>\n')
        return res
