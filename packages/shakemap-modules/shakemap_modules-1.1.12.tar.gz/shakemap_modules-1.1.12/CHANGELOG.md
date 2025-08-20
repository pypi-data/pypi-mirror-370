# main

## l.1.12 / 2025-08-19
    - Workaround for cartopy bug in mapping.py.

## l.1.11 / 2025-08-14
    - Update to esi-shakelib v1.1.13 for numpy 2.

## 1.1.10 / 2025-07-31
    - Add subduction sub-types to origin to support FFSimmer, esi-shakelib v1.1.12.

## 1.1.9 / 2025-07-23
    - Add __del__ method to MercatorMap class to fix memory leak in 
      uncertaintymaps and mapping.
    - Black reformatting of mapmaker.py and mercatormap.py.

## 1.1.8 / 2025-07-16
    - Change ffsim_min/max_dx_frac to dy in model.conf.

## 1.1.7 / 2025-07-14
    - Tweak to gmpe_sets.conf.
    - Change esi-shakelib dependency to v1.1.10 in pyproject.toml.
    - Added ffsim_area_trunc config parameter.

## 1.1.6 / 2025-07-08
    Fixes:                                                                                  
    - gridxml now correctly reports shakemap code version.                              
    - model support for new ffsimmer parameters.                                        
    - model turn off generic amplification factors for regression plots

## 1.1.5 / 2025-07-01
    - Revving version number to fix glitch.

## 1.1.4 / 2025-07-01
    - Refactor to output data needed for realizations for all IMs.
    - Fix bug where the Generic Amplification Factors were not applied by ffsimmer.
    - Fix test.
    - Fixed a bug in sm_clone that prevented the preferred Atlas shakemap from being chosen by default.
    - Fixed a bug that caused sm_clone to incorrectly fail on older fault text files.

## 1.1.3 / 2025-03-20
    - Added an option to mapping module to save figure objects to files that can be overplotted later.

## 1.1.2 / 2025-03-13
    - Fix points mode in model to use the same bounds that grid mode would use, insuring consistent bias between modes.
    - Set a fixed seed for FFSimmer RNG (RFF) to make results between runs and across deployments consistent.

## 1.1.1 / 2025-02-28
    - Refactor strings for sqlite to single quote string literals.
    - Refactor to emove a bunch of linter warnings.
    - Eliminate a bunch of deprecation warnings (datetime.utcnow(), etc.)

## 1.1.0 / 2025-02-07
    - Adding parameter for system_id in transfer_pdl.
    - Handling edge case in smclone where event does not have a depth. Logging a warning 
      and setting to 10 km in these cases.
    - Limit range of ztor for CY14 in modules.conf.

## 1.0.25 / 2024-09-28
    - Modify pyproject.toml to use updated (python 3.12) shakelib.
    - Modify .gitlab-ci.yml to use python 3.12 image.

## 1.0.24 / 2024-09-24
    - Vince's fixes to dyfi.
    - Bug fix to model to allow data to contain IMTs not in output.

## 1.0.23 / 2024-09-24
    - Dummy version to catch up to pip version.

## 1.0.22 / 2024-09-24
    - Dummy version to catch up to pip version.

## 1.0.21 / 2024-09-06
    - Revise region for europe_share to match the Kotho 2020 tectonic region.
    - Fix bug in select.conf re: Australia.

## 1.0.20 / 2024-08-31
    - Fix handling of openquake imt specifiers to be consistent with latest OQ.
    - Remove unnecessary geographic layer wkt files.
    - Upgrade version of shakelib to 1.0.13.

## 1.0.19 / 2024-08-26
    - Added layers for alaska, cascadia, south africa; revised layers for new
      zealand, australia, hawaii.
    - Reconfigured select to use new regions, revised existing regional config,
      changed horizontal buffer from 100 to 50.
    - Reconfigured gmpe_sets to more closely match NSHM GMPE selections, added
      new regions and revised others; dropped gmpes for sites and long-distance.
    - Revised model to drop output IMTs when a multigmpe cannot be created.
    - Fix many linter complaints.

## 1.0.18 / 2024-08-08
    - Bugfix in kml coremod to allow 0.6 sec data; cleanup of kml.pm.
    - Fixed bugs in sm_create that prevented creation of ShakeMap input when no ShakeMap exists online.

## 1.0.17 / 2024-07-16
    - Update model to use new true_grid method of FFSimmer when constraints are specified.
    - Modify ffsim_ constraints to include ztor; other fixes.

## 1.0.16 / 2024-07-08
    - Remove numpy from dependencies: is included by shakelib.
    - FIX: Use the preferred source when source is not specified.
    - Change gitlab runner tag to build
    - Force numpy to be less than v2.0
    - Updating smclone to prefer atlas, then us, then preferred network ShakeMap...

## 1.0.15 / 2024-06-05
    - Refactor to use latest FFSimmer; add configs for FFSimmer simulations; 
      reduce default number of simulations to 50; fix bug in shape module.

## 1.0.14 / 2024-05-28
    - Fix shape.py to only make shapefile of the original ShakeMap IMTs; fix model.py
      to work with the latest changes in shakelib.

## 1.0.13 / 2024-05-20
    - No-op.

## 1.0.12 / 2024-05-20
    - Fix bug in stddev types in _derive_imts_from_mmi.

## 1.0.11 / 2024-05-13
    - Clean up model.py.
    - Fix bug that occurred when GMM only has total stddev.
    - Clean up the CLI functions.

## 1.0.10 / 2024-04-23
    - Modify model to use FFSimmer; fix tests.

## 1.0.9 / 2024-02-05
    - Fix bug: wrong gmice library in modules.conf.

## 1.0.8 / ---?
    - smclone stuff.

## 1.0.7 / 2023-12-21

    - Changes to support running scenarios with and without finite faults.
    - Add --points argument back into assemble module.

## 1.0.6 / 2023-12-18

    - Re-add cont_mi.json to outputs to make USGS website happy.

## 1.0.5 / 2023-12-8

    - Fix transfer_email to work with encrypted servers.

## 1.0.4 / 2023-12-5

    - Fix bug in transfer_base.py.

## 1.0.3 / 2023-11-28

    - Remove the openquake.engine dependencies since it is included in the shakelib install.

## 1.0.2 / 2023-11-27

    - Add versioning to model module

## 1.0.1 / 2023-11-2

    - Fix imports for makecsv.py
    - Add coverage report generation and artifact upload to CI
    - Add badges to repository for latest release version, pipeline tests and coverage

## 1.0.0 / 2023-10-31

    - Initial repository setup
    - Update CI file for testing and deployment
    - Add points fixes 
    - Improve test cleanup
    - Make test data paths relative to tests rather than install location
    - Bring esi-utils-cartopy functionality into this repository, remove as dep
    - Test deployment and path fix for .whl installations
