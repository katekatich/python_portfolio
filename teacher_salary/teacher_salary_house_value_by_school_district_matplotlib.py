import numpy as np
import pandas as pd
import math #to find the ceiling of a float
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings

from matplotlib import ticker as mtick

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 35)
pd.set_option('display.max_colwidth', 150)
pd.set_option('future.no_silent_downcasting', True)

###STEP 1: Read and prepare house values data.
#https://data.census.gov/table/ACSDT1Y2017.B25075?t=Housing%20Value%20and%20Purchase%20Price&g=9700000US1705220,1708430,5101260,5102250&y=2017
housefile = 'housing_data/census_acs5_2017_owner_occupied_house_values.csv'

house_df = pd.read_csv(housefile, header=0, skiprows=[1], usecols=[0,1,3,5,7]) #skips hardcoded totals; when n number of school districts is chosen, usecols should go to n*2-1

## Removes extraneous '!!' and 'Estimate' from original column names
column_renames = house_df.columns.str.split('!!').str.get(0)

house_df.columns = column_renames
house_df['house_values'] = house_df['Label (Grouping)']
house_df.drop('Label (Grouping)', axis=1, inplace=True)
house_df['house_values'] = house_df['house_values'].str.lstrip()

## Strips text out of string fields and reassigns the data type as int32.
for col_name, col in house_df.items():
	if col_name !='house_values':
		if col.dtype=='object':
			col=col.str.strip('\u00B1')
			col=col.str.replace(',','')
			col= col.astype('int32')
		house_df[col_name]=col

#Isolate the last number in the label,e.g "14,999" from "$10,000 to $14,999"; create a list for each label consisting of chunks originally separated by commas,e.g [14, 999]
house_df['house_label'] = house_df['house_values'].str.rsplit(' ').str.get(-1).str.strip('$').str.split(',')

#Create x-axis labels
house_val_lab={}
house_int_vals = {}
for i, row in house_df.iterrows():
	separator=''
	label=separator.join(row['house_label'])
	
	if i!=0 and i!=25 and i!=23 and i!=24: # 'or' does not work, the 'and' is exclusive
		val=int(label)+1
		lab = str(val)
	elif i==0:
		val=int(label)
		lab=label	
	elif i in [23,24,25]:
		val=1000001
		lab=label
	
	if len(lab)>=5 and len(lab)<7:
		label_='$'+lab.removesuffix('000')+'k'
	elif len(lab)>6:
		pre_label=lab.removesuffix('00000')
		it=iter(pre_label)
		first=next(it)
		second=next(it)
		label_='$'+first+'.'+second+'M'
	else:
 		label_=label	
	house_val_lab[row['house_values']]=label_
	house_int_vals[row['house_values']]=val

house_df['house_val_labels']=house_df['house_values'].replace(house_val_lab)
house_df['house_ints']=house_df['house_values'].replace(house_int_vals)


## Create a list of districts by stripping the term 'estimate' from the estimate column names.
district_list = []
for col_name, col in house_df.items():
	if ',' in col_name:
		brief_name = col_name.split(',')[0]
		district_list.append((col_name, brief_name))#.split(',')[0])


##STEP 2: Read and prepare teacher salary data.
salaryilfile = 'teacher_data/illinois_teacher_salary_study_2017.xlsx'
salary_il_df = pd.read_excel(salaryilfile, usecols=[1,19])#, usecols=[1,16,19])
salary_il_df.columns=salary_il_df.columns.str.replace('Beginning','Starting')

district_name_map={}
for i, row in salary_il_df.iterrows():
	district_name_list = row['District Name'].split(' ')
	length = len(district_name_list)
	new_list =[]
	for word in district_name_list:
		word2 = word.replace('CUSD','Community Unit School District')
		word3 = word2.replace('CCSD','Community Consolidated School District')
		word4 = word3.replace('USD','Unit School District')
		word5 = word4.replace('GSD','Grade School District')
		word6 = word5.replace('CHSD','Community High School District')
		word7 = word6.replace('ESD','Elementary School District')
		word8 = word7.replace('HSD','High School District')
		word9 = word8.replace('UD','Unit School District')
		word10 = word9.replace('SD','School District')
		new_list.append(word10)
	new_district=' '.join(new_list)	
	district_name_map[row['District Name']]=new_district
salary_il_df['District Name']=salary_il_df['District Name'].replace(district_name_map)	

for col_name, col in salary_il_df.items():
	col_name=col_name.strip()

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
salaryvafile = 'teacher_data/virginia_teacher_salary_study_2017.xlsx'
salary_va_df = pd.read_excel(salaryvafile, sheet_name='Starting Teacher Salaries', skiprows=5, nrows=133, usecols=[1,3])#usecols=[1,2,3])

salary_va_df['District Name']=salary_va_df['Division Name']
salary_va_df.drop('Division Name', axis=1, inplace=True)
for col_name, col in salary_va_df.items():
	col_name=col_name.strip()

salary=pd.concat([salary_va_df, salary_il_df], axis=0)

## STEP 3: Build teh visualization.

##Create a tuple of districts and subplot locations on the figure.
n_rows=math.ceil(len(district_list)/2)
axes_list = [(x,y) for x in range(n_rows) for y in range(2)]
district_axes = zip(district_list, axes_list)

def thousands(x,pos):
	"""The two arguements are the value and the tick position."""
	return f'{x:,.0f}'

def make_axes2(district, m, n, sal_name):
	"""Specifies and creates axis variables for each district into a different subplot."""
	sal = salary[salary['District Name']==sal_name]["Master's Starting Salary"].values[0]
	color_map={}
	for i, row in house_df.iterrows():
		if row['house_ints']<=sal*4:
			color_map[i]='blue'
		else:
			color_map[i]='red'
	house_df[district+'_affordable']=color_map
	ax[m,n].bar(house_df['house_val_labels'], house_df[district], color=house_df[district+'_affordable'])
	name=district.replace('_', ' ').title()
	ax[m,n].set_xlabel(name)
	ax[m,n].set(xticks=[2, 9, 16, 23])
	ax[m,n].yaxis.set_major_formatter(thousands)
	
def run_make_axes2():
	"""Assigns values for arguments in the make_axes() fn by unpacking the district_axes list and tuple."""	
	for district_list, axes in district_axes:
		d, name=district_list
		x,y=axes
		make_axes2(d,x,y,name)

## Make small multiples
fig,ax = plt.subplots(n_rows,2, figsize=(11,8))
run_make_axes2()
handles, labels = ax[n_rows-1,1].get_legend_handles_labels()
red_patch = mpatches.Patch(color='blue', label='Affordable')
blue_patch = mpatches.Patch(color='red', label='Not Affordable')
fig.legend(handles=[red_patch, blue_patch], loc='upper right')
plt.figtext(0.5, 0.92, "Affordability is based on 4 times the starting salary for a teacher with a master's degree.",ha='center', fontsize=12)
plt.figtext(0.1, 0.0075, "Sources: data.census.gov, American Community Survey, B25075; Illinois Teacher Salary Study 2016-2017, https://www.isbe.net/Pages/TeacherSalaryStudy.aspx;\n2016-2017 Teacher Salary Report, https://www.doe.virginia.gov/teaching-learning-assessment/teaching-in-virginia/education-workforce-data-reports", ha="left", fontsize=8)
plt.figtext(.045, .1, "Estimated number of homes at or under a particular price", rotation='vertical', snap=True,  fontsize=12)
fig.suptitle('House Values by School District in 2017', fontsize=14)
plt.show()




