# 23andMe Common Relatives Scraper

This tool came from an idea: I wanted to be able to create a network graph
from the "Common Relatives" information within 23andMe's DNA Relatives tool,
but there wasn't any way to easily get that data. Downloading aggregate
data only gave you your matches' relations to you, but not to each other.

Using selenium and BeautifulSoup, this script will open a web browser
window to 23andMe, log in, and then go through your relatives one-by-one
and pull their relations to your common relatives.

## Requirements
* Python (tested only on 3.6.2)
* Selenium with the gecko webdriver
* BeautifulSoup
* 23andMe account that has received ancestry results
* Aggregate data downloaded from the DNA Relatives tool

## Usage
When you run the script, you'll be asked for the following:
* 23andMe username and password: This is needed for the webdriver to log
into your account and pull the data. You can check the code and see that
it gets sent only to 23andme
* Full path to your aggegrate data, OR you can save it next to this script

As it runs, you'll see in the console window where it is in the process.
In general, it'll take several hours to run for your thousands of relatives.

Once finished, it'll save a .csv titled 'Common Relatives per Relative.csv'
The output data is in 6 columns as follows:

Relative ID | Relative Name | Your % w/ Relative | Common Relative ID | Common Relative Name | Your % With Common | Their % With Common
:-----------|:--------------|-------------------:|:-------------------|:---------------------|-------------------:|-------------------|
|long hash  | John Doe      | 25.0%              |another long hash   |Jane Doe              |               12.5%|                50%


## Visualizing your data

Included in this repo is 'output to graphml.py', which will create a
.graphml file for you to use with the program of your choice (like Gephi)
You can edit the variables starting with `cutoff_` to percentages of your
choice (where '100%' = 100.0) to change the number of nodes and edges
that are output.

 Attribute | Description | Nodes? | Edges? |
|----------|-------------|--------|--------|
Weight | Strength of the relationship | Relationship to you | Relationship between nodes
Label | Description of the node | Relative's name | N/A
