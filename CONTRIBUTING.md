# Contributing

Keep application metadata in `app.json`; generated headers and package files
must not be committed. Before opening a change, run:

```sh
./scripts/build.sh native debug
./scripts/check.sh native
```

For packaging changes, also run the target check with an installed SDK:

```sh
./scripts/build.sh kindlehf release
./scripts/check.sh kindlehf
```

Changes that affect the Kindle UI or lifecycle should be tested on a device.
Include its KPM platform and firmware family in the change description.
