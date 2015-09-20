#!/usr/bin/env python
import re
import sys
from bs4 import BeautifulSoup, Comment, Doctype

# soup = BeautifulSoup(open(sys.argv[1]), "html.parser")
soup = BeautifulSoup(open(sys.argv[1]), "html5lib")


def combine_citation_links(soup):
  for e in soup.find_all("a", href=re.compile("^#")):
    # print e
    # print '---'
    # print (True if e.parent else False)
    # print '==='
    # print e.next_sibling == u',\xa0'
    # print '+++'
    # print True if e.next_sibling.next_sibling.children else False
    # e.parent and
    
    
    # if comma separates the parts of a references:
    #if e.next_sibling == u',\xa0' and e.next_sibling.next_sibling.children:
    if e.next_sibling == u'\xa0' and e.next_sibling.next_sibling.children:
      #print e
      comma_space_node = e.next_sibling
      year_node_a      = e.next_sibling.next_sibling
      assert e.href == year_node_a.href # should be always the same, because we want to merge those two <a> tags
      year_node        = year_node_a.contents[0]
      comma_space_node.extract()
      year_node_a.extract()
      e.append(comma_space_node)
      e.append(year_node)


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
    if e.has_attr('name') and e['name'] in ['date', 'src', 'originator', 'generator']:
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
      

def wrap_body_in_article(soup):
    body = soup.find("body")
    article = soup.new_tag("article")
    # can't loop over .contents directly because it is changing
    while len(body.contents) > 0:
        article.append(body.contents[0].extract())
    body.append(article)


wrap_body_in_article(soup)
remove_tex4ht_comments(soup)
remove_unwanted_meta(soup)

remove_superfluous_id_after_footnote(soup)
combine_citation_links(soup)
remove_font_spans(soup) 
print soup.encode(encoding="utf-8", formatter="html")
