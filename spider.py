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


def crawl_domain(url):
	core = urlparse(url).netloc
	page = urllib2.urlopen(url)
	links = []

	page.getcode()

	filetype = page.info().getheader('content-type')

	if 'text/html' in filetype:
            soup = BeautifulSoup(page)
            links = [tag['href'] for tag in soup.findAll('a', href=True)]
        
	if filetype not in types:
		types[filetype] = 1
	types[filetype] += 1

	page.close()

	organize_links(url, core, links)

	print("visited", visited)
	print("External", external)

	
def organize_links(url, core, links):
	visited.add(url)

	if len(links) < 1: return
	links = [format_url(url, link) for link in links] # format_urls(url, links)
	print("links", links)
	print(urlparse(links[0]).netloc)
	for link in links:
		if core in link:
			queue.add(link)
		else:
			external.add(link)

def format_url(current_url, link):
	link = link.split('#', 1)[0]
	link = link.split('?', 1)[0]
	return urljoin(current_url, link)



def main():
	if len(sys.argv) == 1:
		print("Peter Z's website resource counter")
		print("Usage: %s [FULL_URL]" % sys.argv[0])
		sys.exit(-1)
	
	for site in sys.argv[1:]:
		
		crawl_domain(site)


if __name__ == '__main__':
	main()