# Hovåsskolan – automatically updated school lunch calendar

This project fetches the Hovåsskolan school lunch menu from Skolmaten.se and publishes an Outlook-compatible ICS calendar.

## Set up GitHub Pages (one time)

In **Settings → Pages → Build and deployment**, select **Deploy from a branch**, branch **main**, folder **/docs**, then **Save**.

## Run and test

Open **Actions → Update school lunch calendar → Run workflow**. Check the run logs. If Skolmaten blocks the RSS endpoint or returns no menu, the job fails rather than publishing invented meals. The generator preserves the previous ICS on a fetch failure.

After a successful run, subscribe to:

https://ohel75.github.io/hovasskolan-lunch/skolmat.ics

In Hotmail/Outlook.com: Calendar → Add calendar → Subscribe from web → paste URL.

**Note:** Outlook.com controls subscription refresh timing. This is a separate subscribed calendar displayed alongside your Family calendar, not a write-back to the Family calendar. Skolmaten's unofficial RSS endpoint may change or become unavailable.

Source: https://skolmaten.se/hovasskolan
