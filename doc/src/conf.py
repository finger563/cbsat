project = 'CBSAT'
version = '0.2'
release = '0.2.0'
copyright = '2015, finger563'

master_doc = 'index'
source_suffix = '.rst'
exclude_patterns = ['**/.#*']
extensions = ['sphinx.ext.mathjax', 'sphinxcontrib.spelling', 'sphinx.ext.todo']
templates_path = ['_templates']

pygments_style = 'sphinx'
import sphinx_rtd_theme
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
htmlhelp_basename = 'cbsat-doc'
html_static_path = ['crafts','scripts','_static']
html_context = { 'css_files': ['./_static/custom.css'] }

todo_include_todos = True

spelling_word_list_filename = 'dictionary.txt'
