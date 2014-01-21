"""Simple GPX converter"""

#    This file is part of the Route Analysis Toolkit.
#
#    The Route Analysis Toolkit is free software:
#    you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with the Route Analysis Toolkit.
#    If not, see <http://www.gnu.org/licenses/>.

# Author: Dave Richards


import re
import datetime

def convertgpx( gpxin, dataout ):
    """Convert GPX data to CSV
    gpxin - a GPX file
    dataout - a name to contain CSV data in the following format:
              input line, segment, longitude, latitude, elevation, time
              """
    track_break = re.compile('<trkseg>')

    long_lat_re = re.compile('<trkpt lat="([-+]?\d+\.\d*)" lon="([-+]?\d+\.\d*)">')
    elevation_re = re.compile('<ele>([-+]?\d+\.\d*)</ele>')
    time_re = re.compile('<time>(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)Z</time>')
    endpoint = re.compile('</trkpt>')

    segment = 0
    inputline = 0

    thistime = None
    lastsegment = None
    lasttime = None

    with open(gpxin, 'r') as instream:
        with open(dataout, 'w') as outstream:

            for gpxdata in instream:
                inputline += 1

                if track_break.search( gpxdata ) != None:
                    segment += 1
                    pointdata = dict()
                    pointdata['input_line'] = inputline
                    pointdata['segment'] = segment

                long_lat_match = long_lat_re.search( gpxdata )
                elevation_match = elevation_re.search( gpxdata )
                time_match = time_re.search( gpxdata )
                end_match = endpoint.search( gpxdata )

                if long_lat_match != None:
                    pointdata['longitude'] = long_lat_match.group(1)
                    pointdata['latitude'] = long_lat_match.group(2)

                if elevation_match != None:
                    pointdata['elevation'] = elevation_match.group(1)

                if time_match != None:
                    pointdata['time'] = ','.join(time_match.groups() )
                    thistime = datetime.datetime( *map(int, time_match.groups()) )

                if end_match != None:
                    if not pointdata.has_key('longitude'):
                        pointdata['longitude'] = 'LONG'
                    if not pointdata.has_key('latitude'):
                        pointdata['latitude'] = 'LAT'

                    if not pointdata.has_key('time'):
                        pointdata['time'] = 'NoTime'
                    if not pointdata.has_key('elevation'):
                        pointdata['elevation'] = '-1'

                    if thistime != None and lasttime != None and segment == lastsegment:
                        if (thistime-lasttime) >= datetime.timedelta( minutes = 10 ):
                            segment += 1
                            pointdata['segment'] = segment

                    print >> outstream, ','.join( [ str(pointdata['input_line']), str(pointdata['segment']),pointdata['longitude'], pointdata['latitude'], pointdata['elevation'], pointdata['time'] ] )
                    lasttime = thistime
                    lastsegment = segment

                    pointdata = dict()
                    pointdata['input_line'] = inputline
                    pointdata['segment'] = segment
