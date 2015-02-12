import os, sys, shutil

if "SGE_ROOT" not in os.environ:
    print "main(): Please set SGE_ROOT to the path of your SGE installation"
    print "main(): before scrambling DRMAA_python"
    sys.exit(1)

# change back to the build dir
if os.path.dirname( sys.argv[0] ) != "":
    os.chdir( os.path.dirname( sys.argv[0] ) )

# find setuptools
sys.path.insert( 1, os.path.join( '..', '..', '..', 'lib' ) )
from scramble_lib import *

tag = get_tag() # get the tag
clean() # clean up any existing stuff (could happen if you run scramble.py by hand)

# patch
file = "setup.py"
print "main(): Patching", file
if not os.access( "%s.orig" %file, os.F_OK ):
    shutil.copyfile( file, "%s.orig" %file )
i = open( "%s.orig" %file, "r" )
o = open( file, "w" )
for line in i.readlines():
    if line == 'SGE6_ROOT="/scratch_test02/SGE6"\n':
        line = 'SGE6_ROOT="%s"\n' % os.environ["SGE_ROOT"]
    if line.startswith('link_args ='):
        line = 'link_args = [ "-L%s" % os.path.join(SGE6_ROOT, "lib", SGE6_ARCH), "-ldrmaa"  ]\n'
    print >>o, line,
i.close()
o.close()

# build
me = sys.argv[0]
sys.argv = [ me ]
sys.argv.append( "build" )
execfile( "setup.py", globals(), locals() )

# fix _cDRMAA.so rpath
so = "build/lib.%s-%s/_cDRMAA.so" % ( pkg_resources.get_platform(), sys.version[:3] )
libdrmaa = os.path.join(SGE6_ROOT, "lib", SGE6_ARCH, "libdrmaa.dylib.1.0" )
os.system( "install_name_tool -change libdrmaa.dylib.1.0 %s %s" % ( libdrmaa, so ) )

# package
sys.argv = [ me ]
sys.argv.append( "bdist_egg" )
execfile( "setup.py", globals(), locals() )
