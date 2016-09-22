from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup as bs
import gzip


def request(url):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) ' \
	             'Chrome/52.0.2743.116 Safari/537.36',
		'Upgrade-Insecure-Requests': '1',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'DNT': '1',
		'Accept-Encoding': 'gzip, deflate, sdch',
		'Accept-Language': 'en-US,en;q=0.8,da;q=0.6'
	}
	
	req = Request(url, headers=headers)
	try:
		response = urlopen(req, timeout=10)
	except HTTPError as e:
		print(url)
		print('Error code: ', e.code)
		return None
	except URLError as e:
		print(url)
		print('Reason: ', e.reason)
		return None
	else:
		return response


def soup_maker(response):
	content = gzip.decompress(response.read())
	content = str(content, response.headers.get_content_charset())
	soup = bs(content, 'lxml')
	return soup

