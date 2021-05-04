import re
import os
import test_class


# line looks like one of following:
# [ 10%] tokudb_bugs.checkpoint_lock_2             [ disabled ]   BUG#0 test can not work when the
# [  0%] binlog_gtid.binlog_gtid_cache 'mix'       [ skipped ]  Doesn't support --binlog-format = 'mixed'         
# [  1%] binlog_gtid.binlog_gtid_utils 'row'      w1  [ pass ]   1181
# [ 42%] main.flush2                              w4  [ pass ]    155
def parseLine(line):
    leadingPercent = True
    # print (line)
    l = re.search("^\[.*\%\]", line)

    if l == None:
        # OK, maybe this is log from Jenkins...
        l = re.search("^.+\[.*\%\]", line)

    if(l == None):
        # probably 5.6, no leading [ n% ]
        leadingPercent = False
        l = re.search("^.+\..+ \[ .* \]", line)
        if(l == None):
        # ok, we are not interested with this line
            # print ("continue")
            # line = infile.readline()
            return None

    #print '######################'
    #print 'FULL LINE:' + line

    # test name start
    tokenStart = 0
    if (leadingPercent):
        tokenStart = line.find(']') + int(1)

    line = line[tokenStart:]
    line = line.strip()
    #print 'LINE TEST NAME:' + line
    tokenEnd = line.find(' ')
    testName = line[:tokenEnd]

    # binlog, worker or status
    binlogType = ''
    worker = ''
    testStatus = ''

    line = line[tokenEnd:]
    tokenStart = re.search('\S', line)
    line = line[tokenStart.span()[0]:]
    #print 'BWR LINE:' + line
    tokenEnd = line.find(' ')

    if (line[0] == "'"):
        #print 'LINE BINLOG TYPE:' + line
        tokenEnd = line.find(" ")
        binlogType = line[:tokenEnd]
        #print 'binlogType:' + binlogType
        line = line[tokenEnd:]
        tokenStart = re.search('\S', line)
        line = line[tokenStart.span()[0]:]
        #print 'BWR LINE:' + line
        tokenEnd = line.find(' ')

    if (line[0] == "w"):
        #print 'LINE WORKER:' + line
        tokenEnd = line.find(' ')
        worker = line[:tokenEnd]
        #print 'worker:' + worker
        line = line[tokenEnd:]
        tokenStart = re.search('\S', line)
        line = line[tokenStart.span()[0]:]
        #print 'BWR LINE:' + line
        tokenEnd = line.find(' ')

    if (line[0] == "["):
        #print print 'LINE STATUS:' + line
        tokenEnd = line.find(']') + int(1)
        testStatus = line[1:tokenEnd-int(1)].strip()
        # print 'testStatus:' + testStatus
        line = line[tokenEnd:]
        tokenStart = re.search('\S', line)
        if (tokenStart != None):
            line = line[tokenStart.span()[0]:]

        # print 'BWR LINE:' + line
        tokenEnd = line.find(' ')

    # the last token is comment
    line = line[tokenEnd:]
    #print 'LINE COMMENT:' + line
    testComment = line

    return test_class.Test(testName, binlogType, worker, testStatus, testComment, '')