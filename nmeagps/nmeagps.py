#!/usr/bin/env python 
#////////////////////////////////////////////////////////////////////////////// 
# 
# Copyright (C) 2017 Jonathan Racicot 
# 
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
# <author>Jonathan Racicot</author> 
# <email>cyberrecce@gmail.com</email> 
# <date>2017-03-07</date> 
# <url>https://github.com/infectedpacket</url> 
#////////////////////////////////////////////////////////////////////////////// 
# Program Information 
# 
PROGRAM_NAME = "sirf-tx" 
PROGRAM_DESC = "Generates randomized NMEA-0183 messages for traffic emulation/fuzzing purposes." 
PROGRAM_USAGE = '''
%(prog)s -m|--msgid GGA,GSA,GSV,RMC,VTG|all -C|--config FILE [-c|--count NB_MESSAGES] [-s|--sleep MILLISECONDS] [-d|--use-defaults] [-h|--help]" 
'''

__version_info__ = ('0','1','0') 
__version__ = '.'.join(__version_info__) 
 
#////////////////////////////////////////////////////////////////////////////// 
# Imports Statements
import os
import sys
import time
import argparse
import string
from datetime import datetime
import random
#
#//////////////////////////////////////////////////////////////////////////////
# Global variables and constants
#
COMMENT = "#"
PARAM_SEP = "="
NO_VALUE = ""
CHOICE_SEP = ","

PARAM_LATITUDE = "latitude"
PARAM_LONGITUDE = "longitude"
PARAM_LAT_CARDINAL = "latitude_cardinal"
PARAM_LONG_CARDINAL = "longitude_cardinal"
PARAM_YEAR = "year"
PARAM_MONTH = "month"
PARAM_DAY = "day"
PARAM_HOUR = "hour"
PARAM_MINUTE = "minute"
PARAM_SECOND = "seconds"
PARAM_POSFIX = "posfix"
PARAM_SATCOUNT = "sat_count"
PARAM_SATVIEWS = "sat_views"
PARAM_HDOP = "hdop"
PARAM_VDOP = "vdop"
PARAM_PDOP = "pdop"
PARAM_ALTITUDE = "altitude"
PARAM_SPEED = "speed"

FIELD_MSGID = "MessageID"
FIELD_UTCTIME = "UTC Time"
FIELD_LATITUDE = "Latitude"
FIELD_LONGITUDE = "Lontitude"
FIELD_NS = "N/S Indicator"
FIELD_EW = "E/W Indicator"
FIELD_POS_FIX = "Position Fix"
FIELD_SAT_USED = "Satellite Used"
FIELD_SAT_IN_VIEWS = "Satellites in Views"
FIELD_SAT_ID = "Satellite ID"
FIELD_ELEVATION = "Elevation"
FIELD_AZIMUTH = "Azimuth"
FIELD_SNR = "SNR"
FIELD_HDOP = "HDOP"
FIELD_SPEED_GROUND = "Speed Over Ground"
FIELD_COURSE_GROUND = "Course Over Ground"
FIELD_MSL_ALTITUDE = "MSL Altitude"
FIELD_MSL_ALTITUDE_UNITS = "MSL Altitude Unit"
FIELD_UNITS = "Units"
FIELD_GEOID_SEP = "Geoid Separation"
FIELD_GEOID_SEP_UNITS = "Geoid Separation Unit"
FIELD_AGE_DIFF_CORR = "Age of Diff. Corr."
FIELD_DIFF_STATION_ID = "Diff. Ref. Station ID"
FIELD_MODE = "Mode"
FIELD_SAT_USED = "Satellite Used"
FIELD_VDOP = "VDOP"
FIELD_PDOP = "PDOP"
FIELD_NB_MESSAGES = "Number of Messages"
FIELD_CHECKSUM = "Checksum"
FIELD_MAGN_VAR = "Magnetic Variation"
FIELD_DATE = "Date"
FIELD_COURSE = "Course"
FIELD_REFERENCE = "Reference"

ID_GGA = "$GPGGA"
ID_GSA = "$GPGSA"
ID_GSV = "$GPGSV"
ID_RMC = "$GPRMC"
ID_VTG = "$GPVTG"

SUPPORTED_MESSAGES = [ID_GGA, ID_GSA, ID_GSV, ID_RMC, ID_VTG]

NORTH = "N"
SOUTH = "S"
EAST = "E"
WEST = "W"

MODE_AUTO = "A"
MODE_DGPS = "D"
MODE_DR = "E"

MODE1_MANUAL = "M"
MODE1_AUTO = "A"

MODE2_NOT_AVAIL =1
MODE2_2D = 2
MODE2_3D = 3

MODE_AUTONOMOUS = "A"
MODE_DPGS = "D"
MODE_DR = "E"

POSFIX_NOT_AVAIL = 0
POSFIX_GPS_SPS = 1
POSFIX_DIFF_GPS = 2
POSFIX_UNSUPPORTED = 3
POSFIX_DEAD_RECK = 6

UNIT_METERS = "M"

STATUS_VALID = "A"
STATUS_INVALID = "V"

DEFAULT_SAT_COUNT = 7
DEFAULT_HDOP = 1.0
DEFAULT_VDOP = 1.0
DEFAULT_PDOP = 1.0
DEFAULT_MSL_ALT = 9.0
DEFAULT_GEO_ID = None
DEFAULT_AGE_DIFF = None
DEFAULT_STATION_ID = "0000"
DEFAULT_MODE1 = MODE_AUTO
DEFAULT_MODE2 = MODE2_2D
DEFAULT_NB_MSG = 1
DEFAULT_MSG_NO = 1
DEFAULT_SAT_VIEWS = 1
DEFAULT_MAGNETIC_VAR = EAST
DEFAULT_SPEED_GROUND = 0.13
DEFAULT_COURSE_GROUND = 309.62
DEFAULT_STATUS = STATUS_VALID
DEFAULT_MODE = MODE_AUTO
#
#//////////////////////////////////////////////////////////////////////////////
#
#////////////////////////////////////////////////////////////////////////////// 
# Argument Parser Declaration 
# 
usage = PROGRAM_USAGE 
parser = argparse.ArgumentParser( 
	usage=usage,  
	prog=PROGRAM_NAME,  
	version="%(prog)s "+__version__,  
	description=PROGRAM_DESC) 

msg_options = parser.add_argument_group("Generation Options",  "Specifies message generation options") 
msg_options.add_argument("-m", "--msgid",  
	dest="message_ids", 
	default="ALL",
	help="Specifies one or more ID of messages to generate. Supported IDs are GGA, GSA, GSV, RMC, VTG or 'all'.") 
msg_options.add_argument("-c", "--count",  
	dest="nb_messages",  
	type=int, 
	default=1,
	help="Specifies the number of messages to generate.")
msg_options.add_argument("-s", "--sleep",  
	dest="delay",  
	type=int, 
	default=100,
	help="Delay in ms between each message generated.")	
	
gps_options = parser.add_argument_group("GPS Options",  "Specifies values for GPS-generated data.")

gps_options.add_argument("-C", "--config",  
	dest="config",
	default="nmea0183.conf",
	help="Configuration file for message generation.")
gps_options.add_argument("-d", "--use-defaults",  
	dest="use_defaults",
	action="store_true",
	default=False,
	help="Uses default values only and does not randomize GPS message options and values.")


#////////////////////////////////////////////////////////////////////////////// 

class Satellite(object):

	def __init__(self, id, elevation, azimuth, snr):
		self.id = id
		self.elevation = elevation
		self.azimuth = azimuth
		self.snr = snr

	def __str__():
		return "{id:s},{elev:d},{az:f},{snr:f}".format(
			id=self.id, 
			elev=self.elevation,
			az=self.azimuth,
			snr=self.snr)

class NMEASiRFOutputTransmitter(object):

	def __init__(self, ids, config, fixed_values, msg_count, output_delay):
		self.message_ids = ids
		self.config = config
		self.use_fixed_values = fixed_values
		self.message_count = msg_count
		self.delay = output_delay

	def Start(self):
		transmit = True
		self.messages_sent = 0
		
		while (transmit):
			message = OutputMessageFactory.GenerateNMEAMessage(
				self.message_ids, 
				self.config, 
				self.use_fixed_values)
				
			self.OutputMessage(message)
			self.messages_sent += 1
			time.sleep(self.delay)
			transmit = (self.messages_sent < self.message_count)

	def OutputMessage(message):
		print message

class NMEASiRFOutputMessage(object):
	
	_fields = {}
	
	def __init__(self, msg_id):
		set(FIELD_MSGID, msg_id)
	
	def _set(self, field, value):
		_fields[field] = value
		
	def _get(self, field):
		t = _fields[field]
		if (t == None):
			return NO_VALUE
		else:
			return _fields[field]
		
	@property
	def message_id(self):
		return _get(FIELD_MSGID)
	
	def checksum(self):
	'''
	Ref. https://en.wikipedia.org/wiki/NMEA_0183
	'''
		csum = 0
		return csum
	
class ValuesFactory(object):

	def __init__(self, config, fixed_values = False):
		self.config = config
		self.fixed_values = fixed_values

	def Bool(self, bool_val):
		return bool_val.lower() == 'true'

	def GetParameter(self, param_name, no_value_return = NO_VALUE):
		if param_name in self.config:
			return self.config[param_name]
		else:
			return no_value_return

	def _GenerateRandomIntValue(self, param_name):
		gen_value = NO_VALUE
		if (self.fixed_values):
			gen_value = self.GetParameter("{param:s}_default".format(param=param_name))
		else:
			min_value = self.GetParameter("min_{param:s}".format(param=param_name), 0)
			max_value = self.GetParameter("max_{param:s}".format(param=param_name), 100)
			gen_value = self.RandomInt(min_value, max_value)
			can_be_null = self.Bool(self.GetParameter("{param:s}_optional").format(param=param_name), False)
			if can_be_null:
				gen_value = self.RandomChoice(NO_VALUE, gen_value)
		return gen_value

	def _GenerateRandomFloatValue(self, param_name):
		gen_value = NO_VALUE
		if (self.fixed_values):
			gen_value = self.GetParameter("{param:s}_default".format(param=param_name))
		else:
			min_value = self.GetParameter("min_{param:s}".format(param=param_name), 0.0)
			max_value = self.GetParameter("max_{param:s}".format(param=param_name), 100.0)
			gen_value = self.RandomFloat(min_value, max_value)
			can_be_null = self.Bool(self.GetParameter("{param:s}_optional").format(param=param_name), False)
			if can_be_null:
				gen_value = self.RandomChoice(NO_VALUE, gen_value)
		return gen_value

	def _GenerateRandomChoice(self, param_name):
		gen_value = NO_VALUE
		if (self.fixed_values):
			gen_value = self.GetParameter("{param:s}_default".format(param=param_name))
		else:	
			choices = self.GetParameter(param_name).split(CHOICE_SEP)
			gen_choice = self.RandomChoice(choices)
			can_be_null = self.Bool(self.GetParameter("{param:s}_optional".format(param=param_name), False))
			if can_be_null:
				gen_value = self.RandomChoice(NO_VALUE, gen_value)
		return gen_value
		
	def RandomInt(self, min_value, max_value):
		return random.randint(min_value, max_value)
		
	def RandomString(self, alphabet, min_len, max_len):
		s = ""
		r = self.RandomInt(min_len, max_len)
		for i in range(0, r):
			s += self.RandomChoice(alphabet)
		return s
		
	def RandomFloat(self, min_value, max_value):
		return random.random()*float(max_value) + min_value
		
	def RandomChoice(self, choices):
		return random.choice(choices)
		
	def RandomLatitude(self):
		return self._GenerateRandomFloatValue(PARAM_LATITUDE);
		
	def RandomNorthSouth(self):
		return self._GenerateRandomChoice(PARAM_LAT_CARDINAL)
		
	def RandomLongitude(self):
		return self._GenerateRandomFloatValue(PARAM_LONGITUDE);
		
	def RandomEastWest(self):
		return self._GenerateRandomChoice(PARAM_LONG_CARDINAL);
		
	def RandomDateTime(self):
		year = self._GenerateRandomInt(PARAM_YEAR)
		month = self._GenerateRandomInt(PARAM_MONTH)
		day = self._GenerateRandomInt(PARAM_DAY)
		hours = self._GenerateRandomInt(PARAM_HOUR)
		minutes = self._GenerateRandomInt(PARAM_MINUTE)
		seconds = self._GenerateRandomInt(PARAM_SECONDS)
		generated_date = datetime.date(year, month, day)
		generated_time = datetime.time(hours, minutes, seconds)
		return generated_date.combine(generated_time)
		
	def RandomPositionFix(self):
		return self._GenerateRandomChoice(PARAM_POSFIX)
	
	def RandomSatelliteCount(self):
		return self._GenerateRandomIntValue(PARAM_SATCOUNT)
		
	def RandomSatelliteInViews(self):
		return self._GenerateRandomIntValue(PARAM_SATVIEWS)
		
	def RandomHdop(self):
		return self._GenerateRandomFloatValue(PARAM_HDOP);
	
	def RandomVdop(self):
		return self._GenerateRandomFloatValue(PARAM_VDOP);
	
	def RandomPdop(self):
		return self._GenerateRandomFloatValue(PARAM_PDOP);
	
	def RandomAltitude(self):
		return self._GenerateRandomFloatValue(PARAM_ALTITUDE);
	
	def RandomUnits(self):
		param = "dist_units"
		return self._GenerateRandomChoice(param)
	
	def RandomGeoIdSeparation(self):
		param = "geoid"
		return self._GenerateRandomFloatValue(param);
	
	def RandomAgeDiffCorrelation(self):
		param = "age_diff"
		return self._GenerateRandomFloatValue(param);
	
	def RandomStationId(self):
		return self.RandomString(strings.digits, 4, 4);
	
	def RandomMode1(self):
		param = "mode_manual_auto"
		return self._GenerateRandomChoice(param)
	
	def RandomMode2(self):
		param = "mode_2d_3d"
		return self._GenerateRandomChoice(param)
	
	def RandomRMCMode(self):
		param = "mode_rmc"
		return self._GenerateRandomChoice(param)
	
	def RandomSatellite(self):
		sat_id = self._GenerateRandomIntValue("sat_id")
		sat_elev = self._GenerateRandomIntValue("sat_elev")
		sat_azi = sself._GenerateRandomIntValue("sat_azimuth")
		sat_snr = self._GenerateRandomIntValue("sat_snr")
		satellite = Satellite(sat_id, sat_elev, sat_azi, sat_snr)
		return satellite
		
	def RandomNbMessage(self):
		param = "nb_message"
		return self._GenerateRandomIntValue(param)
		
	def RandomNoMessage(self):
		param = "no_message"
		return self._GenerateRandomIntValue(param)		
		
	def RandomStatus(self):
		param = "status"
		return self._GenerateRandomChoice(param)
		
	def RandomSpeed(self):
		return self._GenerateRandomFloatValue(PARAM_SPEED);
		
	def RandomCourse(self):
		param = "course"
		return self._GenerateRandomFloatValue(param);
	
class OutputMessageFactory(object):

	@staticmethod
	def GenerateNMEAMessage(message_ids, config, fixed_values):

		vf = ValuesFactory(config, fixed_values)		
		msg_id = vf.RandomChoice(message_ids)
		message = None

		if (msg_id == ID_GGA):
			message = OutputMessageFactory.GenerateRandomGGAMessage(vf)
		elif (msg_id == ID_GSA):
			message = OutputMessageFactory.GenerateRandomGSAMessage(vf)
		elif (msg_id == ID_GSV):
			message = OutputMessageFactory.GenerateRandomGSVMessage(vf)
		elif (msg_id == ID_RMC):
			message = OutputMessageFactory.GenerateRandomRMCMessage(vf)
		#elif (msg_id == ID_VTG):
		#	message = OutputMessageFactory.GenerateRandomVTGMessage(vf)
		else:
			raise Exception("Unknown message id: {id:s}".format(msg_id))
		
		return message

	@staticmethod
	def GenerateRandomGGAMessage(vf):

		latitude = vf.RandomLatitude()
		latcard = vf.RandomNorthSouth()
		longitude = vf.RandomLongitude()
		longcard = vf.RandomEastWest()
		utctime = vf.RandomDateTime().utcnow()
		posfix = vf.RandomPositionFix()
		satcount = vf.RandomSatelliteCount()
		hdop = vf.RandomHdop()
		altitude = vf.RandomAltitude()
		alt_units = vf.RandomUnits()
		geoid_sep = vf.RandomGeoIdSeparation()
		geo_units = vf.RandomUnits()
		agediff = vf.RandomAgeDiffCorrelation()
		station_id = vf.RandomStationId()

		message = OutputMessageFactory.CreateGGAMessage(
			latitude,
			latcard,
			longitude,
			longcard,
			utctime,
			posfix,
			satcount,
			hdop,
			altitude,
			alt_units,
			geoid_sep,
			geo_units,
			agediff,
			station_id)
		
		return message

	# Global Positionng System Fixed Data
	@staticmethod
	def CreateGGAMessage(latitude, latcardinal, longitude, longcardinal, 
		utctime = datetime.utcnow(), 
		posfix = POSFIX_GPS_SPS, 
		satcount = DEFAULT_SAT_COUNT, 
		hdop = DEFAULT_HDOP, 
		msl_alt = DEFAULT_MSL_ALT, 
		msl_unit = UNIT_METERS, 
		geoid = DEFAULT_GEO_ID, 
		geoid_unit = UNIT_METERS, 
		age_diff = DEFAULT_AGE_DIFF,
		station_id = DEFAULT_STATION_ID):
		
		message = GGAOutputMessage()
		message.set_utc_time(utctime)
		message.set_latitude(latitude)
		message.set_north_or_south(latcardinal)
		message.set_longitude(longitude)
		message.set_east_or_west(longcardinal)
		message.set_position_fix(posfix)
		message.set_satellites_used(satcount)
		message.set_hdop(hdop)
		message.set_msl_altitude(msl_alt)
		message.set_msl_altitude_units(msl_unit)
		message.set_geoid_separation(geoid)
		message.set_geoid_separation_units(geoid_unit)
		message.set_age_diff_corr(age_diff)
		message.set_diff_station_id(station_id)
		
		return message
	
	@staticmethod
	def GenerateRandomGSAMessage(vf):
	
		mode1 = vf.RandomMode1()
		mode2 = vf.RandomMode2()
		
		satellites = random.shuffle(range(1, vf.RandomInt(1,12)))
		
		pdop = vf.RandomPdop()
		hdop = vf.RandomHdop()
		vdop = vf.RandomVdop()
		
		message = OutputMessageFactory.CreateGSAMessage(
			mode1,
			mode2,
			satellites,
			pdop,
			hdop,
			vdop)
		return  message
	
	# GNSS DOP and Active Satellites
	@staticmethod
	def CreateGSAMessage(mode1 = DEFAULT_MODE1,
		mode2 = DEFAULT_MODE2,
		satellites = [],
		pdop = DEFAULT_PDOP,
		hdop = DEFAULT_HDOP,
		vdop = DEFAULT_VDOP):
		
		message = GSAOutputMessage()
		
		message.set_mode(1, mode1)
		message.set_mode(2, mode2)
		message.set_pdop(pdop)
		message.set_vdop(vdop)
		message.set_hdop(hdop)
		
		return message

	@staticmethod
	def GenerateRandomGSVMessage(vf):
	
		nb_msg = vf.RandomNbMessage()
		msg_number = vf.RandomInt(1, nb_msg)
		satellites = []
		satinviews = vf.RandomSatelliteInViews()
		
		for i in range (1, nb_msg):
			satellites.append(vf.RandomSatellite())
		
		message = OutputMessageFactory.CreateGSVMessage(
			nb_msg,
			msg_number,
			satinviews,
			satellites)
		return  message

	# GNSS Satellites in View
	@staticmethod
	def CreateGSVMessage(nb_msg = DEFAULT_NB_MSG, 
		msg_no= DEFAULT_MSG_NO,
		satviews = DEFAULT_SAT_VIEWS,
		satellites = []):
	
		message = GSVOutputMessage()
		message.set_nb_messages(nb_msg)
		message.set_msg_no(msg_no)
		message.set_nb_sat_in_view(satviews)
		message.add_satellites(satellites)
		
		return message

	@staticmethod
	def GenerateRandomRMCMessage(vf):
	
		latitude = vf.RandomLatitude()
		latcard = vf.RandomNorthSouth()
		longitude = vf.RandomLongitude()
		longcard = vf.RandomEastWest()
		utctime = vf.RandomDateTime().utcnow()
		status = vf.RandomStatus()
		speed = vf.RandomSpeed()
		course = vf.RandomCourse()
		dtg = vf.RandomDateTime()
		magnetic = vf.RandomEastWest()
		mode = vf.RandomRMCMode()
		
		message = OutputMessageFactory.CreateRMCMessage(
			utctime,
			latitude,
			latcard,
			longitude,
			longcard,
			status,
			speed,
			course,
			dtg,
			magnetic,
			mode);
		return  message

	# Recommended Minimum GNSS Data
	@staticmethod
	def CreateRMCMessage(latitude, latcardinal, longitude, longcardinal, 
		utctime = datetime.utcnow(),
		status = DEFAULT_STATUS,
		speedgnd = DEFAULT_SPEED_GROUND,
		coursegnd = DEFAULT_COURSE_GROUND,
		date = datetime.now(),
		magvar = DEFAULT_MAGNETIC_VAR,
		mode = DEFAULT_MODE):
	
		message = RMCOutputMessage()
		message.set_utc_time(utctime)
		message.set_latitude(latitude)
		message.set_north_or_south(latcardinal)
		message.set_longitude(longitude)
		message.set_east_or_west(longcardinal)
		message.set_status(status)
		message.set_speed_ground(speedgnd)
		message.set_course_ground(coursegnd)
		message.set_date(date)
		message.set_magnetic_var(magvar)
		message.set_mode(mode)
		
		return message
		
	@staticmethod
	def GenerateRandomVTGMessage(vf):
		raise Exception("Not implemented")

class GGAOutputMessage(NMEASiRFOutputMessage):

	def __init__(self):
		super.__init__(ID_GGA)

	def __str__(self):
		fmt='''
{msgid:s}, {time:s}, {lat:f}, {latc:s}, {long:f}, {longc:s}, {posf:d}, {sats:d}, {hdop:f}, {msl:f}, {mslu:s}, {geoid:f}, {geoidu:s}, {age:f}, {staid:s}*{csum:d}\r\n
'''
		msg = fmt.format(msgid = self.message_id,
			time = self.utc_time,
			lat = self.latitude,
			latc = north_or_south,
			long = longitude,
			longc = east_or_west,
			posf = position_fix,
			sats = satellites_used,
			hdop = hdop,
			msl = msl_altitude,
			mslu = msl_altitude_units,
			geoid = geoid_separation,
			geoidu = geoid_separation_units,
			age = age_diff_corr,
			staid = diff_station_id,
			csum = self.checksum())
		return msg
		
		
	def set_utc_time(self, time):
		_set(FIELD_UTCTIME, time)
		
	@property
	def utc_time(self):
		return _get(FIELD_UTCTIME)
	
	def set_latitude(self, latitude):
		_set(FIELD_LATITUDE, latitude)
			
	@property
	def latitude(self):
		return _get(FIELD_LATITUDE)
		
	def set_longitude(self, latitude):
		_set(FIELD_LONGITUDE, longitude)
				
	@property
	def longitude(self):
		return _get(FIELD_LONGITUDE)
		
	def set_north_or_south(self, _ns):
		_set(FIELD_NS, _ns)
			
	@property
	def north_or_south(self):
		return _get(FIELD_NS)
		
	def set_east_or_west(self, _ew):
		_set(FIELD_EW, _ew)
		
	@property
	def east_or_west(self):
		return _get(FIELD_EW)
		
	def set_position_fix(self, posfix):
		_set(FIELD_POS_FIX, posfix)
			
	@property
	def position_fix(self):
		return _get(FIELD_POS_FIX)

	def set_satellites_used(self, satused):
		_set(FIELD_SAT_USED, satused)
			
	@property
	def satellites_used(self):
		return _get(FIELD_SAT_USED)
		
	def set_hdop(self, hdop):
		_set(FIELD_HDOP, hdop)
		
	@property
	def hdop(self):
		return _get(FIELD_HDOP)
		
	def set_msl_altitude(self, altitude):
		_set(FIELD_MSL_ALTITUDE, altitude)

	@property
	def msl_altitude(self):
		return _get(FIELD_MSL_ALTITUDE)
		
	def set_msl_altitude_units(self, units):
		_set(FIELD_MSL_ALTITUDE_UNITS, units)
	
	@property
	def msl_altitude_units(self):
		return _get(FIELD_MSL_ALTITUDE_UNITS)
		
	def set_geoid_separation(self, geoid):
		_set(FIELD_GEOID_SEP, geoid)
	
	@property
	def geoid_separation(self):
		return _get(FIELD_GEOID_SEP)
		
	def set_geoid_separation_units(self, units):
		_set(FIELD_GEOID_SEP_UNITS, units)
	
	@property
	def geoid_separation_units(self):
		return _get(FIELD_GEOID_SEP_UNITS)

	def set_age_diff_corr(self, corr):
		_set(FIELD_AGE_DIFF_CORR, corr)
	
	@property
	def age_diff_corr(self):
		return _get(FIELD_AGE_DIFF_CORR)
	
	def set_diff_station_id(self, stationid):
		_set(FIELD_DIFF_STATION_ID, stationid)
	
	@property
	def diff_station_id(self):
		return _get(FIELD_DIFF_STATION_ID)
		
class GSAOutputMessage(NMEASiRFOutputMessage):

	def __init__(self):
		super.__init__(ID_GSA)
		super._satellites = []

	def __str__():
		fmt ='''
{msgid:s}, {mode1:s}, {mode2:s}, {satused:d}, {pdop:f}, {hdop:f}, {vdop:f}*{csum:d}\r\n
'''
		msg = fmt.format(msgid = self.message_id,
			mode1 = self.mode(1),
			mode2 = self.mode(2),
			satused = self.get_sat_str(),
			pdop = self.pdop,
			hdop = self.hdop,
			vdop = self.vdop,			
			csum = self.checksum())
			
		return msg
		
	def set_mode(self, modeno, mode):	
		_set(FIELD_MODE+"1", mode)
		
	@property
	def mode(self, modeno):
		return _get(FIELD_MODE+"modeno")
		
	def add_satellite(self, satno):
		self._satellites.append(satno)
		
	@property
	def get_satellites(self):
		return self._satellites
		
	def get_sat_str(self):
		return ", ".join(self._satellites)
		
	def set_hdop(self, hdop):
		_set(FIELD_HDOP, hdop)
		
	@property
	def hdop(self):
		return _get(FIELD_HDOP)
		
	def set_vdop(self, vdop):
		_set(FIELD_VDOP, vdop)
		
	@property
	def vdop(self):
		return _get(FIELD_VDOP)
		
	def set_pdop(self, vdop):
		_set(FIELD_PDOP, pdop)
		
	@property
	def pdop(self):
		return _get(FIELD_PDOP)
		
class GSVOutputMessage(NMEASiRFOutputMessage):

	def __init__(self):
		super.__init__(ID_GSV)
		self._satellites = []

	def __str__():
		fmt ='''
{msgid:s}, {nbmsg:d}, {satsv:d}, {sats:s}*{csum:d}\r\n
'''
		msg = fmt.format(msgid = self.message_id,
			nbmsg = self.nb_messages,
			satsv = self.nb_sat_in_view,
			sats = self.get_sat_str(), 
			csum = self.checksum())
			
		return msg
		
	def set_nb_messages(self, nbmsg):
		self._set(FIELD_NB_MESSAGES, nbmsg)
		
	@property
	def nb_messages():
		return self._get(FIELD_NB_MESSAGES)
		
	def set_msg_no(self, msgno):
		self._set(FIELD_MSG_NO, msgno)
	
	@property
	def msg_no(self):
		return self._get(FIELD_MSG_NO)
		
	def set_nb_sat_in_view(self, nbsats):
		self._set(FIELD_NB_MESSAGES, nbsats)
	
	@property
	def nb_sat_in_view(self):
		return self._get(FIELD_SAT_IN_VIEWS)
	
	def add_satellite(self, sat):
		self._satellites.append(sat)
		
	def add_satellites(self, sats):
		self._satellites += sats
		
	def get_sat_str(self):
		sat_strs = []
		fmt_sat = "{id:s}, {elev:d}, {azi:d}, {snr:d}"
		for sat in self._satellites:
			sat_strs.append(fmt_sat.format(
						id = sat.id,
						elev = sat.elevation,
						azi = sat.azimuth,
						snr = sat.snr))
		return ",".join(sat_strs)
		
		

class RMCOutputMessage(NMEASiRFOutputMessage):

	def __init__(self):
		super.__init__(ID_RMC)

	def __str__(self):
		fmt ='''
{msgid:s}, {time:s}, {stat:s}, {lat:f}, {latc:s}, {long:f}, {longc:s}, {sog:f}, {cog:f}, {date:s}, {magv:s}, {mode:s}*{csum:d}\r\n
'''
		msg = fmt.format(msgid = self.message_id,
			time = self.utc_time,
			stat = self.status,
			lat = self.latitude,
			latc = self.north_or_south,
			long = self.longitude,
			longc = self.east_or_west,
			sog = self.speed_over_ground,
			cog = self.course_over_ground,
			date = self.date,
			magv = self.magnetic_var,
			mode = self.mode,
			csum = self.checksum())
		return msg
		
	def set_utc_time(self, time):
		_set(FIELD_UTCTIME, time)
		
	@property
	def utc_time(self):
		return _get(FIELD_UTCTIME)
	
	def set_latitude(self, latitude):
		_set(FIELD_LATITUDE, latitude)
			
	@property
	def latitude(self):
		return _get(FIELD_LATITUDE)
		
	def set_longitude(self, latitude):
		_set(FIELD_LONGITUDE, longitude)
				
	@property
	def longitude(self):
		return _get(FIELD_LONGITUDE)
		
	def set_north_or_south(self, _ns):
		_set(FIELD_NS, _ns)
			
	@property
	def north_or_south(self):
		return _get(FIELD_NS)
		
	def set_east_or_west(self, _ew):
		_set(FIELD_EW, _ew)
		
	@property
	def east_or_west(self):
		return _get(FIELD_EW)
		
	def set_speed_over_ground(self):
		self._set(FIELD_SPEED_GROUND)
	
	@property
	def speed_over_ground(self):
		return self._get(FIELD_SPEED_GROUND)
		
	def set_course_over_ground(self):
		self._set(FIELD_COURSE_GROUND)
	
	@property
	def course_over_ground(self):
		return self._get(FIELD_COURSE_GROUND)
		
	def set_date(self, date):
		self._set(FIELD_DATE)
	
	@property
	def date(self):
		return self._get(FIELD_DATE)
		
	def set_magnetic_var(self, magv):
		self._set(FIELD_MAGN_VAR, magv)
	
	@property
	def magnetic_var(self):
		return self._get(FIELD_MAGN_VAR)
		
	def set_status(self, status):
		self._set(status)
	
	@property
	def status(self):
		return self._get(status)
		
		
	def set_mode(self, mode):
		self._set(FIELD_MODE, mode)
	
	@property
	def mode(self):
		return self._get(FIELD_MODE)
	
class VTGOutputMessage(NMEASiRFOutputMessage):

	def __init__(self):
		super.__init__(ID_VTG)

	def __str__(self):
		fmt ='''
{msgid:s}, {crse1:f}, {ref1:s}, {crse2:f}, {ref2:s}, {spd1:f}, {unt1:s}, {spd2:s}, {unt2:s}, {mode:s}*{csum:d}\r\n
'''
		msg = fmt.format(msgid = self.message_id,
			crse1 = self.course(1),
			ref1 = self.reference(1),
			crse2 = self.course(2),
			ref2 = self.reference(2),
			crse3 = self.course(3),
			ref3 = self.reference(3),
			mode = self.mode,
			csum = self.checksum())
		return msg

	def set_course(self, crseid, course, ref):
		self._set(FIELD_COURSE+str(crseid), course)
		self._set(FIELD_REFERENCE+str(crseid), ref)
		
	def course(self, crseid):
		return self._get(FIELD_COURSE+str(crseid))
		
	def reference(self, refid):
		return self._get(FIELD_REFERENCE+str(refid))
		
	def set_mode(self, mode):
		self._set(FIELD_MODE, mode)
	
	@property
	def mode(self):
		return self._get(FIELD_MODE)
		
		
class GLLOutputMessage(NMEASiRFOutputMessage):

	def __init__(self):
		super.__init__(ID_GLL)

	def __str__(self):
		fmt ='''
{msgid:s}, {lat:f}, {latc:s}, {long:f}, {longc:s}, {time:s}, {stat:s}, {mode:s}*{csum:d}\r\n
'''
		msg = fmt.format(msgid = self.message_id,
			lat = self.latitude,
			latc = self.north_or_south,
			long = self.longitude,
			longc = self.east_or_west,
			time = self.utc_time,
			status = self.status,
			mode = self.mode,
			csum = self.checksum())
		return msg
		
	def set_utc_time(self, time):
		_set(FIELD_UTCTIME, time)
		
	@property
	def utc_time(self):
		return _get(FIELD_UTCTIME)
	
	def set_latitude(self, latitude):
		_set(FIELD_LATITUDE, latitude)
			
	@property
	def latitude(self):
		return _get(FIELD_LATITUDE)
		
	def set_longitude(self, latitude):
		_set(FIELD_LONGITUDE, longitude)
				
	@property
	def longitude(self):
		return _get(FIELD_LONGITUDE)
		
	def set_north_or_south(self, _ns):
		_set(FIELD_NS, _ns)
			
	@property
	def north_or_south(self):
		return _get(FIELD_NS)
		
	def set_east_or_west(self, _ew):
		_set(FIELD_EW, _ew)
		
	@property
	def east_or_west(self):
		return _get(FIELD_EW)
		
	def set_status(self, status):
		self._set(status)
	
	@property
	def status(self):
		return self._get(status)
		
	def set_mode(self, mode):
		self._set(FIELD_MODE, mode)

	@property
	def mode(self):
		return self._get(FIELD_MODE)
		
def read_config(config_file):
	params = []
	config = {}
	with open(config_file, "r") as f:
		params = f.readlines()
		
	for param in params:
		param = param.strip()
		if (len(param) > 0 and param[0] != COMMENT):
			if (PARAM_SEP in param):
				(param_name, param_value) = param.split(PARAM_SEP, 1)
				config[param_name] = param_value
			else:
				raise Exception("Invalid parameter definition: {line:s}".format(line = param))
	return config
		
def main(args):
	message_ids = args.message_ids.upper()
	nb_messages = args.nb_messages
	config_file = args.config
	use_defaults_only = args.use_defaults
	delay = float(args.delay)/1000.0
	param_error = False

	if ("ALL" in message_ids):
		message_ids = SUPPORTED_MESSAGES
	else:
		ids = message_ids.split(CHOICE_SEP)
		message_ids = []
		for id in ids:
			nmea_id = "$GP{id:s}".format(id)
			if nmea_id in SUPPORTED_MESSAGES:
				message_ids.append(nmea_id)
			else:
				print "[-] Unknown message id: {id:s}".format(nmea_id)
				param_error = True
	
	try:
		config = read_config(config_file)
	except:
		param_error = True
	
	if param_error:
		print "[!] Invalid parameters were ignored. Do you wish to continue nonetheless? [Y/n]"
		answer = input("[?]: ")
		if (not answer.lower() in ['y', 'yes', 'yeah', 'yup']):
			print "[!] Program terminated."
			sys.exit(1)
	
	tx = NMEASiRFOutputTransmitter(message_ids, config, use_defaults_only, nb_messages, delay)
	tx.Start()
		
if __name__ == "__main__": 
	main(parser.parse_args()) 
