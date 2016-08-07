#!/usr/bin/env python
import re
import sys
from bs4 import BeautifulSoup, Comment, Doctype, Tag, NavigableString

# soup = BeautifulSoup(open(sys.argv[1]), "html.parser")
soup = BeautifulSoup(open(sys.argv[1]), "html5lib")


def combine_citation_links(soup):
    for e in soup.find_all("a", href=re.compile("^#")):
        # find_all will create a list, that also contains stuff
        # we already processed, i.e., without parent
        if e.parent is None:
            continue

        if e.previous_sibling == u',\xa0':
            # within a list, use normal spaces to avoid typesetting issues
            e.previous_sibling.replace_with(", ")

        # also ignore just year links, we might just have fixed the space before
        if e.contents[0].isnumeric():
            continue

        # Process text like '<a>Author</a>&nbsp;[<a>Year</a>]'
        if (e.next_sibling == u'\xa0[' and e.next_sibling and
                e.next_sibling.next_sibling and
                e.next_sibling.next_sibling.next_sibling):
            space_bracket = e.next_sibling
            year_node_a   = e.next_sibling.next_sibling
            following_bracket_and_more = e.next_sibling.next_sibling.next_sibling

            if unicode(following_bracket_and_more)[0] == ']':
                assert e.attrs['href'] == year_node_a.attrs['href'], "should be always the same, because we want to merge those two <a> tags"
                year = unicode(year_node_a.contents[0])
                e.contents[0].replace_with(e.contents[0] + u'\xa0[' + year + "]")
                space_bracket.extract()
                year_node_a.extract()

                # remove closing bracket
                following_bracket_and_more.replace_with(
                    unicode(following_bracket_and_more)[1:])
                continue
            else:
                # transform 'Author&nbsp;[<a>Year</a>, <a>Year2</a>]'
                e.replace_with(e.contents[0])  # remove link from author
                continue

        # Process text like '[<a>Author</a>,&nbsp;<a>Year</a>]'
        # This also includes situations with multiple references, that are
        # listed with author+year.
        if (e.next_sibling == u',\xa0' and
                isinstance(e.next_sibling.next_sibling, Tag) and
                e.next_sibling.next_sibling.name == "a" and
                e.next_sibling.next_sibling.attrs['href'] == e.attrs['href']):
            comma_space_node = e.next_sibling
            year_node_a      = e.next_sibling.next_sibling
            year_node        = year_node_a.contents[0]

            if (year_node_a.next_sibling and
                    year_node_a.next_sibling.next_sibling and
                    year_node_a.next_sibling.next_sibling.name == "a" and
                    year_node_a.next_sibling.next_sibling.contents[0].isnumeric()):
                # looks like we got multiple years with the same author in
                # succession, remove the link on the author to avoid confusion
                prev = e.previous_sibling
                if prev == u',\xa0':
                    prev.replace_with(", ")
                elif (isinstance(prev, NavigableString) and
                        unicode(prev)[-1] == "["):
                    prev.replace_with(s[:-2] + u"\N{THIN SPACE}[")
                e.replace_with(e.contents[0])

            else:
                comma_space_node.extract()
                year_node_a.extract()
                e.append(comma_space_node)
                e.append(year_node)

                # if we are the first in the list, make sure the bracket is
                # directly connected with a &thinsp; to the element before
                if isinstance(e.previous_sibling, NavigableString):
                    s = unicode(e.previous_sibling)
                    if s[-1] == "[" and s[-2].isspace():
                        e.previous_sibling.replace_with(s[:-2] +
                                                        u"\N{THIN SPACE}[")


def remove_font_spans(soup):
    for e in soup.find_all("span", {'class' : re.compile("^cm") }):
        e.replace_with(e.contents[0])
    for e in soup.find_all("span", {'class' : re.compile("^pcrr") }):
        e.replace_with(e.contents[0])
    for e in soup.find_all("span", {'class' : re.compile("^ptmr") }):
        e.replace_with(e.contents[0])


def remove_following_newline(e):
    sibling = e.next_sibling
    if sibling.string == '\n':
        sibling.extract()


def remove_unwanted_meta(soup):
    for e in soup.find_all("meta"):
        if e.has_attr('name') and e['name'] in ['date', 'src', 'originator',
                                                'generator']:
            remove_following_newline(e)
            e.extract()


def remove_tex4ht_comments(soup):
    for e in soup.find_all(text=lambda text:isinstance(text, Doctype)):
        remove_following_newline(e)
        e.extract()

    for e in soup.find_all(text=lambda text:isinstance(text, Comment)):
        if 'fn-in,' in e.string or e.string.startswith('?xml') or e.string.startswith('http://www.w3.org/TR/xhtml1'):
            remove_following_newline(e)
            e.extract()
        else:
            print e


def remove_superfluous_id_after_footnote(soup):
    for e in soup.find_all("sup", {'class' : 'textsuperscript'}):
        sib = e.next_sibling
        if sib.name == "a" and sib.has_attr('id') and sib.has_attr('name') and sib['id'] == sib['name']:
            sib.extract()
      

def transform_header(soap):
    head = soup.find("div", {"class" : "maketitle"})
    if (not head or head.contents[1].name != "h2" or
                head.contents[3].name != "div"):
        return  # the format of the header is not currently supported

    if head.contents[0] == "\n":
        head.contents[0].extract()
    title_h2 = head.contents[0].extract()
    title = title_h2.getText()

    if head.contents[0] == "\n":
        head.contents[0].extract()
    author_div = head.contents[0].extract()
    authors = author_div.string

    title_h1 = soup.new_tag("h1")
    title_h1.string = title

    title_tag = soup.find("title")
    title_tag.string = title
    meta_author = soup.new_tag("meta")
    meta_author.attrs['name'] = "author"
    meta_author.attrs['content'] = authors

    head_tag = soup.find("head")
    head_tag.append(meta_author)

    header = soup.new_tag("header")
    header.append(title_h1)
    header.append(author_div)

    while len(head.contents) > 0:
        e = head.contents[0].extract()
        header.append(e)
    head.replace_with(header)

    # move abstract, if available
    abstract = soup.find("div", {"class" : "abstract"})
    if abstract and abstract.find("div", {"class" : "center"}):
        header.append(abstract.extract())
        ab_t = abstract.find("div", {"class" : "center"})
        if ab_t.p.string == "Abstract":
            ab_t.extract()
            ab_t = soup.new_tag("h3")
            ab_t.string = "Abstract"
            abstract.insert(0, ab_t)


def wrap_body_in_article(soup):
    body = soup.find("body")
    article = soup.new_tag("article")
    # can't loop over .contents directly because it is changing
    while len(body.contents) > 0:
        article.append(body.contents[0].extract())
    body.append(article)


def add_line_numbers_to_listings(soup):
    for f in soup.find_all("figure"):
        div_ln = f.find("div", {"class" : "linenumbers"})
        if div_ln:
            code = f.find("code")
            lines = code.find_all("a")  # find by labels, might be brittle
            ln_nums = " ".join([str(i) for i in range(1, len(lines) + 1)])
            div_ln.string = ln_nums


wrap_body_in_article(soup)
remove_tex4ht_comments(soup)
remove_unwanted_meta(soup)

remove_superfluous_id_after_footnote(soup)
combine_citation_links(soup)
remove_font_spans(soup)
transform_header(soup)
add_line_numbers_to_listings(soup)
result = soup.encode(encoding="utf-8", formatter="html")

result = result.replace('\xef\xac\x80', 'ff')
result = result.replace('\xef\xac\x81', 'fi')
result = result.replace('\xef\xac\x82', 'fl')
result = result.replace('\xef\xac\x83', 'ffi')
result = result.replace('\xef\xac\x84', 'ffl')

print result
