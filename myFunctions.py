#filepath = "testFileNames.txt"
import os
import csv
# from scipy.integrate import simps
import scipy.integrate # https://github.com/conda/conda/issues/6396#issuecomment-350254762
# import scipy.integrate as simps
import math

def readlines(filepath):

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
        
    fileNames = readlines(filepath)
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
    
    removeFile(outputFileName) # Remove the file if it already exists
    
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
  
# https://stackoverflow.com/questions/26082718/python-write-two-lists-into-two-column-text-file/33324278  
def exportToCSV(myTuple, filename, headerTuple) :
    removeFile(filename)    # If the file exists already, remove it.
    with open(filename, 'w+', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(headerTuple)        
        writer.writerows(myTuple)
        
def diffList(list1,list2):
    differenceList = []

    zip_object = zip(list1, list2)

    for list1_i, list2_i in zip_object:
        differenceList.append(list1_i-list2_i)

    return differenceList      
        
def calc_list_avg(list_of_lists, numAverages) :
    zipped_lists = zip(*list_of_lists)
    avg_list = []
    for list in zipped_lists :
        avg_list.append(sum(list)/float(numAverages))

    return avg_list


def calc_area(trace_points_dBm, freq_array):
    # Calculate area under the curve
    # Convert dBm to mW
    points_mW = []
    for point in trace_points_dBm:
        point_W = 10.0**(point/10.0)    # Convert dBm to W
        point_mW = 0.001*point_W        # Convert W to mW
        points_mW.append(point_mW)

    area = scipy.integrate.simps(points_mW, freq_array) # scipy.integrate.

    areadB = 10.0*math.log10(area)

    return areadB

def calc_max_min(listofLists):
    zipped_lists = zip(*listofLists)
    max_list = []
    min_list = []
    for list in zipped_lists :
        max_list.append(max(list))
        min_list.append(min(list))

    return max_list, min_list    