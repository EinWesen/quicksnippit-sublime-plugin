import sublime
import sublime_plugin
import re
import os
from xml.dom import minidom

# ******* DEF SHARED FUNCTIONS *******
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

# ******* END SHARED FUNCTIONS *******

class InsertSelectionsplitSnippetCommand(sublime_plugin.TextCommand):	

	class _DelimiterInputHandler(sublime_plugin.TextInputHandler):
		def __init__(self): pass			
		def name(self): return "delimiter"
		def description(self, text): return text
		def placeholder(self): return self.initial_text()	
		def initial_text(self): return get_quicksnippets_setting("default_delimiter", "|")
		def validate(self, text): return is_str_not_empty(text)
		def preview(self, text):
			if is_str_empty(text): 
				return "Choose the delimiter!"
			else:
				return "Choose the delimiter! Example data for current input: A{0}B{0}C".format(text)
			#end if
		#end def
	#end sub class

	def run(self, edit, delimiter, contents=None, name=None, variable=None, **args):
		if is_str_empty(contents) and is_str_not_empty(name):
			try:
				contents = minidom.parseString(sublime.load_resource(name)).getElementsByTagName('content')[0].firstChild.data		
			except (IOError, ValueError) as e:
				sublime.error_message(repr(e))
				contents=""
			#end try
		#end if empty contents 

		if is_str_not_empty(contents) and is_str_not_empty(delimiter): # if we finally have content

			#apply some defaults
			if is_str_empty(variable): variable=get_quicksnippets_setting("default_variable", "SEL_SPLIT")

			view = self.view
			for sel in view.sel():
				columns = view.substr(sel).split(delimiter)
				myDict = dict(args)

				for col in range (0, len(columns)):
					myDict[variable+str(col)] = columns[col];

				line = sublime.expand_variables(contents, myDict)
			 
				view.erase(edit, sel)
				view.insert(edit, sel.begin(), line)
			#end for each sel			

		#end if	contents not empty 
	#end def

	def input(self, args):
		if is_str_empty(args.get("delimiter")) and get_quicksnippets_setting("confirm_default_delimiter", True):
			return InsertSelectionsplitSnippetCommand._DelimiterInputHandler()
		else:
			return None
		#end if
	#end def

#end class

class RunQuicksnippetCommandCommand(sublime_plugin.ApplicationCommand):
	def castAsDict(self, variables):
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

	class _SnippetInputHandler(sublime_plugin.ListInputHandler):
		def __init__(self, child): self.__child = child
		def name(self): return "name"
		def description(self, key, value): return value
		def placeholder(self): return "Choose a snippet"
		def next_input(self, cmdargs): return self.__child
		
		def list_items(self):
			filterpattern = get_quicksnippets_setting("snippet_resource_pattern", "*.sublime-snippet")			
			filterexp = get_quicksnippets_setting("snippet_filter_expression", None)
			if filterexp != None:
				filterexp = re.compile(filterexp,re.IGNORECASE)
			# end if

			snippets = [(os.path.splitext(os.path.basename(f))[0], f) for f in sublime.find_resources(filterpattern) if (filterexp == None or filterexp.search(f))]
			if len(snippets)==0:
				sublime.status_message("No Snippets match the defined filters")
			return snippets
		#end def

		def preview(self, text):
#			if is_str_empty(text): text=get_quicksnippets_setting("default_delimiter", "|")
			path, file = os.path.split(text)
			return sublime.Html("{}<br>{}<br><i>{}</i>".format(path, file, "----"))
		#end def
	#end sub class
	
	class _ArgsInputHandler(sublime_plugin.TextInputHandler):
		def __init__(self, parentCmd): self.__parentCmd=parentCmd
		def name(self): return "inputArgs"
		def description(self, text): return text		
		def placeholder(self): return "Enter additional values as JSON keymap"
		def validate(self, text): return self.preview(text) != '--ERROR--'
		
		def preview(self, text):
			try:
				return sublime.Html("Result: <i>{}</i>".format(str(self.__parentCmd.castAsDict(text))))
			except:
				return "--ERROR--"
		#end def
	#end sub class

	def run(self, callbackCommand, inputArgs, contents=None, name=None, **args):
		
		if contents == "$CLIPBOARD": 
			contents = sublime.get_clipboard()
		#end if

		runargs = dict()
		runargs.update(args)
		
		if inputArgs != None and inputArgs != False:
			runargs.update(self.castAsDict(inputArgs))

		runargs.update(dict(contents=contents, name=name))
		sublime.active_window().active_view().run_command(callbackCommand, runargs)
	#end def

	def input(self, args):
		handler1 = None
		handler2 = None
		
		if args.get("inputArgs"):
			handler2 = RunQuicksnippetCommandCommand._ArgsInputHandler(self)
		#end if

		if is_str_empty(args.get("contents")) and is_str_empty(args.get("name")):
			handler1 = RunQuicksnippetCommandCommand._SnippetInputHandler(handler2)
		else:
			handler1 = handler2
		#end if
		
		return handler1
	#end def