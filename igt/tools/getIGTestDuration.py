import json, datetime, time, os, csv
import pdb

def getDelta(startTime,endTime):

	startTime = datetime.datetime.fromtimestamp(float(startTime))
	endTime = datetime.datetime.fromtimestamp(float(endTime))
	delta = endTime - startTime
	return delta.total_seconds()

#jsonFile = '/home/hiperezr/Downloads/tmp/trc/html/results.json'
csvFile = '/tmp/igtFull.csv'

c = csv.writer(open(csvFile,'w'))
c.writerow(['COMPONENT','NAME','TEST DURATION',])

mainPath = '/home/hiperezr/allJsons'
for root, dirs, files in os.walk(mainPath):
	for jsonFile in files:
		with open(mainPath + '/' + jsonFile) as json_file:
			data = json.load(json_file)
			tests = data['tests']
			for test in tests:
				startTime = data['tests'][test]['time']['start']
				endTime = data['tests'][test]['time']['end']
				#seconds = str(test) + str(round(getDelta(startTime,endTime),2)) + ' seconds'
				seconds = round(getDelta(startTime,endTime),2) # two decimals
				hoursAbsolutes = time.strftime("%H:%M:%S", time.gmtime(seconds)).split(':')[0] # like 00
				minutesAbsolutes = time.strftime("%H:%M:%S", time.gmtime(seconds)).split(':')[1] # like 00
				secondsAbsolutes = time.strftime("%H:%M:%S", time.gmtime(seconds)).split(':')[2] # like 00

				#print '*****minutesAbsolutes **** : ' + str(minutesAbsolutes)

				if minutesAbsolutes != '00' :
					# here the test takes more than 1 minute
					print str(test)  + ' == duration : ' + str(time.strftime("%H:%M:%S", time.gmtime(seconds))) + ' minutes'
					c.writerow(['igt',test,str(time.strftime("%H:%M:%S", time.gmtime(seconds))) + ' minutes',])
				else:
					# here the test took less than 1 minute
					print str(test)  + ' == duration : ' + str(seconds) + ' seconds'
					c.writerow(['igt',test,str(seconds)+ ' seconds',])