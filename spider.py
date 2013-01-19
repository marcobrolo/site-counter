from __future__ import print_function
import urllib2
import sys
from urlparse import urlparse, urljoin
from bs4 import BeautifulSoup


visited = set()
external = set()
errors = set()
queue = set()
types = {}


def crawl(url):
	""" Gets all links from a URL and updates all of the sets """
	core = urlparse(url).netloc
	try:
		page = urllib2.urlopen(url)
		links = []

		filetype = page.info().getheader('content-type')

		#If it is a site, extract the links from it
		if 'text/html' in filetype:
			soup = BeautifulSoup(page)
			links = [tag['href'] for tag in soup.findAll('a', href=True) if "mailto:" not in tag['href']]
        
        #Keep count of how many different types of resources there are
		if filetype not in types:
			types[filetype] = 1
		types[filetype] += 1

		page.close()

		organize_links(url, core, links)

	except urllib2.HTTPError as e:
		errors.add(url)
	except urllib2.URLError as e:
		errors.add(url)


	
def organize_links(url, core, links):
	""" Formats and organizes the set of links """
	visited.add(url)

	if len(links) < 1: return
	links = [format_url(url, link) for link in links] # format_urls(url, links)

	for link in links:
		if core in link:
			queue.add(link)
		else:
			external.add(link)

	queue.difference_update(visited)
	queue.difference_update(errors)

def format_url(current_url, link):
	""" Removes extra parameters from a URL and joins the parts together """
	link = link.split('#', 1)[0]
	link = link.split('?', 1)[0]
	return urljoin(current_url, link)


def generate_reports(ext, vis, err, typ):
	""" See title """
	f_external = open('external.txt', 'ab+')
	f_visited = open('visited.txt', 'ab+')
	f_report = open('report.txt', 'ab+')


	print(ext, file=f_external)
	print(vis, file=f_visited)

	sites = len(vis)+len(ext)

	s = "Internal sites: %d\n" % len(vis)
	for key, val in typ.iteritems():
		s += "\t %s: %d\n" % (key, len(val))
	s += "External sites: %d\n" % len(ext)
	s += "Error pages: %d\n" % len(err)
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

		while len(queue) > 0:
			item = queue.pop()
			crawl(item)
			print("Q: %d - V: %d - E: %d - B: %d" % (len(queue), len(visited), len(external), len(errors)))
			print("Crawling: ", item)
	generate_reports(external, visited, errors, types)


if __name__ == '__main__':
	main()