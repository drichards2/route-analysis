"""Convert routes to SVG"""

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

import cairo

import re
import datetime
import math


def rendergpx( gpxin, svgout ):
    """Render a GPX file to an SVG
    gpxin - a GPX file
    svgout - an SVG containing a rendering of the routes contained in the file
    """
    track_break = re.compile('<trkseg>')

    long_lat_re = re.compile('<trkpt lat="([-+]?\d+\.\d*)" lon="([-+]?\d+\.\d*)">')
    elevation_re = re.compile('<ele>([-+]?\d+\.\d*)</ele>')
    time_re = re.compile('<time>(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)Z</time>')
    endpoint = re.compile('</trkpt>')

    segment = 0
    inputline = 0

    # Currently set up for a whole of England view

    # Roughly A5 size at 300ppi
    HEIGHT = 2490
    WIDTH = 1740

    # In 'degrees' lat/long
    X_TARGET_WIDTH = 5
    X_CENTRE = -0.893
    Y_CENTRE = 52.230

    LEFT = X_CENTRE - X_TARGET_WIDTH/2
    BOTTOM = Y_CENTRE + HEIGHT*X_TARGET_WIDTH/(2*WIDTH)

    SCALE = WIDTH/X_TARGET_WIDTH

    thistime = None
    lastsegment = None
    lasttime = None

    with open(gpxin, 'r') as instream:
        fo = file(svgout, 'w')

        surface = cairo.SVGSurface(fo, WIDTH, HEIGHT)
        ctx = cairo.Context(surface)
        ctx.scale(SCALE, -SCALE)
        ctx.translate(-LEFT, -BOTTOM)

        drawing_sector = False


        for gpxdata in instream:
            inputline += 1

            if track_break.search( gpxdata ) != None:
                if drawing_sector:
                    ctx.set_source_rgb(0.3, 0.2, 0.5)
                    ctx.set_line_width(0.04)
                    ctx.stroke()
                    drawing_sector = False

                segment += 1
                pointdata = dict()
                pointdata['input_line'] = inputline
                pointdata['segment'] = segment

            long_lat_match = long_lat_re.search( gpxdata )
            elevation_match = elevation_re.search( gpxdata )
            time_match = time_re.search( gpxdata )
            end_match = endpoint.search( gpxdata )

            if long_lat_match != None:
                pointdata['latitude'] = long_lat_match.group(1)
                pointdata['longitude'] = long_lat_match.group(2)
 
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

                        if drawing_sector:
                            ctx.set_source_rgb(0.3, 0.2, 0.5)
                            ctx.set_line_width(0.04)
                            ctx.stroke()
                            drawing_sector = False
                    else:
                        if drawing_sector:
                            ctx.line_to( float(pointdata['longitude']), float(pointdata['latitude']) )
                        else:
                            ctx.move_to( float(pointdata['longitude']), float(pointdata['latitude']) )
                            drawing_sector = True
 
                lasttime = thistime
                lastsegment = segment
 
                pointdata = dict()
                pointdata['input_line'] = inputline
                pointdata['segment'] = segment

        surface.finish()
        fo.close()
