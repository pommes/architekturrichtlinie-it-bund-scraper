# Architekturrichtlinie IT-Bund Scraper
Scrapes the PDF files of [Architekturrichtlinie für die IT des Bundes](https://www.cio.bund.de/Web/DE/Architekturen-und-Standards/Architekturrichtlinie-IT-Bund/architekturrichtlinie_it_bund_node.html) for artifacts to manage them in a database.

## DB Model
![Model](http://www.plantuml.com/plantuml/proxy?src=https://raw.githubusercontent.com/pommes/architekturrichtlinie-it-bund-scraper/main/db-schema-model.puml)
* `AR_RICHTLINIE` is a unique guideline identified by an never changed audit proof id.
* `AR_DETAIL` is the specific guideline valid for a period of time. It contains the rule text itself, the version and the year this version came up. So it contains the history of changes.
* `AR_TAG` is for tagging a guidline so it can be found by searching for specific aspects.
* `AR_NOTIZ` is the note pad for commenting every guideline without losing the comments during change of version.


# Links
1. [MS Word: Convert text to a table or a table to text][1]
2. [75 Of The Coolest Color Combinations For 2020][2]


[1]: <https://support.microsoft.com/en-us/office/convert-text-to-a-table-or-a-table-to-text-b5ce45db-52d5-4fe3-8e9c-e04b62f189e1> "MS Word: Convert text to a table or a table to text"
[2]: <https://www.designwizard.com/blog/design-trends/colour-combination> "75 Of The Coolest Color Combinations For 2020"
