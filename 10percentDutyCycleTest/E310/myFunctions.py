#filepath = "testFileNames.txt"
import os


def getFileNames(filepath):

    with open(filepath) as fp:
        lines = fp.readlines()

    # Clean the commands by stripping the newline characters (\n) and the \r
    filenames = []
    for line in lines:
        line = line.strip("\n").strip("\r")
        filenames.append(line)

    return filenames
    
def splitOnOffFileNames(filepath):

    # First remove the file it if exists
    removeFile("OnList.txt")
    removeFile("OffList.txt")
        
    fileNames = getFileNames(filepath)
    onList = []
    offList = []
    filepath = ""
    for file in fileNames:
        if "On" in file :
            filepath = "OnList.txt"
            onList.append(file)
        elif "Off" in file :
            filepath = "OffList.txt"
            offList.append(file)
        else:
            filepath = "errorPath.txt"
            print("Error in splitOnOffFileNames")
            
        with open(filepath, "a+") as f:
            f.write(file)
            f.write("\n")
            
    return onList, offList

def writeValues(outputFileName, listItems):
    
    #removeFile(outputFileName) # Remove the file if it already exists
    
    for item in listItems:
        with open(outputFileName, "a+") as file:
            file.write(str(item))
            file.write("\n")         
 
 
def removeFile(fileName):
    # Handle errors while calling os.remove()
    try:
        os.remove(fileName)
    except:
        print("")