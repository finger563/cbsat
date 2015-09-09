project = 'Research Progress Report'
html_short_title = 'Research Progress Report'
#project = 'PNP2'
#version = '0.2'
#release = '0.2.0'
copyright = '2015, finger563'

import os,inspect,sys
analysis = os.path.realpath(os.path.abspath
                                    (os.path.join
                                     (os.path.split
                                      (inspect.getfile
                                       (inspect.currentframe()
                                    )
                                   )[0], "../../src/analysis/v2.0/")
                                 ))
if analysis not in sys.path:
    sys.path.insert(0, analysis)
middleware = os.path.realpath(os.path.abspath
                                    (os.path.join
                                     (os.path.split
                                      (inspect.getfile
                                       (inspect.currentframe()
                                    )
                                   )[0], "../../src/middleware/v2.0/")
                                 ))
if middleware not in sys.path:
    sys.path.insert(0, middleware)

sys.path.insert(0, os.path.abspath('.'))

master_doc = 'index'
source_suffix = '.rst'
exclude_patterns = ['**/.#*']
extensions = ['numfig','sphinx.ext.pngmath', 'sphinx.ext.autodoc', 'sphinxcontrib.spelling', 'sphinx.ext.todo']
templates_path = ['_templates']
autoclass_content = "both"
autodoc_member_order = "bysource"

pygments_style = 'sphinx'
import sphinx_rtd_theme
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
htmlhelp_basename = 'cbsat-doc'
html_static_path = ['_static']
html_context = { 'css_files': ['./_static/custom.css'] }

todo_include_todos = True

add_module_names = False
show_authors = True

spelling_word_list_filename = 'dictionary.txt'

latex_elements = {}
latex_elements['preamble'] = '\usepackage{amsmath}\n\usepackage{amssymb}\n'
latex_elements['classoptions'] = ',openany,oneside'
latex_elements['babel'] = '\\usepackage[english]{babel}'
latex_elements['title'] = 'Research Progress Report'
latex_elements['release'] = ''
latex_elements['releasename'] = ''
latex_elements['author'] = 'William Emfinger'
