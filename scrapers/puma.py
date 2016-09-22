"""
author: Mykal Burris
created: 19-Sept-2016
updated: 20-Sept-2016
version: 1.6
"""

from collections import OrderedDict
from scraperlibs import*
import urllib.request
import timeit
import json
import time
import os

base_url = 'http://us.puma.com/en_US'
product_urls = set()

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
archive_file = open(parent_dir + '/puma/puma_urls.txt', 'a+')
url_archive = set(archive_file)


def retrieve_links():
	categories = {
		'Womens': base_url + '/women/shoes/sneakers',
		'Men': base_url + '/men/shoes/sneakers'
	}

	for val in categories:
		url = categories[val]
		while url is not None:
			soup = soup_maker(request(url))

			for a in soup.find_all('a', {'class': 'swatch selected'}):
				product_url = a['href']
				if 'pd' in product_url:
					if product_url not in product_urls and product_url not in url_archive:
						product_urls.add(product_url)
			
			# load more products
			loader = soup.find('div', {'class': 'infinite-scroll-placeholder'})
			if loader is not None:
				url = loader['data-grid-url']
			else:
				url = None
	

def product_data():
	release_type = dict.fromkeys(['QS', 'HS', 'GR', 'LR', 'T0'], False)
	
	size_run = OrderedDict.fromkeys(['3.5', '4', '4.5', '5', '5.5', '6', '6.5', '7', '7.5'], False)
	size_run.update(OrderedDict.fromkeys(['8', '8.5', '9', '9.5', '10', '10.5', '11', '11.5'], False))
	size_run.update(OrderedDict.fromkeys(['12', '12.5', '13', '13.5', '14', '15', '16', '17', '18'], False))
	
	for url in product_urls:
		req = request(url)
		if req is not None:
			soup = soup_maker(req)
		else:
			print(url)
			continue
		
		# retrieve data
		release_date = time.strftime("%Y")
	
		model = soup.find('h1', {'class': 'product-name'}).string.replace('\n', '')
		brand = 'Puma'
		category = 'null'
		
		if 'Women' in model:
			gender = 'Women'
			model = model[:model.find('Women\'s')].strip()
		else:
			gender = 'Men'
			model = model[:model.find('Men\'s')].strip()
		
		product_id = soup.find('span', {'itemprop': 'productID'}).string
		style_code = product_id[:product_id.find('-')]
		color_code = product_id[product_id.find('-') + 1:]
		color_desc = soup.find('label', {'itemprop': 'color'}).text.replace('\n', '')
		price = soup.find('span', {'class': 'price-standard'})
		if price is None:
			price = soup.find('span', {'product-sales-price'}).string.replace('$', '')
		else:
			price = price.string.replace('$', '')
			
		if '.00' in price:
			price = price[:price.find('.')]
		width = 'null'
		
		release_type['GR'] = True
		
		# doesnt account for sizes oos
		if soup.find('p', {'class': 'not-available-msg'}) is None:
			for size in soup.find('ul', {'class': 'size'}).find_all('a'):
				size = size['title']
				size_run[size] = True
				
		# create product folder
		folder_path = parent_dir + '/data' + '/{}/{}/{}/{}'.format(brand, model, gender, product_id)
		os.makedirs(folder_path, exist_ok=True)
		
		# download images
		image_array = []
		previous_time = ''
		for image in soup.find_all('img', {'class': 'primary-image'}):
			image_url = image['data-zoom-image']
			if 'png' in image_url:
				ext = '.png'
			else:
				ext = '.jpeg'
			
			timer = str(time.time())
			file_time = timer[:timer.find('.')]
			if file_time == previous_time:
				file_time = int(file_time) + 1
			previous_time = file_time
			
			image_path = os.path.join(folder_path, '{}_{}{}'.format(product_id, file_time, ext))
			image_array.append(image_path)
			urllib.request.urlretrieve(image_url, image_path)
		image_array = ([dict(file_path=url) for url in image_array])
		url_archive.add(url)
	
		product_json = {
			'brand': brand,
			'model': model,
			'category': category,
			'gender': gender,
			'color description': color_desc,
			'color code': color_code,
			'style code': style_code,
			'product id': product_id,
			'collection': 'null',
			'release type': release_type,
			'release date': release_date,
			'geo': 'US',
			'width': width,
			'price': price.strip(),
			'size run': size_run,
			'images': image_array,
			'source': 'http://www.puma.com'
		}
		
		# write json file
		json_path = product_id + '.json'
		file_name = open(os.path.join(folder_path, json_path), 'w')
		print(json.dumps(product_json, indent=3), file=file_name)

		# revert dict values to false
		release_type = dict.fromkeys(release_type.fromkeys(release_type), False)
		size_run = OrderedDict.fromkeys(size_run.fromkeys(size_run), False)
		
		url_archive.add(url)
		time.sleep(5)


# Main
def main():
	start = timeit.default_timer()
	
	retrieve_links()
	product_data()
	
	print(url_archive, file=archive_file)
	archive_file.close()
	
	print('{} mins'.format((timeit.default_timer() - start) / 60))
