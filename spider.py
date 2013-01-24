from __future__ import print_function
import urllib2
import sys
import Queue
import threading
import time
from urlparse import urlparse, urljoin
from bs4 import BeautifulSoup

types = {}

MAX_THREADS = 5

visited = set()
external = set()
internal = set()
errors = set()
parse_errors = set()
to_visit = Queue.Queue()
to_parse = Queue.Queue()


class crawl_thread (threading.Thread):
	def __init__(self, visit, parse):
		threading.Thread.__init__(self)
		self.q = visit
		self.out = parse

	def run(self):

		if self.q:
			print("starting thread\n")
			while True:
				if self.q.qsize() > 0:
					try:
						url = self.q.get()
						self.openurl(url)
					except Queue.Empty:
						pass 
				time.sleep(1)
                        
	def openurl(self, url):
		print("Visiting: %s" % url)
		visited.add(url)
		core = urlparse(url).netloc
		try:
			page = urllib2.urlopen(url)
			filetype = page.info().getheader('content-type')
			if 'text/html' in filetype:
				try:
					soup = BeautifulSoup(page)
					page.close()
					self.out.put((url, soup, core, filetype)) #Takes 1 argument, 4 given
				except:
					parse_errors.add(url)
		except urllib2.HTTPError as e:
			errors.add(url)
		except urllib2.URLError as e:
			errors.add(url)

def parse(url, soup, core, filetype):
	""" Gets all links from a URL and updates all of the sets """
	print("parsing %s" % url)
	links = []

	links = [tag['href'] for tag in soup.findAll('a', href=True) if "mailto:" not in tag['href']]

	if filetype not in types:
		types[filetype] = 1
	types[filetype] += 1

	organize_links(url, core, links)

	
def organize_links(url, core, links):
	""" Formats and organizes the set of links """

	if len(links) < 1: return
	links = [format_url(url, link) for link in links] # format_urls(url, links)

	for link in links:
   		#if link not in visited and link not in errors and link not in parse_errors:
		if core in link:
			if link not in visited and link not in internal and link not in errors and link not in parse_errors:
				internal.add(link)
				to_visit.put(link)
		else:
			external.add(link)

def format_url(current_url, link):
	""" Removes extra parameters from a URL and joins the parts together """
	link = link.split('#', 1)[0]
	link = link.split('?', 1)[0]
	link = link.split(' ', 1)[0]
	return urljoin(current_url, link)


def generate_reports(ext, vis, err, typ, perr):
	""" See title """
	print("Making Report")
	print(ext)
	print(vis)
	print(err)
	f_external = open('external.txt', 'ab+')
	f_visited = open('visited.txt', 'ab+')
	f_report = open('report.txt', 'ab+')


	print(ext, file=f_external)
	print(vis, file=f_visited)

	sites = len(vis)+len(ext)
	internal_sites = len(vis) - len(err)

	s = "Internal sites: %d\n" % internal_sites
	for key, val in typ.iteritems():
		s += "\t %s: %d\n" % (key, val)
	s += "External sites: %d\n" % len(ext)
	s += "Error pages: %d\n" % len(err)
	s += "Parsing errors: %d\n" % len(perr)
	s += "Total working links: %d\n" % sites

	print(s, file=f_report)

	f_external.close()
	f_visited.close()
	f_report.close()

def main():
	if len(sys.argv) == 1:
		print("Peter Zenger's website resource counter")
		print("Usage: %s [FULL_URL]" % sys.argv[0])
		sys.exit(-1)

	threads = []
	count = 0

	for site in sys.argv[1:]:
		to_visit.put(site)

		for i in xrange(MAX_THREADS):
				p = crawl_thread(to_visit, to_parse)
				p.daemon = True
				p.start()
				threads.append(p)
        
		while not to_visit.empty() or not to_parse.empty() or count < 5:
			count += 1
			try:
				s = to_parse.get_nowait()
				parse(s[0], s[1], s[2], s[3])
				print("Q: %d - V: %d - E: %d - B: %d" % (to_visit.qsize(), len(visited), len(external), len(errors)))
			except Queue.Empty:
				print("Empty queue, waiting 1")
				time.sleep(1)
		
	generate_reports(external, visited, errors, types, parse_errors)

if __name__ == '__main__':
	main()
