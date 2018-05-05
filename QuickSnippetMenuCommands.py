import sublime
import sublime_plugin

# ******* END SHARED FUNCTIONS *******

class ToggleSettingGlobalCommand(sublime_plugin.ApplicationCommand):
	def run(self, setting):
		s = sublime.load_settings("Preferences.sublime-settings")
		s.set(setting, not s.get(setting, False))
		sublime.save_settings("Preferences.sublime-settings")
	#end if
    
	def is_checked(self, setting):
		return sublime.load_settings("Preferences.sublime-settings").get(setting, False)
	#end def
#end class