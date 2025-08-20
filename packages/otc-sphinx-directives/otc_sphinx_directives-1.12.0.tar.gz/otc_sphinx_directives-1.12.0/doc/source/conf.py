project = 'otc_sphinx_directives'
copyright = '2024, Ecosystem Squad'
author = 'Open Telekom Cloud Ecosystem Squad'

extensions = [
    'otcdocstheme',
    'otc_sphinx_directives'
]

exclude_patterns = ['_build']
source_suffix = '.rst'
master_doc = 'index'
html_theme = 'otcdocs'
html_static_path = ['_static']

otcdocs_doc_environment = 'internal'
otcdocs_search_environment = 'hc_de'
otcdocs_service_environment = 'internal'
otcdocs_cloud_environment = 'eu_de'
