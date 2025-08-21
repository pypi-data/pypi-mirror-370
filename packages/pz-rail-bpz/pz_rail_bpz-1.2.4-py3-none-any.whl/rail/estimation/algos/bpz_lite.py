"""
Port of *some* parts of BPZ, not the entire codebase.
Much of the code is directly ported from BPZ, written
by Txitxo Benitez and Dan Coe (Benitez 2000), which
was modified by Will Hartley and Sam Schmidt to make
it python3 compatible.  It was then modified to work
with TXPipe and ceci by Joe Zuntz and Sam Schmidt
for BPZPipe.  This version for RAIL removes a few
features and concentrates on just predicting the PDF.

Missing from full BPZ:
-no tracking of 'best' type/TB
-no "interp" between templates
-no ODDS, chi^2, ML quantities
-plotting utilities
-no output of 2D probs (maybe later add back in)
-no 'cluster' prior mods
-no 'ONLY_TYPE' mode

"""

import os
import numpy as np
import scipy.optimize as sciop
import scipy.integrate
import glob
import qp
import tables_io
from ceci.config import StageParameter as Param
from rail.estimation.estimator import CatEstimator, CatInformer
from rail.utils.path_utils import RAILDIR
from rail.core.common_params import SHARED_PARAMS


def nzfunc(z, z0, alpha, km, m, m0):  # pragma: no cover
    zm = z0 + (km * (m - m0))
    return np.power(z, alpha) * np.exp(-1. * np.power((z / zm), alpha))


class BPZliteInformer(CatInformer):
    """Inform stage for BPZliteEstimator, this stage *assumes* that you have a set of
    SED templates and that the training data has already been assigned a
    'best fit broad type' (that is, something like ellliptical, spiral,
    irregular, or starburst, similar to how the six SEDs in the CWW/SB set
    of Benitez (2000) are assigned 3 broad types).  This informer will then
    fit parameters for the evolving type fraction as a function of apparent
    magnitude in a reference band, P(T|m), as well as the redshift prior
    of finding a galaxy of the broad type at a particular redshift, p(z|m, T)
    where z is redshift, m is apparent magnitude in the reference band, and T
    is the 'broad type'.  We will use the same forms for these functions as
    parameterized in Benitez (2000).  For p(T|m) we have
    p(T|m) = exp(-kt(m-m0))
    where m0 is a constant and we fit for values of kt
    For p(z|T,m) we have

    ```
    P(z|T,m) = f_x*z0_x^a *exp(-(z/zm_x)^a)
    where zm_x = z0_x*(km_x-m0)
    ```

    where f_x is the type fraction from p(T|m), and we fit for values of
    z0, km, and a for each type.  These parameters are then fed to the BPZ
    prior for use in the estimation stage.
    """
    name = "BPZliteInformer"
    config_options = CatInformer.config_options.copy()
    config_options.update(zmin=SHARED_PARAMS,
                          zmax=SHARED_PARAMS,
                          nzbins=SHARED_PARAMS,
                          nondetect_val=SHARED_PARAMS,
                          mag_limits=SHARED_PARAMS,
                          bands=SHARED_PARAMS,
                          err_bands=SHARED_PARAMS,
                          ref_band=SHARED_PARAMS,
                          redshift_col=SHARED_PARAMS,
                          data_path=Param(str, "None",
                                          msg="data_path (str): file path to the "
                                          "SED, FILTER, and AB directories.  If left to "
                                          "default `None` it will use the install "
                                          "directory for rail + rail/examples_data/estimation_data/data"),
                          spectra_file=Param(str, "CWWSB4.list",
                                             msg="name of the file specifying the list of SEDs to use"),
                          m0=Param(float, 20.0, msg="reference apparent mag, used in prior param"),
                          nt_array=Param(list, [1, 2, 5], msg="list of integer number of templates per 'broad type', "
                                         "must be in same order as the template set, and must sum to the same number "
                                         "as the # of templates in the spectra file"),
                          mmin=Param(float, 18.0, msg="lowest apparent mag in ref band, lower values ignored"),
                          mmax=Param(float, 29.0, msg="highest apparent mag in ref band, higher values ignored"),
                          init_kt=Param(float, 0.3, msg="initial guess for kt in training"),
                          init_zo=Param(float, 0.4, msg="initial guess for z0 in training"),
                          init_alpha=Param(float, 1.8, msg="initial guess for alpha in training"),
                          init_km=Param(float, 0.1, msg="initial guess for km in training"),
                          type_file=Param(str, "", msg="name of file with the broad type fits for the training data"),
                          output_hdfn=Param(bool, True, msg="if True, just return the default HDFN prior params rather than fitting"))

    def __init__(self, args, **kwargs):
        """Init function, init config stuff
        """
        super().__init__(args, **kwargs)
        self.fo_arr = None
        self.kt_arr = None
        self.typmask = None
        self.ntyp = None
        self.mags = None
        self.szs = None
        self.besttypes = None
        self.m0 = self.config.m0

    def _frac_likelihood(self, frac_params):
        ngal = len(self.mags)
        probs = np.zeros([self.ntyp, ngal])
        foarr = frac_params[:self.ntyp - 1]
        ktarr = frac_params[self.ntyp - 1:]
        for i in range(self.ntyp - 1):
            probs[i, :] = [foarr[i] * np.exp(-1. * ktarr[i] * (mag - self.m0)) for mag in self.mags]
        # set the probability of last element to 1 - sum of the others to
        # keep normalized, this is the way BPZ does things
        probs[self.ntyp - 1, :] = 1. - np.sum(probs[:-1, :], axis=0)
        likelihood = 0.0
        for i, typ in enumerate(self.besttypes):
            if probs[typ, i] > 0.0:
                likelihood += -2. * np.log10(probs[typ, i])
        return likelihood

    def _find_fractions(self):
        # set up fo and kt arrays, choose default start values
        if self.ntyp == 1:
            fo_init = np.array([1.0])
            kt_init = np.array([self.config.init_kt])
        else:
            fo_init = np.ones(self.ntyp - 1) / (self.ntyp)
            kt_init = np.ones(self.ntyp - 1) * self.config.init_kt
        fracparams = np.hstack([fo_init, kt_init])
        # run scipy optimize to find best params
        # note that best fit vals are stored as "x" for some reason
        frac_results = sciop.minimize(self._frac_likelihood, fracparams, method="nelder-mead").x
        if self.ntyp == 1:
            self.fo_arr = np.array([frac_results[0]])
            self.kt_arr = np.array([frac_results[1]])
        else:
            tmpfo = frac_results[:self.ntyp - 1]
            # minimizer can sometimes give fractions greater than one, if so normalize
            fracnorm = np.sum(tmpfo)
            if fracnorm > 1.:  # pragma: no cover
                print("bad norm for f0, normalizing")
                tmpfo /= fracnorm
            self.fo_arr = tmpfo
            self.kt_arr = frac_results[self.ntyp - 1:]

    def _dndz_likelihood(self, params):
        mags = self.mags[self.typmask]
        szs = self.szs[self.typmask]

        z0, alpha, km = params
        zm = z0 + (km * (mags - self.m0))

        # The normalization to the likelihood, which is needed here
        Inorm = zm ** (alpha + 1) * scipy.special.gamma(1 + 1 / alpha) / alpha

        # This is a vector of loglike per object
        loglike = alpha * np.log(szs) - ((szs / zm)**alpha) - np.log(Inorm)

        # We are minimizing not maximizing so return the negative
        mloglike = -(loglike.sum())

        # print(params, mloglike)
        return mloglike

    def _find_dndz_params(self):

        # initial parameters for zo, alpha, and km
        zo_arr = np.ones(self.ntyp)
        a_arr = np.ones(self.ntyp)
        km_arr = np.ones(self.ntyp)
        for i in range(self.ntyp):
            print(f"minimizing for type {i}")
            self.typmask = (self.besttypes == i)
            dndzparams = np.hstack([self.config.init_zo, self.config.init_alpha, self.config.init_km])
            result = sciop.minimize(self._dndz_likelihood, dndzparams, method="nelder-mead").x
            zo_arr[i] = result[0]
            a_arr[i] = result[1]
            km_arr[i] = result[2]
            print(f"best fit z0, alpha, km for type {i}: {result}")
        return zo_arr, km_arr, a_arr

    def _get_broad_type(self, ngal):
        typefile = self.config.type_file
        if typefile == "":  # pragma: no cover
            typedata = np.zeros(ngal, dtype=int)
        else:
            typedata = tables_io.read(typefile)["types"]  # pragma: no cover
        numtypes = len(list(set(typedata)))
        return numtypes, typedata

    def run(self):
        """compute the best fit prior parameters
        """
        if self.config.output_hdfn:
            # the parameters for the HDFN prior
            self.fo_arr = np.array([0.35, 0.5])
            self.kt_arr = np.array([0.45, 0.147])
            self.zo_arr = np.array([0.431, 0.39, 0.0626])
            self.km_arr = np.array([0.0913, 0.0636, 0.123])
            self.a_arr = np.array([2.465, 1.806, 0.906])
            self.m0 = 20.0
            self.nt_array = self.config.nt_array
        else:
            self.m0 = self.config.m0
            if self.config.hdf5_groupname:
                training_data = self.get_data("input")[self.config.hdf5_groupname]
            else:  # pragma: no cover
                training_data = self.get_data("input")

            # convert training data format to numpy dictionary
            if tables_io.types.table_type(training_data) != 1:
                training_data = self._convert_table_format(training_data, out_fmt_str="numpyDict")

            ngal = len(training_data[self.config.ref_band])

            if self.config.ref_band not in training_data.keys():  # pragma: no cover
                raise KeyError(f"ref_band {self.config.ref_band} not found in input data!")
            if self.config.redshift_col not in training_data.keys():  # pragma: no cover
                raise KeyError(f"redshift column {self.config.redshift_col} not found in input data!")

            # cal function to get broad types
            Ntyp, broad_types = self._get_broad_type(ngal)
            self.ntyp = Ntyp
            # trim data to between mmin and mmax
            ref_mags = training_data[self.config.ref_band]
            mask = ((ref_mags >= self.config.mmin) & (ref_mags <= self.config.mmax))
            self.mags = ref_mags[mask]
            # To not screw up likelihood calculation, set objs with mag
            # brighter than m0 to value of m0
            brightmask = (self.mags < self.m0)
            self.mags[brightmask] = self.m0
            self.szs = training_data[self.config.redshift_col][mask]
            self.besttypes = broad_types[mask]

            numused = len(self.besttypes)
            print(f"using {numused} galaxies in calculation")

            self._find_fractions()
            print("best values for fo and kt:")
            print(self.fo_arr)
            print(self.kt_arr)
            self.zo_arr, self.km_arr, self.a_arr = self._find_dndz_params()
            self.a_arr = np.abs(self.a_arr)

        self.model = dict(fo_arr=self.fo_arr, kt_arr=self.kt_arr, zo_arr=self.zo_arr,
                          km_arr=self.km_arr, a_arr=self.a_arr, mo=self.m0,
                          nt_array=self.config.nt_array)
        self.add_data("model", self.model)


class BPZliteEstimator(CatEstimator):
    """CatEstimator subclass to implement basic marginalized PDF for BPZ
    In addition to the marginalized redshift PDF, we also compute several
    ancillary quantities that will be stored in the ensemble ancil data:
    zmode: mode of the PDF
    amean: mean of the PDF
    tb: integer specifying the best-fit SED *at the redshift mode*
    todds: fraction of marginalized posterior prob. of best template,
    so lower numbers mean other templates could be better fits, likely
    at other redshifts
    """
    name = "BPZliteEstimator"
    config_options = CatEstimator.config_options.copy()
    config_options.update(zmin=SHARED_PARAMS,
                          zmax=SHARED_PARAMS,
                          nzbins=SHARED_PARAMS,
                          nondetect_val=SHARED_PARAMS,
                          mag_limits=SHARED_PARAMS,
                          bands=SHARED_PARAMS,
                          ref_band=SHARED_PARAMS,
                          err_bands=SHARED_PARAMS,
                          redshift_col=SHARED_PARAMS,
                          dz=Param(float, 0.01, msg="delta z in grid"),
                          unobserved_val=Param(float, -99.0, msg="value to be replaced with zero flux and given large errors for non-observed filters"),
                          data_path=Param(str, "None",
                                          msg="data_path (str): file path to the "
                                          "SED, FILTER, and AB directories.  If left to "
                                          "default `None` it will use the install "
                                          "directory for rail + ../examples_data/estimation_data/data"),
                          filter_list=SHARED_PARAMS,
                          spectra_file=Param(str, "CWWSB4.list",
                                             msg="name of the file specifying the list of SEDs to use"),
                          madau_flag=Param(str, "no",
                                           msg="set to 'yes' or 'no' to set whether to include intergalactic "
                                               "Madau reddening when constructing model fluxes"),
                          no_prior=Param(bool, False, msg="set to True if you want to run with no prior"),
                          p_min=Param(float, 0.005,
                                      msg="BPZ sets all values of "
                                      "the PDF that are below p_min*peak_value to 0.0, "
                                      "p_min controls that fractional cutoff"),
                          gauss_kernel=Param(float, 0.0,
                                             msg="gauss_kernel (float): BPZ "
                                             "convolves the PDF with a kernel if this is set "
                                             "to a non-zero number"),
                          zp_errors=SHARED_PARAMS,
                          mag_err_min=Param(float, 0.005,
                                            msg="a minimum floor for the magnitude errors to prevent a "
                                            "large chi^2 for very very bright objects"))

    def __init__(self, args, **kwargs):
        """Constructor, build the CatEstimator, then do BPZ specific setup
        """
        super().__init__(args, **kwargs)

        datapath = self.config["data_path"]
        if datapath is None or datapath == "None":
            tmpdatapath = os.path.join(RAILDIR, "rail/examples_data/estimation_data/data")
            os.environ["BPZDATAPATH"] = tmpdatapath
            self.data_path = tmpdatapath
        else:  # pragma: no cover
            self.data_path = datapath
            os.environ["BPZDATAPATH"] = self.data_path
        if not os.path.exists(self.data_path):  # pragma: no cover
            raise FileNotFoundError("BPZDATAPATH " + self.data_path + " does not exist! Check value of data_path in config file!")

        # check on bands, errs, and prior band
        if len(self.config.bands) != len(self.config.err_bands):  # pragma: no cover
            raise ValueError("Number of bands specified in bands must be equal to number of mag errors specified in err_bands!")
        if self.config.ref_band not in self.config.bands:  # pragma: no cover
            raise ValueError(f"reference band not found in bands specified in bands: {str(self.config.bands)}")
        if len(self.config.bands) != len(self.config.err_bands) or len(self.config.bands) != len(self.config.filter_list):
            raise ValueError(
                f"length of bands {len(self.config.bands)}), "
                f"err_bands, {len(self.config.err_bands)} and "
                f"filter_list {len(self.config.filter_list)} are not the same!"
            )

    def _initialize_run(self):
        super()._initialize_run()

        # If we are not the root process then we wait for
        # the root to (potentially) create all the templates before
        # reading them ourselves.
        if self.rank > 0:  # pragma: no cover
            # The Barrier method causes all processes to stop
            # until all the others have also reached the barrier.
            # If our rank is > 0 then we must be running under MPI.
            self.comm.Barrier()
            self.flux_templates = self._load_templates()
        # But if we are the root process then we just go
        # ahead and load them before getting to the Barrier,
        # which will allow the other processes to continue
        else:
            self.flux_templates = self._load_templates()
            # We might only be running in serial, so check.
            # If we are running MPI, then now we have created
            # the templates we let all the other processes that
            # stopped at the Barrier above continue and read them.
            if self.is_mpi():  # pragma: no cover
                self.comm.Barrier()

    def open_model(self, **kwargs):
        CatEstimator.open_model(self, **kwargs)
        self.modeldict = self.model

    def _load_templates(self):
        from desc_bpz.useful_py3 import get_str, get_data, match_resol

        # The redshift range we will evaluate on
        self.zgrid = np.linspace(self.config.zmin, self.config.zmax, self.config.nzbins)
        z = self.zgrid

        data_path = self.data_path
        filters = self.config.filter_list

        spectra_file = os.path.join(data_path, "SED", self.config.spectra_file)
        spectra = [s[:-4] for s in get_str(spectra_file)]

        nt = len(spectra)
        nf = len(filters)
        nz = len(z)
        flux_templates = np.zeros((nz, nt, nf))

        ab_dir = os.path.join(data_path, "AB")
        os.makedirs(ab_dir, exist_ok=True)

        # make a list of all available AB files in the AB directory
        ab_file_list = glob.glob(ab_dir + "/*.AB")
        ab_file_db = [os.path.split(x)[-1] for x in ab_file_list]

        for i, s in enumerate(spectra):
            for j, f in enumerate(filters):
                model = f"{s}.{f}.AB"
                if model not in ab_file_db:  # pragma: no cover
                    self._make_new_ab_file(s, f)
                model_path = os.path.join(data_path, "AB", model)
                zo, f_mod_0 = get_data(model_path, (0, 1))
                flux_templates[:, i, j] = match_resol(zo, f_mod_0, z)

        return flux_templates

    def _make_new_ab_file(self, spectrum, filter_):  # pragma: no cover
        from desc_bpz.bpz_tools_py3 import ABflux

        new_file = f"{spectrum}.{filter_}.AB"
        print(f"  Generating new AB file {new_file}....")
        ABflux(spectrum, filter_, self.config.madau_flag)

    def _preprocess_magnitudes(self, data):
        from desc_bpz.bpz_tools_py3 import e_mag2frac

        bands = self.config.bands
        errs = self.config.err_bands

        fluxdict = {}

        # Load the magnitudes
        zp_frac = e_mag2frac(np.array(self.config.zp_errors))

        # replace non-detects with 99 and mag_err with lim_mag for consistency
        # with typical BPZ performance
        for bandname, errname in zip(bands, errs):
            if np.isnan(self.config.nondetect_val):  # pragma: no cover
                detmask = np.isnan(data[bandname])
            else:
                detmask = np.isclose(data[bandname], self.config.nondetect_val)
            data[bandname][detmask] = 99.0
            data[errname][detmask] = self.config.mag_limits[bandname]

        # replace non-observations with -99, again to match BPZ standard
        # below the fluxes for these will be set to zero but with enormous
        # flux errors
        for bandname, errname in zip(bands, errs):
            if np.isnan(self.config.unobserved_val):  # pragma: no cover
                obsmask = np.isnan(data[bandname])
            else:
                obsmask = np.isclose(data[bandname], self.config.unobserved_val)
            data[bandname][obsmask] = -99.0
            data[errname][obsmask] = 20.0

        # Only one set of mag errors
        mag_errs = np.array([data[er] for er in errs]).T

        # Group the magnitudes and errors into one big array
        mags = np.array([data[b] for b in bands]).T

        # Clip to min mag errors.
        # JZ: Changed the max value here to 20 as values in the lensfit
        # catalog of ~ 200 were causing underflows below that turned into
        # zero errors on the fluxes and then nans in the output
        np.clip(mag_errs, self.config.mag_err_min, 20, mag_errs)

        # Convert to pseudo-fluxes
        flux = 10.0**(-0.4 * mags)
        flux_err = flux * (10.0**(0.4 * mag_errs) - 1.0)

        # Check if an object is seen in each band at all.
        # Fluxes not seen at all are listed as infinity in the input,
        # so will come out as zero flux and zero flux_err.
        # Check which is which here, to use with the ZP errors below
        seen1 = (flux > 0) & (flux_err > 0)
        seen = np.where(seen1)
        # unseen = np.where(~seen1)
        # replace Joe's definition with more standard BPZ style
        nondetect = 99.
        nondetflux = 10.**(-0.4 * nondetect)
        unseen = np.isclose(flux, nondetflux, atol=nondetflux * 0.5)

        # replace mag = 99 values with 0 flux and 1 sigma limiting magnitude
        # value, which is stored in the mag_errs column for non-detects
        # NOTE: We should check that this same convention will be used in
        # LSST, or change how we handle non-detects here!
        flux[unseen] = 0.
        flux_err[unseen] = 10.**(-0.4 * np.abs(mag_errs[unseen]))

        # Add zero point magnitude errors.
        # In the case that the object is detected, this
        # correction depends onthe flux.  If it is not detected
        # then BPZ uses half the errors instead
        add_err = np.zeros_like(flux_err)
        add_err[seen] = ((zp_frac * flux)**2)[seen]
        add_err[unseen] = ((zp_frac * 0.5 * flux_err)**2)[unseen]
        flux_err = np.sqrt(flux_err**2 + add_err)

        # Convert non-observed objects to have zero flux
        # and enormous error, so that their likelihood will be
        # flat. This follows what's done in the bpz script.
        nonobserved = -99.
        unobserved = np.isclose(mags, nonobserved)
        flux[unobserved] = 0.0
        flux_err[unobserved] = 1e108

        # Upate the flux dictionary with new things we have calculated
        fluxdict['flux'] = flux
        fluxdict['flux_err'] = flux_err
        m_0_col = self.config.bands.index(self.config.ref_band)
        fluxdict['mag0'] = mags[:, m_0_col]

        return fluxdict

    def _estimate_pdf(self, flux_templates, kernel, flux, flux_err, mag_0, z):
        from desc_bpz.bpz_tools_py3 import p_c_z_t
        from desc_bpz.prior_from_dict import prior_function

        modeldict = self.modeldict
        p_min = self.config.p_min
        nt = flux_templates.shape[1]

        # The likelihood and prior...
        pczt = p_c_z_t(flux, flux_err, flux_templates)
        L = pczt.likelihood

        # old prior code returns NoneType for prior if "flat" or "none"
        # just hard code the no prior case for now for backward compatibility
        if self.config.no_prior:  # pragma: no cover
            P = np.ones(L.shape)
        else:
            # set num templates to nt, which is hardcoding to "interp=0"
            # in BPZ, i.e. do not create any interpolated templates
            P = prior_function(z, mag_0, modeldict, nt)

        post = L * P
        # Right now we jave the joint PDF of p(z,template). Marginalize
        # over the templates to just get p(z)
        post_z = post.sum(axis=1)

        # Convolve with Gaussian kernel, if present
        if kernel is not None:  # pragma: no cover
            post_z = np.convolve(post_z, kernel, 1)

        # Find the mode
        zpos = np.argmax(post_z)
        zmode = self.zgrid[zpos]

        # Trim probabilities
        # below a certain threshold pct of p_max
        p_max = post_z.max()
        post_z[post_z < (p_max * p_min)] = 0

        # Normalize in the same way that BPZ does
        # But, only normalize if the elements don't sum to zero
        # if they are all zero, just leave p(z) as all zeros, as no templates
        # are a good fit.
        if not np.isclose(post_z.sum(), 0.0):
            post_z /= post_z.sum()

        # Find T_B, the highest probability template *at zmode*
        tmode = post[zpos, :]
        t_b = np.argmax(tmode)

        # compute TODDS, the fraction of probability of the "best" template
        # relative to the other templates
        tmarg = post.sum(axis=0)
        todds = tmarg[t_b] / np.sum(tmarg)

        return post_z, zmode, t_b, todds

    def _process_chunk(self, start, end, data, first):
        """
        Run BPZ on a chunk of data
        """
        # replace non-detects, traditional BPZ had nondet=99 and err = maglim
        
        # convert data format to numpy dictionary
        if tables_io.types.table_type(data) != 1:
            data = self._convert_table_format(data, "numpyDict")
        
        # put in that format here
        test_data = self._preprocess_magnitudes(data)
        m_0_col = self.config.bands.index(self.config.ref_band)

        nz = len(self.zgrid)
        ng = test_data['flux'].shape[0]

        # Set up Gauss kernel for extra smoothing, if needed
        if self.config.gauss_kernel > 0:  # pragma: no cover
            dz = self.config.dz
            x = np.arange(-3. * self.config.gauss_kernel,
                          3. * self.config.gauss_kernel + dz / 10., dz)
            kernel = np.exp(-(x / self.config.gauss_kernel)**2)
        else:
            kernel = None

        pdfs = np.zeros((ng, nz))
        zmode = np.zeros(ng)
        zmean = np.zeros(ng)
        tb = np.zeros(ng)
        todds = np.zeros(ng)
        flux_temps = self.flux_templates
        zgrid = self.zgrid
        # Loop over all ng galaxies!
        for i in range(ng):
            mag_0 = test_data['mag0'][i]
            flux = test_data['flux'][i]
            flux_err = test_data['flux_err'][i]
            pdfs[i], zmode[i], tb[i], todds[i] = self._estimate_pdf(flux_temps,
                                                                    kernel, flux,
                                                                    flux_err, mag_0,
                                                                    zgrid)
            zmean[i] = (zgrid * pdfs[i]).sum() / pdfs[i].sum()
        qp_dstn = qp.Ensemble(qp.interp, data=dict(xvals=self.zgrid, yvals=pdfs))
        qp_dstn.set_ancil(dict(zmode=zmode, zmean=zmean, tb=tb, todds=todds))
        self._do_chunk_output(qp_dstn, start, end, first, data=data)
