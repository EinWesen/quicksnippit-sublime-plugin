import re
import sublime

def get_quicksnippets_setting(key, default):
	return sublime.active_window().active_view().settings().get("plugin.quicksnippet."+key, default) #load_settings("Preferences.sublime-settings")

def is_str_empty(s):
	try:
		return s == None or s.strip() == ""
	except:
		return False
#end def

def is_str_not_empty(s):
	try:
		return s.strip() != ""
	except:
		return True
#end def

def castStringAsDict(variables):
	if variables!=None:		
		if (type(variables) is dict) != True:
			
			try:

				if (variables.strip() != ""):					

					try:
						variables = sublime.decode_value(variables) # may throw ValueError
					except:
						# we do try some simple things
						if re.match("[a-zA-z_]\\w*?=[^\"]*$", variables) != None:
							key,val = variables.split("=",1)
							variables = sublime.decode_value("{\"" + key + "\":\""+ val + "\"}") # may still throw ValueError
						elif re.match("(['\"])[^'\"]*?\\1=(['\"])[^'\"]*?\\2", variables) != None:
							key,val = variables.split("\"=\"",1)
							variables = sublime.decode_value("{" + key + "\":\""+ val + "}") # may still throw ValueError
						elif re.match("(['\"])[^'\"]?\\1\\:(['\"])[^'\"]*?\\2", variables) != None:
							variables = sublime.decode_value("{" + variables + "}") # may still throw ValueError
						#end if
					#end try

					# Still not dict?
					if (type(variables) is dict) != True: raise ValueError("still no dict after stringdecode")

				else:
					variables=dict()
				#end if variables empty					

			except: # AttributeError (strip) if no string,  ValueError from decode, or raised
				raise ValueError("variables argument can not be converted to / used as dict")
			#end except

		#end if variables not dict already
	return variables
#end def