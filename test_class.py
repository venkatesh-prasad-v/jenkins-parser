class Test:
  def __init__(self, testName, binlogType, worker, testStatus, testComment, platform):
    self.testName = testName
    self.binlogType = binlogType
    self.worker = worker
    self.testStatus = testStatus
    self.testComment = testComment
    self.platforms = []

  def platformsString(self):
    str = ''
    self.platforms.sort()
    for p in self.platforms:
      str = str + p + ", "
    if str.endswith(', '):
      str = str[: -2]

    return str