from __future__ import print_function
import urllib2
import sys
import Queue
import threading
from urlparse import urlparse, urljoin
from bs4 import BeautifulSoup

types = {}

MAX_THREADS = 5
PROCESS_AMOUNT = 1

class SetQueue(Queue.Queue):
        def __init__(self):
                Queue.Queue.__init__(self)
                self.history = set()

        def _put(self, item):
                if item not in self.history:
                        self.history.add(item)
                        Queue.Queue._put(self, item)
                        

visited = SetQueue()
external = SetQueue()
errors = SetQueue()
parse_errors = SetQueue()
queue = SetQueue()


class crawl_thread (threading.Thread):
        def __init__(self, queue=None):
                threading.Thread.__init__(self)
                self.q = queue

        def run(self):
                if self.q:
                        for x in xrange(PROCESS_AMOUNT):
                                try:
                                        url = self.q.get_nowait()
                                except Queue.Empty:
                                        return
                                
                                print("Q: %d - V: %d - E: %d - B: %d" % (queue.qsize(), visited.qsize(), external.qsize(), errors.qsize()))
                                crawl(url)
                        
def crawl(url):
	""" Gets all links from a URL and updates all of the sets """
	print("VISITING: ", url)
	visited.put(url)
	core = urlparse(url).netloc
	print(core)
	try:
		page = urllib2.urlopen(url)
		print(page)
		links = []

		filetype = page.info().getheader('content-type')


		print(filetype)

		#If it is a site, extract the links from it
		if 'text/html' in filetype:
			try:
                                print("1")
				soup = BeautifulSoup(page)
				print("2")
			except:
				parse_errors.put(url)
				return
			links = [tag['href'] for tag in soup.findAll('a', href=True) if "mailto:" not in tag['href']]

                page.close()

                print(links)
                
                #Keep count of how many different types of resources there are
		if filetype not in types:
			types[filetype] = 1
		types[filetype] += 1

		organize_links(url, core, links)

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


	print(ext.history, file=f_external)
	print(vis.history, file=f_visited)

	sites = len(vis.history)+len(ext.history)

	s = "Internal sites: %d\n" % len(vis.history)
	for key, val in typ.iteritems():
		s += "\t %s: %d\n" % (key, val)
	s += "External sites: %d\n" % len(ext.history)
	s += "Error pages: %d\n" % len(err.history)
	s += "Parsing errors: %d\n" % len(perr.history)
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

	threads = []

	
	for site in sys.argv[1:]:
		crawl(site)
                
		while not queue.empty():
                        for i in xrange(MAX_THREADS):
                                p = crawl_thread(queue)
                                p.daemon = True
                                p.start()
                                threads.append(p)

                        [thread.join() for thread in threads]
		
	generate_reports(external, visited, errors, types, parse_errors)

if __name__ == '__main__':
	main()
