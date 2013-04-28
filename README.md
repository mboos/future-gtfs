Future GTFS
===========

Tool for augmenting GTFS datasets with potential future transit routes and service frequencies.

Sample GTFS data provided is taken from the 
[Region of Waterloo Open Dataset](http://www.regionofwaterloo.ca/opendata 
"Contains information provided by the Regional Municipality of Waterloo under licence"), 
while the `sample.json` file is based on best-guesses of future 
[Rapid Transit](http://rapidtransit.regionofwaterloo.ca/en/) and iXpress service with 
[Grand River Transit](http://www.grt.ca/).

Usage
-----

`createGTFS.py -j jsonfile -g gtfsDir -o outputDir`

where `jsonfile` is a json file containing information about the stops and service frequencies of new routes, 
`gtfsDir` is the directory where the GTFS dataset resides, 
and `outputDir` is the directory where the newly generated GTFS dataset is to be written.

Note that outputDir will be completely overwritten by this command.

JSON input file
---------------

    [
       {
          "id": "LRT", // Route id
          "type": "0", // GTFS route type 0=rail, 3=bus
          "name": "Light Rail",
          "trips": [
             {
                "headsign": "Conestoga Mall",
                "schedule": [
                   {
                      "start": "5:30:00",
                      "headway": 900 // in seconds
                   },
                   {
                      "start": "6:30:00",
                      "headway": 450
                   },
                   {
                      "start": "7:00:00",
                      "headway": 450,
                      "factor": 1.05 // slowdown factor based on time of day
                   },
                   ...
                   {
                      "start": "21:45:00",
                      "headway": 900,
                      "factor": 1
                   },
                   {
                      "start": "24:20:00" // end of service for day
                   }
                ],
                "stops": [
                   {
                      "stop_id": "1046", // existing stop
                      "time_from_last": 0,
                      "cumulative_time": 0
                   },
                   {
                      "lat": "43.422459", // new stop requires name, lat, lon
                      "lon": "-80.462486", 
                      "name": "Block Line",
                      "cumulative_time": 167, // cumulative_time and time_from_last are optional
                      "time_from_last": 167   // if not supplied, will be estimated via OpenMapquest
                   },
                   ...
                   {
                      "stop_id": "3798",
                      "time_from_last": 246,
                      "cumulative_time": 2083
                   }
                ]
             },
             {
                "headsign": "Fairview Park Mall", // opposite direction
                "schedule": [
                   ...
                ],
                "stops": [
                   ...
                ]
             }
          ]
       },
       ...
    ]
