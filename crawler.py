from __future__ import print_function
import urlparse
import urllib2, lister, sgmllib
import re


#Lists needed
visited = []
external = []
internal = []
four04 = []
#base = "http://www.ethanholmes.me/"
#core = "www.ethanholmes.me"
base = "http://www.cs.sfu.ca/"
#base = "http://www.cs.sfu.ca/~stella/"
core = "cs.sfu.ca"
types = {}

#TODO:
#Use 1 dictionary of lists rather than N lists.

def read_page(url):
    """Reads a page"""
    try:
        try:
            usock = urllib2.urlopen(url)
        except urllib2.HTTPError as e:
            four04.append(url)
            return
        except urllib2.URLError as e:
            four04.append(url)
            return


        filetype = usock.info().getheader('content-type')
        f = open("log.txt", 'a')
        print (usock.getcode(), " : ", url, " : ", filetype, file=f)
        f.close()
        parser = lister.Lister()
    
        if 'text/html' in filetype:
            parser.feed(usock.read())
        
        if filetype not in types: types[filetype] = []

        types[filetype].append(url)
        visited.append(url)
        usock.close()
        parser.close()

        return parser

    except sgmllib.SGMLParseError:
        t = open("invalids.txt", 'ab+')
        print(url, file=t)
        t.close()
        four04.append(url)
        return

def local_url(url):
    """ """
    cond = [(url.count('.') == 1) and url[0] == '/'] #Full URL's have at least 2
    cond.append(url[0] == '/' and url.count('.') == 0) #Filters out http links and javascript
    return True in cond

def local_full_url(url):
    """ """
    cond = [core in url] #Check if the full core of the url (cs.sfu.ca) is in the url
    return cond.count(False) == 0

def strip_url(u):
    """ """
    #temp_url = urlparse.urlparse(u)
    #fixed_url = urlparse.unparse()
    temp_url = u.split('#', 1)[0]
    temp_url = temp_url.split('?', 1)[0]
    if len(temp_url) > 3 and temp_url[0] == 'w' and temp_url[1] == 'w' and temp_url[2] == 'w':
        temp_url = "http://" + temp_url
    return temp_url
    
def filter_urls(p):
    """Place the urls into the appropriate list
    Some URL's are written /stuff
    Other are written completely starting with http://"""
    if p is None: return

    for url in p.urls:
        print("URL", url)
        f_url = strip_url(url)
        #f_url = urlparse.urlparse(url)
        print("fURL", f_url)
        if f_url:
            if local_url(f_url):
                internal.append(base+f_url[1:])
            elif local_full_url(f_url):
                internal.append(f_url)
            else:
                external.append(f_url)

def remove_dupes():
    """Removes duplicate elements from the internal, external and visited lists"""
    return list(set(internal)-set(visited)-set(four04)), list(set(external)), list(set(visited))

def generate_reports(e, v, f04, t):
    f_external = open('external.txt', 'ab+')
    f_visited = open('visited.txt', 'ab+')
    f_report = open('report.txt', 'ab+')


    print(e, file=f_external)
    print(v, file=f_visited)

    sites = len(v)+len(e)

    s = "Internal sites: %d\n" % len(v)
    for key, val in t.iteritems():
        s += "\t %s: %d\n" % (key, len(val))
    s += "External sites: %d\n" % len(e)
    s += "404's: %d\n" % len(f04)
    s += "Total working links: %d\n" % sites

    print(s, file=f_report)

    f_external.close()
    f_visited.close()
    f_report.close()
    

def main():
    parser = read_page(base)
    filter_urls(parser)
    internal, external, visited = remove_dupes()

    print ("internal: ",internal)
    
    while len(internal) > 0:
        #print("Internal: ",internal, len(internal))
        #print("external: ",external, len(external))
        print("visited: ", len(visited))

        pages = map(read_page, internal)
        map(filter_urls, pages)
        internal, external, visited = remove_dupes()
        
    generate_reports(external, visited, four04, types)

    for url in internal:
        print (url)
    print ("done")

if __name__ == "__main__":
    main()