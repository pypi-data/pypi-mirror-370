# Running Korona through Python

## Prerequisites

### Install LSSS/Korona.

This version of the KoronaScript is tested against lsss-2.16.0-alpha
version. LSSS and korona is usually placed at
`~/lsss/lsss-2.16.0-alpha` or a similar directory.

Download the appropriate version from here:

https://marec.no/tmp/lsss-2.16.0-alpha-20230922-1417-linux.zip

https://marec.no/tmp/lsss-2.18.0-alpha-20240918-0847-linux.zip

https://marec.no/tmp/lsss-2.16.0-alpha-20230922-1417-windows.zip

https://marec.no/tmp/lsss-2.18.0-alpha-20240918-0847-windows.zip

If you run linux you need to install the netcdf separately:

`apt-get install libnetcdf` or `sudo apt install libnetcdf-dev`


### Add license 

You need an LSSS licence. The licence have to be added according to the LSSS manual. the licence files are typically placed at the `~/marec/license` directory.

### Set system variables

The `LSSS` environment variable should point to the root directory of your
LSSS installation.  It can be set at run time either by setting the LSSS environment
variable in the shell
~~~
export LSSS=~/lsss-2.16.0-alpha
~~~
before running your script, or by adding it manually from inside Python:
~~~
lsss = '~/lsss-2.16.0-alpha'
os.environ["LSSS"] = lsss
~~~

# Usage

Import the modules:

	import KoronaScript as ks
	import KoronaScript.Modules as ksm

Create a script object:

	ks = ks.KoronaScript(Categorization='categorization.xml',
                     HorizontalTransducerOffsets='HorizontalTransducerOffsets.xml')

Add some modules:

	ks.add(ksm.EmptyPingRemoval())
	ks.add(ksm.Comment(LineBreak='false', Label='CW_0256ms'))
	ks.add(ksm.ChannelRemoval(Channels=[1,5,9,13,17],KeepSpecified='true'))
	ks.add(ksm.Writer(RelativeDirectory='CW_0256ms'))

Write out the resulting configuration:

	ks.write()
	
Run the script:

	ks.run(src="input_dir", dst="output_dir")

The list of modules and their parameters can be found in the
[configuration/korona-info.json](configuration/korona-info.json) file. 
