# QuickSnippit - A SublimeText 3 - Plugin

This is jusst a small plugin for my personal use.

It allowes me to apply some kind of snippet-like template to structured data, effectively giving the opportunity of filling multiple values at predifend places in a text.

Currently the template to be applied is taken from the clipboard. i plan to be able to take from a regular snippet file in the future.
As well as the possibility to use meaningful variable names.

# Whats supported right now?

Create a snippet / template like

    Dear ${PARAM0} ${PARAM1},
    We have registered your birth year as ${PARAM2].
    Sincerely,
    Name


Copy it to the clipboard and create your structured data like

    Sir|Newton|1642
    Madam|Curie|1897

Select each line with one individual cursor and apply the snippet with the command in the command palette.

