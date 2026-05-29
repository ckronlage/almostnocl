
### NiiVue local/offline bundle

The app uses a single local NiiVue bundle file:

`shared/niivue_assets/niivue.webgl2.single.min.js`

This avoids runtime internet dependency.

To refresh that bundle from GitHub (`niivue/mono`) without installing npm/bun on host, run `bash ./scripts/update_niivue_bundle.sh `