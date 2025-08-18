import importlib.metadata
pkg_name='scilens'
product_name='SciLens'
pkg_version=importlib.metadata.version(pkg_name)
pkg_homepage=importlib.metadata.metadata(pkg_name).get('home-page')
pkg_documentations_url=None
try:pkg_documentations_url=importlib.metadata.metadata(pkg_name)['Project-URL'].split(', ')[1]
except Exception:pass
powered_by={'name':'CesGensLab','url':'https://cesgenslab.cloud'}