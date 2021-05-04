# for f in *.gz; do gzip -d $f; done
# for f in *; do mv $f $f.txt; done

import argparse
import os

import test_class
import mtr_line_parser

possibleTestStatuses = ['skipped', 'disabled', 'pass', 'fail', 'retry-fail', 'retry-pass', 'rerun-pass']
tests_skipped = 0
tests_disabled = 0
tests_pass = 0
tests_fail = 0
tests_retry_fail = 0
tests_retry_pass = 0
tests_rerun_pass = 0

testResultsList = []
rerunPassedTests = []

def valid(testStatus):
  # print 'TS: ' + testStatus
  if testStatus in possibleTestStatuses:
    return True
  return False

def accumulate(testStatus):
  global tests_skipped
  global tests_disabled
  global tests_pass
  global tests_fail
  global tests_retry_fail
  global tests_retry_pass
  global tests_rerun_pass

  if testStatus == 'skipped':
    tests_skipped += 1
  elif testStatus == 'disabled':
    tests_disabled += 1
  elif testStatus == 'fail':
    tests_fail += 1
  elif testStatus == 'pass':
    tests_pass += 1
  elif testStatus == 'retry-fail':
    tests_retry_fail += 1
  elif testStatus == 'retry-pass':
    tests_retry_pass += 1
  elif testStatus == 'rerun-pass':
    tests_rerun_pass += 1
  else:
    print "unknown test status: " + testStatus
    exit(1)

def failed(test):
  if test.testStatus == 'fail' or test.testStatus == 'retry-fail':
    return True
  return False

def printSummary():
  print 'skipped:        ' + str(tests_skipped)
  print 'disabled:       ' + str(tests_disabled)
  print 'pass:           ' + str(tests_pass)
  print 'fail:           ' + str(tests_fail)
  print 'retry-fail:     ' + str(tests_retry_fail)
  print 'retry-pass:     ' + str(tests_retry_pass)
  print 'rerun-pass:     ' + str(tests_rerun_pass)
  print '------------------------------------'
  OK = tests_pass + tests_retry_pass
  UNSTABLE = tests_retry_pass + tests_rerun_pass
  FAILED = tests_fail - tests_retry_pass - tests_rerun_pass
  TOTAL = OK + UNSTABLE + FAILED
  print 'OK:             ' + str(OK)
  print 'UNSTABLE (r-p): ' + str(UNSTABLE)
  print 'FAILED          ' + str(FAILED)
  print 'TOTAL:          ' + str(TOTAL)

def saveTest(test):
  for t in testResultsList:
    if t.testName == test.testName and t.binlogType == test.binlogType and t.testStatus == test.testStatus:
      t.platforms.extend(test.platforms)
      return

  testResultsList.append(test)

def dump(filename):
  with open(filename, 'w') as outfile:
    outfile.write("{};{};{};{};{};{}\n".format("Name", "Binlog", "Worker", "Status", "Platforms", "Comment"))
    for test in testResultsList:
      outfile.write("{};{};{};{};{};{}\n".format(test.testName, test.binlogType, test.worker, test.testStatus, test.platformsString(), test.testComment))

def dumpRetryFailed(filename):
  dumped = []
  with open(filename, 'w') as outfile:
    for test in testResultsList:
      if test.testStatus == 'retry-fail' and not test.testName in dumped:
        outfile.write("{}\n".format(test.testName))
        dumped.append(test.testName)


def applyRerunStatus(test):
  if test.testStatus == 'retry-fail':
    for t in rerunPassedTests:
      if test.testName == t.testName and test.binlogType == t.binlogType:
        test.testStatus = 'rerun-pass'
        return


def processFile(inFilename, dir):
  with open(dir + inFilename) as infile:
    platform = inFilename[:inFilename.find('.txt')]

    line = infile.readline()
    while line:
      testResult = mtr_line_parser.parseLine(line)

      if testResult != None and valid(testResult.testStatus):
        testResult.platforms.append(platform)
        applyRerunStatus(testResult)
        accumulate(testResult.testStatus)
        saveTest(testResult)

      line = infile.readline()

def processRerunFile(inFilename):
  print "processing rerun file: " + inFilename
  with open(inFilename) as infile:
    line = infile.readline()
    while line:
      testResult = mtr_line_parser.parseLine(line)
      if testResult != None and valid(testResult.testStatus) and testResult.testStatus == 'pass':
        rerunPassedTests.append(testResult)

      line = infile.readline()

  print "processing rerun file DONE. retry passed cnt: " + str(len(rerunPassedTests))


def main():
  parser = argparse.ArgumentParser(description='MTR report parser')
  parser.add_argument('-i', '--inDir', help='input directory', required=True)
  parser.add_argument('-r', '--rerunFile', help='rerun results file', required=False)
  args = parser.parse_args()

  rerunFilenamePart = ''

  if args.rerunFile != None :
      processRerunFile(args.rerunFile)
      rerunFilenamePart = '.with-rerun'

  for file in os.listdir(args.inDir):
    if file.endswith(".txt"):
      print ("Processing file: " + args.inDir + "/" + file)
      processFile(file, args.inDir + "/")

  dump(args.inDir + '.result' + rerunFilenamePart)
  dumpRetryFailed(args.inDir + '.retry-fail' + rerunFilenamePart)
  printSummary()

if __name__ == "__main__":
  main()


