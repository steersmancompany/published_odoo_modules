{
	'name': 'Product Manufacturers',
	'summary': "Assign manufacturers to products and maintain manufacturer's product codes and MAP pricing",
	'category': 'Sales',
	'version': '0.0.2',
	'author': 'Steersman Company',
	'website': 'https://steersman.works',
	'depends': ['product'],
	'data': [
		'views/product_template_views.xml',
        'views/product_views.xml'
    ],
    'images': ['static/description/banner.png'],
	'application': False,
	'installable': True,
	'auto_install': True,
}
