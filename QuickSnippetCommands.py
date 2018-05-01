import sublime
import sublime_plugin


class QuickOtfSnippetCommand(sublime_plugin.TextCommand):
	mySperator="|"
	myTemplate=""

	def logText(str):
		print("OneTimeSnippet:" + str)


	def defineSeperator(self, edit):		
		def on_done(input_string):
			self.mySperator=input_string.substr(1,1)		
		self.view.window().show_input_panel("Please enter seperator", self.mySperator, on_done, None, None)
 

	def defineTemplate(self, edit):
		self.myTemplate = ""
		for sel in self.view.sel():
			self.myTemplate += self.view.substr(sel)


	def replaceClipboardTabs(self, edit):
		sublime.set_clipboard(sublime.get_clipboard().replace('\t', self.mySperator)) 		


	def applyTemplate(self, edit):
		if (self.myTemplate != ""):
			for sel in self.view.sel():
				columns = self.view.substr(sel).split(self.mySperator)
				line = "" + self.myTemplate

				for col in range (0, len(columns)):
					line=line.replace("$PARAM"+str(col), columns[col])				
	 
				self.view.erase(edit, sel)
				self.view.insert(edit, sel.begin(), line)


	def run(self, edit, subCommand):
		if subCommand == "template":
   			self.defineTemplate(edit)
		elif subCommand == "seperator":
   			self.defineSeperator(edit)
		elif subCommand == "replace":
   			self.replaceClipboardTabs(edit)
		elif subCommand == "apply":
   			self.applyTemplate(edit)   			
		else:
   			self.logText("Unknown subCommand: " + subCommand)
