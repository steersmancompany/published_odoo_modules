{
	'name': 'US/Imperial Product Measurements',
	'summary': 'Maintain product weight, volume and dimensions in any UoM',
	'category': 'Localization',
	'version': '0.0.4',
	'author': 'Steersman Company',
	'website': 'https://steersman.works',
	'depends': ['stock'],
	'data': [
		'views/product_template_views.xml',
        'views/product_views.xml',
		'data/product_data.xml'
    ],
    'images': ['static/description/banner.png'],
	'application': False,
	'installable': True,
	'auto_install': True,
}
