# FUNPACK - FMRIB configuration profile


[![PyPi version](https://img.shields.io/pypi/v/fmrib-unpack-fmrib-config.svg)](https://pypi.python.org/pypi/fmrib-unpack-fmrib-config/)[![Anaconda version](https://anaconda.org/conda-forge/fmrib-unpack-fmrib-config/badges/version.svg)](https://anaconda.org/conda-forge/fmrib-unpack-fmrib-config/)


[**FUNPACK**](https://open.win.ox.ac.uk/pages/fsl/funpack/) is a Python
library for pre-processing of UK BioBank data. The `fmrib-unpack-fmrib-config`
package contains a configuration profile for FUNPACK which encodes a large set
of cleaning and processing rules for a range of UK BioBank data fields.


FUNPACK depends on `fmrib-unpack-fmrib-config`, so if FUNPACK is installed,
then you already have the `fmrib` configuration profile, and can use it like
so:

    fmrib_unpack -cfg fmrib_standard out.tsv <input.csv>


## Overview


The FUNPACK ``fmrib_standard`` configuration profile performs the following
steps. This is an overview - refer to the configuration files for all details:


### Data import


All data-fields from the categories listed in
[`fmrib_cats.cfg`](funpack/configs/fmrib_cats.cfg) are imported. These
categories are defined in
[`categories.tsv`](funpack/configs/fmrib/categories.tsv). Data fields which
are not in any of these categories are *not* imported.

*Notes:*

 - Some data-field categories which are not of direct interest are
   explicitly excluded (currently category 100).
 - Some categories (specifically 1, 31, 60, 70, 96, 98, and 99) contain
   secondary/auxillary data-fields which are not of direct interest, but
   need to be in the output file. These categories are excluded from
   some processing steps (see below).


### Cleaning/preprocessing


1. **NA value replacement** (removing certain values and replacing them with
   NA) is performed on all data fields which use the data codings listed in
   [`datacodings_navalues.tsv`](funpack/configs/fmrib/datacodings_navalues.tsv).

2. All date/time data-fields are converted into floating point numbers of the
   form `<YYYY>.fraction`. This rule is defined in
   [`datetime_formatting.tsv`](funpack/configs/fmrib/datetime_formatting.tsv),
   and the conversion logic defined in the
   [`funpack.plugins.fmrib`](https://open.win.ox.ac.uk/pages/fsl/funpack/funpack.plugins.fmrib.html)
   module.

3. **Categorical quantitative recoding** (e.g. replacing potentially
   quantitative quantised/categorical codings with more monotonic/sensible
   codings) is performed on all data fields which use the data codings listed
   in
   [`datacodings_recoding.tsv`](funpack/configs/fmrib/datacodings_recoding.tsv).

4. **Child value replacement** (inferring the values of missing data-fields
   based on responses to parent data-fields) is performed on all data-fields
   listed in
   [`variables_parentvalues.tsv`](funpack/configs/fmrib/variables_parentvalues.tsv).


### Processing


All subsequent processing steps are specified in
[`processing.tsv`](funpack/configs/fmrib/processing.tsv), and are described
here:


1. A number of categorical data fields are *binarised* - a separate column is
   created for each category, with a `1` for subjects in that category, or a
   `0` otherwise.

2. ICD9 and ICD10 data-fields
   [41270](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41270), and
   [41271](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41271) are
   binarised, but instead of containing `1`/`0`, they contain the
   corresponding diagnosis dates, taken respectively from data-fields
   [41280](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41280), and
   [41281](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41281).

3. Sparse columns are removed. For most data-fields, a column is deemed
   sparse if any of these conditions hold:
     - Contains 50 or fewer data points
     - Has a standard deviation of less than `1e-6` (only applied to numeric
       data-fields)
     - If categorical, one category comprises 99% or more of all data
   Data-fields from secondary/auxillary categories are excluded from this
   sparsity test.

4. Columns which were binarised as outlined above are subjected to a different
   sparsity test - any columns which have less than 10 non-0 entries are
   dropped.

5. Redundant columns are removed. Correlation and missingness correlation is
   calculated between all pairs of columns. If the correlation between a pair
   of columns exceeds 0.99 and the missingness correlation exceeds 0.2, the
   column with more missing values is removed. ICD9/10 columns are excluded
   from this step, along with data-fields from secondary/auxillary categories.

6. New binary columns are generated for the ICD9 and ICD10 in-patient hospital
   diagnosis data fields
   [41270](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41270), and
   [41271](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41271) (for the
   columns remaining after the sparsity/redundancy tests) indicating, for each
   diagnosis, whether it was a primary or secondary diagnosis. This
   information is obtained from data-fields
   [41202](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41202),
   [41203](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41203),
   [41204](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41204), and
   [41205](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41205), which
   are subsequently removed from the data set.


> _Notes on ICD9/ICD10 data-fields_
>
> ICD10 in-patient hospital diagnosis codes are available in the raw data in
> the following data fields:
>
>  - [41270](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41270): ICD10
>    diagnoses across all hospital visits, including primary and secondary
>    diagnoses, and external causes. Corresponding dates for each diagnosis
>    are given in
>    [41280](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41280).

>  - [41201](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41201): As
>    above, but containing external causes only. Corresponding dates are not
>    available in a separate data field, (but are available in 41270/41280).
>
>  - [41202](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41202):
>    As above, but containing primary diagnoses only. Corresponding dates
>    are given in
>    [41262](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41262).
>
>  - [41204](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41204):
>    As above, but containing secondary diagnoses only. Corresponding dates
>    are not available in a separate data field, (but are available in
>    41270/41280).
>
> ICD9 diagnosis codes follow the same structure, and are available in data
> fields [41271](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41271)
> (all diagnoses, dates in
> [41281](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41281)),
> [41203](https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41203) (primary
> diagnoses, dates in
> [41263]((https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41263)), and
> [41205]((https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=41205) (secondary
> diagnoses).
>
> In the output data, data-fields 41270 (ICD10) and 41271 (ICD9) are
> re-arranged so that there is one column per diagnosis code. These columns
> are named as `41270-<code>` or `41271-<code>`, e.g. `41270-A044`, and
> contain the diagnosis date (taken from 41280 and 41281) for subjects with
> the diagnosis, or a `0` for subjects without the diagnosis.
>
> Binary columns are also generated for each diagnosis code indicating whether
> it was a primary or secondary diagnosis - this information is obtained from
> data fields 41202, 41203, 41204, and 41205. These columns are given names:
>
>  - `41202-<code>.primary`
>  - `41203-<code>.secondary`
>  - `41204-<code>.primary`
>  - `41205-<code>.secondary`



### Output files

For this command:

    fmrib_unpack -cfg fmrib_standard out.tsv <input.csv>

All processed data-fields will be saved to `out.tsv`. Note that all non-numeric
columns are removed, so this file only contains numeric columns.

The following files are also saved:

 - `out_log.txt`: Log messages, useful for troubleshooting
 - `out_summary.txt`: Summary of all rules applied to every data-field in the
   input file
 - `out_description.txt`: Description of every column in the output file.
 - `out_icd10_map.txt`: Every ICD10 diagnosis code in the output file, along
   with their equivalent numeric code, and text desccription

The `fmrib_new_release` profile (see below) also produces:

 - `out_unknown_vars.txt`: List of all columns from previously
   unknown/uncategorised data-fields, and whether or not they passed
   processing and were exported.


## Other configuration profiles

The `fmrib_standard` profile, as described above, is used within FMRIB for the
preprocessing of all non-imaging UKB data. Some other configurations profiles
are also available:

 - [`fmrib`](funpack/configs/fmrib_cats.cfg): As above, but all data-fields
   present in the input file(s) are loaded, and logging/additional output
   files are not generated.
 - [`fmrib_new_release`](funpack/configs/fmrib_new_release.cfg): Equivalent to
   `fmrib_standard`, but load and process **all** data-fields (except those in
   explicitly excluded categories), and output a summary of any unknown/
   uncategorised data-fields.
