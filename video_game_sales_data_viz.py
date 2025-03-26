import pandas as pd
import numpy as np
#import missingno as msno
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import PercentFormatter
import seaborn as sns
import pickle

from great_tables import GT, md, html, style, loc, vals

# Set print display options
pd.set_option('display.max_rows', 200)
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_colwidth', 150)

# Suppress chained assignments warning
pd.options.mode.chained_assignment = None 

# Set palette for visualizations.
palette = sns.color_palette("Paired")
sns.set_palette(palette="Paired", n_colors=12)

# Formatting Functions
def custom_dollar_formatter(x):
    """Returns $X.XXB if number in millions is 4 or more digits long, returns $X.XXM if number is less than 1. For formatting numbers in tables."""
    if x > 1000:
        return f'${x/1000:,.2f}B'
    elif x >1:
        return f'${x:,.0f}M'
    else:
        return f'${x*1000000:,.0f}'      
  
# def custom_dollar2f_formatter(x):
#     """Returns $X.XXB if number in millions is 4 or more digits long, otherwise returns $X.XXM. For formatting numbers in tables."""
#     return f'${x/1000:,.2f}B'if x > 1000 else f'${x:,.2f}M'    

# def custom_percent_formatter(x):
#     """Returns $X.XXB if number in millions is 4 or more digits long, otherwise returns $X.XXM. For formatting numbers in tables."""
#     return f'{x*100:,.2f}%'    

# def custom_formatter(x, pos):
#     """Returns ($X,XXX) if number is less than 0, otherwise returns $X,XXX. For formatting tick mark labels."""
#     return f'(${abs(x*1000000):,.0f})' if x < 0 else f'${x*1000000:,.0f}'    


# # Table Creation Functions
# def games_sales_table (df, ttl):
#     """Creates a table with game titles and associated global sales."""
#     tbl = GT(df[['Name', 'Global_Sales']]).tab_header(
#         title=ttl).fmt(custom_dollar2f_formatter, columns='Global_Sales').cols_label(
#     Global_Sales=html("Global Sales")).tab_style(
#     style=style.text(color='black'),
#     locations=[loc.body(), loc.column_labels()])
#     return tbl

    
# def game_year_platform_table(df, ttl):
#     """Creates a table with game title, platform, and year."""
#     tbl = GT(df[['Name', 'Year', 'Platform']]).tab_header(title=ttl).tab_style(
#     style=style.text(color='black'),
#     locations=[loc.body(), loc.column_labels()])
#     return tbl

# def impact_of_missing_table(dfs_enum, field):
#     """Creates a table showing the percentage of data recaptured by data cleaning methods.""" 
#     # Create a list of row heading titles.
#     row_headings_list = ['All Records', 'Missing Records Before Fix', 'Missing Records After First Fix', 'Missing Records After Second Fix']

#     impact = []
#     for i, df in dfs_enum:
#         #Sum global sales associated with all remaining records within this dataframe.
#         sales= df[['Global_Sales']].sum(axis=0)
#         # Create a tuple from the global sales float and a count of all records within this dataframe.
#         totals = (sales.iloc[0], df.shape[0])
#         # Add a row heading label to the tuple.
#         totals_labeled = (row_headings_list[i], totals)
#         # Place the tuple in a list.
#         impact.append(totals_labeled)

#     missing_list = []
#     for row_heading,totals in impact:
#         #Unpack the sales records from the tuple
#         sales, records = totals
#         #Create a dictionary for each row of the table.  complete_records and games_total_sales are global variables.
#         tbl={'row_heading':row_heading,'Number of Records':'{:,.0f}'.format(records), '% of Records':'{:,.2%}'.format(records/complete_records), 'Sales':sales,'% of Sales':'{:,.2%}'.format(sales/games_total_sales)}
#         #Create a list of table row dictionaries.
#         missing_list.append(tbl)
#     #Convert the list of dictionaries into a dataframe.    
#     missing_df = pd.DataFrame(missing_list)
#     #Create a nice looking table from the dataframe.
#     missing_tbl = GT(missing_df).tab_header(title='The Impact of Missing '+field+' Data').tab_stub(rowname_col='row_heading').fmt(custom_dollar_formatter, columns='Sales')
#     return missing_tbl

# def compare_tbl(df,field):
#     compare_tbl=(GT(df, rowname_col=field).tab_header(title=f"Missing Year Sales by "+field, subtitle=f"").fmt(custom_dollar_formatter, columns=['Global_Sales_missing','Global_Sales']).fmt(custom_percent_formatter, columns=['frac_missing']).tab_stubhead(label=field).tab_spanner(label='Global Sales', columns=['Global_Sales_missing', 'Global_Sales', 'frac_missing'])).cols_label(
#         Global_Sales=html("Total"),
#         Global_Sales_missing=html("Missing Year"),
#         frac_missing=html("% Missing")).tab_style(
#         style=style.text(color='black'),
#         locations=[loc.body(), loc.column_labels(), loc.stub()]).tab_style(
#             style=style.fill("lightblue"), 
#             locations=loc.body(
#             rows=lambda x: x['frac_missing']>.01,)) 

#     return compare_tbl 


def pickle_input(df_str):
    with open(df_str+'.pickle', 'rb') as file:
        df=pickle.load(file)
        return df

games_complete_year_final=pickle_input('games_complete_year_final')
games_complete_pub_year_final=pickle_input('games_complete_pub_year_final')
games_complete_pub_final=pickle_input('games_complete_pub_final')
games_final=pickle_input('games_final')
# Create a map from individual year to decade.
decade_mapping = {}
for yr in range(1980, 2021):
    if yr >= 1980 and yr <1990: 
        decade_mapping[yr]='1980s'
    elif  yr >= 1990 and yr <2000: 
        decade_mapping[yr]='1990s' 
    elif  yr >= 2000 and yr <2010: 
        decade_mapping[yr]='2000s' 
    elif  yr >= 2000 and yr <2021: 
        decade_mapping[yr]='2010s'  
  
games_complete_year_final['decade'] = games_complete_year_final['year'].replace(decade_mapping) 
games_complete_pub_year_final['decade'] = games_complete_pub_year_final['year'].replace(decade_mapping) 

# Create a dataframe of total sales by decade and publisher.
pub_sales_by_decade = games_complete_pub_year_final.groupby(['Publisher', 'decade'])['Global_Sales'].sum().reset_index()
# Select top 5 publishers in the 1980s for a later chart.
early_publishers = pub_sales_by_decade.sort_values(['decade','Global_Sales'], ascending=[True, False] ).head(5)['Publisher']
# Create a dataframe of total sales by decade.
sales_by_decade = games_complete_year_final.groupby(['decade'])['Global_Sales'].sum().reset_index()
# Create a dataframe of total sales by decade and publisher.
games_grouped_by_genre = games_complete_year_final.groupby(['Genre', 'decade'])['Global_Sales'].sum().reset_index()

# Create a dataframe to include the percentage of sales within each decade associated with each genre.
genres_with_decade_sales = games_grouped_by_genre.merge(sales_by_decade, on='decade', how='left', suffixes=('', '_total_by_decade'))
genres_with_decade_sales['global_sales_percent'] = genres_with_decade_sales['Global_Sales']/genres_with_decade_sales['Global_Sales_total_by_decade']

# Create a chart showing the percentage of each decade's total sales each genre generated.
#Axes Level
g = sns.catplot(data=genres_with_decade_sales, kind = 'bar', x='decade', y='global_sales_percent',  hue='Genre', height=8, aspect=1.5)
g.ax.set_xlabel("")
g.ax.set_ylabel("Percentage of Each Decade's Total Video Game Sales", fontsize=14, labelpad=12)
g.ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0,0))
g.fig.suptitle("Genre Popularity within each Decade", fontsize=16)
# plt.savefig('genre_sales_by_decade.png')

## Publishing Teams Over Time
# Calculate total sales generated by each publisher from 1980 to 2016.
games_by_publisher = games_complete_pub_year_final.groupby(['Publisher', 'year'])['Global_Sales'].sum().reset_index()
# Use the dataframe early_publishers to create a chart showing the market share of the most popular early publishers.
early_publisher_sales = games_by_publisher[games_by_publisher['Publisher'].isin(early_publishers)]
sales_by_publisher = games_complete_pub_year_final.groupby(['Publisher'])['Global_Sales'].sum().reset_index()
highest_sales_publisher = sales_by_publisher[sales_by_publisher['Global_Sales']>=350.0]
sales_by_year = games_complete_year_final.groupby(['year'])['Global_Sales'].sum().reset_index() 
publishers_with_year_sales = games_by_publisher.merge(sales_by_year, on='year', how='left', suffixes=('', '_total_by_year'))
publishers_with_year_sales['global_sales_percent'] = publishers_with_year_sales['Global_Sales']/publishers_with_year_sales['Global_Sales_total_by_year']


early_publishers_with_year_sales = early_publisher_sales.merge(sales_by_year, on='year', how='left', suffixes=('', '_total_by_year'))

early_publishers_with_year_sales['global_sales_percent'] = early_publishers_with_year_sales['Global_Sales']/early_publishers_with_year_sales['Global_Sales_total_by_year']
top_publishers = publishers_with_year_sales.merge(highest_sales_publisher, on='Publisher', how='inner', suffixes=('', '_top'))
top_pub_pivot = top_publishers.pivot_table(values="Global_Sales", index="year",columns="Publisher", fill_value=0, aggfunc='sum', margins=False).reset_index()

###Early Leaders Publishing 
sales_by_year = games_complete_year_final.groupby(['year'])['Global_Sales'].sum().reset_index() 


highest_sales_publishers_list=highest_sales_publisher['Publisher'].values.tolist()
early_publishers_list=early_publishers.values.tolist()
interesting_publishers=enumerate(list(set(early_publishers_list+highest_sales_publishers_list)))

def color_map_to_category(category_list):
    """Returns a dictionary mapping categorical variables to colors."""
    hue_colors={}
    for i,j in category_list: 
        color=palette[i]
        hue_colors[j]=color
    return hue_colors
hue_colors=color_map_to_category(interesting_publishers)

def market_share_by_year_plot(df,sup_ttl):
    sns.set_context(rc={"lines.linewidth":6})
    g = sns.relplot(data=df, kind='line', x='year', y='global_sales_percent', hue='Publisher', palette=hue_colors, height=8, aspect=1.5, legend='full')
    g.set_axis_labels("", "Percentage of Each Year's Total Video Game Sales", fontsize=12,labelpad=10)
    sns.move_legend(g, 'upper right', bbox_to_anchor=(0.5, 0.42, 0.5, 0.5), title="", fontsize=12, draggable=True)
    g.ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    g.fig.suptitle(sup_ttl, fontsize=16)
    plt.tight_layout()
# plt.savefig('publisher_by_year.png')

market_share_by_year_plot(top_publishers, "The Six Top Selling Publishers' Market Share by Year")
market_share_by_year_plot(early_publishers_with_year_sales, "Publishers Dominating the Eighties")

# Create chart of publisher sales by year.
bottom=np.zeros(37)
legend_labels =[]
fig, ax = plt.subplots(figsize=(12,8))
for n in range(1,7):
   ax.bar(x=top_pub_pivot['year'], height=top_pub_pivot.iloc[:, n], bottom=bottom)
   bottom += top_pub_pivot.iloc[:, n]
   label=top_pub_pivot.columns[n]
   legend_labels.append(label)
ax.legend(labels=legend_labels)
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:.0f}'))
ax.set_ylabel("Sales (in Millions)", fontsize=14, labelpad=12)
ax.spines[['top', 'right']].set_visible(False)
fig.suptitle("Annual Global Sales by the Six Top Selling Publishers", fontsize=16)
#plt.savefig('Publisher Sales by Year.png')

def publisher_success(publisher, pdf_name):
    """Which individual games contributed the most to these publishers' success?"""
    games_ = games_complete_pub_final[games_complete_pub_final['Publisher']==publisher]
    total_sales = games_['Global_Sales'].sum()
    top_games_= games_.groupby(['Name'])['Global_Sales'].sum().reset_index().sort_values('Global_Sales', ascending=False)
    top_games_['percent_sales']=top_games_['Global_Sales']/total_sales
    top_games_['cum_percent']=top_games_['percent_sales'].cumsum(axis=0)
    top_15_pct = top_games_[top_games_['cum_percent']<=.15]
    top_15_pct.drop(['cum_percent'], axis=1, inplace=True)
    top_15_pct['Game Title']=top_15_pct['Name']
    top_15_pct['Sales']=top_15_pct['Global_Sales'].map('${:,.2f}M'.format)
    top_15_pct["Percentage of Total Sales"]=top_15_pct['percent_sales'].map('{:.2%}'.format)
    top_15 = top_15_pct[['Game Title', 'Sales', 'Percentage of Total Sales']]

    if publisher=='Electronic Arts':
        gt_tbl=(GT(top_15, rowname_col='Game Title').tab_header(title=f"Top 15% of {publisher.title()}' Video Game Sales", subtitle=f"Global Sales Between 1980 and 2016:  {custom_dollar_formatter(total_sales)}").tab_stubhead(label='Game Title').tab_style(
            style=style.text(color='black'),
            locations=[loc.body(), loc.column_labels(), loc.stubhead(), loc.header(), loc.stub()]))
    else: 
        gt_tbl=(GT(top_15, rowname_col='Game Title').tab_header(title=f"Top 15% of {publisher.title()}'s Video Game Sales", subtitle=f"Global Sales Between 1980 and 2016:  {custom_dollar_formatter(total_sales)}").tab_stubhead(label='Game Title').tab_style(
            style=style.text(color='black'),
            locations=[loc.body(), loc.column_labels(), loc.stubhead(), loc.header(), loc.stub()]))
    #gt_tbl.show()
   # gt_tbl.save(pdf_name)
publisher_success('Activision', 'activision.pdf')
publisher_success('Electronic Arts', 'electronic arts.pdf')
publisher_success('Nintendo', 'nintendo.pdf')
publisher_success('Sony Computer Entertainment','sony computer entertainment.pdf')
publisher_success('Ubisoft','ubisoft.pdf')
publisher_success('Take-Two Interactive','take-two interactive.pdf')    


## The following commented out section is back of the envelope work I did to support my blog post's text.

# ea=games_complete_pub_final[games_complete_pub_final['Publisher']=='Electronic Arts']
# ea_grouped = ea.groupby(['Name'])['NA_Sales'].sum().reset_index()
# ea_madden_07 = ea[ea['Name']=='Madden NFL 07']
# print(ea_madden_07.groupby(['Name'])['Global_Sales'].sum())
#print(ea_grouped.sort_values(['NA_Sales'], ascending=False).head(20))

# s=games_complete_pub_final[games_complete_pub_final['Publisher']=='Sony Computer Entertainment']
# s_grouped = s.groupby(['Name'])[['NA_Sales']].sum().reset_index()
# s_gt = s[s['Name']=='Gran Turismo 3: A-Spec']
# print(s_gt.groupby(['Name'])['NA_Sales'].sum())

# ubi=games_complete_pub_final[games_complete_pub_final['Publisher']=='Ubisoft']
# ubi_grouped = ubi.groupby(['Name', 'Year'])['Global_Sales'].sum().reset_index()
# ubi_r6 = ubi_grouped[ubi_grouped['Name'].str.contains('Rainbow Six')]
# ubi_assassin = ubi_grouped[ubi_grouped['Name'].str.contains('Assassin')]
#print(ubi_r6.sum())
#print(ubi_r6)

# act=games_complete_pub_final[games_complete_pub_final['Publisher']=='Activision']
# act_grouped = act.groupby(['Name'])['Global_Sales'].sum().reset_index()
# act_cod = act_grouped[act_grouped['Name'].str.contains('Call of Duty')]
# print(act_cod.sum())
#print(ubi_assassin)

## What are the top selling games of all time?
best_games = games_final.groupby(['Name'])[['Global_Sales', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum().reset_index()
best_games_sorted = best_games.sort_values(['Global_Sales'], ascending=False)
top_25_games_world = best_games.sort_values(['Global_Sales'], ascending=False).head(25)

surprises = []
def regional_surprises(region, sales):
    # Are there any games in any region's top 5 that are NOT in the global top 25?
    top_5_reg_games = best_games.sort_values([sales], ascending=False).head(5)
    reg_merged = top_5_reg_games.merge(top_25_games_world, on='Name', how ='left', suffixes=('', '_top_25'), indicator=True)
    reg_surprises = reg_merged.loc[reg_merged['_merge']=='left_only', ['Name', 'Global_Sales', sales]]
    reg_surprises['Game Title']=reg_surprises['Name']
    reg_surprises['Region']=region
    reg_surprises['Regional Sales']=reg_surprises[sales].map('${:,.2f}M'.format)
    reg_surprises['Global Sales']=reg_surprises['Global_Sales'].map('${:,.2f}M'.format)
    reg_surprises.drop([sales, 'Global_Sales'], axis=1, inplace=True)
    for i, row in reg_surprises.iterrows():
        surprises.append(row)

regional_surprises('North America', 'NA_Sales')   
regional_surprises('Europe', 'EU_Sales')   
regional_surprises('Japan', 'JP_Sales')   
regional_surprises('Other', 'Other_Sales')

region_hits = pd.DataFrame(surprises)
region_tbl = (GT(region_hits, rowname_col='Game Title').tab_header(title="Regional Best Sellers", subtitle="Games ranked in the top 5 bestselling by region, but not ranked in the top 25 bestselling globally").tab_style(
            style=style.text(color='black'),
            locations=[loc.body(), loc.column_labels(), loc.stubhead(), loc.header(), loc.stub()]))
region_tbl.show()
#region_tbl.save('region_tbl.pdf')

top_sellers_world = top_25_games_world[['Name', 'Global_Sales']].sort_values('Global_Sales', ascending=True).reset_index()

fig, ax = plt.subplots(figsize=(12.5,10), constrained_layout=True)
ax.barh(y='Name', data=top_sellers_world, width='Global_Sales', color='#33a02c')
ax.set_title("Top 25 Games by Global Sales", fontsize=16, linespacing=1.5)
ax.set_xlabel("Global Sales in Millions of Dollars", fontsize=16, labelpad=12)
ax.spines[['top', 'right']].set_visible(False)
ax.xaxis.set_major_formatter(mtick.StrMethodFormatter('${x:.0f}M'))
plt.yticks(fontsize=10)
#plt.show()

## Top Selling Game Series
## Begin by strip digits from the right
games_final['simple_name'] = games_final['Name'].str.rstrip('0123456789')
## Strip roman numerals from the right
games_final['simple_name'] = games_final['simple_name'].str.rstrip('ivxIVX')
## Split at colon
games_final['simple_name'] = games_final['simple_name'].str.split(':').str[0]
## Strip digits again
games_final['simple_name'] = games_final['simple_name'].str.rstrip('0123456789')
## Strip 'new' from Super Mario Bros.
games_final['simple_name'] = games_final['simple_name'].str.removeprefix('New')
## Strip white space
games_final['simple_name'] = games_final['simple_name'].str.strip()

simplenames = games_final['simple_name'].to_list()
name_map = {}
for name in simplenames:
    if 'Pokemon' in name:
        name_map[name]='Pokemon'
    elif 'Super Mario' in name:
        name_map[name]='Super Mario' 
    elif 'FIFA' in name:
        name_map[name]='FIFA' 
    elif 'Wii Sports' in name:
        name_map[name]='Wii Sports'     

games_final['simple_name'] = games_final['simple_name'].replace(name_map)
game_team = games_final.groupby(['simple_name'])['Global_Sales'].sum().reset_index()
game_team_sorted = game_team.sort_values('Global_Sales', ascending=False)

#print(game_team_sorted.head(20))

top_team = game_team_sorted.head(20).sort_values('Global_Sales', ascending=True).reset_index()

fig, ax = plt.subplots(figsize=(12,10), constrained_layout=True)
ax.barh(y='simple_name', data=top_team, width='Global_Sales', color='#6a3d9a')
ax.set_xlabel("Global Sales in Millions of Dollars", fontsize=16, labelpad=12)
ax.set_title("Top 20 Game Series by Global Sales", fontsize=16)
ax.spines[['top', 'right']].set_visible(False)
ax.xaxis.set_major_formatter(mtick.StrMethodFormatter('${x:.0f}M'))
plt.xticks(fontsize=8)
plt.yticks(fontsize=10)
#plt.show()
