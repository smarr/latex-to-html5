#!/usr/bin/python
import os
import subprocess
import sys

DEV_NULL = open(os.devnull, 'w')

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

def check_delta_available():
    """Delta is a nice tool for nicer diffs"""
    try:
        ret_code = subprocess.call(['delta', '--version'], stdout=DEV_NULL)
        return ret_code == 0
    except:
        return False


HAS_DELTA = check_delta_available()


def cleanup_directory(d):
    subprocess.call(['rm', '-f', 'test.aux', 'test.css', 'test.fls', 'test.lg',
                           'test.4ct', 'test.bbl', 'test.dvi', 'test.html',
                           'test.log', 'test.tmp', 'test.4tc', 'test.blg',
                           'test.fdb_latexmk', 'test.idv', 'test.pdf',
                           'test.xref', 'test-final.html', 'test-tidy.html',
                           '.test.lb'])


def exec_test(d):
    try:
        os.chdir(d)
    except FileNotFoundError as e:
        print(d, 'does not seem to exist')
        return False
    try:
        subprocess.check_output([BASE_DIR + '/ht-latex', 'test.tex', '.'], stderr=subprocess.STDOUT)
        try:
            if HAS_DELTA:
                diff_cmd = ['delta', '--syntax-theme', 'Solarized (light)']
            else:
                diff_cmd = ['diff']

            subprocess.check_output(diff_cmd + ['expected.html', 'test-final.html'])
        except subprocess.CalledProcessError as e:
            print(d, 'FAILED')
            print("Diff between expected and actual HTML:")
            print(e.output.decode('utf-8'))
            return False

        cleanup_directory(d)
        return True
    except subprocess.CalledProcessError as e:
        print(d, 'FAILED')
        print("Latex Output:")
        print(e.output.decode('utf-8'))
        return False


def exec_tests():
    all_pass = True

    for f in sorted(os.listdir('tests')):
        os.chdir(BASE_DIR)
        if os.path.isdir('tests/' + f):
            print("-------", f)
            if not exec_test('tests/' + f):
                all_pass = False
    return all_pass


if len(sys.argv) > 1:
    result = exec_test(sys.argv[1])
else:
    result = exec_tests()

if result:
    sys.exit(0)
else:
    sys.exit(1)
