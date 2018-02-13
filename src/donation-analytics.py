import os
import datetime
import math

def extractInfo(line):
    fields = line.split('|')
    
    #CMTE_ID
    CMTE_ID = fields[0]
    if not CMTE_ID:
        return None
    
    #NAME
    NAME = fields[7]
    if not NAME:
        return None
    
    names = NAME.split(',')
    if len(names) != 2: 
        #if the name is not splited into last name and first name
        return None
    else:
        #check if any illegal symbols exist in the name
        if not names[0].isalpha():
            return None
        else:
            subNames = names[1].split(' ')[1:]
            for subName in subNames:
                if not subName.isalpha():
                    return None
    
    #ZIP_CODE
    ZIP_CODE = fields[10]  
    if not ZIP_CODE or len(ZIP_CODE) < 5:
        return None
    
    ZIP_CODE = ZIP_CODE[0:5]
    
    #TRANSACTION_DT
    TRANSACTION_DT = fields[13]
    transDate = None
    
    #if the format is valid
    if not TRANSACTION_DT or len(TRANSACTION_DT) != 8:
        return None
    else:
        month = int(TRANSACTION_DT[0:2])
        day = int(TRANSACTION_DT[2:4])
        year = int(TRANSACTION_DT[4:])
        try:
            transDate = datetime.datetime(year, month, day)
        except ValueError:
            return None
    
    #TRANSACTION_AMT
    TRANSACTION_AMT = fields[14]
    if not TRANSACTION_AMT:
        return None
    
    transAmt = round(float(TRANSACTION_AMT))
    
    #OTHER_ID
    OTHER_ID = fields[15]
    if OTHER_ID:
        return None
    
    return [CMTE_ID, NAME, ZIP_CODE, transDate, transAmt]

def calculatePercentile(amounts, percent):
    if len(amounts) == 1:
        return amounts[0]
    else:
        sortedAmts = sorted(amounts)
        index = math.ceil(percent / 100 * len(amounts)) - 1
        return sortedAmts[index]

def makeOutput(info, amounts, percent):
    percentile = calculatePercentile(amounts, percent)
    totalAmt = sum(amounts)
    number = len(amounts)
    output = info[0] + '|' + info[2]  + '|'  + str(info[3].year)  + '|'  + str(percentile)  + '|' + str(totalAmt)  + '|'  + str(number) + '\n'
    return output

#get the file path
path = os.getcwd()
pathList = path.split('/')

#generate the directories for the input and output folders
inPath = '/'.join(pathList) + '/input'
outPath = '/'.join(pathList) + '/output'

#open files in the input 
itcontPath = inPath + '/itcont.txt'
percentilePath = inPath + '/percentile.txt'
itcont = open(itcontPath, 'r')
percentile = open(percentilePath, 'r')

#open the repeat_donors file
repDonorsPath = outPath + '/repeat_donors.txt'
repDonors = open(repDonorsPath, 'w')

#get the percentile
percentStr = percentile.readline()[:-1]
percent = int(percentStr)
percentile.close()

#lookup table of donors
donors = []

#donations to the same recipient and zip code in a year
recips = []
year = None

#read lines in itcont
for line in itcont:
    info = extractInfo(line) 
    if info is not None:
        #make the combination of name and zip code as a serial value
        serial = info[1] + info[2]
        identity = (serial, info[3].year)

        #if a new calendar year comes, clear the recipient list
        if year is not None and info[3].year > year: 
            recips = []

        year = info[3].year
        newDonor = True

        if donors:          
            i = 0
            for donor in donors:
                #the name is found in donors' list
                if donor[0] == identity[0]: 
                    newDonor = False                        

                    if donor[1] < identity[1]:       
                        #from the new calendar year
                        output = ''
                        recipId = info[0] + info[2]

                        #from an existed recipient 
                        if recips:
                            for recip in recips:
                                if recipId == recip[0]:
                                    recip[1].append(info[4])
                                    output = makeOutput(info, recip[1], percent)
                                    break

                        #from a new recipient
                        if output == '':
                            newRecip = (recipId, [info[4]])
                            recips.append(newRecip)
                            output = makeOutput(info, newRecip[1], percent)

                        #write to file
                        repDonors.write(output)                       
                    elif donor[1] > identity[1]:
                        #from a previous calendar year, don't output
                        donors[i] = identity
                    break
                else:
                    i += 1
        #add a new donor
        if newDonor:
            donors.append(identity)   

#close files
itcont.close()
repDonors.close()