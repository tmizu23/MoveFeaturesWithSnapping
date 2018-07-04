# -*- coding: utf-8 -*-

def name():
    return "MoveFeaturesWithSnapping"


def description():
    return "MoveFeaturesWithSnapping"


def version():
    return "Version 0.2.0"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "2.18"

def author():
    return "Takayuki Mizutani"

def email():
    return "mizutani@ecoris.co.jp"

def classFactory(iface):
  from movefeatureswithsnapping import MoveFeaturesWithSnapping
  return MoveFeaturesWithSnapping(iface)

