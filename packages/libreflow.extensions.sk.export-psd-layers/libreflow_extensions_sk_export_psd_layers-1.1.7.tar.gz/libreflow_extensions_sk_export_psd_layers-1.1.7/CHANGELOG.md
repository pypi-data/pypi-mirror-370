# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)[^1].

<!---
Types of changes

- Added for new features.
- Changed for changes in existing functionality.
- Deprecated for soon-to-be removed features.
- Removed for now removed features.
- Fixed for any bug fixes.
- Security in case of vulnerabilities.

-->

## [Unreleased]

### Added

* Warning message when publishing regarding resolution and colour depth.
* Message in the window when creating a new working copy.

## [1.1.6] - 2025-08-07

### Fixed

* Export resized to psd canvas - makes the action less prone to crash from a lack of RAM

## [1.1.5] - 2025-07-03

### Fixed

* Top level layers are forced to be shown when exported and are not added to "hidden_layers" in JSON layers file anymore

## [1.1.4] - 2025-05-09

### Fixed

* The exported image will now have the correct filename

## [1.1.3] - 2025-04-30

### Changed

* Action renamed to "Export" in actions submenu

### Added

* BG Color projects will be exported as a png 

### Fixed

* Faster no_chara export in ExportPSDPreview

## [1.1.2] - 2025-04-25

### Fixed

* Export layers action: layers with invalid filename characters break the script

## [1.1.1] - 2025-04-24

### Fixed

* Export layers action: render folder do not create

## [1.1.0] - 2025-04-24

### Added

* An action to export a psd for preview
  * Use the `psd-tools` python module
  * Three PNGs, one in full format, one with no characters and one without a safety margin
    * These files are not tracked in Libreflow, they remain local
  * A specific upload to kitsu action is available for this use case
* An action to publish and export at the same time
* An action to export layers in batch
  * Available at a film hierarchy level

### Changed

* Export layers action now uses `psd-tools` python module instead of a Adobe extend script
    * Process can takes longer, but Photoshop is no longer required

### Fixed

* Hide export layers action when file has no published revisions

## [1.0.1] - 2025-04-04

### Fixed

* including .jsx files in setup.py

## [1.0.0] - 2025-03-27

### Added

* Extension to export the layers of a Photoshop project as png images 
