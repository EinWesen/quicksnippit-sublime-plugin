import sublime
import sublime_plugin
import re

# ******* DEF SHARED FUNCTIONS *******


# ******* END SHARED FUNCTIONS *******
class InsertSelectionsplitSnippetCommand(sublime_plugin.TextCommand):	
	SETTINGS_FILE = "QuickSnippets.sublime-settings"

	def is_str_empty(self, s):
		try:
			return s == None or s.strip() == ""
		except:
			return False
	#end def

	def is_str_not_empty(self, s):
		try:
			return s.strip() != ""
		except:
			return True
	#end def

	def run(self, edit, contents=None, name=None, delimiter=None, variable=None, **args):
		if self.is_str_empty(contents) and self.is_str_not_empty(name):
			raise ValueError("empty contents / loading from snippet file is not supported yet")
		#end if empty contents 

		if self.is_str_not_empty(contents) and self.is_str_not_empty(delimiter): # if we finally have content

			#apply some defaults
			if self.is_str_empty(delimiter): delimiter=sublime.load_settings(SETTINGS_FILE).get("default_delimiter", "|")
			if self.is_str_empty(variable): variable=sublime.load_settings(SETTINGS_FILE).get("default_variable", "SEL_SPLIT")

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

class RunQuicksnippetCommandCommand(sublime_plugin.TextCommand):

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

	def run(self, edit, callbackCommand, contentType, inputPrompt):
	
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
					sublime.error_message(str(e))
			#end def handleInput
		
			if inputPrompt == "True":
				sublime.active_window().show_input_panel("Enter additional values as JSON keymap", "", handleInput, None, None)				
			else:
				runCallbackCommand(runargs)
			#end if	
		#end def prepare_input
		
		def show_snippet_list():
			snippets=[]
				
			def handleSelect(selected_index):
				if selected_index > -1: # if not canceled
					prepare_input(dict(name=snippets[selected_index]))
				#end if
			#end def handleSelect

			sublime.error_message("Not implemented yet, coming soon!")
			#sublime.active_window().show_quick_panel(snippets, handleSelect)
		#end def show_snippet_list
		
		if contentType=='file':
			show_snippet_list()
		elif contentType=='clipboard':			
			prepare_input(dict(contents=sublime.get_clipboard()))
		else:
			sublime.error_message("Invalid contentType for RunQuicksnippetCommand")
		#end if
	
	#end def run
#end class