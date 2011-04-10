# ----------------------------------------------------------------------------
#
# Copyright (c) 2011 Thomas P. Robitaille
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
# ----------------------------------------------------------------------------
#
# Instructions
#
# This script searches a LaTeX file for citekeys, and tries to match citekeys
# in the form author:year:page to the NASA ADS database. For cite keys that
# successfully resolve to a unique article, the script downloads the BibTeX
# entry and appends it to a file called [original]_auto.bib where [original] is
# the original name of the input file, with the .tex extension stripped. For
# example, the following command
#
# $ python auto_bibtex.py ms.tex
# 
# will produce an output file called ms_auto.bib. This bibliography can then
# be included in the LaTeX file with
#
# \bibliography{ms_auto, custom}
#
# where custom.bib would contain any references not resolved by ADS.
#
# ----------------------------------------------------------------------------

import sys
import warnings
import urllib
import string
from multiprocessing import Pool

# Define base URL for querying the article database
base_url = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?db_key=AST&'

# Define base URL for retrieving BibTeX entries
bibtex_url = 'http://adsabs.harvard.edu/cgi-bin/nph-bib_query?db_key=AST&data_type=BIBTEX&'

# Define custom return format for query
format = 'author=%25za1+,+year=%25Y+,+page=%25p+,+bibcode=%25R'


def get_bibtex(bibcode):
    '''
    Retrieve the BibTeX abstract given by `bibcode`
    '''

    # Set query parameters
    parameters = {}
    parameters['bibcode'] = bibcode

    # Construct query string
    query = string.join(["%s=%s" % (key, parameters[key]) for key in parameters], "&")

    # Submit query
    entry = urllib.urlopen(bibtex_url + query).read()

    # Find where the BibTeX starts
    p1 = entry.index('@')

    # Return the entry
    return entry[p1:]


def query_bibtex(author, year, page):
    '''
    Given an author, year, and page, return a BibTeX entry if a unique match
    is found. If no or multiple matches are found, returns None.
    '''

    # Set query parameters
    parameters = {}
    parameters['data_type'] = "Custom"
    parameters['format'] = format
    parameters['author'] = "^%s" % author
    parameters['start_year'] = year
    parameters['end_year'] = year

    # Construct query string
    query = string.join(["%s=%s" % (key, parameters[key]) for key in parameters], "&")

    # Submit query
    f = urllib.urlopen(base_url + query)

    # Initalize list of bibcodes
    bibcodes = []

    # Loop through results and only look at lines containing a result
    for line in f.readlines():
        if 'bibcode=' in line:

            # Construct dictionary for this entry
            entry = {}
            for pair in line.split(','):
                key, value = pair.split('=')
                entry[key.strip()] = value.strip()

            # If this entry is a match (in terms of page number), keep it
            if entry['page'] == str(page):
                bibcodes.append(entry['bibcode'])

    # Check how many results were returned
    if len(bibcodes) == 0:

        warnings.warn("No article matches the author/year/page combination")

        return None

    elif len(bibcodes) == 1:

        # Retrieve the unique BibTeX entry
        entry = get_bibtex(bibcodes[0])

        # Change the citekey to author:year:page format
        entry = entry.replace(bibcodes[0], '%s:%s:%s' % (author, str(year)[2:], str(page)), 1)

        return entry

    else:

        warnings.warn("More than one article matches the author/year/page combination")

        return None


def citekey_to_bibtex(citekey):
    '''
    Given a citekey in the author:year:page format, return a unique BibTeX
    abstract. If no or multiple matches are found, or if the citekey does not
    conform to the author:year:page format, this function returns None
    '''

    try:

        author, year, page = citekey.strip().split(':')

        if int(year) > 20:
            year = 1900 + int(year)
        else:
            year = 2000 + int(year)

        return query_bibtex(author, year, page)

    except ValueError:

        return None

# Initalize an empty list to contain all citekeys found in the paper
all_citekeys = []

# Check input file name
if not sys.argv[1].endswith('.tex'):
    raise Exception("Input filename should end in .tex")

# Open the input file
text = open(sys.argv[1], 'rb').read().replace('\n', ' ')

# Extract all citekeys
if "\cite" in text:
    pos1 = -1
    while True:
        try:
            pos1 = text.index('\cite', pos1 + 1)
            pos2 = text.index('{', pos1)
            pos3 = text.index('}', pos2)
            citekeys = text[pos2 + 1:pos3]
            all_citekeys += [s.lower() for s in citekeys.split(',')]
        except ValueError:
            break

# Create unique list
all_citekeys = list(set(all_citekeys))

# Sort list alphabetically
all_citekeys.sort()

# Query all the citekeys. We use multiprocessing.Pool to submit many requests
# at the same time. I'm sure ADS love me for this.
p = Pool(processes=25)
results = p.map(citekey_to_bibtex, all_citekeys)

# Create output file
f = open(sys.argv[1].replace('.tex', '_auto.bib'), 'wb')

# Loop through results, and write out
for entry in results:
    if entry is not None:
        f.write(entry)

# Close file
f.close()
