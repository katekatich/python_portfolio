import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import pickle
import os

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
  
def custom_dollar2f_formatter(x):
    """Returns $X.XXB if number in millions is 4 or more digits long, otherwise returns $X.XXM. For formatting numbers in tables."""
    return f'${x/1000:,.2f}B'if x > 1000 else f'${x:,.2f}M'    

def custom_percent_formatter(x):
    """Returns $X.XXB if number in millions is 4 or more digits long, otherwise returns $X.XXM. For formatting numbers in tables."""
    return f'{x*100:,.2f}%'    

def custom_formatter(x, pos):
    """Returns ($X,XXX) if number is less than 0, otherwise returns $X,XXX. For formatting tick mark labels."""
    return f'(${abs(x*1000000):,.0f})' if x < 0 else f'${x*1000000:,.0f}'    


# Table Creation Functions
def games_sales_table (df, ttl):
    """Creates a table with game titles and associated global sales."""
    tbl = GT(df[['Name', 'Global_Sales']]).tab_header(
        title=ttl).fmt(custom_dollar2f_formatter, columns='Global_Sales').cols_label(
    Global_Sales=html("Global Sales")).tab_style(
    style=style.text(color='black'),
    locations=[loc.body(), loc.column_labels(), loc.header()])
    return tbl

def game_year_platform_table(df, ttl):
    """Creates a table with game title, platform, and year."""
    tbl = GT(df[['Name', 'Year', 'Platform']]).tab_header(title=ttl).tab_style(
    style=style.text(color='black'),
    locations=[loc.body(), loc.column_labels(), loc.header()])
    return tbl

def impact_of_missing_table(dfs_enum, field):
    """Creates a table showing the percentage of data recaptured by data cleaning methods.""" 
    # Create a list of row heading titles.
    row_headings_list = ['All Records', 'Missing Records Before Fix', 'Missing Records After First Fix', 'Missing Records After Second Fix']

    impact = []
    for i, df in dfs_enum:
        #Sum global sales associated with all remaining records within this dataframe.
        sales= df[['Global_Sales']].sum(axis=0)
        # Create a tuple from the global sales float and a count of all records within this dataframe.
        totals = (sales.iloc[0], df.shape[0])
        # Add a row heading label to the tuple.
        totals_labeled = (row_headings_list[i], totals)
        # Place the tuple in a list.
        impact.append(totals_labeled)

    missing_list = []
    for row_heading,totals in impact:
        #Unpack the sales records from the tuple
        sales, records = totals
        #Create a dictionary for each row of the table.  complete_records and games_total_sales are global variables.
        tbl={'row_heading':row_heading,'Number of Records':'{:,.0f}'.format(records), '% of Records':'{:,.2%}'.format(records/complete_records), 'Sales':sales,'% of Sales':'{:,.2%}'.format(sales/games_total_sales)}
        #Create a list of table row dictionaries.
        missing_list.append(tbl)
    #Convert the list of dictionaries into a dataframe.    
    missing_df = pd.DataFrame(missing_list)
    #Create a nice looking table from the dataframe.
    missing_tbl = GT(missing_df).tab_header(title='The Impact of Missing '+field+' Data').tab_stub(rowname_col='row_heading').fmt(custom_dollar_formatter, columns='Sales').tab_style(
    style=style.text(color='black'),
    locations=[loc.body(), loc.column_labels(), loc.header(), loc.stub(), loc.stubhead()])
    return missing_tbl

def compare_tbl(df,field):
    compare_tbl=(GT(df, rowname_col=field).tab_header(title=f"Missing Year Sales by "+field, subtitle=f"").fmt(custom_dollar_formatter, columns=['Global_Sales_missing','Global_Sales']).fmt(custom_percent_formatter, columns=['frac_missing']).tab_stubhead(label=field).tab_spanner(label='Global Sales', columns=['Global_Sales_missing', 'Global_Sales', 'frac_missing'])).cols_label(
        Global_Sales=html("Total"),
        Global_Sales_missing=html("Missing Year"),
        frac_missing=html("% Missing")).tab_style(
        style=style.text(color='black'),
        locations=[loc.body(),loc.stub(),loc.stubhead(), loc.column_header(), loc.header()]).tab_style(
            style=style.fill("lightblue"), 
            locations=loc.body(
            rows=lambda x: x['frac_missing']>.01,)) 

    return compare_tbl 

# Begin data work.
filename = 'vgsales.csv'

## Import the video game data from the Kaggle .csv; remove the variable "Rank" because it is redundant
games = pd.read_csv(filename, usecols=['Year', 'Genre', 'Name', 'Publisher', 'Global_Sales', 'NA_Sales','EU_Sales', 'JP_Sales', 'Other_Sales', 'Platform'], dtype={'Year':'str', 'Name':'str', 'Platform':'str', 'Genre':'str', 'Publisher':'str'}, na_values={'Unknown', 'unknown', 'UNKNOWN','NaN', 'nan', 'NAN'}) 

# Clean any white space from string fields. Make all capitalization lower case. This ensures that textual duplicates are found and two diferent capitalization styles are not considered unique records.--No need for lowercase. 2/13/25
games_clean = games.copy()

games_clean['Name'] =  games_clean['Name'].str.strip()
games_clean['Publisher'] = games_clean['Publisher'].str.strip()
games_clean['Genre'] = games_clean['Genre'].str.strip()
games_clean['Platform'] = games_clean['Platform'].str.strip()
#The Year field cannot be converted to an integer type while it contains null values.
games_clean['Year'] = games_clean['Year'].str.strip()

# FIND DUPLICATES
# Don't print.  Make note of this game in the exposition.
duplicates = games_clean[games_clean.duplicated(subset=(['Year', 'Genre', 'Name', 'Publisher', 'Platform', 'Global_Sales', 'NA_Sales', 'JP_Sales', 'EU_Sales', 'Other_Sales']), keep=False)]

# Remove the duplicate record.
games_almost_unique = games_clean[~games_clean.duplicated(subset=(['Year', 'Genre', 'Name', 'Publisher', 'Platform', 'Global_Sales', 'NA_Sales', 'JP_Sales', 'EU_Sales', 'Other_Sales']), keep='first')]

# Looks for duplicate descriptive information only. Groups by descriptive fields.
# Don't print.  Make note in exposition.
duplicates_with_different_sales_numbers = games_almost_unique[games_almost_unique.duplicated(subset=(['Year', 'Genre', 'Name', 'Publisher', 'Platform']), keep=False)]

# There are two records for "Madden NFL 13" on PS3 with different sales numbers. The first record contains most of the sales, the second record contains $10,000 sales in Europe.  In order to maintain missing values, dropna must be set to False.
games_unique = games_almost_unique.groupby(['Name', 'Year', 'Publisher', 'Platform', 'Genre'], dropna=False).agg({'NA_Sales':'sum', 'EU_Sales':'sum', 'JP_Sales':'sum', 'Other_Sales':'sum', 'Global_Sales':'sum'}).reset_index()


##FIND TOTALS.
complete_records = (games_unique.shape[0])
games_sales = games_unique[['Global_Sales']].sum(axis=0)
games_total_sales = games_sales.iloc[0]

##BEGIN MISSING YEAR FIXES
##Look for missing years.
games_missing_year = games_unique[games_unique['Year'].isna()]
missing_year_records = (games_missing_year.shape[0])

#Create a table with the top 5 highest selling game titles with null Year.
games_missing_year_max_sales = games_missing_year.sort_values('Global_Sales', ascending=False).head(5)
missing_years_max_sales_tbl = games_sales_table(games_missing_year_max_sales,'Highest selling games with missing years')
missing_years_max_sales_tbl.show()

## Check for data integrity
games_complete_year = games_unique[~games_unique['Year'].isna()]
assert games_missing_year.shape[0] + games_complete_year.shape[0]==games_unique.shape[0]

# Call game_year_platform_table to create a nice looking table of an example game with year information within its own title. 
year_in_title_ex = games_complete_year[games_complete_year['Name']=='FIFA 15']
year_in_title_tbl = game_year_platform_table(year_in_title_ex,'A game with year data in the title')
year_in_title_tbl.show()

## Some game titles contain missing year information.  Collect and adjust accordingly. 
# Split the title into individual "words" so that each "word" can be examined individually.
games_missing_year['name_parts']=games_missing_year['Name'].str.split(' ')
# Explicitly identify the index so that new information is assigned to the correct record.
games_missing_year['indx']=games_missing_year.index

years=[]
# Loop through each row in the games_missing_year dataframe.
for i, row in games_missing_year.iterrows():
    # Loop through each "word" in the name_parts list field.
    for word in row['name_parts']:
        if word.isdigit():
            if len(word)==2:
                #Ignore any instance of 64.  This is for Nintendo64 and refers to game platform, not the year.
                if word=='64':
                    next
                # Any two-digit date greater than 79 will apply to the years 1980-1999.    
                elif int(word) > 79:   
                    year= '19'+ word
                    new_year = int(year)-1
                # Any other two-digit date will apply to the years 2000-2020.     
                else:
                    year='20'+word
                    new_year = int(year)-1
            # Four-digit dates are kept as is, but cleaned of white space.        
            elif len(word)==4:
                new_year=word.strip()
            # Put the new year in the list as the value associated with the key of the index.    
            years.append({'indx':i, 'Year':new_year})

new_years = pd.DataFrame(years)
# Merge the original dataframe with the new one containing the extracted year information.  Merge on indices.  Call the old Year field Year_missing.
games_fix_year = games_missing_year.merge(new_years, on='indx', how='left', suffixes=('_missing', ''), indicator=False)
games_fix_year.drop(['Year_missing', 'name_parts', 'indx'], axis=1, inplace=True)
# Subset containing all remaining records with null Year.
games_missing_year2 = games_fix_year[games_fix_year['Year'].isna()]
# Subset containing all records with complete year data.
games_fixed_year = games_fix_year[~games_fix_year['Year'].isna()]

# Check data integrity before adding games_fixed_year to the games_complete_year dataset.
assert games_fixed_year.shape[0]+games_missing_year2.shape[0]==games_missing_year.shape[0]
assert games_unique.shape[1]==games_fixed_year.shape[1]
## games_1 is the current complete year dataset.
games_1 = pd.concat([games_complete_year, games_fixed_year], axis=0)
assert games_unique.shape[0] == games_missing_year2.shape[0] + games_1.shape[0]

# Call game_year_platform_table to create a nice looking table of games with missing years for specific platforms.
games_missing_years_platforms_ex = games_unique[games_unique['Name'].isin(['LEGO Batman: The Videogame', 'Call of Duty: Black Ops'])][['Name','Platform', 'Year']].sort_values(['Name','Year'])
games_missing_years_platforms_tbl = game_year_platform_table(games_missing_years_platforms_ex,'Games missing year data for certain platforms')
games_missing_years_platforms_tbl.show()

## SECOND YEAR FIX: games for which one of the platforms did not have a year label

# Create subset of complete games containing only Name, Publisher, Platform, and Year.
games_year = games_1[['Name', 'Publisher', 'Platform', 'Year']]
# Merge games remaining games without release years on complete games by name and publisher. This will drag along platforms and years from the complete data. In fact, for some titles, this will create multiple records from one record in the games_missing_year2 dataframe. Later in the script, I will identify the one record that is useful.
games_fix2 = games_missing_year2.merge(games_year, on=['Name', 'Publisher'], how='left', suffixes=('_missing', ''), indicator=True)
# Split games_fix2 into game titles that might be able to recapture release year (games_with_possible_years) and game titles that will still be missing release year data (games_missing still).
games_with_possible_years = games_fix2[games_fix2['_merge']=='both']
games_missing_still = games_fix2[games_fix2['_merge']=='left_only']
games_missing_still[['Platform', 'Year']]=games_missing_still[['Platform_missing', 'Year_missing']]
games_missing_still.drop(['Platform_missing', 'Year_missing', '_merge'], axis=1, inplace=True)
games_missing_still.drop_duplicates(inplace=True)
# Create games_not_fixed to find all the records whose platforms are already assigned a release year.  These games will have the same platform from both the games_missing_year2 dataframe and the games_year dataframe.
games_not_fixed = games_with_possible_years[games_with_possible_years['Platform_missing']==games_with_possible_years['Platform']]
games_not_fixed[['Platform', 'Year']]=games_not_fixed[['Platform_missing', 'Year_missing']]
games_not_fixed.drop(['Platform_missing', 'Year_missing', '_merge'], axis=1, inplace=True)
games_not_fixed.drop_duplicates(inplace=True)
# Create a dataframe containing the records whose year field remains null.
games_missing_year3 = pd.concat([games_missing_still, games_not_fixed], axis=0)
## Create games_remaining to assign the year associated with the game on its other platforms to the game and platform missing the year data.  This could result in duplicate records.
games_remaining = games_with_possible_years[games_with_possible_years['Platform_missing']!=games_with_possible_years['Platform']]
# Drop the platforms from the complete games data. 
games_remaining.drop(['Platform', '_merge'], axis=1, inplace=True)
# Rename Platform_missing (the true platform for this data) to Platform.
games_remaining[['Platform']]=games_remaining[['Platform_missing']]
games_remaining.drop(['Platform_missing', 'Year_missing'], axis=1, inplace=True)
# Get rid of the duplicates created from the one to many merge at 191. 
games_remaining.drop_duplicates(inplace=True)
# All duplicates were not removed: Hitman 2: Silent Assassin (2003,2004), PES 2009: Pro Evolution Soccer (2008, 2009), Tomb Raider (2013) (2013, 2014)--If this dataset were being used for a true business objective, I would drop this recapture strategy.  It is too risky and does not recapture enough data. 
# Drop second year assignment of record
games_fix_year2 = games_remaining[~games_remaining.duplicated(subset=['Name','Publisher','Genre', 'NA_Sales','EU_Sales','JP_Sales', 'Other_Sales', 'Global_Sales','Platform'], keep='first')]

# Check data integrity before adding new cleaned records to the complete dataset.
#games_missing_year3.drop(['Platform_missing', 'Year_missing', '_merge'], axis=1, inplace=True)
assert games_fix_year2.shape[0]+games_missing_year3.shape[0]==games_missing_year2.shape[0]
assert games_unique.shape[1]==games_fix_year2.shape[1]
games_2 = pd.concat([games_1, games_fix_year2], axis=0)
assert games_unique.shape[0] == games_missing_year3.shape[0] + games_2.shape[0]
assert games_missing_year3.shape[1]==games_2.shape[1]

year_df_enum = enumerate([games_unique, games_missing_year, games_missing_year2, games_missing_year3])
missing_years_tbl = impact_of_missing_table(year_df_enum, 'Year')
missing_years_tbl.show()
#missing_years_tbl.save('missing_years_tbl.pdf')
##END MISSING YEAR FIX

##BEGIN PUBLISHER FIX
# The following dataset is as clean as it can be of null years, but still missing publisher data.
games_partial_clean = pd.concat([games_2,games_missing_year3], axis=0)
# Create a dataframe containing only missing publisher data.
games_missing_publisher = games_partial_clean[games_partial_clean['Publisher'].isna()]

# Create a nice looking table of the top five highest grossing titles with missing publisher data.
#Create a dataframe of the highest grossing 5 games with missing publisher data.
games_missing_pub_max = games_missing_publisher[['Name', 'Global_Sales']].sort_values('Global_Sales', ascending=False).head(5)
missing_pub_tbl = games_sales_table(games_missing_pub_max,'Highest Selling Games with Missing Publisher Data')
missing_pub_tbl.show()

missing_pub_ex = games_partial_clean[games_partial_clean['Name'].isin(['Teenage Mutant Ninja Turtles', 'NASCAR Thunder 2003'])].sort_values(['Name', 'Year', 'Platform'])
missing_pub_ex_tbl = GT(missing_pub_ex[['Name', 'Year', 'Platform','Publisher']]).tab_header(title='Examples of games missing publisher information').tab_style(
    style=style.text(color='black'),
    locations=[loc.body(), loc.column_labels(), loc.header()])
missing_pub_ex_tbl.show()

##PUBLISHER FIX (merged with exact same title and only one publisher to obtain good publisher data)
games_complete_publisher = games_partial_clean[~games_partial_clean['Publisher'].isna()]

# Check integrity of the data.
assert games_complete_publisher.shape[0]+games_missing_publisher.shape[0]==games_partial_clean.shape[0]

## Looking for games with only one publisher. Assumptions: games that only have one non-null publisher value should have the same publisher value for null publisher fields. 
#Create df with unique game title and publisher combinations.
unique_games_complete = games_complete_publisher[['Name', 'Publisher']].drop_duplicates() 
#Create df of games that only have one publisher.
unique_games_pub_counts = unique_games_complete['Name'].value_counts().reset_index()
unique_games_one_pub = unique_games_pub_counts[unique_games_pub_counts['count']==1]
#Merge unique name, publisher combinations with the subset of games that are only associated with one publisher. Creates a one-to-one relationship between game title and publisher.--Perhaps there is a better way to do this??? maybe using sets???
unique_games_unique_pub = unique_games_complete.merge(unique_games_one_pub, how='inner', on='Name')
#Merge games with missing publishers with games that only have one publisher.  Reasssign the known publisher to the null publisher.
games_fix_publisher = games_missing_publisher.merge(unique_games_unique_pub, on=['Name'], how='left', suffixes = ('_missing', ''), indicator=True)
games_fix = games_fix_publisher[games_fix_publisher['_merge']=='both']
#Collect games that did not match the games that only have on publisher.  These records' publisher data have not been recaptured yet.
games_missing_publisher2 = games_fix_publisher[games_fix_publisher['_merge']=='left_only']
games_fix.drop(['Publisher_missing', '_merge', 'count'], axis=1, inplace=True)
games_missing_publisher2.drop(['Publisher_missing', '_merge', 'count'], axis=1, inplace=True)

## PUBLISHER FIX 2
# Check data integrity.
assert games_partial_clean.shape[1]==games_complete_publisher.shape[1]
assert games_complete_publisher.shape[1]==games_fix.shape[1]
games_3 = pd.concat([games_complete_publisher, games_fix], axis=0)
assert games_3.shape[0] == games_fix.shape[0] + games_complete_publisher.shape[0]
assert games_3.shape[1] == games_missing_publisher2.shape[1]
cleaned_games = pd.concat([games_3, games_missing_publisher2], axis=0)

## Assign publisher to games with null publisher values that match a game and release year with a non-null publisher. Assumes games do not have more than one publisher in a release year.  (This is already found to not be the case as some publishers are determined by platform.)  Merge games_3 with games_missing_publisher2 on game title and release year.
games_unique_year_pub = games_3[['Name', 'Publisher', 'Year']].drop_duplicates()
# Merge games missing a publisher with games having a publisher by game title and release year.
games_fix_publisher2 = games_missing_publisher2.merge(games_unique_year_pub, on=['Name', 'Year'], how='left', suffixes = ('_missing', ''), indicator=True)
#Split into the games that have been assigned a publisher (games_fix2) and games that have not been assigned a publisher (games_missing_publisher3).
# There is only one game title assigned new publisher data: Teenage Mutant Ninja Turtles, released in 2003, published by Konami Digital Entertainment.
games_fix2 = games_fix_publisher2[games_fix_publisher2['_merge']=='both']
games_fix2.drop(['Publisher_missing', '_merge'], axis=1, inplace=True)
games_missing_publisher3 = games_fix_publisher2[games_fix_publisher2['_merge']!='both']
games_missing_publisher3.drop(['Publisher_missing', '_merge'], axis=1, inplace=True)
assert games_partial_clean.shape[1]==games_complete_publisher.shape[1]
assert games_3.shape[1]==games_fix2.shape[1]
games_4 = pd.concat([games_3, games_fix2], axis=0)
assert games_4.shape[0] == games_fix2.shape[0] + games_3.shape[0]
assert games_4.shape[1] == games_missing_publisher3.shape[1]
cleaned_games = pd.concat([games_4, games_missing_publisher3], axis=0)

### TABLE ANALYSIS OF MISSING PUBLISHERS
# Create table with change in missing publishers after subsequent fixes. First, pass an emumerated list of equivalently structured dataframes and the field which is being compared (in this case the Publisher field.)
pub_df_enum = enumerate([games_unique, games_missing_publisher, games_missing_publisher2, games_missing_publisher3])
missing_pub_tbl=impact_of_missing_table(pub_df_enum, 'Publisher') 
missing_pub_tbl.show()
#missing_pub_tbl.save('missing_pub_tbl.pdf')

# Create a nice table of the top highest grossing games with no publisher info.
games_still_missing = games_missing_publisher3[['Name', 'Platform', 'Year', 'Global_Sales']].sort_values('Global_Sales', ascending=False).head(10)
missing_pub3_tbl = GT(games_still_missing[['Name', 'Year', 'Platform','Global_Sales']]).tab_header(title='Top 10 games still missing publisher information').fmt(custom_dollar2f_formatter, columns='Global_Sales').tab_style(
    style=style.text(color='black'),
    locations=[loc.body(), loc.column_labels(), loc.header()])
missing_pub3_tbl.show()
#END MISSING PUBLISHER FIX

#HOW DO MISSING YEARS AFFECT GENRES THRU THE DECADES?
#Since one of the goals is to follow genre popularity over time, it's important to see how each genre is affected by missing years. 
# Group all records with missing years by genre and sum by global sales.
genres_with_missing_years = games_missing_year3.groupby(['Genre'])['Global_Sales'].sum().reset_index()
# Group all records from complete data and sum by global sales.
genre_sales = cleaned_games.groupby(['Genre'])['Global_Sales'].sum().reset_index()
# Merge be genre to compare sales associated with missing year and complete sales.
genre_compare = genres_with_missing_years.merge(genre_sales, on='Genre', suffixes=('_missing',''))
#Calculate the percentage of each genre's sales that are associated with a null release year. 
genre_compare['frac_missing']=(genre_compare['Global_Sales_missing']/genre_compare['Global_Sales'])
#Sort descending by sales.
genre_compare.sort_values('Global_Sales', ascending=False, inplace=True)
# Create a nice looking table to show the gross and missing year sales by genre.
genre_compare_tbl = compare_tbl(genre_compare, 'Genre')
genre_compare_tbl.show()

## HOW DO MISSING YEARS AFFECT PUBLISHERS' GROWTH OVER TIME?
pubs_with_missing_years = games_missing_year3.groupby(['Publisher'])['Global_Sales'].sum().reset_index()
pub_sales = cleaned_games.groupby(['Publisher'])['Global_Sales'].sum().reset_index()
pub_compare = pubs_with_missing_years.merge(pub_sales, on='Publisher', suffixes=('_missing',''))
pub_compare['frac_missing'] = pub_compare['Global_Sales_missing']/pub_compare['Global_Sales']
pub_compare.sort_values('Global_Sales', ascending=False, inplace=True)
pub_compare_tbl = compare_tbl(pub_compare, 'Publisher')
pub_compare_tbl.show()

# Look for game titles that have been assigned multiple genres.
# Subset on unique name and genre combinations.
#games_genres = cleaned_games[['Name', 'Genre']].drop_duplicates()
games_genres = cleaned_games.groupby(['Name', 'Genre']).sum('Global_Sales').reset_index()
# Keep only games that are associated with more than one genre.
incorrect_genre = games_genres[games_genres.duplicated(subset=['Name'], keep=False)].sort_values('Name')
incorrect_genre_sales = incorrect_genre[['Global_Sales']].sum(axis=0).iloc[0]
possible_incorrect_genre = incorrect_genre.drop(['NA_Sales', 'JP_Sales', 'EU_Sales', 'Other_Sales'], axis=1)

tbl_multi_genre = (GT(possible_incorrect_genre, rowname_col='Name').tab_header(title="Games with Multiple Genres", subtitle=f"Total Global Sales: {custom_dollar_formatter(incorrect_genre_sales)}").tab_stubhead(label='Name').fmt(custom_dollar_formatter, columns=['Global_Sales'])).tab_style(
    style=style.text(color='black'),
    locations=[loc.body(), loc.column_labels(), loc.header(), loc.stub(), loc.stubhead()])
tbl_multi_genre.show()

# # Culdcept is strategy and is similar to a board game; https://en.wikipedia.org/wiki/Culdcept
# # Little Busters! visual novel from Wikipedia; https://en.wikipedia.org/wiki/Little_Busters!
# # Steins; Gate: Hiyoku Renri no Darling visual novel ; https://en.wikipedia.org/wiki/Steins;Gate:_My_Darling%27s_Embrace
# # Syndicate is strategy with shooting; https://en.wikipedia.org/wiki/Syndicate_(1993_video_game)

## DISCREPANCY BETWEEN CALCULATED SALES TOTALS AND GLOBAL SALES TOTALS
## 6772 games total sales do not match global sales
cleaned_games['totals'] = cleaned_games[['NA_Sales','EU_Sales', 'JP_Sales', 'Other_Sales']].sum(axis=1)
cleaned_games['discrepancy'] = (cleaned_games['Global_Sales']-cleaned_games['totals'])
discrepancy = cleaned_games['discrepancy'].sum().round()
discrep_percent = (cleaned_games['discrepancy'].sum()/cleaned_games['Global_Sales'].sum())

fig, ax = plt.subplots(figsize=(12,10))
g = sns.histplot(data=cleaned_games, x='discrepancy', ax=ax, color='#ca9161')

sns.despine(bottom=False, left=True)
for p in g.patches:
    height = p.get_height()
    if height > 0:  # Only label bars with non-zero height  "${:,.0f}".format(discrepancy)
        ax.text(p.get_x() + p.get_width() / 2., height, "{:,.0f}".format(int(height)), ha="center", va="bottom")
g.set_title('Number of Titles with Discrepancies between Global Sales and Total Regional Sales', fontdict={'fontsize': 16})
ax.set_xlabel('Difference (in dollars) between Reported Global Sales and the Sum of Regional Sales', fontsize=12, labelpad=12)
ax.set_ylabel('')
ax.tick_params(axis='y', left=False, labelleft=False)
plt.text(5000,8000, f'Total discrepancy between Global Sales\nand Total Regional Sales: {custom_dollar_formatter(discrepancy)}\n\nDiscrepancy as a Percentage\nof Global Sales: {custom_percent_formatter(discrep_percent)}', fontdict={'ha':'left', 'size':'large'})
ax.xaxis.set_major_formatter(mtick.FuncFormatter(custom_formatter))
plt.grid(visible=False)
plt.show()

# Show the number of games released by year.
# Subset on records with a non-null year value.
cleaned_complete_year = cleaned_games[~cleaned_games['Year'].isna()]
# Make an integer valued year field.
cleaned_complete_year['year']=cleaned_complete_year['Year'].astype('int32')
game_count_by_year = cleaned_complete_year.value_counts('year').reset_index()

#FacetGrid, Axes Level
j = sns.relplot(data=game_count_by_year, x='year', y='count', height=8, aspect=1.5, color='#0173b2')
j.ax.set_xlabel(xlabel='')
j.ax.set_ylabel(ylabel='Number of Games Released', fontsize=14)
j.ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
plt.annotate(2009, xy=(2009, 1431), xytext=(2011, 1427), arrowprops={'facecolor':'black', 'width':1, 'headwidth': 6, 'headlength': 12, 'linewidth': 0.5})
plt.annotate(2017, xy=(2017, 5), xytext=(2018, 50), arrowprops={'facecolor':'black', 'width':1, 'headwidth': 6, 'headlength': 12, 'linewidth': 0.5})
j.fig.suptitle('Number of Published Games by Year', fontsize=16)
plt.show()

# Create final datasets for visualization use.
# Since there is clearly not complete data after 2016, remove the records from those years.
incomplete_years = cleaned_games['Year'].isin(['2017', '2018', '2019', '2020'])
games_4 = cleaned_games[~incomplete_years]

##FINAL DATASETS
#All cleaned and complete records including those with null years and null publishers.
games_final = games_4.drop(['totals', 'discrepancy'], axis=1)
#All cleaned and complete records with non-null release year data.  
games_complete_year_final = games_final[~games_final['Year'].isna()]
# Sometimes the release year will need to be an integer. Only non-null valuea can be converted to integer.
games_complete_year_final['year']=games_complete_year_final['Year'].astype('int32')
#All cleaned and complete records with non-null publisher data.
games_complete_pub_final = games_final[~games_final['Publisher'].isna()] 
#All cleaned and complete records with non-null publisher and non-null release year data.
games_complete_pub_year_final = games_complete_pub_final[~games_complete_pub_final['Year'].isna()]
games_complete_pub_year_final['year']=games_complete_pub_year_final['Year'].astype('int32')

# Write the pickle files to folder for data visualization.
print(f"Current directory: {os.getcwd()}")
new_dir = '/home/kate/python_scripts/blog/video_games_ii'
os.chdir(new_dir)
print(f"New directory: {os.getcwd()}")

def pickle_output(df_str, df):
    with open(df_str+'.pickle', 'wb') as file:
        pickle.dump(df, file)

pickle_output('games_final',games_final)   
pickle_output('games_complete_year_final', games_complete_year_final)   
pickle_output('games_complete_pub_final', games_complete_pub_final)   
pickle_output('games_complete_pub_year_final', games_complete_pub_year_final)   
