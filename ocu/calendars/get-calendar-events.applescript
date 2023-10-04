-- This script file is a combination of a JSON utility library and an
-- EventKit-based AppleScript written by Shane Stanley; the script has been
-- revised to output a JSON array of raw calendar event data

-----------------------------------------------------------------------

-- A JSON library for AppleScript, written by Alex Morega (@mgax)
--- Source: https://github.com/mgax/applescript-json
--
-- The MIT License (MIT)

-- Copyright (c) 2014 Alex Morega

-- Permission is hereby granted, free of charge, to any person obtaining a copy
-- of this software and associated documentation files (the "Software"), to deal
-- in the Software without restriction, including without limitation the rights
-- to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-- copies of the Software, and to permit persons to whom the Software is
-- furnished to do so, subject to the following conditions:

-- The above copyright notice and this permission notice shall be included in all
-- copies or substantial portions of the Software.

-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-- OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
-- SOFTWARE.

on encode(value)
	set type to class of value
	if type = integer or type = boolean
		return value as text
	else if type = text
		return encodeString(value)
	else if type = list
		return encodeList(value)
	else if type = script
		return value's toJson()
	else
		error "Unknown type " & type
	end
end


on encodeList(value_list)
	set out_list to {}
	repeat with value in value_list
		copy encode(value) to end of out_list
	end
	return "[" & join(out_list, ", ") & "]"
end


on encodeString(value)
	set rv to ""
	set codepoints to id of value

	if (class of codepoints) is not list
		set codepoints to {codepoints}
	end

	repeat with codepoint in codepoints
		set codepoint to codepoint as integer
		if codepoint = 34
			set quoted_ch to "\\\""
		else if codepoint = 92 then
			set quoted_ch to "\\\\"
		else if codepoint >= 32 and codepoint < 127
			set quoted_ch to character id codepoint
		else
			set quoted_ch to "\\u" & hex4(codepoint)
		end
		set rv to rv & quoted_ch
	end
	return "\"" & rv & "\""
end


on join(value_list, delimiter)
	set original_delimiter to AppleScript's text item delimiters
	set AppleScript's text item delimiters to delimiter
	set rv to value_list as text
	set AppleScript's text item delimiters to original_delimiter
	return rv
end


on hex4(n)
	set digit_list to "0123456789abcdef"
	set rv to ""
	repeat until length of rv = 4
		set digit to (n mod 16)
		set n to (n - digit) / 16 as integer
		set rv to (character (1+digit) of digit_list) & rv
	end
	return rv
end


on createDictWith(item_pairs)
	set item_list to {}

	script Dict
		on setkv(key, value)
			copy {key, value} to end of item_list
		end

		on toJson()
			set item_strings to {}
			repeat with kv in item_list
				set key_str to encodeString(item 1 of kv)
				set value_str to encode(item 2 of kv)
				copy key_str & ": " & value_str to end of item_strings
			end
			return "{" & join(item_strings, ", ") & "}"
		end
	end

	repeat with pair in item_pairs
		Dict's setkv(item 1 of pair, item 2 of pair)
	end

	return Dict
end


on createDict()
	return createDictWith({})
end

-- calendar script
-- written by Shane Stanley
-- https://macscripter.net/viewtopic.php?pid=183519#p183519

-- Performance note: This script is a few hundred milliseconds faster than the
-- equivalent icalBuddy search, hence why we are using it

use AppleScript version "2.4"
use scripting additions
use framework "Foundation"
use framework "EventKit"

-- convert an event property to a string
on prop2str(theProp)
	return (theProp as list) as text
end prop2str

-- Convert the given number to a string, padding it with a single zero if it is less than 10
on zpad(theNumber)
    if theNumber is less than 10
        return "0" & (theNumber as text)
    else
        return theNumber as text
    end if
end zpad

-- Convert a localized date string into a date string in a standard format
-- which we can safely consume in other scripts
on normalizeDateString(dateString)
    set theDate to (dateString as list) as date
    set AppleScript's text item delimiters to {""}
    return ((theDate's year) & "-" & zpad(theDate's month as number) & "-" & zpad(theDate's day) & "T" & zpad(theDate's hours) & ":" & zpad(theDate's minutes)) as text
end normalizeDateString

on split(value_list_str, delimiter)
    set old_delimiters to AppleScript's text item delimiters
    set AppleScript's text item delimiters to delimiter
    set value_list to every text item of value_list_str
    set AppleScript's text item delimiters to old_delimiters
    return value_list
end split

on run(listOfCalNames)

    -- create start date and end date for occurances
    set nowDate to current application's NSDate's |date|()
    set todaysDate to current application's NSCalendar's currentCalendar()'s dateBySettingHour:0 minute:0 |second|:0 ofDate:nowDate options:0
    set tomorrowsDate to todaysDate's dateByAddingTimeInterval:1 * days

    -- create event store and get the OK to access Calendars
    set theEKEventStore to current application's EKEventStore's alloc()'s init()
	-- trigger request for full access to calendar (this is crucial to ensure
	-- that the workflow has calendar access); as of macOS Sonoma,
	-- requestAccessToEntityType is deprecated (source:
	-- <https://developer.apple.com/documentation/eventkit/ekeventstore/1507547-requestaccesstoentitytype>)
	-- because the calendar permissions have become more granular (e.g. "Full
	-- Access" vs. "Add Only"); the recommended alternative is to use
	-- requestFullAccessToEventsWithCompletion (documentation here:
	-- <https://developer.apple.com/documentation/eventkit/ekeventstore/4162272-requestfullaccesstoeventswithcom>)
    theEKEventStore's requestFullAccessToEventsWithCompletion:(missing value)

    -- get calendars that can store events
    set theCalendars to theEKEventStore's calendarsForEntityType:0
    -- filter down to the calendars you want
    if count of listOfCalNames > 0 then
        set theNSPredicate to current application's NSPredicate's predicateWithFormat_("title IN %@", listOfCalNames)
        set calsToSearch to theCalendars's filteredArrayUsingPredicate:theNSPredicate
        if count of calsToSearch < 1 then return encode({})
    else
        set calsToSearch to theCalendars
    end if

    -- find matching events
    set thePred to theEKEventStore's predicateForEventsWithStartDate:todaysDate endDate:tomorrowsDate calendars:calsToSearch
    set theEvents to (theEKEventStore's eventsMatchingPredicate:thePred)
    -- sort by date
    set theEvents to theEvents's sortedArrayUsingSelector:"compareStartDateWithEvent:"
    set AppleScript's text item delimiters to {","}

    -- construct a JSON array of the calendar events
    set eventObjects to {}
    set eventProps to {"title", "startDate", "endDate", "isAllDay", "location", "notes"}
    repeat with theEvent in theEvents
        -- set eventDataStr to eventDataStr & return & {startDate: prop2str(theEvent's startDate)}
        set eventObject to createDict()
        repeat with theEventProp in eventProps
            if (theEventProp as text) is "startDate" or (theEventProp as text) is "endDate" then
                eventObject's setkv(theEventProp, normalizeDateString(theEvent's valueForKey:theEventProp))
            else
                eventObject's setkv(theEventProp, prop2str(theEvent's valueForKey:theEventProp))
            end if
        end repeat
        copy eventObject to end of eventObjects
    end repeat
    return encode(eventObjects)

end run
