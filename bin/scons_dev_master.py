#!/bin/sh
#

# A script for turning a generic Ubuntu system into a master for
# SCons development.
from __future__ import print_function
from builtins import str

import getopt
import sys

from Command import CommandRunner, Usage

INITIAL_PACKAGES = [
    'mercurial',
]

INSTALL_PACKAGES = [
    'wget',
]

PYTHON_PACKAGES = [
    'g++',
    'gcc',
    'make',
    'zlib1g-dev',
]

BUILDING_PACKAGES = [
    'python-libxml2',
    'python-libxslt1',
    'fop',
    'python-dev',
    'python-epydoc',
    'rpm',
    'tar',
    
    # additional packages that Bill Deegan's web page suggests
    #'docbook-to-man',
    #'docbook-xsl',
    #'docbook2x',
    #'tetex-bin',
    #'tetex-latex',

    # for ubuntu 9.10 
    # 'texlive-lang-french'

]

DOCUMENTATION_PACKAGES = [
    'docbook-doc',
    'epydoc-doc',
    'gcc-doc',
    'pkg-config',
    'python-doc',
    'sun-java5-doc',
    'sun-java6-doc',
    'swig-doc',
    'texlive-doc',
]

TESTING_PACKAGES = [
    'bison',
    'cssc',
    'cvs',
    'flex',
    'g++',
    'gcc',
    'gcj',
    'ghostscript',
#    'libgcj7-dev',
    'm4',
    'openssh-client',
    'openssh-server',
    'python-profiler',
    'python-all-dev',
    'rcs',
    'rpm',
#    'sun-java5-jdk',
    'sun-java6-jdk',
    'swig',
    'texlive-base-bin',
    'texlive-extra-utils',
    'texlive-latex-base',
    'texlive-latex-extra',
    'zip',
]

BUILDBOT_PACKAGES = [
    'buildbot',
    'cron',
]

default_args = [
    'upgrade',
    'checkout',
    'building',
    'testing',
    'python-versions',
    'scons-versions',
]

def main(argv=None):
    if argv is None:
        argv = sys.argv

    short_options = 'hnqy'
    long_options = ['help', 'no-exec', 'password=', 'quiet', 'username=',
                    'yes', 'assume-yes']

    helpstr = """\
Usage:  scons_dev_master.py [-hnqy] [--password PASSWORD] [--username USER]
                            [ACTIONS ...]

    ACTIONS (in default order):
        upgrade                 Upgrade the system
        checkout                Check out SCons
        building                Install packages for building SCons
        testing                 Install packages for testing SCons
        scons-versions          Install versions of SCons
        python-versions         Install versions of Python

    ACTIONS (optional):
        buildbot                Install packages for running BuildBot
"""

    scons_url = 'https://bdbaddog@bitbucket.org/scons/scons'
    sudo = 'sudo'
    password = '""'
    username = 'guest'
    yesflag = ''

    try:
        try:
            opts, args = getopt.getopt(argv[1:], short_options, long_options)
        except getopt.error as msg:
            raise Usage(msg)

        for o, a in opts:
            if o in ('-h', '--help'):
                print(helpstr)
                sys.exit(0)
            elif o in ('-n', '--no-exec'):
                CommandRunner.execute = CommandRunner.do_not_execute
            elif o in ('--password'):
                password = a
            elif o in ('-q', '--quiet'):
                CommandRunner.display = CommandRunner.do_not_display
            elif o in ('--username'):
                username = a
            elif o in ('-y', '--yes', '--assume-yes'):
                yesflag = o
    except Usage as err:
        sys.stderr.write(str(err.msg) + '\n')
        sys.stderr.write('use -h to get help\n')
        return 2

    if not args:
        args = default_args

    initial_packages = ' '.join(INITIAL_PACKAGES)
    install_packages = ' '.join(INSTALL_PACKAGES)
    building_packages = ' '.join(BUILDING_PACKAGES)
    testing_packages = ' '.join(TESTING_PACKAGES)
    buildbot_packages = ' '.join(BUILDBOT_PACKAGES)
    python_packages = ' '.join(PYTHON_PACKAGES)

    cmd = CommandRunner(locals())

    for arg in args:
        if arg == 'upgrade':
            cmd.run('%(sudo)s apt-get %(yesflag)s upgrade')
        elif arg == 'checkout':
            cmd.run('%(sudo)s apt-get %(yesflag)s install %(initial_packages)s')
            cmd.run('hg clone" %(scons_url)s')
        elif arg == 'building':
            cmd.run('%(sudo)s apt-get %(yesflag)s install %(building_packages)s')
        elif arg == 'testing':
            cmd.run('%(sudo)s apt-get %(yesflag)s install %(testing_packages)s')
        elif arg == 'buildbot':
            cmd.run('%(sudo)s apt-get %(yesflag)s install %(buildbot_packages)s')
        elif arg == 'python-versions':
            if install_packages:
                cmd.run('%(sudo)s apt-get %(yesflag)s install %(install_packages)s')
                install_packages = None
            cmd.run('%(sudo)s apt-get %(yesflag)s install %(python_packages)s')
            try:
                import install_python
            except ImportError:
                msg = 'Could not import install_python; skipping python-versions.\n'
                sys.stderr.write(msg)
            else:
                install_python.main(['install_python.py', '-a'])
        elif arg == 'scons-versions':
            if install_packages:
                cmd.run('%(sudo)s apt-get %(yesflag)s install %(install_packages)s')
                install_packages = None
            try:
                import install_scons
            except ImportError:
                msg = 'Could not import install_scons; skipping scons-versions.\n'
                sys.stderr.write(msg)
            else:
                install_scons.main(['install_scons.py', '-a'])
        else:
            msg = '%s:  unknown argument %s\n'
            sys.stderr.write(msg % (argv[0], repr(arg)))
            sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
