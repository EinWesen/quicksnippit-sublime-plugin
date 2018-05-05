# QuickSnippit - A plugin for SublimeText 3

This is jusst a small plugin mainly for my personal use.

It allowes me to apply some kind of snippet-like template to structured data, effectively giving the opportunity of filling multiple values at predifend places in a text.

# Features
* Insert the current contents of the clipboard as a snippet
* Insert an existing snippet, but show an input to define variables first (need to enter a Json-Structure)
* Apply a snippet to a selection, which will be split by a delimiter, and each split is made avaiable as varaible in the snippet
   * This feature can be used with one of the feature mentioned above 

I choose not to clutter your key bindings and menu by default. So apart from teh settings menu items all feature are made availble through the command palette.


# Usage of structured data

Create a snippet / template like

    Dear $SEL_SPLIT0 $SEL_SPLIT1
    We have registered your birth year as $SEL_SPLIT2.
    Sincerely,
    Name

Copy it to the clipboard and create your structured data like

    Sir|Newton|1642
    Madam|Curie|1897

Select each line with one individual cursor and apply the snippet with the command in the command palette.

# Important hints / How it works
Sublime's own snippet system does not provide a way to specify different snippet values for different cursors.
When applying a snippet to structured data this plugin works around this limition by using the following worflow:

* Get the snippet contents
* Loop through all selections
    * Split the selection by a delimiter and assing it to variables
    * Pass the snippet content to expand_variables with the create dvariables as a dictinary
    * Replace the selection with the result

While this works well (for me ;]), it also has the following caveats:
* The usual variables available in snippets can not be used (although some simple ones like SELECTION could be added)
* As we don't really insert a snippet, all functionality based on it like placeholders is not available
* I don't know how this performs on large datasets

