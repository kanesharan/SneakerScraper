#!/usr/bin/env python
# author: Mykal Burris
# created: 17-09-2016
# updated: 18-09-2016
# version: 3.1

from collections import OrderedDict
import urllib.request
from scraperlibs import*
import timeit
import json
import time
import os

# TODO: better way of archiving urls, universal json structure

base_url = 'http://store.nike.com/us/en_us'
product_urls = set()

today = time.strftime("%d%b%Y")
archive_file = open(os.getcwd() + '/nike/nike_urls.txt', 'a+')
url_archive = set(archive_file)


def retrieve_links():
	black_list = ['Sandals', 'Slide', 'Flip', 'iD', 'Spike', 'Training']
	black_list += ['Soccer', 'Cleat', 'Football, Golf', 'Track']

	categories = {
		'Lab': base_url + '/pw/nikelab-shoes/ofoZoi3',
		'Womens Lifestyle': base_url + '/pw/womens-lifestyle-shoes/7ptZoneZpipZonoZonpZoi3',
		'Womens Running': base_url + '/pw/womens-running-shoes/7ptZ8yzZpipZonoZonpZoi3',
		'Mens Lifestyle': base_url + '/pw/mens-lifestyle-shoes/7puZoneZoi3',
		'Mens Running': base_url + '/pw/mens-running-shoes/7puZ8yzZoi3',
		'Mens Basketball': base_url + '/pw/mens-basketball-shoes/7puZ8r1Zoi3',
		'Mens Skateboarding': base_url + '/pw/mens-nike-skateboarding-shoes/7puZ9yqZpipZoi3?ipp=107',
		'Boys': base_url + '/pw/youth-boys-shoes/7pvZ88nZpipZonoZonnZoi3',
		'Girls': base_url + '/pw/youth-girls-shoes/7pwZ88nZpipZonnZonoZoi3?ipp=101'
	}

	for val in categories:
		url = categories[val]
		soup = soup_maker(request(url))
		for a in soup.find('div', {'class': 'exp-product-wall'}).find_all('a', href=True):
			try:
				name = a.parent.parent.parent.parent.parent.find('p', {'class': 'product-display-name'}).string
				sub_name = a.parent.parent.parent.parent.parent.find('p', {'class': 'product-subtitle'}).string
			except:
				continue

			if not any(black_word in name for black_word in black_list) and not any(black_word in sub_name for black_word in black_list):
				if a['href'] not in product_urls and a['href'] not in url_archive:
					product_urls.add(a['href'])
	product_data()
	
	
def product_data():
	collection = dict.fromkeys(['ACG', 'BHM', 'HTM', 'LOTC', 'NikeLab', 'OG', 'PRM', 'Retro', 'SB'], False)
	release_type = dict.fromkeys(['QS', 'HS', 'GR', 'LR', 'T0'], False)
	
	size_run = OrderedDict.fromkeys(['3.5', '4', '4.5', '5', '5.5', '6', '6.5', '7', '7.5'], False)
	size_run.update(OrderedDict.fromkeys(['8', '8.5', '9', '9.5', '10', '10.5', '11', '11.5'], False))
	size_run.update(OrderedDict.fromkeys(['12', '12.5', '13', '13.5', '14', '15', '16', '17', '18'], False))
	
	gender_dict = {
		'1': 'Men',
		'2': 'Women',
		'3': 'GS',
		'4': 'GS'
	}
	
	for url in product_urls:
		print(url)
		try:
			soup = soup_maker(request(url))
		except:
			print('ERROR: ', url)
			continue
		
		data = soup.find('script', id="product-data")
		
		if data is None:
			continue
			
		for script in data:
			data = script.extract()
		
		json_data = json.loads(data)
		
		# retrieve data
		start_date = json_data["startDate"] / 1000.0
		release_date = time.strftime("%d %B %Y", time.localtime(start_date))
		model = json_data['productTitle']
		brand = json_data['chat']['brand']
		category = json_data['chat']['primarySport']
		gender = gender_dict[json_data['chat']['gender']]
		color_desc = json_data['colorDescription']
		color_code = json_data['colorNumber']
		style_code = json_data['desktopBazaarVoiceConfiguration']['productId']
		product_id = json_data['chat']['productId']
		price = json_data['overriddenLocalPrice']
		width = json_data['desktopBazaarVoiceConfiguration']['productWidth']
		tech_specs = json_data['techSpecs']
		featured_tech = json_data['featuredTechnology']
		geo = json_data['chat']['geo']
		
		if width is None:
			width = 'null'
		elif width is 'Regular':
			width = 'Standard'
		else:
			width = width.title()
		
		if price is None:
			price = json_data["chat"]["productPrice"]
		else:
			price = price.strip('$')
		
		sizes = json_data['trackingData']['sizeRun']
		sizes = sizes.replace(':y', '').replace(':n', '').split('|')
		for size in sizes:
			size_run[size] = True
	
		# collections
		if 'PRM' in model or 'Premium' in model:
			model = model.replace('PRM', '')
			collection['PRM'] = True
		
		if 'BHM' in model:
			model = model.replace('BHM', '')
			collection['BHM'] = True

		if 'ACG' in model:
			model = model.replace('ACG', '')
			collection['ACG'] = True

		if 'HTM' in model:
			model = model.replace('HTM', '')
			collection['HTM'] = True

		if 'LOTC' in model:
			model = model.replace('LOTC', '')
			collection['LOTC'] = True

		if 'NikeLab' in model:
			model = model.replace('NikeLab', '')
			collection['NikeLab'] = True

		if 'Retro' in model:
			collection['Retro'] = True

		if 'OG' in model:
			collection['OG'] = True

		if 'SB' in model:
			collection['SB'] = True

		# release type
		if 'QS' in model:
			model = model.replace('QS', '')
			release_type['QS'] = True
		else:
			release_type['GR'] = True
			
		if 'Nike' in model:
			model = model.replace('Nike', '')
			
		product_json = {
			'brand': brand,
			'model': model.strip(),
			'category': category,  # better name
			'gender': gender,
			'color description': color_desc,
			'color code': color_code,
			'style code': style_code,
			'product id': product_id,
			'collection': collection,
			'release type': release_type,
			'release date': release_date,
			'geo': geo,
			'width': width,
			'price': price,
			'size run': size_run,
			'source': 'http://www.nike.com'
		}
	
		# create product folder
		folder_path = os.getcwd() + '/nike/{}/{}/{}/{}'.format(brand, model, gender, product_id)
		os.makedirs(folder_path, exist_ok=True)

		# write json file
		json_path = product_id + '.json'
		file_name = open(os.path.join(folder_path, json_path), 'w')
		print(json.dumps(product_json, indent=3), file=file_name)
	
		# download images
		for counter, image_url in enumerate(json_data['imagesHeroZoom']):
			if 'png' in image_url:
				ext = '.png'
			else:
				ext = '.jpeg'
			image_path = os.path.join(folder_path, '{}|{}{}'.format(product_id, str(counter), ext))
			urllib.request.urlretrieve(image_url, image_path)

		url_archive.add(url)

		# revert dict values to false
		collection = dict.fromkeys(collection.fromkeys(collection), False)
		release_type = dict.fromkeys(release_type.fromkeys(release_type), False)
		size_run = OrderedDict.fromkeys(size_run.fromkeys(size_run), False)
		
		time.sleep(5)
			
# Main
start = timeit.default_timer()

retrieve_links()
 
print(url_archive, file=archive_file)
archive_file.close()

print(timeit.default_timer()-start)
