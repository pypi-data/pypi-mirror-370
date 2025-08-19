# inventree-common-data

This simple plugin provides Common Data for InvenTree selection lists.
The goal is to reduce the burden of adopting InvenTree and remove the need to maintain a separate repository and automations for common data by different organisations.

Data is provided for the following sysstems / schemes:
- RAL Colors
- UN/LOCODE / ISO 3166-1

Feel free to request additional data sets in the [plugin discussion](https://talk.invenhost.com/t/plugin-discussion-inventree-common-data/43).

## Setup

1. Install
Install this plugin in the webinterface with the packagename `inventree-common-data`

2. Enable
Enable the plugin in the plugin settings. You need to be signed in as a superuser for this.
**The server will restart if you enable the plugin**

3. Configure
Enable `Auto-Sync` to start the automatic creation and maintenance of selection lists. This is disabled by default as it pushes changes to the database.

## Helpful Links

- [Discussion thread for this plugin](https://talk.invenhost.com/t/plugin-discussion-inventree-common-data/43)
- [InvenTree Documentation on selection lists](https://docs.inventree.org/en/stable/part/parameter/#selection-lists)

## Technical Details

The plugin does not use custom models to provide maximum deployment flexibility and supports all releases starting with InvenTree 0.16.0 through to current master.

Source data is kept in yaml format. It is technically possible to ship data-only plugins, that would still be orchestrated by this plugin. This is however not officially documented right now and only used in-house as there are a few foot-guns with this approach if you do not have proper performance monitoring in place.

Due to this data delivery design, there is no internet connection required after plugin install so private PyPI caches (if you have a company-mandated proxy for example) can be used without problems.
