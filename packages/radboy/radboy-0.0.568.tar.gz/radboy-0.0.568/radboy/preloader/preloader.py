from . import *
unit_registry=pint.UnitRegistry()

def volume():
	height=Prompt.__init2__(None,func=FormBuilderMkText,ptext="height?: ",helpText="height=1",data="dec.dec")
	if height is None:
		return
	elif height in ['d',]:
		height=Decimal('1')
	
	width=Prompt.__init2__(None,func=FormBuilderMkText,ptext="width?: ",helpText="width=1 ",data="dec.dec")
	if width is None:
		return
	elif width in ['d',]:
		width=Decimal('1')
	


	length=Prompt.__init2__(None,func=FormBuilderMkText,ptext="length?: ",helpText="length=1",data="dec.dec")
	if length is None:
		return
	elif length in ['d',]:
		length=Decimal('1')

	return length*width*height

def volume_pint():
	height=Prompt.__init2__(None,func=FormBuilderMkText,ptext="height?: ",helpText="height=1",data="string")
	if height is None:
		return
	elif height in ['d',]:
		height='1'
	
	width=Prompt.__init2__(None,func=FormBuilderMkText,ptext="width?: ",helpText="width=1 ",data="string")
	if width is None:
		return
	elif width in ['d',]:
		width='1'
	


	length=Prompt.__init2__(None,func=FormBuilderMkText,ptext="length?: ",helpText="length=1",data="string")
	if length is None:
		return
	elif length in ['d',]:
		length='1'

	return unit_registry.Quantity(length)*unit_registry.Quantity(width)*unit_registry.Quantity(height)

def inductance_pint():
	relative_permeability=Prompt.__init2__(None,func=FormBuilderMkText,ptext="relative_permeability?: ",helpText="relative_permeability(air)=1",data="string")
	if relative_permeability is None:
		return
	elif relative_permeability in ['d',]:
		relative_permeability='1'
	relative_permeability=float(relative_permeability)

	turns_of_wire_on_coil=Prompt.__init2__(None,func=FormBuilderMkText,ptext="turns_of_wire_on_coil?: ",helpText="turns_of_wire_on_coil=1",data="string")
	if turns_of_wire_on_coil is None:
		return
	elif turns_of_wire_on_coil in ['d',]:
		turns_of_wire_on_coil='1'
	turns_of_wire_on_coil=int(turns_of_wire_on_coil)

	#convert to meters
	core_cross_sectional_area_meters=Prompt.__init2__(None,func=FormBuilderMkText,ptext="core_cross_sectional_area_meters?: ",helpText="core_cross_sectional_area_meters=1",data="string")
	if core_cross_sectional_area_meters is None:
		return
	elif core_cross_sectional_area_meters in ['d',]:
		core_cross_sectional_area_meters='1m'
	try:
		core_cross_sectional_area_meters=unit_registry.Quantity(core_cross_sectional_area_meters).to("meters")
	except Exception as e:
		print(e,"defaulting to meters")
		core_cross_sectional_area_meters=unit_registry.Quantity(f"{core_cross_sectional_area_meters} meters")

	length_of_coil_meters=Prompt.__init2__(None,func=FormBuilderMkText,ptext="length_of_coil_meters?: ",helpText="length_of_coil_meters=1",data="string")
	if length_of_coil_meters is None:
		return
	elif length_of_coil_meters in ['d',]:
		length_of_coil_meters='1m'
	try:
		length_of_coil_meters=unit_registry.Quantity(length_of_coil_meters).to('meters')
	except Exception as e:
		print(e,"defaulting to meters")
		length_of_coil_meters=unit_registry.Quantity(f"{length_of_coil_meters} meters")
	
	numerator=((turns_of_wire_on_coil**2)*core_cross_sectional_area_meters)
	f=relative_permeability*(numerator/length_of_coil_meters)*1.26e-6
	f=unit_registry.Quantity(f"{f.magnitude} H")
	return f


	
preloader={
	f'{uuid1()}':{
						'cmds':['volume',],
						'desc':f'find the volume of height*width*length without dimensions',
						'exec':volume
					},
	f'{uuid1()}':{
						'cmds':['volume pint',],
						'desc':f'find the volume of height*width*length using pint to normalize the values',
						'exec':volume_pint
					},
	f'{uuid1()}':{
						'cmds':['self-inductance pint',],
						'desc':f'find self-inductance using pint to normalize the values for self-inductance=relative_permeability*(((turns**2)*area)/length)*1.26e-6',
						'exec':inductance_pint
					},
}

