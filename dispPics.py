
import os
import sys
import optparse
import sqlite3 as sqlite
from bottle import route, post, get, run, static_file, request, response
import json

picDB = 'test.db'

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
header = """<!DOCTYPE html>
      <html>
      <head>
      <title>%s</title>
      <meta name="ROBOTS" content="NOINDEX, NOFOLLOW">
      <meta http-equiv="content-type" content="text/html; charset=UTF-8">
      <meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8">
      <meta http-equiv="content-style-type" content="text/css">
      <meta http-equiv="expires" content="0">
      </head>
      """
footer = """
         </html>
         """


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def arg_parse():
   """
      parse the command line
      return options and arguments
   """
   parser = optparse.OptionParser()
   # parser.add_option('-l', action='store',dest='list', default=None, help='create list')
   #parser.add_option('-d', action='store',dest='dirt', default='.', help='head of directory tree')
   #parser.add_option('-i', action='store_true',dest='nocase', default=False, help='ignore case')
   # parser.add_option('-A', action='store_true',dest='almost', default=False, help='Almost all files and directories')
   #parser.add_option('-v', action='store_true',dest='verbose', default=False, help='verbose')
   (options,args) = parser.parse_args()

   return (options, args)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class dbConnect():
   """
      data base connect/disconnect etc
   """

   def __init__(self):
      self.con = None
      self.cur = None
      

   def mk_connect(self):
      """
      make connection to data base
      return cursor
      """
      #self.con = sqlite.connect('test.db')
      self.con = sqlite.connect('ourPictures.db')
      self.cur = self.con.cursor()
      return self.cur

   def close_connect(self):
      """
      close connection to data base
      """
      self.con.close()


def fetch_row(tid,table):
   """
   """
   query = 'SELECT * FROM %s WHERE id = %s;' % (table,tid)
   myconn = dbConnect()
   myconn.mk_connect()
   myconn.cur.execute(query)
   row = myconn.cur.fetchone()
   myconn.close_connect()
   
   return row

def fetch_allRows(table):
   """
   """
   query = 'SELECT * FROM %s;' % table
   myconn = dbConnect()
   myconn.mk_connect()
   myconn.cur.execute(query)
   rows = myconn.cur.fetchall()
   myconn.close_connect()
   
   return rows


def fetch_listRows(tid_lst,table):
   """
   """
   ts = []
   for tid in tid_lst:
      if len(ts) != 0:
         ts += ','
      ts += tid

   query = 'SELECT * FROM %s WHERE id IN (%s);' % (table,tid_lst)
   myconn = dbConnect()
   myconn.mk_connect()
   myconn.cur.execute(query)
   row = myconn.cur.fetchall()
   myconn.close_connect()
   
   return row

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@route('/Linda')
@route('/Linda/<page>')
@route('/Linda/<page>/<pic>')
def LindasStuff(page=None,pic='0'):
   """
   """
   if not page:
      return gen_LindaTop()
   else:
      #plst = page_stuff[page]
      curr =request.GET.get('c', '')
      if curr:
         ipic = int(curr)
      else:
         ipic = 0

      if pic == 'next':
         ipic += 1
      elif pic == 'prev':
         ipic -= 1
      elif pic == 'index':
         return gen_lindaPicIndex(page,ipic)
      elif pic.isdigit():
         ipic = int(pic)
      elif pic.startswith('-'):
         ipic = int(pic)

      return gen_LindaPic(page,ipic)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def gen_LindaTop():
   """
   """

   rows = fetch_allRows('list')

   lineOut = header % ("Linda's Pics")
   lineOut += '<body>'
   for row in rows:
      lineOut += '<a href="/Linda/%s">%s</a> ' % (row[0],row[1])
      lineOut += '<a href="/Linda/%s/index">(index)' % (row[0])
      lineOut += '<br>'

   lineOut += '</body>'
   lineOut += footer

   return lineOut

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def gen_LindaPic(tid=None,ndx=0):
   """
   """
   row = fetch_row(tid,'list')
   lst = json.loads(row[4])
   pic = lst[ndx]
   ndxList = gen_ndxList(ndx-2,lst,5)
   ndxList.pop(2)

   lineOut = header % ("Linda's Pics")
   lineOut += '<body>'
   lineOut += '<a href="/Linda/%s/prev?c=%d">prev</a> ' % (tid,ndx)
   lineOut += '<a href="/Linda/%s/next?c=%d">next</a> ' % (tid,ndx)
   lineOut += '<br>'
   lineOut += '<table width="920">'
   url = '/Linda/%s' % tid
   img = '/lndaThumb' 
   lineOut += gen_lindaPicRow(url, img, ndxList)
   lineOut += '</table>'
   lineOut += '<br>'

   # generate the pic/img statement
   lineOut += '<img src="/lndaPic/%d" ' % (pic)
   lineOut += 'width="90%"/>'
   lineOut += '<br>'
   #lineOut += gen_lindaTable(tid,ndx)
   lineOut += '<br>'

   lineOut += '</body>'
   lineOut += footer

   return lineOut

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def gen_lindaPicIndex(tid=None, ndx=0):
   """
   """

   form = False
   row = fetch_row(tid,'list')
   lst = json.loads(row[4])
   url = '/Linda/%s' % tid
   img = '/lndaThumb'

   lineOut = header % "Linda's Pics Index"
   lineOut += '<br>'
   lineOut += '<a href="/Linda/%s/index?c=%d">prev</a> ' % (tid,(ndx-20))
   lineOut += '<a href="/Linda/%s/index?c=%d">next</a> ' % (tid,(ndx+20))
   lineOut += '<br>'
   if form:
      lineOut += '<form method="post" action="/Linda/saveLst">'
   lineOut += '<table width="920">'
   for i in xrange(ndx,ndx+20,4):
      ndxList = gen_ndxList(i,lst,4)
      lineOut += '<tr>'
      lineOut += gen_lindaPicRow(url, img, ndxList, form=form)
      lineOut += '</tr>'
   lineOut += '</table>'
   if form:
      lineOut += '<button name="rst" type="reset">reset</button>'
      lineOut += '<button name="submit" type="submit">submit</button>'
   lineOut += '<br>'
   lineOut += footer
   return lineOut

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def gen_lindaPicRow(url, img, ndxList, form=False):
   """
   """
   lineOut = '<tr>'
   for i in ndxList:
      lineOut += '<td width="230">'
      lineOut += '<a href="%s/%s"><img src="%s/%s" ' % (url,i[0],img,i[1])
      lineOut += 'width = "60%"> </a>'
      if form:
         lineOut += '<input type="checkbox" name="thisOne" value="%s" />' % i[0]
      lineOut += '</td>'
   lineOut += '</tr>'
   return lineOut


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def gen_ndxList(ndx,lst,num):
   """
   """
   ndxList = []
   for i in xrange(ndx, ndx+num):
      i1 = i % len(lst)
      t1 = lst[i1]
      ndxList.append((i1,t1))
      i += 1

   return ndxList

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@route('/lndaPic/<pic>')
def show_lndPic(pic='0'):
   """
   """
   ndx = int(pic)
   row = fetch_row(ndx,'pictures')
   p0 = row[1].strip()
   p1 = row[2].strip()
   #return 'file: %s ::: path: %s' % (p1, p0)
   return static_file(p0, root=p1)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@route('/lndaThumb/<pic>')
def show_lndPic(pic='0'):
   """
   """
   ndx = int(pic)
   row = fetch_row(ndx,'pictures')
   p0a,p1a = os.path.split(row[5])
   p0 = p0a.strip()
   p1 = p1a.strip()
   #return 'file: %s ::: path: %s' % (p1, p0)
   return static_file(p1, root=p0)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def dispPics(args,option):
   """
   """
   
   myUname = os.uname()
   if myUname[1] =='Ruth':
      run(host='192.168.1.63', port=8000, debug=True)
   elif myUname[1] =='Tina':
      run( host='192.168.1.17', port=8000, debug=True)
   else:
      run(host='localhost', port=8000, debug=True)
   #run(host='192.168.1.17', port=8001, debug=True)
   #run(host='192.168.1.17', port=8000, debug=True)


if __name__ == '__main__':
   option, args = arg_parse()

   dispPics(args,option)


