"""
author: Mykal Burris
created: 18-Sept-2016
updated: 21-Sept-2016
version: 1.7
"""
from scraper_lib import*
from collections import OrderedDict
import urllib.request
import timeit
import time
import json
import os

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
archive_file = open(parent_dir + '/data/asics/asics_urls.txt', 'a+')
url_archive = set(archive_file)

base_url = 'http://www.asicstiger.com/us/en-us'

product_urls = set()


def retrieve_links():
	categories = {
		'Mens': base_url + '/mens/c/mens-shoes?show=All',
		'Womens': base_url + '/womens/c/womens-shoes?show=All',
		'GS': base_url + '/kids/c/kids-shoes?show=All&q=:relevance:shoeSizeCode:4:shoeSizeCode:5:shoeSizeCode:6:shoeSizeCode:7:shoeSizeCode:3.5:shoeSizeCode:4.5:shoeSizeCode:5.5:shoeSizeCode:6.5'
	}

	for val in categories:
		url = categories[val]
		soup = soup_maker(request(url))
		for a in soup.find('div', {'class': 'col-sm-9 product-list'}).find_all('a', href=True):
			url = base_url + a['href']
			if url not in product_urls and url not in url_archive:
				product_urls.add(url)
	
	
def product_data():
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
		data = soup.find_all('script', type='text/javascript')[1]
		for script in data:
			data = script.extract()
		
		start = 'initArr.ecommerce = '
		end = '"USD"}'
		
		data = data[data.find(start) + len(start):data.find(end) + len(end)]
		json_data = json.loads(data)
		json_data = json_data['product']
		
		brand = 'ASICS'
		model = json_data['name'].strip()
		width = json_data['width'].title()
		gender = json_data['gender'].title()
		color_desc = json_data['variant']
		color_code = json_data['id'][json_data['id'].find('.') + 1:]
		style_code = json_data['style-code']
		product_id = '{}-{}'.format(style_code, color_code)
		price = json_data['price']
		
		release_date = time.strftime("%Y")
		
		if width is 'Undefined':
			width = 'null'
		else:
			width = width
		
		if 'GS' in model:
			model = model.replace('GS', '').strip()
		
		for size in json_data['stock-size']:
			size_run[size] = True
			
		if gender is 'Female':
			gender = 'Women'
		elif gender is 'Male':
			gender = 'Men'
		elif gender == 'Kids':
			gender = 'GS'
		else:
			gender = gender
		
		# create product folder
		folder_path = parent_dir + '/data' + '/{}/{}/{}/{}'.format(brand, model, gender, product_id)
		os.makedirs(folder_path, exist_ok=True)
		
		# download images
		image_array = []
		for image in soup.find_all('img', {'class': 'rsImg'}):
			image_url = image['src']
			if 'png' in image_url:
				ext = '.png'
			else:
				ext = '.jpeg'
			
			image_path = os.path.join(folder_path, '{}_{}{}'.format(product_id, int(time.time()), ext))
			image_array.append(image_path)
			urllib.request.urlretrieve(image_url, image_path)
		image_array = ([dict(file_path=url) for url in image_array])
		url_archive.add(url)
	
		product_json = {
			'brand': brand,
			'model': model,
			'gender': gender,
			'color description': color_desc,
			'color code': color_code,
			'style code': style_code,
			'product id': product_id,
			'release type': 'GR',
			'release date': release_date,
			'geo': 'US',
			'width': width,
			'price': price,
			'size run': size_run,
			'images': image_array,
			'source': 'http://www.asicstiger.com'
		}
		
		# write json file
		json_path = product_id + '.json'
		file_name = open(os.path.join(folder_path, json_path), 'w')
		print(json.dumps(product_json, indent=3), file=file_name)
		
		# revert dict values to false
		size_run = OrderedDict.fromkeys(size_run.fromkeys(size_run), False)
		
		url_archive.add(url)
		time.sleep(5)


def main():
	start = timeit.default_timer()
	
	retrieve_links()
	product_data()

	print(url_archive, file=archive_file)
	archive_file.close()
	
	print('{} mins'.format((timeit.default_timer()-start)/60))
