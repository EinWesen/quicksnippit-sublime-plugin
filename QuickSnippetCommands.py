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

# ******* END SHARED FUNCTIONS *******

class InsertSelectionsplitSnippetCommand(sublime_plugin.TextCommand):	

	def is_str_not_empty(self, s):
		try:
			return s.strip() != ""
		except:
			return True
	#end def

	def run(self, edit, delimiter, contents=None, name=None, variable=None, **args):
		if is_str_empty(contents) and self.is_str_not_empty(name):
			try:
				contents = minidom.parseString(sublime.load_resource(name)).getElementsByTagName('content')[0].firstChild.data		
			except (IOError, ValueError) as e:
				sublime.error_message(repr(e))
				contents=""
			#end try
		#end if empty contents 

		if self.is_str_not_empty(contents) and self.is_str_not_empty(delimiter): # if we finally have content

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
#end class

# Helper class, as the current sublimw version does not support the input method yet
class CallInsertSelectionsplitSnippetCommand(sublime_plugin.TextCommand):

	def run(self, edit, delimiter=None, **args):
		
		def handledelimiter(input_string):
			if is_str_empty(input_string):
				input_string = get_quicksnippets_setting("default_delimiter", "|")
			#end if			

			runargs = None			
			if args != None: # i don't really know why i need to create a copy
				runargs = dict(args)
				runargs["delimiter"] = input_string
			else:
				runargs=dict(delimiter=input_string)
			#end if

			sublime.active_window().active_view().run_command("insert_selectionsplit_snippet", runargs)
		#end def

		if is_str_empty(delimiter):
			if get_quicksnippets_setting("confirm_default_delimiter", True):			
				sublime.active_window().show_input_panel("Delimiter?", get_quicksnippets_setting("default_delimiter", "|"), handledelimiter, None, None)
			else:
				handledelimiter("")
			#end if
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
							elif re.match("(['\"])[^'\"]?\\1:(['\"])[^'\"]*?\\2", variables) != None:
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

	def run(self, callbackCommand, contentType, inputPrompt):
	
		def runCallbackCommand(runargs):
			sublime.active_window().active_view().run_command(callbackCommand, runargs)
		#end def runCallbackCommand
	
		def prepare_input(runargs):
			 
			def handleInput(input_string):
				try:
					finalrunargs=self.castAsDict(input_string)
					finalrunargs.update(runargs)
					runCallbackCommand(finalrunargs)
				except ValueError as e:
					sublime.error_message(repr(e))
			#end def handleInput
		
			if inputPrompt == True:
				sublime.active_window().show_input_panel("Enter additional values as JSON keymap", "", handleInput, None, None)				
			else:
				runCallbackCommand(runargs)
			#end if	
		#end def prepare_input
		
		if contentType=='file':
			
			filterpattern = get_quicksnippets_setting("snippet_resource_pattern", "*.sublime-snippet")			
			filterexp = get_quicksnippets_setting("snippet_filter_expression", None)
			if filterexp != None:
				filterexp = re.compile(filterexp,re.IGNORECASE)
			# end if

			snippet_files = [f for f in sublime.find_resources(filterpattern) if (filterexp == None or filterexp.search(f))]
			snippets = [list(reversed(os.path.split(f))) for f in snippet_files]

			if (len(snippet_files))>0:
				def handleSelect(selected_index):
					if selected_index > -1: # if not canceled
						prepare_input(dict(name=snippet_files[selected_index]))
					#end if
				#end def handleSelect				
				sublime.active_window().show_quick_panel(snippets, handleSelect)			
			else:
				sublime.status_message("No Snippets match the defined filters")
			#end if	
			
		elif contentType=='clipboard':			
			prepare_input(dict(contents=sublime.get_clipboard()))
		else:
			sublime.error_message("Invalid contentType for RunQuicksnippetCommand")
		#end if
	
	#end def run
#end class

