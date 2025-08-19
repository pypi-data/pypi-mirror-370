# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0]

### Added

-   Add `is_insertion` and `is_deletion` properties to `Variant`.
-   Add `DnaModel` abstract base class.
-   Add support for center mask scoring over the entire sequence by passing
    `None` for width.

### Changed

-   Move RPC requests and responses to `dna_model_service.proto`.
-   Move functionality to convert `TrackData` to/from protocol buffers to
    utility module.

## [0.1.0]

### Added

-   Add `L2_DIFF_LOG1P` variant scoring aggregation type.
-   Add `is_snv` property to `Variant`.
-   Add non-zero mean track metadata field to model output metadata.
-   Add optional interval argument to `predict_sequence`.

## [0.0.2]

### Added

-   `colab_utils` module to wrap reading API keys from environment variables or
    Google Colab secrets.

## [0.0.1]

Initial release.
