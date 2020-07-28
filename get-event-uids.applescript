-- calendar script
-- written by Shane Stanley
-- https://macscripter.net/viewtopic.php?pid=183519#p183519

use AppleScript version "2.4"
use scripting additions
use framework "Foundation"
use framework "EventKit"

-- list of one or more calendar names
set listOfCalNames to {"General", "Caleb Evans"}
-- create start date and end date for occurances
set nowDate to current application's NSDate's |date|()
set todaysDate to current application's NSCalendar's currentCalendar()'s dateBySettingHour:0 minute:0 |second|:0 ofDate:nowDate options:0
set tomorrowsDate to todaysDate's dateByAddingTimeInterval:1 * days

-- create event store and get the OK to access Calendars
set theEKEventStore to current application's EKEventStore's alloc()'s init()
theEKEventStore's requestAccessToEntityType:0 completion:(missing value)

-- check if app has access; this will still occur the first time you OK
-- authorization
set authorizationStatus to current application's EKEventStore's authorizationStatusForEntityType:0 -- work around enum bug
if authorizationStatus is not 3 then
	display dialog "Access must be given in System Preferences" & linefeed & "-> Security & Privacy first." buttons {"OK"} default button 1
	tell application "System Preferences"
		activate
		tell pane id "com.apple.preference.security" to reveal anchor "Privacy"
	end tell
    -- Explicitly abort the script with an error
	error number -128
end if

-- get calendars that can store events
set theCalendars to theEKEventStore's calendarsForEntityType:0
-- filter out the one you want
set theNSPredicate to current application's NSPredicate's predicateWithFormat_("title IN %@", listOfCalNames)
set calsToSearch to theCalendars's filteredArrayUsingPredicate:theNSPredicate
if (count of calsToSearch) < 1 then error "No such calendar(s)."

-- find matching events
set thePred to theEKEventStore's predicateForEventsWithStartDate:todaysDate endDate:tomorrowsDate calendars:calsToSearch
set theEvents to (theEKEventStore's eventsMatchingPredicate:thePred)
-- sort by date
set theEvents to theEvents's sortedArrayUsingSelector:"compareStartDateWithEvent:"
set AppleScript's text item delimiters to {","}
-- useful properties: title, localUID, sharedUID, notes, summary
return ((theEvents's valueForKey:"sharedUID") as list) as string
