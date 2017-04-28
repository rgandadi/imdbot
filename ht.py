from bs4 import BeautifulSoup
import requests, bs4, json

import numpy as np
import pandas as pd
import utilities


baseUrl="http://www.imdb.com"


def getTopChart():
	url = baseUrl+"/chart/top"
	r=requests.get(url)
	data = r.text
	print(r.headers)
	print(len(r.content))
	
	soup = BeautifulSoup(data,"html.parser")
	table = soup.find_all('table', class_="chart full-width")[0]
	rows = table.find_all('tr')
	data = []

	for row in list(rows):
		d = {}
		cols = row.find_all('td')
		for col in cols:
			colName = col['class'][0]
			anchors = col.find_all('a')
			for anchor in anchors:
				if colName == "titleColumn"  and anchor.has_attr('href'):
					d[colName+"-link"] = cleanupHref(anchor['href'])
					d[colName+"-text"] = anchor.text
			spans = col.find_all('span')
			for span in spans:
				if span.has_attr('name') and span.has_attr('data-value'):
					d[span['name']] = span['data-value']
		
			secInfo = spans = col.find_all('span', class_="secondaryInfo")
			if len(secInfo)>0:
				d['year'] = secInfo[0].text.replace("(","").replace(")","")
			
		data.append(d)
	
	#print (json.dumps(data,indent=4))	
	return data



def process(results):
	d=[]
	for result in results:
		data={}
		if type(result) is bs4.element.Tag:
			a={}
			a["attributes"] = result.attrs
			a["children"] = process(result.children)
			data[result.name] = a
		else:
			if utilities.trim(result) != "":
				data["value"] = result
		if len(data) >0:
			d.append(data)
	
	return d

def getDetailsForMovie(d):
	d['props'] = extractDataForMovie(d)
	#print(json.dumps(d,indent=4))
	rank = d.get('rk', None)
	if rank is None:
		print ("Error while processing "+str(d))
	else:
		utilities.printJsonToFile('imdb_',rank,d,False)


def expandProps(movieData):
	props = movieData.pop('props',[])
	for prop in props:
		prop = prop.update(movieData)

	#print(json.dumps(props,indent=4))
	return props

def analyzeData(f):
	files =  utilities.getAllFilesInFolder(f)
	responses = utilities.processExecuteMethodForObjectsWithThreads(utilities.readFileAsJsonForFullFilePath,files,50)
	responses = list(filter(lambda x : "props" in x	, responses))
	responses = list(map(lambda x : expandProps(x), responses))
	fullData = []
	for response in responses:
		fullData.extend(response)
	
	df = pd.DataFrame.from_records(fullData)
	

	print(df.columns)
	
	table = pd.pivot_table(df,index=["name"],columns=["itemprop"],fill_value=0,aggfunc=np.size)
#agg({"name": "count"}).	
#	p = df.groupby("name").size()
	
	#print(table)
	
	writer = pd.ExcelWriter(f+'/_summary.xlsx')
	df.to_excel(writer,'list')
	#table.to_excel(writer,'Sheet2')
	writer.save()
	
	
def execute(forceRefresh=False, ts=None):
	
	if forceRefresh:
		utilities.removeFolder()
	if not utilities.folderExists(ts) and ts is None:
		data = getTopChart()
		ts = utilities.printJsonToFile('imdb_',"_topChart",data,False)
		#getDetailsForMovie(data[10])
		utilities.processExecuteMethodForObjectsWithThreads(getDetailsForMovie,data,100)
	else:
		ts=utilities.getDefaultTimestamp()	
	
	f = "output/"+ts

	print(f)
	if not utilities.fileExists(f+"/_summary.xlsx"):
		analyzeData(f)
	else:
		print("Returning precalculated output")
	return f

def extractJsonFromHtmlForMovie(d):
	returnObj = {}
	
	url = baseUrl+ d.get('titleColumn-link',"")
	print(url)
	r=requests.get(url)
	data=r.text

	soup = BeautifulSoup(data,"html.parser")
	creditSummary = soup.find_all('div', class_="credit_summary_item")
	returnObj["credit_summary_item"]=process(creditSummary)
	#print(json.dumps(d,indent=4))
	
	castListSoup = soup.find_all('table', class_="cast_list")
	if castListSoup is not None and len(castListSoup)>0:
		castList = soup.find_all('table', class_="cast_list")[0].find_all("tr")
		returnObj["castList"]=process(castList)
	#print(json.dumps(returnObj,indent=4))
	
	return returnObj


def getDictFromComponent(itemComponent):
	v={}
	v['itemprop'] = utilities.getValueForKeyPath(itemComponent,"attributes.itemprop",None)
	#v['itemtype'] = utilities.getValueForKeyPath(itemComponent,"attributes.itemtype",None)
	v['name'] = utilities.getValueForKeyPath(itemComponent,"children.[0].a.children.[0].span.children.[0].value",None)
	href = utilities.getValueForKeyPath(itemComponent,"children.[0].a.attributes.href",None)
	v['href'] = cleanupHref(href)
	return v

def cleanupHref(href):
	if type(href) == str and href is not None:
		endIndex = href.find("/?")
		if endIndex == -1:
			endIndex = href.find("?")
		if endIndex >0:
			return (href[0:endIndex])
	
	return href
			
def extractDataForMovie(d):
	movieJson = extractJsonFromHtmlForMovie(d)
	vals = []
	for dataKey in movieJson:
		tags = movieJson.get(dataKey,{})
		if dataKey=="credit_summary_item":
			for tag in tags:
				spanWrappers = utilities.getValueForKeyPath(tag,"div.children")
				for spanWrapper in spanWrappers:
					if 'span' in spanWrapper :
						itemComponent = utilities.getValueForKeyPath(spanWrapper,"span",{})
						v = getDictFromComponent(itemComponent)
						if v.get('itemprop') is not None:
							v['segment'] = "summary"
							vals.append(v)
		if dataKey=="castList":
			for trWrapper in tags:
				tds = utilities.getValueForKeyPath(trWrapper,"tr.children",[])
				for tdWrapper in tds:
					itemComponent = utilities.getValueForKeyPath(tdWrapper,"td",{})
					v = getDictFromComponent(itemComponent)
					if v.get('itemprop') is not None:
						v['segment'] = "castList"
						vals.append(v)
					
					#print(json.dumps(tdWrapper,indent=4))
		
	#print(json.dumps(vals,indent=4))
	vals= list(map( lambda x: cleanupHref(x), vals))
	return vals

#execute()
