# Given an emacs org file with headings in the following format,
# generate an html using beautiful soup and pandas.
# The typical link block structure:
# ** LINK_TITLE
# :PROPERTIES:
# :ID: Link_ID
# :Title: Link Title = LINK_TITLE
# :Date: yyyy-mm-dd
# :Description: BRIEF_DESCRIPTION
# :CanonicalURI: -- this is my own url, which is set with rel="canonical" for SEO purposes
# :ExternalURI: -- this is the external url where i may have published my content
# :END:
# <longer meta description that could span several lines before the next heading>

from bs4 import BeautifulSoup  # to print out html code
import pandas as pd  # to read and wrangle source file
from datetime import datetime  # to sort writings chronologically
import export_to_org as org_export

# Read the org file
org_file_location = "./links.org"  # input("Enter the input .org file path:")
html_file_name = "content-portfolio.html"  # HTML output
org_file_name = "content-portfolio.org"  # ORG output

with open(org_file_location, 'r') as file:
    data = file.readlines()
file.close()

# Initialize org-mode property literals:
ORG_H1 = '* '
ORG_H2 = '** '
ORG_PROPERTIES = ':PROPERTIES:'
ORG_ID = ':ID:'
ORG_TITLE = ':Title:'
ORG_DATE = ':Date:'
ORG_DESCRIPTION = ':Description:'
ORG_CANONICAL_URI = ':CanonicalURI:'
ORG_EXTERNAL_URI = ':ExternalURI:'
ORG_END = ':END:'

# Initialize list of link dictionaries and a link dictionary for iteration
link_data = []
current_link = {}

# Parse the org file
end_of_h1_properties = False  # signal if we're done processing H1 properties, to store the category of links
end_of_h2_properties = False  # signal if the H2 properties block has ended, to read the meta description lines
link_category = '' # this will store the H1 titles, or link categories
for line in data:
    line = line.lstrip()  # remove any leading spaces

    if line.startswith(ORG_H1):
        end_of_h1_properties = False
        end_of_h2_properties = True
        # set the category of H2 links that follow - the title H1 by convention:
        link_category = line.strip(ORG_H1)

    if line.startswith(ORG_H2):
        # signal that new H2 properties are starting, so don't add ORG_H2 line and title to current meta desc.
        end_of_h2_properties = False
        end_of_h1_properties = True
        current_link = {}  # new dictionary

    if end_of_h1_properties:
        if line.startswith(ORG_PROPERTIES): # this is the :PROPERTIES: of H2
            # Start a new link
            # add the link category (from the title of ORG_H1_
            current_link['category'] = link_category
        elif line.startswith(ORG_ID):
            current_link['id'] = line.strip(ORG_ID).strip()
        elif line.startswith(ORG_TITLE):
            current_link['title'] = line.strip(ORG_TITLE).strip()
        elif line.startswith(ORG_DATE):
            current_link['date'] = line.strip(ORG_DATE).strip()
        elif line.startswith(ORG_DESCRIPTION):
            current_link['description'] = line.strip(ORG_DESCRIPTION).strip()
        elif line.startswith(ORG_CANONICAL_URI):
            current_link['canonicalURI'] = line.strip(ORG_CANONICAL_URI)
        elif line.startswith(ORG_EXTERNAL_URI):
            current_link['externalURI'] = line.strip(ORG_EXTERNAL_URI)
        elif line.startswith(ORG_END):
            end_of_h2_properties = True  # properties done, now read the meta text, if available
            current_link['meta_description'] = ''
            # Save the current link if it exists and has a date and at least a URI
            if current_link:
                if ('date' in current_link and
                        ('canonicalURI' in current_link or 'externalURI' in current_link)):
                    link_data.append(current_link)

        # if we're done processing :PROPERTIES: after reaching :END:, store any text between this line
        # and until we reach the next heading (see code above starting with if line.startswith(ORG_H2):)
        if end_of_h2_properties:
            if line.startswith(ORG_END):
                current_link['meta_description'] += line.strip(ORG_END)
            else:
                current_link['meta_description'] += line.strip()

# Convert the date strings to datetime objects and sort the list chronologically
link_data_sorted = sorted(link_data,
                          key=lambda writing: datetime.strptime(writing['date'],
                                                                '%Y-%m-%d') if 'date' in writing else datetime.min)

link_data = link_data_sorted
print(link_data)
# Instantiate a new BeautifulSoup object
soup = BeautifulSoup('<!DOCTYPE html><html></html>', 'html.parser')

############## Head content
# Add a meta description for SEO purposes:
head = soup.new_tag('head')
meta = soup.new_tag('meta')
meta.attrs['name'] = 'description'
meta.attrs['content'] = 'Content portfolio of Will Borici, Strategy and Entropy.'
head.append(meta)

# Add the style.css link in the head section
stylesheet = soup.new_tag('link', rel='stylesheet', href='https://strategyentropy.com/master-content/style.css')
head.append(stylesheet)

# once finished adding head tags, insert the head into the html
soup.html.insert(0, head)

############## Body content
body = soup.new_tag('body')

# Add a row for each link, but create a table for each link category
current_category = []  # grab all categories to generate a table for each:
for link in link_data:
    if link.get('category') not in current_category:
        current_category.append(link.get('category'))

for category in current_category:
    # create a div for the current category:
    category_div = soup.new_tag('div')
    category_div['id'] = category.strip('\n').replace(' ', '_') + '_id'
    category_div['class'] = 'div-heading'

    # Add the category name as the div name
    category_div.string = category

    # Add the div to the soup with the appended table
    soup.html.append(category_div)

    # place each table under the category_div:
    # create a new table for the current category:
    table = soup.new_tag('table')
    # assign the portfolio table style to override the category div style
    table['class'] = 'portfolio-table'

    for link in link_data:
        if link.get('category') == category:
            # now create the rows for this category:
            row = soup.new_tag('tr')
            table.append(row)

            # Add the date to the left column
            date = pd.to_datetime(link.get('date', ''))
            if pd.notnull(date):
                date_cell = soup.new_tag('td')
                # use the five-digit year, per Long Now:
                date_cell.string = '0' + date.strftime('%Y-%m-%d')
                row.append(date_cell)
            else:
                row.append(soup.new_tag('td'))

            # Add a bunch of other properties to the right column
            title = link.get('title', '')
            description = link.get('description', '')
            canonical_URI = link.get('canonicalURI', '').strip()
            external_URI = link.get('externalURI', '').strip()
            meta_description = link.get('meta_description', '')

            if title:
                title_cell = soup.new_tag('td')
                if len(canonical_URI) > 0:  # prefer canonical URIs before external ones
                    a_tag = soup.new_tag('a', href=canonical_URI)
                    if description:
                        a_tag['title'] = description
                    a_tag['rel'] = 'canonical'  # prefer internal link first, but ensure rel="canonical" for SEO
                    a_tag.string = title
                    title_cell.append(a_tag)
                elif len(external_URI) > 0:
                    EXTERNAL_LINK_CSS_CLASS = "external text"  # css a.external.text for PNG arrow
                    a_tag = soup.new_tag('a', href=external_URI)
                    a_tag['class'] = EXTERNAL_LINK_CSS_CLASS
                    a_tag['target'] = '_blank'
                    if description:
                        a_tag['title'] = description
                    a_tag.string = title
                    title_cell.append(a_tag)
                else:  # just print static title
                    title_cell.string = title

                row.append(title_cell)
            else:
                row.append(soup.new_tag('td'))

            if meta_description:
                meta_cell = soup.new_tag('td')
                meta_cell.string = meta_description
                row.append(meta_cell)
            else:
                row.append(soup.new_tag('td'))

        # add the table to the current category div
        category_div.append(table)

    # add the category contents to the body
    body.append(category_div)

# append the body tag:
soup.html.append(body)

str_html = soup.prettify()
# Write the HTML to a file
with open(html_file_name, 'w') as file:
    file.write(str_html)
file.close()

# export str_html to org:
# NB: the following function is defined in a file in .gitignore (sorry!)
org_export.export_string_to_org(org_file_name, str_html)
