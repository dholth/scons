#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment()
env.Program(target = 'f1', source = 'f1.c')
env.Program(target = 'f2', source = 'f2.c')
env.Program(target = 'f3', source = 'f3.c')
env.Program(target = 'f4', source = 'f4.c')
""")

test.write('f1.c', """
int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    printf(\"f1.c\n\");
    exit (0);
}
""")

test.write('f2.c', """
int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    printf(\"f2.c\n\");
    exit (0);
}
""")


test.write('f3.c', """
int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    printf(\"f3.c\n\");
    exit (0);
}
""")

test.write('f4.c', """
int
main(int argc, char *argv[])
{
    argv[argc++] = "--";
    printf(\"f4.c\n\");
    exit (0);
}
""")


test.run(arguments = '-j 3 f1 f2 f3 f4')

test.run(program = test.workpath('f1'), stdout = "f1.c\n")

test.run(program = test.workpath('f2'), stdout = "f2.c\n")

test.run(program = test.workpath('f3'), stdout = "f3.c\n")

test.run(program = test.workpath('f4'), stdout = "f4.c\n")

test.pass_test()
