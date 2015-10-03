
import shelve


def header_normalise(message):
  'Normalise the header part of a message'
  result = []
  heading = ''
  for line in message:
    tidy = line.strip()
    if tidy == '': # End of the header
      break # End of header
#    print(type(line[0]))
    if str(line[0]) in ' \t': # If begins with whitespace
      heading = heading + ' ' + tidy # Append to the current header
    else: # New heading
      result.append(heading) # Append this heading to the result list
      heading = tidy # Start new heading line
  result.append(heading)
  res = []
  for line in result[1:]:
#    print(' about to split', repr(line))
    key, value = line.split(':', 1)
    res.append((key.lower(), value.strip()))
  return res

def summary_make(header):
  'Make a summary object from a message'
  summ = {}
  interesting = ('from', 'subject', 'date', 'lines', 'references',
     'message-id')
  for line in header_normalise(header):
#    print('Header  %26s: %r' % line)
    if line[0] in interesting:
      summ[line[0]] = line[1]
#      print(' set summ.%s to %s' % (line[0], summ[line[0]]))
  return summ

class Usenetclient:

  def dbnew(self):
    self.messages = {}
    self.heads = {}

  def dbdump(self, db):
    store = shelve.open(db)
    try:
      ver = store['activever']
    except KeyError:
      print 'No version number stored in database'
      return
    print 'Active version:', ver

    print 'Heads'
    vals = store['heads.' + str(ver)]
    for val in vals:
      print ' %s: %s' % (val, vals[val])

    print 'Messages'
    vals = store['messages.' + str(ver)]
    for val in vals:
      print ' %s: %s' % (val, vals[val])

    store.close()

  def state_load(self, db):
    if db == '':
      self.dbnew()
    else:
      store = shelve.open(db)
      ver = store['activever']
      self.messages = store['messages.' + str(ver)]
      self.heads = store['heads.' + str(ver)]
      store.close()

  def state_save(self, db):
    store = shelve.open(db)
    try:
      ver = store['activever']
    except KeyError:
      ver = 0
    else:
      if ver != 0:
        ver = 0
      else:
        ver = 1
    store['messages.' + str(ver)] = self.messages
    store['heads.' + str(ver)] = self.heads
    store.close()
    store = shelve.open(db)
    store['activever'] = ver
    store.close()

  def message_add(self, msource):
    msg_list = [line for line in msource]
    summ = summary_make(msg_list)
    mid = summ['message-id']
    self.heads[mid] = summ
    self.messages[mid] = msg_list


if __name__ == '__main__':
  dbfilename = 'shelv.db'
  uc = Usenetclient()
  uc.state_load('')
  uc.message_add(open('initial.txt'))
  uc.message_add(open('reply1.txt'))
  uc.state_save(dbfilename)

  uc.dbdump(dbfilename)

#  init = summary_make(open('initial.txt', 'rb'))
#  print 'Returned:', init
#  print
#  repl = summary_make(open('reply1.txt', 'rb'))
#  print 'Returned:', repl

#  shelf = shelve.open('shelv.db')
#  shelf['activever'] = 0
#  shelf['head1'] = (init, repl)
#  shelf.close()

#  sh = shelve.open('shelv.db')
#  for key in sh:
#    pass #    print key, sh[key]
#  sh.close()


