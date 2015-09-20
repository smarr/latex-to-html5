#!/usr/bin/python
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def cleanup_directory(d):
    subprocess.call(['rm', '-f', 'test.aux', 'test.css', 'test.fls', 'test.lg',
                           'test.4ct', 'test.bbl', 'test.dvi', 'test.html',
                           'test.log', 'test.tmp', 'test.4tc', 'test.blg',
                           'test.fdb_latexmk', 'test.idv', 'test.pdf',
                           'test.xref', 'test-final.html', 'test-tidy.html',
                           '.test.lb'])


def exec_test(d):
    os.chdir(d)
    try:
        subprocess.check_output([BASE_DIR + '/ht-latex', 'test.tex', '.'])
        try:
            subprocess.check_output(['diff', 'expected.html', 'test-final.html'])
        except subprocess.CalledProcessError as e:
            print d, 'FAILED'
            print "Diff between expected and actual HTML:"
            print e.output
            return False

        cleanup_directory(d)
        return True
    except subprocess.CalledProcessError as e:
        print d, 'FAILED'
        print "Latex Output:"
        print e.output
        return False


def exec_tests():
    failed = False
  
    for f in os.listdir('tests'):
        os.chdir(BASE_DIR)
        print "-------", f
        if os.path.isdir('tests/' + f):
            if not exec_test('tests/' + f):
                failed = True
    return failed


if len(sys.argv) > 1:
    result = exec_test(sys.argv[1])
else:
    result = exec_tests()

if result:
    sys.exit(0)
else:
    sys.exit(1)
