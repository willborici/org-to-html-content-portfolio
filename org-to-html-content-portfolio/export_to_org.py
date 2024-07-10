
# create a content-portfolio.org file as well, based on my org file structures:
# They have preamble (first #+INCLUDE directive), a title and some properties
# and the postamble (last #+INCLUDE directive).
# TODO DO NOT commit this code to git
def export_string_to_org(org_file_name, str_html):
    org_header = '''#+INCLUDE: "/Users/wb/Documents/strategyentropy.com/master-content/preamble.org" \n\n
                    #+TITLE: Content Portfolio 
                    #+CREATE_DATE: 02008-08-18 
                    #+UPDATE_DATE: 02024-07-09 
                    #+EXPORT_FILE_NAME: writings 
                    #+DESCRIPTION: Index of offsite and onsite published work 
                    #+KEYWORDS: articles, guest posts, posts, essays, books'''

    org_footer = '#+INCLUDE: "/Users/wb/Documents/strategyentropy.com/master-content/postamble.org"'

    with open(org_file_name, 'w') as file:
        file.write(org_header + '\n\n')
        for line in str_html.splitlines():
            file.write('#+HTML: ' + line + '\n\n')
        file.write(org_footer)
    file.close()
