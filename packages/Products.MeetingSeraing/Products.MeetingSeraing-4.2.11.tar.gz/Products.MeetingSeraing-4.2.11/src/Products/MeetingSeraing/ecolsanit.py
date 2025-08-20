#!/usr/bin/env python
#coding:utf-8
# Author:  Hughes Damry -- hghes@damry.org
# Purpose: Nettoyer les templates d'eCollege
# Created: 10/06/2015

VERSION = '1.00'

from os.path import dirname
from os.path import join as pjoin

import sys


APPPATH = dirname(__file__)
APPNAME = 'ecolsanit'

class template(object):
  #REMPLACEMENTS = (('\xc2\xa0 \xc2\xa0 ', '&nbsp;'),
  #                 ('\xc2\xa0\xc2\xa0','&nbsp;'),
  #                 (' \xc2\xa0','&nbsp;'),
  #                 ('\xc2\xa0 ','&nbsp;'),
  #                 ('<p> \xc2\xa0','<p>'),
  #                 ('<p>\xc2\xa0','<p>'),
  #                 ('\xc2\xa0 </p>','</p>'),
  #                 ('\xc2\xa0</p>','</p>'),
  #                 ('  ','&nbsp;'),
  #                 ('&nbsp; &nbsp;','&nbsp;'),
  #                 ('&nbsp;&nbsp;','&nbsp;'),
  #                 (' &nbsp;','&nbsp;'),
  #                 ('&nbsp; ','&nbsp;'),
  #                 ('<p> &nbsp;','<p>'),
  #                 ('<p>&nbsp;','<p>'),
  #                 ('&nbsp; </p>','</p>'),
  #                 ('&nbsp;</p>','</p>'),
  #                 )

  REMPLACEMENTS = ((':','&nbsp;: ')
                   (';','&nbsp;; '),
                   ('!','&nbsp;! '),
                   ('?','&nbsp;? '),
                   ('€','&nbsp;€ '),
                   ('%','&nbsp;% '),
                   ('n°','n°&nbsp;'),
                   ('N°','N°&nbsp;'),
                   (',',', '),
                   (' ,',','),
                   ('( ','('),
                   ('(',' ('),
                   (' )',')'),
                   (')',') '),
                   ('Monsieur','M.&nbsp;'),
                   ('Madame','Mme&nbsp;'),
                   ('Mademoiselle','Mlle&nbsp;'),
                   ('Messieurs','MM.&nbsp;'),
                   ('Maître','Me&nbsp;'),
                   ('\xc2\xa0 \xc2\xa0 ', '&nbsp;'),
                   ('\xc2\xa0\xc2\xa0','&nbsp;'),
                   (' \xc2\xa0','&nbsp;'),
                   ('\xc2\xa0 ','&nbsp;'),
                   ('<p> \xc2\xa0','<p>'),
                   ('<p>\xc2\xa0','<p>'),
                   ('\xc2\xa0 </p>','</p>'),
                   ('\xc2\xa0</p>','</p>'),
                   ('  ','&nbsp;'),
                   ('&nbsp; &nbsp;','&nbsp;'),
                   ('&nbsp;&nbsp;','&nbsp;'),
                   (' &nbsp;','&nbsp;'),
                   ('&nbsp; ','&nbsp;'),
                   ('<p> &nbsp;','<p>'),
                   ('<p>&nbsp;','<p>'),
                   ('&nbsp; </p>','</p>'),
                   ('&nbsp;</p>','</p>'),
                   )

  VERBES=('ABROGE', 'ACCEPTE', 'ACCORDE', 'ADRESSE', 'AFFECTE', 'APPROUVE', 'ARRETE', 'AUTORISE', 'CERTIFIE', 'CHARGE', 'CONCLUT', 'CONSTATE', 'DECIDE', 'DELIVRE', 'DESIGNE', 'DRESSE', 'FIXE', 'IMPOSE', 'IMPUTE', 'INFORME', 'INVITE', 'LANCE', 'MARQUE SON ACCORD', 'MODIFIE', 'OCTROIE', 'PRECISE', 'PREND ACTE', 'PREND CONNAISSANCE', 'PROCEDE', 'PROLONGE', 'PRONONCE', 'RATIFIE', 'RECONDUIT', 'REFUSE', 'REGRETTE', 'RENVOIE', 'SOUMET', 'SUSPEND', 'VISE')
  YELLOWDEB = '<span style="background-color:Yellow">'
  YELLOWDEB2 = '<span style="background-color:yellow">'
  YELLOWEND = '</span>'
  def __init__(self,s):
    self.sanitext=''
    self.text = s

  def __remplacements(self,s):
    for r in self.REMPLACEMENTS:
      while s.find(r[0])>-1:
        s=s.replace(r[0],r[1])
    return s
    
  def sanitize(self):
    idxdeb=0
    lastidxdeb=0
    while idxdeb>-1:
      idxdeb = self.text.find(self.YELLOWDEB,idxdeb)
      idxdeb2 = self.text.find(self.YELLOWDEB2,idxdeb)
      if idxdeb2 > -1 and idxdeb2 < idxdeb:
        idxdeb = idxdeb2
      if idxdeb > -1:
        self.sanitext += self.__remplacements(self.text[lastidxdeb:idxdeb])
        idxend = self.text.find(self.YELLOWEND,idxdeb +len(self.YELLOWDEB))
        if idxend >-1:
          self.sanitext += self.text[idxdeb:idxend +len(self.YELLOWEND)]
          idxdeb = idxend + len(self.YELLOWEND)
          lastidxdeb= idxend + len(self.YELLOWEND)
        else:
          self.sanitext += self.text[idxdeb:]
          lastidxdeb=len(self.text)
    if lastidxdeb ==-0:
      self.sanitext = self.__remplacements(self.text)
    elif lastidxdeb < len(self.text):
      self.sanitext += self.__remplacements(self.text[lastidxdeb:])
    for v in self.VERBES:
      self.sanitext = self.sanitext.replace('<p>%s</p>' % v,'<p class="sdecide">%s</p>' % v)
      self.sanitext = self.sanitext.replace('<p>\xc2\xa0%s</p>' % v,'<p class="sdecide">%s</p>' % v)
      self.sanitext = self.sanitext.replace('<p>%s\xc2\xa0</p>' % v,'<p class="sdecide">%s</p>' % v)
      self.sanitext = self.sanitext.replace('<p> %s </p>' % v,'<p class="sdecide">%s</p>' % v)
      self.sanitext = self.sanitext.replace('<p>\xc2\xa0&nbsp;%s</p>' % v,'<p class="sdecide">%s</p>' % v)
 

def main():
  t=template(sys.stdin.read())
  t.sanitize()
  print t.sanitext

def maintest():
  pass

if __name__=='__main__':
  main()
