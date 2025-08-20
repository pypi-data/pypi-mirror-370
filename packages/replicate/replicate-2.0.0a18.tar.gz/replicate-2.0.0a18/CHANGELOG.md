# Changelog

## 2.0.0-alpha.18 (2025-08-19)

Full Changelog: [v2.0.0-alpha.17...v2.0.0-alpha.18](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.17...v2.0.0-alpha.18)

### Features

* **pipelines:** get API token from cog's current_scope, if available ([#48](https://github.com/replicate/replicate-python-stainless/issues/48)) ([7f60d30](https://github.com/replicate/replicate-python-stainless/commit/7f60d30644bce710fbcb35c247d87452b79ba058))

## 2.0.0-alpha.17 (2025-08-12)

Full Changelog: [v2.0.0-alpha.16...v2.0.0-alpha.17](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.16...v2.0.0-alpha.17)

### Chores

* **internal:** codegen related update ([ea920d5](https://github.com/replicate/replicate-python-stainless/commit/ea920d54977d46705b6dcf449e2fcbe7a9af76c8))
* **internal:** update comment in script ([8e30c35](https://github.com/replicate/replicate-python-stainless/commit/8e30c35f1a5935b9a69046f1e971a3808c4e28b8))

## 2.0.0-alpha.16 (2025-08-09)

Full Changelog: [v2.0.0-alpha.15...v2.0.0-alpha.16](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.15...v2.0.0-alpha.16)

### Chores

* update @stainless-api/prism-cli to v5.15.0 ([6fb0043](https://github.com/replicate/replicate-python-stainless/commit/6fb00432b7b91e8f8e0887e066b3cc5a55a4934b))

## 2.0.0-alpha.15 (2025-08-06)

Full Changelog: [v2.0.0-alpha.14...v2.0.0-alpha.15](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.14...v2.0.0-alpha.15)

### Chores

* **internal:** fix ruff target version ([16c78dc](https://github.com/replicate/replicate-python-stainless/commit/16c78dc5837a91f73f28d8a4d153056587df7090))
* update OpenAPI spec and rebuild SDKs ([fdca0c4](https://github.com/replicate/replicate-python-stainless/commit/fdca0c40e9a8009afe764ec39056d50fb43639f8))

## 2.0.0-alpha.14 (2025-07-31)

Full Changelog: [v2.0.0-alpha.13...v2.0.0-alpha.14](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.13...v2.0.0-alpha.14)

### Features

* add replicate.use() ([a7b12dd](https://github.com/replicate/replicate-python-stainless/commit/a7b12dd4bcd3a6292b6b06a59047994e408dad59))
* **client:** support file upload requests ([756cad1](https://github.com/replicate/replicate-python-stainless/commit/756cad11209fa5d3661cb6fb5636660255ca7fbe))


### Chores

* **docs:** document replicate.run() ([681772d](https://github.com/replicate/replicate-python-stainless/commit/681772de2e0dca70018db9cefafe37277ad0c014))
* **docs:** document replicate.use() ([b47c9bd](https://github.com/replicate/replicate-python-stainless/commit/b47c9bd42e1d390ca4a652247b1b65a936529017))
* make the linter happy ([70c1af2](https://github.com/replicate/replicate-python-stainless/commit/70c1af25352ce7033fb834620a48b8aff275ad65))
* make the mypy happy ([24ddc92](https://github.com/replicate/replicate-python-stainless/commit/24ddc922c5ab2e446fc090f5b5f60b1689712a77))

## 2.0.0-alpha.13 (2025-07-25)

Full Changelog: [v2.0.0-alpha.12...v2.0.0-alpha.13](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.12...v2.0.0-alpha.13)

### Chores

* **project:** add settings file for vscode ([739fe12](https://github.com/replicate/replicate-python-stainless/commit/739fe12a2486b1926efe171d086de63e1ee17029))

## 2.0.0-alpha.12 (2025-07-23)

Full Changelog: [v2.0.0-alpha.11...v2.0.0-alpha.12](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.11...v2.0.0-alpha.12)

### Features

* clean up environment call outs ([3f64d12](https://github.com/replicate/replicate-python-stainless/commit/3f64d12c61eb36be75b9b5044f0cc2e3b6d52658))


### Bug Fixes

* **parsing:** ignore empty metadata ([d54a686](https://github.com/replicate/replicate-python-stainless/commit/d54a68644ded46361180488d36ede3d2c1ee4723))
* **parsing:** parse extra field types ([4fed49d](https://github.com/replicate/replicate-python-stainless/commit/4fed49d8cc6e6a68c59505141574470fb33221f1))

## 2.0.0-alpha.11 (2025-07-12)

Full Changelog: [v2.0.0-alpha.10...v2.0.0-alpha.11](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.10...v2.0.0-alpha.11)

### Bug Fixes

* **client:** don't send Content-Type header on GET requests ([32d3401](https://github.com/replicate/replicate-python-stainless/commit/32d3401e0180ab91d7e8aba5959d15dae8640814))
* **parsing:** correctly handle nested discriminated unions ([2aaaab1](https://github.com/replicate/replicate-python-stainless/commit/2aaaab1999f44d7ee8581cc7466e3be04360f4c7))


### Chores

* **internal:** bump pinned h11 dep ([c3101fc](https://github.com/replicate/replicate-python-stainless/commit/c3101fc57487b08ea55344b8eff1308bb92290cf))
* **package:** mark python 3.13 as supported ([1263862](https://github.com/replicate/replicate-python-stainless/commit/1263862868ee1a2750eb8b66d6b2f76c0b6f753d))
* **readme:** fix version rendering on pypi ([626518b](https://github.com/replicate/replicate-python-stainless/commit/626518b846fd2dcb02ca21e1054a8fd4f0849130))

## 2.0.0-alpha.10 (2025-07-08)

Full Changelog: [v2.0.0-alpha.9...v2.0.0-alpha.10](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.9...v2.0.0-alpha.10)

### Chores

* **internal:** codegen related update ([b31fdbb](https://github.com/replicate/replicate-python-stainless/commit/b31fdbb3ffa3c483c796be98a4206d794dea864b))

## 2.0.0-alpha.9 (2025-07-02)

Full Changelog: [v2.0.0-alpha.8...v2.0.0-alpha.9](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.8...v2.0.0-alpha.9)

### Chores

* **ci:** change upload type ([a588db6](https://github.com/replicate/replicate-python-stainless/commit/a588db620505f606f72a325717c8b32d3cfc58fc))

## 2.0.0-alpha.8 (2025-06-30)

Full Changelog: [v2.0.0-alpha.7...v2.0.0-alpha.8](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.7...v2.0.0-alpha.8)

### Bug Fixes

* **ci:** correct conditional ([b21a288](https://github.com/replicate/replicate-python-stainless/commit/b21a288650ed46c6c2a72f5d4ff73ff66f81d371))


### Chores

* **ci:** only run for pushes and fork pull requests ([33e1f74](https://github.com/replicate/replicate-python-stainless/commit/33e1f74f9c15cbd9102f95045f37061ef9d15504))

## 2.0.0-alpha.7 (2025-06-27)

Full Changelog: [v2.0.0-alpha.6...v2.0.0-alpha.7](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.6...v2.0.0-alpha.7)

### Features

* **api:** api update ([b1c14c8](https://github.com/replicate/replicate-python-stainless/commit/b1c14c8291ca205930dafbf639ba5e7bf9939d3a))

## 2.0.0-alpha.6 (2025-06-26)

Full Changelog: [v2.0.0-alpha.5...v2.0.0-alpha.6](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.5...v2.0.0-alpha.6)

### Bug Fixes

* **ci:** release-doctor — report correct token name ([de5bf18](https://github.com/replicate/replicate-python-stainless/commit/de5bf1856b2aa7167d50b9a4b8e1057430981ba8))

## 2.0.0-alpha.5 (2025-06-25)

Full Changelog: [v2.0.0-alpha.4...v2.0.0-alpha.5](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.4...v2.0.0-alpha.5)

### Features

* **api:** api update ([6e667da](https://github.com/replicate/replicate-python-stainless/commit/6e667da6c2e80add847e612bbd08db1c865793d7))
* **api:** api update ([0a187a9](https://github.com/replicate/replicate-python-stainless/commit/0a187a9ba906c0bc5c4e658883266276fc357665))
* **api:** api update ([edb14b6](https://github.com/replicate/replicate-python-stainless/commit/edb14b65c61203c2e42a1accd384e7b456e33448))
* **client:** add support for aiohttp ([c802a30](https://github.com/replicate/replicate-python-stainless/commit/c802a30a0569cb25eb700ff5501c5a87291ef4b0))


### Chores

* **tests:** skip some failing tests on the latest python versions ([d331b72](https://github.com/replicate/replicate-python-stainless/commit/d331b72364eaed6f935f9b23fdc776303ebf57a6))


### Documentation

* **client:** fix httpx.Timeout documentation reference ([d17c345](https://github.com/replicate/replicate-python-stainless/commit/d17c3454afaa0ae0b022f468515e8478e5ba6568))

## 2.0.0-alpha.4 (2025-06-18)

Full Changelog: [v2.0.0-alpha.3...v2.0.0-alpha.4](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.3...v2.0.0-alpha.4)

### Features

* **api:** api update ([a9be2e0](https://github.com/replicate/replicate-python-stainless/commit/a9be2e087bd6f01301608322a50b321b0b01d4da))


### Bug Fixes

* **tests:** fix: tests which call HTTP endpoints directly with the example parameters ([3dfe4f7](https://github.com/replicate/replicate-python-stainless/commit/3dfe4f711c061b6197017a5b999f9db4e7f2836d))


### Chores

* **ci:** enable for pull requests ([67ffb34](https://github.com/replicate/replicate-python-stainless/commit/67ffb34adaaef43b4e4e469e5fff7ce3cdca3dcf))
* **internal:** update conftest.py ([90da407](https://github.com/replicate/replicate-python-stainless/commit/90da407a4818b21bd5a33347a3c4566189c4377d))
* **readme:** update badges ([4f54c7a](https://github.com/replicate/replicate-python-stainless/commit/4f54c7a76e5107b854e82f5266578e4f84aacc74))

## 2.0.0-alpha.3 (2025-06-17)

Full Changelog: [v2.0.0-alpha.2...v2.0.0-alpha.3](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.2...v2.0.0-alpha.3)

### Chores

* **tests:** add tests for httpx client instantiation & proxies ([b8dfd7a](https://github.com/replicate/replicate-python-stainless/commit/b8dfd7a455abb39f114bf86b89aacf2d9cb88eb3))

## 2.0.0-alpha.2 (2025-06-13)

Full Changelog: [v2.0.0-alpha.1...v2.0.0-alpha.2](https://github.com/replicate/replicate-python-stainless/compare/v2.0.0-alpha.1...v2.0.0-alpha.2)

### Bug Fixes

* **client:** correctly parse binary response | stream ([ec19335](https://github.com/replicate/replicate-python-stainless/commit/ec19335fcce5a7ceba6aa1a4ac67411421a571ec))
* **test:** update prediction response ([b6608ca](https://github.com/replicate/replicate-python-stainless/commit/b6608ca5bbfc38d68a9bbfb853bbb8645e046d39))


### Chores

* **internal:** version bump ([497fe10](https://github.com/replicate/replicate-python-stainless/commit/497fe1047ade040d99bf5d7d4fb99f1b1b95a09d))
* **tests:** run tests in parallel ([9330c56](https://github.com/replicate/replicate-python-stainless/commit/9330c565de11b0c61e43df899f4113c5214572c9))

## 2.0.0-alpha.1 (2025-06-10)

Full Changelog: [v0.6.0...v2.0.0-alpha.1](https://github.com/replicate/replicate-python-stainless/compare/v0.6.0...v2.0.0-alpha.1)

### ⚠ BREAKING CHANGES

* rename package to `replicate`

### Features

* **client:** add follow_redirects request option ([d606061](https://github.com/replicate/replicate-python-stainless/commit/d60606146abbdc778dc33573ccccdf7bedb524e4))


### Chores

* **docs:** remove reference to rye shell ([1dfaea4](https://github.com/replicate/replicate-python-stainless/commit/1dfaea4108bee6ea565c48c9f99ed503476fd58f))
* rename package to `replicate` ([42e30b7](https://github.com/replicate/replicate-python-stainless/commit/42e30b7b0e736fbb39e95ef7744299746a70d1b5))


### Documentation

* **internal:** add support for the client config option default_client_example_name to Python ([b320609](https://github.com/replicate/replicate-python-stainless/commit/b3206093c824676a300bfc68da307fab5a0f3718))

## 0.6.0 (2025-05-22)

Full Changelog: [v0.5.1...v0.6.0](https://github.com/replicate/replicate-python-stainless/compare/v0.5.1...v0.6.0)

### Features

* **api:** api update ([eb2a462](https://github.com/replicate/replicate-python-stainless/commit/eb2a462c8bd7dd8a0e303020e8c09a302ef670a0))


### Chores

* **docs:** grammar improvements ([ba42564](https://github.com/replicate/replicate-python-stainless/commit/ba4256495f92133738016c03b198a1bb88b6ed21))

## 0.5.1 (2025-05-16)

Full Changelog: [v0.5.0...v0.5.1](https://github.com/replicate/replicate-python-stainless/compare/v0.5.0...v0.5.1)

### Chores

* **ci:** fix installation instructions ([eb4702f](https://github.com/replicate/replicate-python-stainless/commit/eb4702fdc5d6ac6eb112f69eb11095393f0de992))
* **ci:** upload sdks to package manager ([59e0758](https://github.com/replicate/replicate-python-stainless/commit/59e075852ee7f4b914b23107018ebfb800fe4b91))

## 0.5.0 (2025-05-14)

Full Changelog: [v0.4.0...v0.5.0](https://github.com/replicate/replicate-python-stainless/compare/v0.4.0...v0.5.0)

### Features

* **api:** api update ([dbbd264](https://github.com/replicate/replicate-python-stainless/commit/dbbd264826d1d1e566c7489fb4dfbca2bb3a138f))

## 0.4.0 (2025-05-13)

Full Changelog: [v0.3.2...v0.4.0](https://github.com/replicate/replicate-python-stainless/compare/v0.3.2...v0.4.0)

### Features

* **api:** api update ([d36589e](https://github.com/replicate/replicate-python-stainless/commit/d36589ef3ec1718ff01948f56bfeb3dd5854d6de))

## 0.3.2 (2025-05-13)

Full Changelog: [v0.3.1...v0.3.2](https://github.com/replicate/replicate-python-stainless/compare/v0.3.1...v0.3.2)

### Bug Fixes

* **package:** support direct resource imports ([97b771a](https://github.com/replicate/replicate-python-stainless/commit/97b771a8f2f318e5907656c04ddb6b711af1d44a))

## 0.3.1 (2025-05-09)

Full Changelog: [v0.3.0...v0.3.1](https://github.com/replicate/replicate-python-stainless/compare/v0.3.0...v0.3.1)

### Chores

* **internal:** avoid errors for isinstance checks on proxies ([b31e651](https://github.com/replicate/replicate-python-stainless/commit/b31e651903235d70ea0f3b03aac56de9320996bf))

## 0.3.0 (2025-05-08)

Full Changelog: [v0.2.1...v0.3.0](https://github.com/replicate/replicate-python-stainless/compare/v0.2.1...v0.3.0)

### Features

* **api:** api update ([0e4a103](https://github.com/replicate/replicate-python-stainless/commit/0e4a10391bebf0cae929c8d11ccd7415d1785500))

## 0.2.1 (2025-05-07)

Full Changelog: [v0.2.0...v0.2.1](https://github.com/replicate/replicate-python-stainless/compare/v0.2.0...v0.2.1)

### Documentation

* update example requests ([eb0ba44](https://github.com/replicate/replicate-python-stainless/commit/eb0ba44af5b5006e758c9d9e65312f88b52dc3f5))

## 0.2.0 (2025-05-07)

Full Changelog: [v0.1.0...v0.2.0](https://github.com/replicate/replicate-python-stainless/compare/v0.1.0...v0.2.0)

### Features

* **api:** add Files API methods ([3173e5f](https://github.com/replicate/replicate-python-stainless/commit/3173e5f61edd89ffe0b64b53fc8e8e9905e145e4))
* **api:** fix bearer token which also regressed when guessing with AI ([13162be](https://github.com/replicate/replicate-python-stainless/commit/13162be9d367de29d222b86506fa921a10800665))


### Bug Fixes

* **api:** fix client_settings.opts.api_key.read_env ([5a9b95c](https://github.com/replicate/replicate-python-stainless/commit/5a9b95ce89e536b539eefe0864a47784fdb0ec08))

## 0.1.0 (2025-05-07)

Full Changelog: [v0.1.0-alpha.10...v0.1.0](https://github.com/replicate/replicate-python-stainless/compare/v0.1.0-alpha.10...v0.1.0)

### Features

* **api:** api update ([e889b3d](https://github.com/replicate/replicate-python-stainless/commit/e889b3d0950cac908d53f0afef0660e50d822455))

## 0.1.0-alpha.10 (2025-05-06)

Full Changelog: [v0.1.0-alpha.9...v0.1.0-alpha.10](https://github.com/replicate/replicate-python-stainless/compare/v0.1.0-alpha.9...v0.1.0-alpha.10)

### Bug Fixes

* disable settings.positional_params ([f018f4b](https://github.com/replicate/replicate-python-stainless/commit/f018f4b81e50ae538d9430aa1cdde7f64100031a))

## 0.1.0-alpha.9 (2025-05-06)

Full Changelog: [v0.1.0-alpha.8...v0.1.0-alpha.9](https://github.com/replicate/replicate-python-stainless/compare/v0.1.0-alpha.8...v0.1.0-alpha.9)

### Bug Fixes

* change organization.name to replicate ([04b0797](https://github.com/replicate/replicate-python-stainless/commit/04b079729cd431cad9e992c5c0a0d82ad838f5ef))


### Chores

* use lazy imports for module level client ([14f6cfc](https://github.com/replicate/replicate-python-stainless/commit/14f6cfcad3045d1bde023d1896b369057d3f6b77))
* use lazy imports for resources ([b2a0246](https://github.com/replicate/replicate-python-stainless/commit/b2a024612fc8b5a1bc7a15038cd33ab29e728b58))

## 0.1.0-alpha.8 (2025-04-30)

Full Changelog: [v0.1.0-alpha.7...v0.1.0-alpha.8](https://github.com/replicate/replicate-python-stainless/compare/v0.1.0-alpha.7...v0.1.0-alpha.8)

### Features

* **api:** api update ([a5aa64a](https://github.com/replicate/replicate-python-stainless/commit/a5aa64a71517fdf74e61e4debe68fba458f2e380))
* **client:** add support for model queries ([6df1fd6](https://github.com/replicate/replicate-python-stainless/commit/6df1fd6b994373a49b602258a8064998c88a0eca))

## 0.1.0-alpha.7 (2025-04-24)

Full Changelog: [v0.1.0-alpha.6...v0.1.0-alpha.7](https://github.com/replicate/replicate-python-stainless/compare/v0.1.0-alpha.6...v0.1.0-alpha.7)

### Features

* enable mcp package publishing ([f116fbb](https://github.com/replicate/replicate-python-stainless/commit/f116fbbb59329b66a998e43c850bcfab05e7398b))

## 0.1.0-alpha.6 (2025-04-24)

Full Changelog: [v0.1.0-alpha.5...v0.1.0-alpha.6](https://github.com/replicate/replicate-python-stainless/compare/v0.1.0-alpha.5...v0.1.0-alpha.6)

### Bug Fixes

* correct mapping for account.get ([e501778](https://github.com/replicate/replicate-python-stainless/commit/e501778a22c481147fbe419803a3f52ac9ba8243))


### Chores

* broadly detect json family of content-type headers ([eeaa507](https://github.com/replicate/replicate-python-stainless/commit/eeaa5071ed47e31264a268d9445fe8c0b8d059b1))
* **ci:** only use depot for staging repos ([f7ec0b8](https://github.com/replicate/replicate-python-stainless/commit/f7ec0b8e11782aa89eee5f4af962158b665eee13))
* **internal:** codegen related update ([fd43800](https://github.com/replicate/replicate-python-stainless/commit/fd43800c1da9a5c6ff06309a6c4a6a3808decff9))

## 0.1.0-alpha.5 (2025-04-24)

Full Changelog: [v0.1.0-alpha.4...v0.1.0-alpha.5](https://github.com/replicate/replicate-python-stainless/compare/v0.1.0-alpha.4...v0.1.0-alpha.5)

### Features

* add missing resources ([8bbddc7](https://github.com/replicate/replicate-python-stainless/commit/8bbddc7a788f4488311b8ed408d4b020db8e006b))
* enable `openapi.code_samples` ([85810f5](https://github.com/replicate/replicate-python-stainless/commit/85810f5f4c0caf680a90fca80f1bfcd639e76894))

## 0.1.0-alpha.4 (2025-04-23)

Full Changelog: [v0.1.0-alpha.3...v0.1.0-alpha.4](https://github.com/replicate/replicate-python-stainless/compare/v0.1.0-alpha.3...v0.1.0-alpha.4)

### Features

* **api:** add `models.readme.get` and `models.examples.list` operations ([bcac9e5](https://github.com/replicate/replicate-python-stainless/commit/bcac9e51671f466b76f5eed7f4336189c6967326))

## 0.1.0-alpha.3 (2025-04-23)

Full Changelog: [v0.1.0-alpha.2...v0.1.0-alpha.3](https://github.com/replicate/replicate-python-stainless/compare/v0.1.0-alpha.2...v0.1.0-alpha.3)

### ⚠ BREAKING CHANGES

* **api:** use correct env var for bearer token

### Features

* **api:** api update ([7ebd598](https://github.com/replicate/replicate-python-stainless/commit/7ebd59873181c74dbaa035ac599abcbbefb3ee62))


### Bug Fixes

* **api:** use correct env var for bearer token ([00eab77](https://github.com/replicate/replicate-python-stainless/commit/00eab7702f8f2699ce9b3070f23202278ac21855))
* **pydantic v1:** more robust ModelField.annotation check ([c907599](https://github.com/replicate/replicate-python-stainless/commit/c907599a6736e781f3f80062eb4d03ed92f03403))


### Chores

* **ci:** add timeout thresholds for CI jobs ([1bad4d3](https://github.com/replicate/replicate-python-stainless/commit/1bad4d3d3676a323032f37f0195ff640fcce3458))
* **internal:** base client updates ([c1d6ed5](https://github.com/replicate/replicate-python-stainless/commit/c1d6ed59ed0f06012922ec6d0bae376852523d81))
* **internal:** bump pyright version ([f1e4d14](https://github.com/replicate/replicate-python-stainless/commit/f1e4d140104ff317b94cb2dd88ec850a9b8bce54))
* **internal:** fix list file params ([2918eba](https://github.com/replicate/replicate-python-stainless/commit/2918ebad39df868485fed02a2d0020bef72d24b9))
* **internal:** import reformatting ([4cdf515](https://github.com/replicate/replicate-python-stainless/commit/4cdf515372a9e936c3a18afd24a444a778b1f7f5))
* **internal:** refactor retries to not use recursion ([75005e1](https://github.com/replicate/replicate-python-stainless/commit/75005e11045385d0596911bbbbb062207450bd14))
* **internal:** update models test ([fc34c6d](https://github.com/replicate/replicate-python-stainless/commit/fc34c6d4fc36a41441ab8417f85343e640b53b76))

## 0.1.0-alpha.2 (2025-04-16)

Full Changelog: [v0.1.0-alpha.1...v0.1.0-alpha.2](https://github.com/replicate/replicate-python-stainless/compare/v0.1.0-alpha.1...v0.1.0-alpha.2)

### Features

* **api:** api update ([79f022a](https://github.com/replicate/replicate-python-stainless/commit/79f022aa879e6c0688197557795e04ffecd93f52))


### Chores

* update SDK settings ([ee5fd8b](https://github.com/replicate/replicate-python-stainless/commit/ee5fd8b119cb4a53467e71a5c52dac4fc1779385))

## 0.1.0-alpha.1 (2025-04-15)

Full Changelog: [v0.0.1-alpha.0...v0.1.0-alpha.1](https://github.com/replicate/replicate-python-stainless/compare/v0.0.1-alpha.0...v0.1.0-alpha.1)

### Features

* **api:** api update ([#19](https://github.com/replicate/replicate-python-stainless/issues/19)) ([fdd9b17](https://github.com/replicate/replicate-python-stainless/commit/fdd9b17918f3b563b6810ee463c500ba17284f53))
* **api:** manual updates ([#20](https://github.com/replicate/replicate-python-stainless/issues/20)) ([33e82c8](https://github.com/replicate/replicate-python-stainless/commit/33e82c8fec082a0af05b82ed5110424b69fb4400))
* **api:** manual updates ([#21](https://github.com/replicate/replicate-python-stainless/issues/21)) ([d50ae4c](https://github.com/replicate/replicate-python-stainless/commit/d50ae4cf5088a214f4751672ad4f1493dbf54768))
* **api:** manual updates ([#22](https://github.com/replicate/replicate-python-stainless/issues/22)) ([573bbb3](https://github.com/replicate/replicate-python-stainless/commit/573bbb3fa46346d1703d076daa85541b947c27a2))
* **api:** manual updates ([#23](https://github.com/replicate/replicate-python-stainless/issues/23)) ([7962ea7](https://github.com/replicate/replicate-python-stainless/commit/7962ea7f5c5e3c8f253f66b8f13eadc9927fae7d))
* **api:** manual updates ([#24](https://github.com/replicate/replicate-python-stainless/issues/24)) ([d31ada3](https://github.com/replicate/replicate-python-stainless/commit/d31ada3ab8d19413c1ca55535f1788ae9b5d443d))
* **api:** re-enable module client ([4f83487](https://github.com/replicate/replicate-python-stainless/commit/4f8348757c683395344c8dea1adb75af941f67e1))
* **api:** update pagination configs ([#25](https://github.com/replicate/replicate-python-stainless/issues/25)) ([8a2cc9f](https://github.com/replicate/replicate-python-stainless/commit/8a2cc9f87cf6edb18ad906bbb0b82372b4b82099))
* **api:** update via SDK Studio ([3bf3415](https://github.com/replicate/replicate-python-stainless/commit/3bf3415ce21bb9fc55f80809239e58d64f34fb61))
* **api:** update via SDK Studio ([aafbabf](https://github.com/replicate/replicate-python-stainless/commit/aafbabfdbac1c43a547f277769c82585c616a3b4))
* **api:** update via SDK Studio ([fdf1072](https://github.com/replicate/replicate-python-stainless/commit/fdf107297bfff5086c330c32db73eb7bc4df249c))
* **api:** update via SDK Studio ([cab4d0e](https://github.com/replicate/replicate-python-stainless/commit/cab4d0e83a9fa40304fa0618d7db30445b625b16))
* **api:** update via SDK Studio ([#16](https://github.com/replicate/replicate-python-stainless/issues/16)) ([ffa306e](https://github.com/replicate/replicate-python-stainless/commit/ffa306e9121fc71133648c46b84272aec3114724))
* **api:** update via SDK Studio ([#17](https://github.com/replicate/replicate-python-stainless/issues/17)) ([958ed88](https://github.com/replicate/replicate-python-stainless/commit/958ed888458134a1235ddecd6e0e7741df6e8b54))
* **api:** update via SDK Studio ([#4](https://github.com/replicate/replicate-python-stainless/issues/4)) ([dd5a024](https://github.com/replicate/replicate-python-stainless/commit/dd5a024b8b112ccac91075890e89ba5fa61aa725))
* **api:** update via SDK Studio ([#5](https://github.com/replicate/replicate-python-stainless/issues/5)) ([5ead241](https://github.com/replicate/replicate-python-stainless/commit/5ead241e786dd7b6266076b039ad2f298848db2e))


### Bug Fixes

* **ci:** ensure pip is always available ([#14](https://github.com/replicate/replicate-python-stainless/issues/14)) ([d4f8f18](https://github.com/replicate/replicate-python-stainless/commit/d4f8f18d0d369dedc9e09551e87483f8f1787fd7))
* **ci:** remove publishing patch ([#15](https://github.com/replicate/replicate-python-stainless/issues/15)) ([002b758](https://github.com/replicate/replicate-python-stainless/commit/002b7581debae5b5bc97ec24cc0cea129100dfde))
* **perf:** optimize some hot paths ([d14ecac](https://github.com/replicate/replicate-python-stainless/commit/d14ecaca89424e6aac85827ae0efd5e6da7d8c03))
* **perf:** skip traversing types for NotGiven values ([35ce48c](https://github.com/replicate/replicate-python-stainless/commit/35ce48c5e3e93605a70f90270487e02e121561b5))
* pluralize `list` response variables ([#26](https://github.com/replicate/replicate-python-stainless/issues/26)) ([19f7bd9](https://github.com/replicate/replicate-python-stainless/commit/19f7bd9fe7d8422ae7abe6d5070e29f4a572a1d7))
* **types:** handle more discriminated union shapes ([#13](https://github.com/replicate/replicate-python-stainless/issues/13)) ([4ca1ca8](https://github.com/replicate/replicate-python-stainless/commit/4ca1ca8606fef7bc40144c1ae6246784ed754687))


### Chores

* **client:** minor internal fixes ([21d9c7b](https://github.com/replicate/replicate-python-stainless/commit/21d9c7be7c1c5cb93466b6f6d16804a7d38701b2))
* fix typos ([#18](https://github.com/replicate/replicate-python-stainless/issues/18)) ([54d4e6d](https://github.com/replicate/replicate-python-stainless/commit/54d4e6da6a757ad6e5c899b79018ca39eed2a124))
* go live ([#1](https://github.com/replicate/replicate-python-stainless/issues/1)) ([bd9a84a](https://github.com/replicate/replicate-python-stainless/commit/bd9a84ae91a2c72fa49182f9ff8ea0b78e7cc343))
* **internal:** bump rye to 0.44.0 ([#12](https://github.com/replicate/replicate-python-stainless/issues/12)) ([c9d2593](https://github.com/replicate/replicate-python-stainless/commit/c9d2593f4e9d324c12e2ca323563a317d0ea1751))
* **internal:** codegen related update ([#11](https://github.com/replicate/replicate-python-stainless/issues/11)) ([41c787d](https://github.com/replicate/replicate-python-stainless/commit/41c787d2c196d59c48ec3056d93dd48bf530de72))
* **internal:** expand CI branch coverage ([183a5dc](https://github.com/replicate/replicate-python-stainless/commit/183a5dc798f30ff70e7e96ecb3b5c8ade704af6a))
* **internal:** fix module client tests ([fc9ac15](https://github.com/replicate/replicate-python-stainless/commit/fc9ac15ad5580b72719da024d95e067316f04ef2))
* **internal:** reduce CI branch coverage ([2c61820](https://github.com/replicate/replicate-python-stainless/commit/2c6182009bbee43f3995be0844983c18e4b147fb))
* **internal:** remove extra empty newlines ([#10](https://github.com/replicate/replicate-python-stainless/issues/10)) ([1c63514](https://github.com/replicate/replicate-python-stainless/commit/1c635145a8a70f3cb0ea432387f72eafa64ca5f6))
* **internal:** remove trailing character ([#27](https://github.com/replicate/replicate-python-stainless/issues/27)) ([0a6e3f2](https://github.com/replicate/replicate-python-stainless/commit/0a6e3f29ddeecd0267c57536cf0fa07218c18d03))
* **internal:** slight transform perf improvement ([#28](https://github.com/replicate/replicate-python-stainless/issues/28)) ([da30360](https://github.com/replicate/replicate-python-stainless/commit/da303609abb6a7d069b4e35036f68bae7b009cb2))
* **internal:** update pyright settings ([65494e5](https://github.com/replicate/replicate-python-stainless/commit/65494e5b623b3d2cf248b6da88c7f3e50160dc94))
* **internal:** updates ([b7424d7](https://github.com/replicate/replicate-python-stainless/commit/b7424d7cc1c9fa440b58fa9e51331f3c77fbd83d))
* remove custom code ([31aa7ed](https://github.com/replicate/replicate-python-stainless/commit/31aa7edc04d5c9f408c06e4051c0ba343b9761ac))
* sync repo ([9a71c71](https://github.com/replicate/replicate-python-stainless/commit/9a71c71fd94f1e216398c616dc6c24e0eff10c89))
* update SDK settings ([#3](https://github.com/replicate/replicate-python-stainless/issues/3)) ([27b5f18](https://github.com/replicate/replicate-python-stainless/commit/27b5f1897b823349b29dbc82b1f6742d5d704c9e))
