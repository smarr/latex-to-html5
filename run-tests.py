#!/usr/bin/python
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

def exec_test(d):
  os.chdir(d)
  subprocess.call([BASE_DIR + '/ht-latex', 'test.tex', '.'])
  subprocess.call(['diff', 'expected.html', 'test-final.html'])


def exec_tests():
  os.chdir(BASE_DIR)
  
  for f in os.listdir('tests'):
    if os.path.isdir('tests/' + f):
      exec_test('tests/' + f)

if len(sys.argv) > 1:
  exec_test(sys.argv[1])
else:
  exec_tests()
  
