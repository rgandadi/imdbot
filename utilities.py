
def isListIndex(key):
	if key.startswith("[") and key.endswith("]"):
		return True

def getIndex(key):
	key = key.replace("[","")
	key = key.replace("]","")
	return int(key)
	
def getValueForKeyPath(dictionary,keyPath, default=None):
	keyPathList=keyPath.split(".")
	value = dictionary
	for key in keyPathList:
		if isListIndex(key):
			try:
				value=value[getIndex(key)]
			except:
				value=default
				pass
		else:	
			try:
				value = value.get(key,default)
			except:
				value = default
				pass

	return value


def trim(s):
	if s is not None:
		return s.replace("\n","").replace(" ","")
	else:
		return ""

from multiprocessing.dummy import Pool as ThreadPool
def processExecuteMethodForObjectsWithThreads(method,objects,threadSize):
	pool = ThreadPool(threadSize) 
	responseWrappers = pool.map(method, objects)
	pool.close()
	pool.join()
	return responseWrappers


def ensureFoldersForFileName(filename):
	folder=os.path.dirname(filename)

	try:
		if not os.path.exists(folder):
			os.makedirs(folder)
	except:
		pass

#.%H.%M.%S
import datetime, time, os, json, gzip
timeStampForFile = datetime.datetime.fromtimestamp(time.time()).strftime("%Y.%m%.%d")
#https://docs.python.org/2/library/gzip.html?highlight=gzip#gzip.GzipFile		
def printJsonToFile(tag, fileName, dataJson,zip = False):
	fullFileName = "output/"+timeStampForFile+"/"+tag+fileName+".js"
	ensureFoldersForFileName(fullFileName)

	if zip:
		with gzip.open(fullFileName+'.gz', 'wt') as f:
			json.dump(dataJson, f, sort_keys=True, indent=4, separators=(',', ': '))
	else:
		with open(fullFileName, 'wt') as out:
			try:
				res = json.dump(dataJson, out, sort_keys=True, indent=4, separators=(',', ': '))
			except:
				print ("Unable to write "+fullFileName)
	return timeStampForFile
	
def removeFolder(folderName=None):
	if folderName is None:
		folderName = getDefaultTimestamp()
	
	folderToRemove = "output/"+folderName
	print ("Removing "+folderToRemove)
	
	files = getAllFilesInFolder(folderToRemove)
	try:
		for file in files:
			os.remove(file)
		os.rmdir(folderToRemove)
	except:
		print ("Unable to remove "+folderToRemove)
		
	
def getDefaultTimestamp(format="%Y.%m%.%d"):
	return  datetime.datetime.fromtimestamp(time.time()).strftime(format)
	
def folderExists(timeStamp=None):
	if timeStamp is None:
		timeStamp = getDefaultTimestamp()
	
	fullFolderPath ="output/"+str(timeStamp)	
	#print(fullFolderPath)
	if os.path.exists(fullFolderPath):
		return True
	else:
		return False

def fileExists(fname):
	return os.path.isfile(fname)
	
def getAllFilesInFolder(folder):
	listOfFiles = []
	for root, dirs, files in os.walk(folder, topdown=False):
	    for name in files:
	        listOfFiles.append(os.path.join(root, name))

	return listOfFiles
					

def readFileAsJsonForFullFilePath(fullFilePath, zip=False):
	dataJson = {}
	if os.path.exists(fullFilePath):
		try:
			if zip:
				with gzip.open(fullFilePath, 'rb') as f:
   					dataJson = json.loads(f.read())
			else:	
				dataJson = json.loads(open(fullFilePath).read())
		except Exception as exp:
			print("Unable to read "+fullFilePath)
			print (str(exp))	
			pass

	return dataJson
							