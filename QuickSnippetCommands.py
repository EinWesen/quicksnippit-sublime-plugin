import sublime
import sublime_plugin

def AskForSeperator(on_done):
	def local_on_done(input_string):
		on_done(input_string[0:1])
	sublime.active_window().show_input_panel("Please enter delimiter", "|", local_on_done, None, None)

class QuickSnippetApplySnippettextCommand(sublime_plugin.TextCommand):	
	def run(self, edit, snippetText=None, delimiter=None):
		if (delimiter != None and snippetText != "" and snippetText != None):
			view = self.view
			for sel in view.sel():
				columns = view.substr(sel).split(delimiter)
				myDict = {}
				for col in range (0, len(columns)):
					myDict["PARAM"+str(col)] = columns[col];

				line = sublime.expand_variables(snippetText, myDict)
		 
				view.erase(edit, sel)
				view.insert(edit, sel.begin(), line)

class QuickSnippetApplyOtfsnippetCommand(sublime_plugin.ApplicationCommand):
	def run(self,delimiter=None):
		def on_done(input_string):
			sublime.active_window().active_view().run_command("quick_snippet_apply_snippettext", {"snippetText": sublime.get_clipboard(), "delimiter": input_string})
		
		if (delimiter == None or delimiter == ""):			
			AskForSeperator(on_done)
		else:
			on_done(delimiter)

 
class QuickSnippetChangeClipboardCommand(sublime_plugin.ApplicationCommand):
	def run(self):
		def on_done(input_string):
			sublime.set_clipboard(sublime.get_clipboard().replace('\t', input_string))
		AskForSeperator(on_done)
