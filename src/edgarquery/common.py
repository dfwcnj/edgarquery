
import os
import sys
import urllib.request

class URLQuery():

    def __init__():
        pass

    def query(self, url, hdr):
        """query(url) - query a url

         url - url of file to retrieve
        """
        if not url:
            print('query: nothing to do', file=sys.stderr)
            sys.exit(0)
        try:
            req = urllib.request.Request(url, headers=hdr)
            resp = urllib.request.urlopen(req)
            return resp
        except urllib.error.URLError as e:
            print("Error %s(%s): %s" % ('query', url, e.reason),
            file=sys.stderr )
            sys.exit(1)

    def storequery(self, qresp, file):
        """storequery(qresp, file) - store the query response in a file

        resp - the query response
        file   - filename that will hold the query response
        """
        if not qresp: 
            print('storequery: no content', file=sys.stderr)
            sys.exit(1)
        if not file:
            print('storequery: no output filename', file=sys.stderr)
            sys.exit(1)
        of = os.path.abspath(file)
        # some downloads can be somewhat large
        with open(of, 'wb') as f:
            parts = iter(partial(qresp.read, self.chunksize), b'')
            for c in parts:
                f.write(c)
            #if c: f.write(c)
            f.flush()
            os.fsync(f.fileno() )
            return

