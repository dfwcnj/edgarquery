
import os
import sys
import webbrowser


class _AA2HTML():
    def __init__(self):
        self.htmla = []

    def aa2table(self, aa):
       """ aa2table(aa)

       convert array of arrays to an html table
       aa - array of arrays
       """
       tbla = []
       # table
       tbla.append('<table border="1">')

       # table header
       hdra = aa[0]
       hdr = '</th><th>'.join(hdra)
       tbla.append('<tr><th>%s</th></tr>' % (hdr) )

       # table rows
       for i in range(1, len(aa) ):
           rowa = aa[i]
           row = '</td><td>'.join(rowa)
           tbla.append('<tr><td>%s</td></tr>' % (row) )

       # close
       tbla.append('</table>')
       return ''.join(tbla)

    def str2html(self, str, name):
       """ str2html(str, name)

       wrap html boilerplate around a string that must be proper html
       str - string containing html data
       name - name of the content
       """
       self.htmla.append('<html>')

       if name:
           self.htmla.append('<title>%s</title>' % (name) )
           self.htmla.append('<h1 style="text-align:center">%s</h1>' % (name) )

       self.htmla.append(str)
       self.htmla.append('</html>')
       return ''.join(self.htmla)

    def aa2html(self, aa, name):
       """ aa2html(aa, name)

       return html of array of arrays
       aa - python array of arrays  with keys in array[0]
       name - html title
       """
       self.htmla.append('<html>')

       if name:
           self.htmla.append('<title>%s</title>' % (name) )
           self.htmla.append('<h1 style="text-align:center">%s</h1>' % (name) )

       self.htmla.append(self.aa2table(aa) )
       self.htmla.append('</html>')
       return ''.join(self.htmla)

    def aashow(self, aa, name):
       """ aashow(as, name)

       generate html from dictionary with dict2html() and save it
       to a file named name.html
       fdict - python dictionary with only key:value pairs
       name - name of html file
       """
       html = self.aa2html(aa, name)
       fn = name
       if len(name.split()) != 1:
           fn = ''.join(name.split() )
       fpath = '%s.html' % os.path.join('/tmp', fn)
       with open(fpath, 'w') as fp:
           fp.write(html)
       webbrowser.open('file://%s' % (fpath) )

