from __future__ import print_function
import urllib, lister, sgmllib
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
        usock = urllib.urlopen(url)
        print (usock.getcode(), " : ", url)
        if usock.getcode() == 404:
            four04.append(url)
            return
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

    
def filter_urls(p):
    """Place the urls into the appropriate list
    Some URL's are written /stuff
    Other are written completely starting with http://"""
    if p is None: return
    for url in p.urls:
        f_url = url.split('#', 1)[0]
        f_url = f_url.split('?', 1)[0]
       
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
    
def report(e, v, f04):
    s = "Internal sites: %d\n" % len(v)
    s += "External sites: %d\n" % len(e)
    s += "404's: %d\n" % len(f04)
    s += "Total working links: %d\n" % (len(v)+len(e))
    return s
    
if __name__ == "__main__":
    parser = read_page(base)
    filter_urls(parser)
    internal, external, visited = remove_dupes()
    
    #while len(internal) - len(visited) > 0:
    while len(internal) > 0:
        print("Internal: ",internal, len(internal))
        print("external: ",external, len(external))
        print("visited: ", visited, len(visited))
        pages = map(read_page, internal)
        
        map(filter_urls, pages)
        internal, external, visited = remove_dupes()
        

    f_internal = open('internal.txt', 'ab+')
    f_external = open('external.txt', 'ab+')
    f_visited = open('visited.txt', 'ab+')
    f_report = open('report.txt', 'ab+')

    print(internal, file=f_internal)
    print(external, file=f_external)
    print(visited, file=f_visited)
    print(report(external, visited, four04) , file=f_report)


    f_internal.close()
    f_external.close()
    f_visited.close()
    f_report.close()
    for url in internal:
        print (url)
    print (":",len(visited))
    print (";", len(external))
    print ("done")

