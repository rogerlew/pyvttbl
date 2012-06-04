.. pyvttbl documentation master file, created by
   sphinx-quickstart on Thu May 31 00:22:55 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

   Notes to future self or curious visitors on setting up the custom layout
   
     TO ADD THE LOGO AND LINKS BELOW THE LOGO TO THE TOP OF EVERY PAGE
       I copied and edited the layout.html folder from the sphinx.pocoo.org repo 
       (doc/_templates/layout.html) to my templates folder.
       
       The version used for this page can be found at:
       https://code.google.com/p/pyvttbl/source/browse/doc/_templates/indexsidebar.html
     
       In conf.py uncomment or add "templates_path = ['_templates']"
     
     TO ADD CUSTOM SIDEBAR TO INDEX PAGE 
       I copied and edited the indexsidbar.html folder from the sphinx.pocoo.org repo 
       (doc/_templates/indexsidebar.html) to my templates folder.

       The version used for this page can be found at:
       https://code.google.com/p/pyvttbl/source/browse/doc/_templates/indexsidebar.html
       
         referenced images have to be in doc/_static from what I can tell
       
       
       inside conf.py initialize an html_sidebars dict to reflect what you would like 
       on the sidebar:
           html_sidebars = {'index': ['indexsidebar.html',
                                      'relations.html',
                                      'searchbox.html',
                                      'sourcelink.html']}
                                      
           'indexsidebar.html' obviously lives in the my doc/_templates folder
           
           the other html files reference files in site-packages/.../sphinx/themes/basic
           
     TO ADD FUNDING CITATION TO FOOTER
       In the _templates/layout.html we need some CSS to handle the div alignment.
       Then we just have to override the footer.

Table of Contents
=================

.. toctree::
   :maxdepth: 0

   install
   quick-start
   DataFrame
   PyvtTbl
   Descriptives
   Marginals
   Histogram
   Correlation
   Anova
   Anova1way
   ChiSquare1way
   ChiSquare2way
   Ttest
   box_plot
   histogram_plot
   interaction_plot
   scatter_plot
   scatter_matrix
   plotting
   stats
   
Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. * :ref:`modindex`
.. * :ref:`glossary`