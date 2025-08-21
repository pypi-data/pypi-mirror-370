# rail_bpz

[![codecov](https://codecov.io/gh/LSSTDESC/rail_bpz/branch/main/graph/badge.svg)](https://codecov.io/gh/LSSTDESC/rail_bpz)
[![PyPI](https://img.shields.io/pypi/v/bpz?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/pz-rail-bpz/)


RAIL interface to BPZ algorithms via the [DESC_BPZ](https://github.com/LSSTDESC/DESC_BPZ) package implementation (also available via PyPI with `pip install desc-bpz`).  Anyone using BPZ via either rail_bpz or DESC_BPZ should cite both [Benitez (2000)](https://ui.adsabs.harvard.edu/abs/2000ApJ...536..571B/abstract) and [Coe et al. (2006)](https://ui.adsabs.harvard.edu/abs/2006AJ....132..926C/abstract).

In addition to the "default" BPZ CWWSB SED template set, `rail_base` now also includes an additional set of 31 template SEDs, a set that was used to compute the COSMOS 30-band photo-z's using LePhare.  The template set consists of empirical templates from [Poletta et al 2007](https://arxiv.org/pdf/astro-ph/0703255) supplemented with blue [BC03](https://ui.adsabs.harvard.edu/abs/2003MNRAS.344.1000B/abstract) SEDs, see [Ilbert et al 2009](https://ui.adsabs.harvard.edu/abs/2009ApJ...690.1236I/abstract) and [Dahlen et al 2013](https://ui.adsabs.harvard.edu/abs/2013ApJ...775...93D/abstract) for details.  The demo notebook [BPZ_lite_demo.ipynb](https://github.com/LSSTDESC/rail/blob/main/examples/estimation_examples/BPZ_lite_demo.ipynb) in the rail examples repository shows an example of how to use this alternate template set.

As the "lite" name implies, not all features of BPZ are implemented, the main product is the marginalized redshift PDF, which is output for a sample as a `qp` ensemble.  However, several other quantities are computed and stored as "ancillary" data and stored with the ensemble, these are:
- zmode (float): the mode of the marginalized posterior redshift PDF distribution.
- zmean (float): the mean of the marginalized posterior redshift PDF distribution.
- tb (int): the integer index for the "best-fit" SED template **at the redshift mode, `zmode`**.  Note that the best-fit template can be different at different redshifts as the SED observed colors change with redshift, so you **can not** assume this single SED for the full marginalized PDF, it should only be used for the "point estimate" redshift `zmode`.
- todds (float): relating to the comment above on tb, `todds` is a new quantity not included with the original BPZ implementation, it is the fraction of marginalized posterior probability assigned to `tb`.  So, high values of `todds` would mean that no other templates fit well, even at other redshifts, while a lower value of `todds` means that there are alternative fits, either at the same redshift or other redshifts.  If you are wanting to compute physical quantities based on `tb`, a lower value of `todds` would mean that such fits would be missing degenerate SED solutions, and should not be trusted. 


## Contributing

The greatest strength of RAIL is its extensibility; those interested in contributing to RAIL should start by consulting the [Contributing guidelines](https://rail-hub.readthedocs.io/en/latest/source/contributing.html) on ReadTheDocs.

## Citing RAIL

RAIL is open source and may be used according to the terms of its [LICENSE](https://github.com/LSSTDESC/RAIL/blob/main/LICENSE) [(BSD 3-Clause)](https://opensource.org/licenses/BSD-3-Clause).
If you used RAIL in your study, please cite this repository <https://github.com/LSSTDESC/RAIL>, and RAIL Team et al. (2025) <https://arxiv.org/abs/2505.02928>
```
@ARTICLE{2025arXiv250502928T,
       author = {{The RAIL Team} and {van den Busch}, Jan Luca and {Charles}, Eric and {Cohen-Tanugi}, Johann and {Crafford}, Alice and {Crenshaw}, John Franklin and {Dagoret}, Sylvie and {De-Santiago}, Josue and {De Vicente}, Juan and {Hang}, Qianjun and {Joachimi}, Benjamin and {Joudaki}, Shahab and {Bryce Kalmbach}, J. and {Kannawadi}, Arun and {Liang}, Shuang and {Lynn}, Olivia and {Malz}, Alex I. and {Mandelbaum}, Rachel and {Merz}, Grant and {Moskowitz}, Irene and {Oldag}, Drew and {Ruiz-Zapatero}, Jaime and {Rahman}, Mubdi and {Rau}, Markus M. and {Schmidt}, Samuel J. and {Scora}, Jennifer and {Shirley}, Raphael and {St{\"o}lzner}, Benjamin and {Toribio San Cipriano}, Laura and {Tortorelli}, Luca and {Yan}, Ziang and {Zhang}, Tianqing and {the Dark Energy Science Collaboration}},
        title = "{Redshift Assessment Infrastructure Layers (RAIL): Rubin-era photometric redshift stress-testing and at-scale production}",
      journal = {arXiv e-prints},
     keywords = {Instrumentation and Methods for Astrophysics, Cosmology and Nongalactic Astrophysics, Astrophysics of Galaxies},
         year = 2025,
        month = may,
          eid = {arXiv:2505.02928},
        pages = {arXiv:2505.02928},
          doi = {10.48550/arXiv.2505.02928},
archivePrefix = {arXiv},
       eprint = {2505.02928},
 primaryClass = {astro-ph.IM},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2025arXiv250502928T},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}
```
Please consider also inviting the developers as co-authors on publications resulting from your use of RAIL by [making an issue](https://github.com/LSSTDESC/rail/issues/new/choose).
