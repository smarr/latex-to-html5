#!/usr/bin/python
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

def exec_test(d):
  os.chdir(d)
  if subprocess.call([BASE_DIR + '/ht-latex', 'test.tex', '.']) == 0:
    if subprocess.call(['diff', 'expected.html', 'test-final.html']) == 0:
      return True
  
  print d, 'FAILED'
  return False


def exec_tests():
  os.chdir(BASE_DIR)
  
  failed = False
  
  for f in os.listdir('tests'):
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
