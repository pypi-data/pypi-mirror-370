from radboy.DB.db import *
from radboy.DB.RandomStringUtil import *
import radboy.Unified.Unified as unified
import radboy.possibleCode as pc
from radboy.DB.Prompt import *
from radboy.DB.Prompt import prefix_text
from radboy.TasksMode.ReFormula import *
from radboy.TasksMode.SetEntryNEU import *
from radboy.FB.FormBuilder import *
from radboy.FB.FBMTXT import *
from radboy.RNE.RNE import *
from radboy.Lookup2.Lookup2 import Lookup as Lookup2
from radboy.DayLog.DayLogger import *
from radboy.DB.masterLookup import *
from collections import namedtuple,OrderedDict
import nanoid,qrcode,io
from password_generator import PasswordGenerator
import random
from pint import UnitRegistry
import pandas as pd
import numpy as np
from datetime import *
from colored import Style,Fore
import json,sys,math,re,calendar,hashlib,haversine
from time import sleep
import itertools
import decimal
unit_registry=pint.UnitRegistry()
def area_triangle():
	height=None
	base=None
	'''
	A=hbb/2
	'''
	while True:
		try:
			base=Control(func=FormBuilderMkText,ptext="base",helpText="base width",data="string")
			if base is None:
				return
			elif base in ['d',]:
				base=unit_registry.Quantity('1')
			else:
				base=unit_registry.Quantity(base)
			break
		except Exception as e:
			print(e)
			try:
				base=Control(func=FormBuilderMkText,ptext="base no units",helpText="base width,do not include units",data="dec.dec")
				if base is None:
					return
				elif base in ['d',]:
					base=decc(1)
				break
			except Exception as e:
				continue

	while True:
		try:
			height=Control(func=FormBuilderMkText,ptext="height",helpText="height width",data="string")
			if height is None:
				return
			elif height in ['d',]:
				height=unit_registry.Quantity('1')
			else:
				height=unit_registry.Quantity(height)
			break
		except Exception as e:
			print(e)
			try:
				height=Control(func=FormBuilderMkText,ptext="height no units",helpText="height width, do not include units",data="dec.dec")
				if height is None:
					return
				elif height in ['d',]:
					height=decc(1)
				break
			except Exception as e:
				continue
	print(type(height),height,type(base))
	if isinstance(height,decimal.Decimal) and isinstance(base,decimal.Decimal):
		return decc((height*base)/decc(2))
	elif isinstance(height,pint.Quantity) and isinstance(base,pint.Quantity):
		return ((height.to(base)*base)/2)
	elif isinstance(height,pint.Quantity) and isinstance(base,decimal.Decimal):
		return ((height*unit_registry.Quantity(base,height.units))/2)
	elif isinstance(height,decimal.Decimal) and isinstance(base,pint.Quantity):
		return ((unit_registry.Quantity(height,base.units)*base)/2)