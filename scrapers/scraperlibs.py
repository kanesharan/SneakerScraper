from bs4 import BeautifulSoup as bs
import urllib.request


def request(url):
	user_agent = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
		              'Chrome/53.0.2785.116 Safari/537.36'}
	req = urllib.request.Request(url, headers=user_agent)
	with urllib.request.urlopen(req) as response:
		content = response.read()
	return content


def soup_maker(html):
	soup = bs(html, 'lxml')
	return soup

