#!/usr/bin/env python
import re
import sys
from bs4 import BeautifulSoup

soup = BeautifulSoup(open(sys.argv[1]))

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

combine_citation_links(soup)
remove_font_spans(soup) 
print soup.encode(encoding="utf-8", formatter="html")
