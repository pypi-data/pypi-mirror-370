# Class to represent and run a sequence of Korona moduleapplications
# Example usage:
#    ks = KoronaScript(global parameters)
#    ks.add(KoronaModule(parametres)
#    ks.add...
#    ks.write(path)
#    ks.run()

import subprocess
import tempfile
import os
import sys

from .KoronaModule import global_spec

lsss = os.getenv('LSSS')
if lsss is None:
    print('KoronaScript: Warning: $LSSS is not set.')

class KoronaScript():
    '''Construct, store, and run a set of Korona modules'''

    def __init__(self, **parameters):  # global parameters
        self._module_list = []
        self._config = global_spec
        for k in parameters:
            if k not in global_spec:
                print(f'Unknown global parameter "{k}" - aborting')
                exit(-1)
            self._config[k] = parameters[k]

    def add(self, module):
        '''Add a module to the script'''
        self._module_list.append(module)
        return self

    def write(self, cfs=sys.stdout, cds=sys.stdout, cdsname=None):
        '''Write the cds and cfs files'''
        cfs.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
        cfs.write('<ConfigFiles context="Korona">\n')
        cfs.write(f'    <parameter name="ModuleConfiguration" ref="CfsDirectory">{cdsname}</parameter>\n')
        for k, v in self._config.items():
            if v is None:
                cfs.write(f'    <parameter name="{k}"/>\n')
            else:
                cfs.write(f'    <parameter name="{k}">{v}</parameter>\n')
        cfs.write('</ConfigFiles>\n')

        cds.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
        cds.write('<ModuleContainer version="3">\n')
        cds.write('  <modules>\n')
        for m in self._module_list:
            cds.write(m.to_xml())
        cds.write('  </modules>\n')
        cds.write('</ModuleContainer>\n')

    def run(self, src, dst, debug=False):
        '''Save the files (to /tmp?) and call Korona to execute them'''
        cfs, cfsname = tempfile.mkstemp(suffix='.cfs')
        cds, cdsname = tempfile.mkstemp(suffix='.cds')
        with os.fdopen(cds, 'w') as cdsfd:
            with os.fdopen(cfs, 'w') as cfsfd:
                self.write(cfs=cfsfd, cds=cdsfd, cdsname=cdsname)

        # if os.getenv('JAVA_HOME'): (...)
        if lsss is None:
            print('KoronaScript: Error: LSSS environment variable not specified')
            exit(-1)
        os.environ['TOP_INSTALLATION_DIR'] = lsss

        java = os.path.join(*[lsss, 'jre', 'bin', 'java'])

        # "-Xmx${MAX_MEMORY_MB}m" -classpath "t$TOP_INSTALLATION_DIR/lib/jar/*" "-Djava.library.path=$JAVA_LIBRARY_PATH" "-Djna.library.path=$JAVA_LIBRARY_PATH" -XX:-UseGCOverheadLimit -XX:-OmitStackTraceInFastThrow -Dno.marec.incubator=true no.imr.korona.main.KoronaCliMain "$@"
        javaopts = ['-classpath', os.path.join(*[lsss, "lib", "jar", "*"]), '-Dno.marec.incubator=true']
        libpath = os.path.join(*[lsss, 'lib', 'native', 'win64'])
        if os.path.exists(libpath):
            for v in ['java.library.path', 'jna.library.path']:
                javaopts.append(f'-D{v}={libpath}')

        cmd = [java] + javaopts + ['no.imr.korona.main.KoronaCliMain', 'batch', '--cfs', cfsname, '--source', src, '--destination', dst]
        if debug: print('Running:\n  ', cmd)
        res = subprocess.run(cmd, capture_output=True, text=True)
        if debug: print(res.stdout)
        if res.returncode != 0:
            err_str = f'Korona subprocess returned an error code: {res.returncode}\n' + '----------------------------------------\n' + res.stderr
            raise Exception(err_str)
        return res.returncode
