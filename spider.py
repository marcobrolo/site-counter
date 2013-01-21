from __future__ import print_function
import urllib2
import sys
import Queue
import threading
from urlparse import urlparse, urljoin
from bs4 import BeautifulSoup

class SetQueue(Queue.Queue):
        def __init__(self):
                Queue.Queue.__init__(self)
                self.history = set()

        def _put(self, item):
                if item not in self.history:
                        print("Adding: ", item)
                        self.history.add(item)
                        Queue.Queue._put(self, item)
                        

visited = SetQueue()
external = SetQueue()
errors = SetQueue()
parse_errors = SetQueue()
queue = SetQueue()
types = {}
queue_lock = threading.Lock()

MAX_THREADS = 2

class crawl_thread (threading.Thread):
        def __init__(self, url):
                threading.Thread.__init__(self)
                self.url = url
        def run(self):
                print ("Starting " , self.url)
                visited.put(self.url)
                crawl(self.url)
                print ("Exiting " , self.url)




def crawl(url):
	""" Gets all links from a URL and updates all of the sets """
	core = urlparse(url).netloc
	try:
		page = urllib2.urlopen(url)
		links = []

		filetype = page.info().getheader('content-type')

		#If it is a site, extract the links from it
		if 'text/html' in filetype:
			try:
				soup = BeautifulSoup(page)
			except:
				parse_errors.put(url)
				return
			links = [tag['href'] for tag in soup.findAll('a', href=True) if "mailto:" not in tag['href']]

                page.close()
                
                #Keep count of how many different types of resources there are
		#GL
		if filetype not in types:
			types[filetype] = 1
		types[filetype] += 1

		organize_links(url, core, links)
		#RL

	except urllib2.HTTPError as e:
		errors.put(url)
	except urllib2.URLError as e:
		errors.put(url)


	
def organize_links(url, core, links):
	""" Formats and organizes the set of links """
	

	if len(links) < 1: return
	links = [format_url(url, link) for link in links] # format_urls(url, links)

	for link in links:
                #if link not in visited and link not in errors and link not in parse_errors:
                if core in link:
                        queue.put(link)
                else:
                        external.put(link)

	#queue.difference_update(visited)
	#queue.difference_update(errors)
	#queue.difference_update(parse_errors)

def format_url(current_url, link):
	""" Removes extra parameters from a URL and joins the parts together """
	link = link.split('#', 1)[0]
	link = link.split('?', 1)[0]
	link = link.split(' ', 1)[0]
	return urljoin(current_url, link)


def generate_reports(ext, vis, err, typ, perr):
	""" See title """
	f_external = open('external.txt', 'ab+')
	f_visited = open('visited.txt', 'ab+')
	f_report = open('report.txt', 'ab+')


	print(ext, file=f_external)
	print(vis, file=f_visited)

	sites = vis.qsize()+ext.qsize()

	s = "Internal sites: %d\n" % vis.qsize()
	for key, val in typ.iteritems():
		s += "\t %s: %d\n" % (key, val)
	s += "External sites: %d\n" % ext.qsize()
	s += "Error pages: %d\n" % err.qsize()
	s += "Parsing errors: %d" % perr.qsize()
	s += "Total working links: %d\n" % sites

	print(s, file=f_report)

	f_external.close()
	f_visited.close()
	f_report.close()



def main():
	if len(sys.argv) == 1:
		print("Peter Z's website resource counter")
		print("Usage: %s [FULL_URL]" % sys.argv[0])
		sys.exit(-1)

	
	for site in sys.argv[1:]:
		crawl(site)
                

		while queue.qsize() > 0:
                        for i in xrange(MAX_THREADS):
                        #if threading.activeCount() < MAX_THREADS:
                                
                                item = queue.get()
                                p = crawl_thread(item)
                                p.setDaemon(True)
                                print("Q: %d - V: %d - E: %d - B: %d" % (queue.qsize(), visited.qsize(), external.qsize(), errors.qsize()))
                                print("Crawling: ", item)
                                p.start()
                        
                        
                        
			#item = queue.get_nowait()
			#crawl(item)
                print ("!!")
                #queue.join()
                print("??")

			
	generate_reports(external, visited, errors, types, parse_errors)


if __name__ == '__main__':
	main()
