from __future__ import print_function
import urllib2, lister, sgmllib
import re


#Lists needed
visited = []
external = []
internal = []
four04 = []
base = "http://www.ethanholmes.me/"
core = "www.ethanholmes.me"
#base = "http://www.cs.sfu.ca/"
#core = "www.cs.sfu.ca"


#TODO:  Use urllib2, check mime type, only open/read if it is html.
#Otherwise check status and continue.  Also keep track of the different types.
#Use 1 dictionary of lists rather than N lists.

def read_page(url):
    """Reads a page"""
    try:
        try:
            usock = urllib2.urlopen(url)
        
        #if usock.getcode() == 404:
        #    four04.append(url)
        #    return
        except urllib2.HTTPError:
            four04.append(url)
            print('404', " : ", url)
            return
        print (usock.getcode(), " : ", url)
        parser = lister.Lister()
        parser.feed(usock.read())
        visited.append(url)
        usock.close()
        parser.close()
        return parser

    except sgmllib.SGMLParseError:
        pass

def local_url(url):
    cond = [(url.count('.') == 1) and url[0] == '/'] #Full URL's have at least 2
    cond.append(url[0] == '/' and url.count('.') == 0) #Filters out http links and javascript
    return True in cond

def local_full_url(url):
    cond = [core in url] #Check if the full core of the url (cs.sfu.ca) is in the url
    return cond.count(False) == 0

def strip_url(u):
    temp_url = u.split('#', 1)[0]
    temp_url = temp_url.split('?', 1)[0]
    return temp_url
    
def filter_urls(p):
    """Place the urls into the appropriate list
    Some URL's are written /stuff
    Other are written completely starting with http://"""
    if p is None: return
    for url in p.urls:
        f_url = strip_url(url)
        if f_url:
            print(f_url)
            if local_url(f_url):
                if f_url in internal:
                    print("NO")
                    no = open("NO.txt",'w')
                    print("NO", file=no)
                    no.close()

                internal.append(base+f_url[1:])
            elif local_full_url(f_url):
                if f_url in internal:
                    print ("NO")
                    no = open("NO.txt",'w')
                    print("NO", file=no)
                    no.close()
                internal.append(f_url)

            else:
                external.append(f_url)



def remove_dupes():
    """Removes duplicate elements from the internal, external and visited lists"""
    return list(set(internal)-set(visited)-set(four04)), list(set(external)), list(set(visited))
#    
#def report(e, v, f04):
#    s = "Internal sites: %d\n" % len(v)
#    s += "External sites: %d\n" % len(e)
#    s += "404's: %d\n" % len(f04)
#    s += "Total working links: %d\n" % (len(v)+len(e))
#    return s

def generate_reports(e, v, f04):
    f_external = open('external.txt', 'ab+')
    f_visited = open('visited.txt', 'ab+')
    f_report = open('report.txt', 'ab+')

    print(e, file=f_external)
    print(v, file=f_visited)

    s = "Internal sites: %d\n" % len(v)
    s += "External sites: %d\n" % len(e)
    s += "404's: %d\n" % len(f04)
    s += "Total working links: %d\n" % (len(v)+len(e))

    print(s, file=f_report)

    f_external.close()
    f_visited.close()
    f_report.close()
    
if __name__ == "__main__":
    parser = read_page(base)
    filter_urls(parser)
    internal, external, visited = remove_dupes()
    
    while len(internal) > 0:
        print("Internal: ",internal, len(internal))
        print("external: ",external, len(external))
        print("visited: ", visited, len(visited))
        pages = map(read_page, internal)
        
        map(filter_urls, pages)
        internal, external, visited = remove_dupes()
        
    generate_reports(external, visited, four04)

    
    for url in internal:
        print (url)
    print (":",len(visited))
    print (";", len(external))
    print ("done")

