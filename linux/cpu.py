#!/usr/bin/env python
from common import get_config, create_rrd
import rrdtool

CONFIG = get_config()
RRD_DATA_SOURCES = [
    "DS:user:DERIVE:120:0:U",
    "DS:nice:DERIVE:120:0:U",
    "DS:system:DERIVE:120:0:U",
    "DS:idle:DERIVE:120:0:U",
    "DS:wait:DERIVE:120:0:U",
    "RRA:AVERAGE:0.5:1:2880",
    "RRA:AVERAGE:0.5:30:672",
    "RRA:AVERAGE:0.5:120:732",
    "RRA:AVERAGE:0.5:720:1460"
]
RRD = "cpu.rrd"

# Create RRD file if it doesn't already exist
create_rrd(RRD, RRD_DATA_SOURCES)

# Get values from /proc/stat
user, nice, system, idle, wait = [int(x) for x in open("/proc/stat", 'r').readline().split()[1:6]]

# Update RRD values
rrdtool.update(
    RRD,
    "-t",
    "user:nice:system:idle:wait",
    "N:%s:%s:%s:%s:%s" % (user, nice, system, idle, wait)
)

# Create images
for period in ["hour", "day", "week", "month", "year"]:
    rrdtool.graph(
        "cpu_%s.png" % period,
        "-s -1%s" % period,
        "-t Cpu usage",
        "--lazy",
        "-h", "150", "-w", "700",
        "-r",
        "-l 0",
        "-a", "PNG",
        "-v cpu usage",
        "DEF:user=cpu.rrd:user:AVERAGE",
        "DEF:nice=cpu.rrd:nice:AVERAGE",
        "DEF:system=cpu.rrd:system:AVERAGE",
        "DEF:idle=cpu.rrd:idle:AVERAGE",
        "DEF:wait=cpu.rrd:wait:AVERAGE",

        "AREA:user#FF0000:User",
        "GPRINT:user:MIN:    Min\\: %4.0lf ",
        "GPRINT:user:AVERAGE: Avg\\: %4.0lf ",
        "GPRINT:user:MAX:  Max\\: %4.0lf \\n",

        "STACK:nice#000099:Nice",
        "GPRINT:nice:MIN:    Min\\: %4.0lf ",
        "GPRINT:nice:AVERAGE: Avg\\: %4.0lf ",
        "GPRINT:nice:MAX:  Max\\: %4.0lf \\n",

        "STACK:system#FFFF00:System",
        "GPRINT:system:MIN:  Min\\: %4.0lf ",
        "GPRINT:system:AVERAGE: Avg\\: %4.0lf ",
        "GPRINT:system:MAX:  Max\\: %4.0lf \\n",

        "STACK:idle#32CD32:Idle",
        "GPRINT:idle:MIN:    Min\\: %4.0lf ",
        "GPRINT:idle:AVERAGE: Avg\\: %4.0lf ",
        "GPRINT:idle:MAX:  Max\\: %4.0lf \\n",

        "STACK:wait#ff9c0f:Wait",
        "GPRINT:wait:MIN:    Min\\: %4.0lf ",
        "GPRINT:wait:AVERAGE: Avg\\: %4.0lf ",
        "GPRINT:wait:MAX:  Max\\: %4.0lf \\n",
        "HRULE:0#000000",
        # Draw a line across the max for what max usage should be
        # this is particularly usefull if you have hyperthreading
        # or if you change processor count
        "HRULE:%s#000000:Max Usage" % (CONFIG['cpu']['physical'] * 100),
    )
