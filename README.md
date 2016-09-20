# Internet Archive Scripts

A collection of scripts to process the Harley-Spiller collection after being scanned by the Internet Archive


## Requirements

- [Internet archive python API](https://internetarchive.readthedocs.io/en/latest/)
- [Redmine Python API](http://python-redmine.readthedocs.io/)
- [Islandora](http://islandora.ca/)
- Islandora Compound Batch Ingest (Coming soon?)

## Workflow
1. Watch for new files
 - Watch Internet Archive (IA) for new sets of menu scans
 - Watch redmine for new tickets containing ingestion targets, meta data, and table of content files
2. Download IA files
3. Divide scan set into individual folders for each menu based on table of contents and _scandata.xml
4. Generate MODS.xml meta data files for each menu
5. Format files for compound batch ingest
6. Generate structure.xml files for ingest using php tool
7. Drush islandora_compound_batch_preprocess
8. Batch ingest with islandora_batch_ingest
9. Capture ingested item information (Currently unused)
10. Update redmine tickets for QA
11. Clean up working directories

## ia_settings.py
To get git to ignore this file use the following command

```git update-index --assume-unchanged ia_settings.py```
