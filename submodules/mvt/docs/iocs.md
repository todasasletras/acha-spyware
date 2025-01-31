# Indicators of Compromise (IOCs)

MVT uses [Structured Threat Information Expression (STIX)](https://oasis-open.github.io/cti-documentation/stix/intro.html) files to identify potential traces of compromise.

These indicators of compromise are contained in a file with a particular structure of [JSON](https://en.wikipedia.org/wiki/JSON) with the `.stix2` or `.json` extensions.

You can indicate a path to a STIX2 indicators file when checking iPhone backups or filesystem dumps. For example:

```bash
mvt-ios check-backup --iocs ~/ios/malware.stix2 --output /path/to/iphone/output /path/to/backup
```

Or, with data from an Android backup:

```bash
mvt-android check-backup --iocs ~/iocs/malware.stix2 /path/to/android/backup/
```

After extracting forensics data from a device, you are also able to compare it with any STIX2 file you indicate:

```bash
mvt-ios check-iocs --iocs ~/iocs/malware.stix2 /path/to/iphone/output/
```

The `--iocs` option can be invoked multiple times to let MVT import multiple STIX2 files at once. For example:

```bash
mvt-ios check-backup --iocs ~/iocs/malware1.stix --iocs ~/iocs/malware2.stix2 /path/to/backup
```

It is also possible to load STIX2 files automatically from the environment variable `MVT_STIX2`:

```bash
export MVT_STIX2="/home/user/IOC1.stix2:/home/user/IOC2.stix2"
```

## STIX2 Support

So far MVT implements only a subset of [STIX2 specifications](https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html):

* It only supports checks for one value (such as `[domain-name:value='DOMAIN']`) and not boolean expressions over multiple comparisons
* It only supports the following types: `domain-name:value`, `process:name`, `email-addr:value`, `file:name`, `file:path`, `file:hashes.md5`, `file:hashes.sha1`, `file:hashes.sha256`, `app:id`, `configuration-profile:id`, `android-property:name`, `url:value` (but each type will only be checked by a module if it is relevant to the type of data obtained)

## Known repositories of STIX2 IOCs

- The [Amnesty International investigations repository](https://github.com/AmnestyTech/investigations) contains STIX-formatted IOCs for:
    - [Pegasus](https://en.wikipedia.org/wiki/Pegasus_(spyware)) ([STIX2](https://raw.githubusercontent.com/AmnestyTech/investigations/master/2021-07-18_nso/pegasus.stix2))
    - [Predator from Cytrox](https://citizenlab.ca/2021/12/pegasus-vs-predator-dissidents-doubly-infected-iphone-reveals-cytrox-mercenary-spyware/) ([STIX2](https://raw.githubusercontent.com/AmnestyTech/investigations/master/2021-12-16_cytrox/cytrox.stix2))
    - [An Android Spyware Campaign Linked to a Mercenary Company](https://github.com/AmnestyTech/investigations/tree/master/2023-03-29_android_campaign) ([STIX2](https://github.com/AmnestyTech/investigations/blob/master/2023-03-29_android_campaign/malware.stix2))
- [This repository](https://github.com/Te-k/stalkerware-indicators) contains IOCs for Android stalkerware including [a STIX MVT-compatible file](https://raw.githubusercontent.com/Te-k/stalkerware-indicators/master/generated/stalkerware.stix2).
- We are also maintaining [a list of IOCs](https://github.com/mvt-project/mvt-indicators) in STIX format from public spyware campaigns.

You can automaticallly download the latest public indicator files with the command `mvt-ios download-iocs` or `mvt-android download-iocs`. These commands download the list of indicators from the [mvt-indicators](https://github.com/mvt-project/mvt-indicators/blob/main/indicators.yaml) repository and store them in the [appdir](https://pypi.org/project/appdirs/) folder. They are then loaded automatically by MVT.

Please [open an issue](https://github.com/mvt-project/mvt/issues/) to suggest new sources of STIX-formatted IOCs.



