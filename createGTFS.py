#!/usr/bin/env python

def readCSV(fileName, idColumn=None, sep=','):
    '''Reads csv file in fileName.
    If idColumn is defined, use values in column as dict keys
    otherwise, put all values in list
    Define sep to use a different separator from ','
    '''
    if idColumn:
        data = {}
    else:
        data = []
    
    with open(fileName, 'r') as file:
        line = file.readline()
        headings = map(str.strip, line.split(sep))
        if idColumn:
            id = headings.index(idColumn)
        for line in file:
            tokens = map(str.strip, line.split(sep))
            if idColumn:
                row = tokens[id]
            else:
                data.append({})
                row = -1
            data[row] = {}
            for i,h in enumerate(headings):
                data[row][h] = tokens[i]
                
    return data, headings

import urllib2, urllib, json
    
def getTripTime(locFrom, locTo):
    url = 'http://open.mapquestapi.com/directions/v1/route'
    
    tripKeys = {
        'from': locFrom['stop_lat'] + ',' + locFrom['stop_lon'],
        'to': locTo['stop_lat'] + ',' + locTo['stop_lon'],
        'narrativeType': 'none',
        'routeType': 'fastest',
        'locale': 'en_GB',
        'unit': 'k' 
    }

    f = urllib2.urlopen(url + '?' + urllib.urlencode(tripKeys))
    result = json.load(f)
    return result['route']['time']#, result['route']['distance']
    
def getRouteData(stops, routeFileName):
    import json
    with open(routeFileName, 'r') as file:
        routes = json.load(file)
    newStops = []
    
    newStopNum = 10000
    
    for route in routes:
        for trip in route['trips']:
            lastStop = None
            for stop in trip['stops']:
                if not stop.has_key('stop_id'):
                    stop_id = None
                    for existing in stops.values():
                        if existing['stop_lat'] == stop['lat']  and existing['stop_lon'] == stop['lon']:
                            stop_id = existing['stop_id']
                    if not stop_id:
                        stop_id = str(newStopNum)
                        newStopNum += 1
                        
                        stops[stop_id] = {
                            'stop_id': stop_id,
                            'stop_lat': stop['lat'],
                            'stop_lon': stop['lon'],
                            'stop_name': stop['name'],
                            'stop_desc': 'easyGo ' + stop_id,
                            'zone_id': '',
                            'location_type': '0'
                        }
                        newStops.append(stop_id)
                    
                    stop['stop_id'] = stop_id
                
                if lastStop is not None:
                    if not stop.has_key('time_from_last'):
                        stop['time_from_last'] = getTripTime(stops[lastStop['stop_id']], stops[stop['stop_id']])
                    stop['cumulative_time'] = stop['time_from_last'] + lastStop['cumulative_time']
                else:
                    stop['time_from_last'] = 0
                    stop['cumulative_time'] = 0
                lastStop = stop
    return routes, newStops

def writeCSVline(rawVals, headings, file, sep=","):
    vals = []
    for heading in headings:
        vals.append(rawVals[heading])
    file.write(sep.join(vals) + '\n')

def writeNewRoute(route, headings, file):
    rawVals = {
        'route_long_name': route['name'],
        'route_id': route['id'],
        'route_type': route['type'],
        'route_short_name': route['id'],
        'route_text_color': '',
        'agency_id': '',
        'route_color': '',
        'route_url': ''
    }
    writeCSVline(rawVals,headings,file)

def writeNewTrip(trip, tripNum, route, headings, file):
    rawVals = {
        'route_id': route['id'],
        'trip_headsign': trip['headsign'],
        'service_id': 'muwtf',
        'trip_id': str(tripNum),
        'block_id': '',
        'shape_id': ''
    }
    writeCSVline(rawVals,headings,file)
    
def parseTime(timeString):
    '''parse a HH:MM:SS formatted string into number of seconds after midnight
    '''
    return sum(60**(2-i)*int(v) for i,v in enumerate(timeString.split(':')))
    
def formatTime(seconds):
    '''return a HH:MM:SS formatted string from number of seconds after midnight
    '''
    m,s = divmod(seconds, 60)
    h,m = divmod(m, 60)
    return '%02d:%02d:%02d' % (h, m, s)

def writeNewStopTime(stop, stopNum, tripNum, time, headings, file):
    timeStr = formatTime(time)
    rawVals = {
        'trip_id': str(tripNum),
        'arrival_time': timeStr,
        'departure_time': timeStr,
        'stop_id': stop['stop_id'],
        'stop_sequence': str(stopNum),
        'stop_headsign': '',
        'pickup_type': '',
        'drop_off_type': '',
        'shape_dist_traveled': ''
    }
    writeCSVline(rawVals,headings,file)
    
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate new GTFS rows based on estimates of future service.')
    parser.add_argument('-j', '--json', dest='jsonFile', required=True,
                       help='json file containing future transit service information')
    parser.add_argument('-g', '--gtfs', dest='gtfsDir', required=True,
                       help='directory containing GTFS of existing service')
    parser.add_argument('-o', '--output', dest='outDir', required=True,
                       help='directory where new GTFS data is to be output')
    
    args = parser.parse_args()
    gtfsDir = args.gtfsDir
    jsonFile = args.jsonFile
    outDir = args.outDir
    
    import os.path
    stopSource = os.path.join(gtfsDir, 'stops.txt')
    routeSource = os.path.join(gtfsDir, 'routes.txt')
    tripSource = os.path.join(gtfsDir, 'trips.txt')
    stopTimeSource = os.path.join(gtfsDir, 'stop_times.txt')
    
    stops, stopHeadings = readCSV(stopSource, 'stop_id')
    dummy, routeHeadings = readCSV(routeSource, 'route_id')
    dummy, tripHeadings = readCSV(tripSource, 'trip_id')
    dummy, stopTimeHeadings = readCSV(stopTimeSource)
    dummy = None
    
    routes, newStops = getRouteData(stops, jsonFile)
    
    stopDest = os.path.join(outDir, 'stops.txt')
    routeDest = os.path.join(outDir, 'routes.txt')
    tripDest = os.path.join(outDir, 'trips.txt')
    stopTimeDest = os.path.join(outDir, 'stop_times.txt')
    
    import shutil
    shutil.rmtree(outDir)
    shutil.copytree(gtfsDir, outDir)
    
    with open(stopDest, 'a') as newStopsFile:
        for stop_id in newStops:
            stop = stops[stop_id]
            vals = []
            for heading in stopHeadings:
                vals.append(stop[heading])
            newStopsFile.write(','.join(vals) + '\n')
    
    newTripNum = 10000000
    with open(routeDest, 'a') as newRoutesFile, open(tripDest, 'a') as newTripsFile, open(stopTimeDest, 'a') as newStopTimesFile:
        for route in routes:
            writeNewRoute(route, routeHeadings, newRoutesFile)
            
            for trip in route['trips']:
                schedIter = iter(trip['schedule'])
                cur = schedIter.next()
                curTime = parseTime(cur['start'])
                headway = cur['headway']
                factor = cur['factor'] if cur.has_key('factor') else 1
                next = schedIter.next()
                nextTime = parseTime(next['start'])
                while next:
                    if curTime >= nextTime:
                        try:
                            headway = next['headway']
                            factor = next['factor'] if next.has_key('factor') else 1
                            next = schedIter.next()
                            nextTime = parseTime(next['start'])
                        except:
                            next = None
                    writeNewTrip(trip, newTripNum, route, tripHeadings, newTripsFile)
                
                    for i,stop in enumerate(trip['stops']):
                        writeNewStopTime(stop, i+1, newTripNum, curTime +
                                         (factor * stop['cumulative_time']),
                                         stopTimeHeadings, newStopTimesFile)
                        
                    newTripNum += 1
                    curTime += headway
 
if __name__ == "__main__":
    main()