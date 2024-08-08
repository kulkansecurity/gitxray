# Pending Work

* Use repository stats, eg the punch_card endpoint to identify commits made at a time of day which break patterns
* SSH Public Keys: Improve BLOB parsing and collect Key strength bits which could be used to link to other User keys.
* Try to identify starring attacks (fake stars in repositories or accounts following eachother) by using a non-expensive path (eg few requests)
* Inspect Issues to identify potential malicious behavior by using a non-expensive path (e.g. a call to events per issue would lead to a lot of data, but it requires 1 request per [open] issue)
* Analyze "reactions" and see if we can identify mood in some way. 
