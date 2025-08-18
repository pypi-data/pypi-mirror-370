import numpy as np
from scipy.special import hermite, factorial, j1
from scipy.integrate import quad



class _PSF:
    def __init__(self, sigma=1, bounds=(None, None), pixel_size=1):
        self.sigma = sigma
        self.pixel_size = pixel_size
        self.bounds = (
            bounds[0] if bounds[0] is not None else np.round(-6 * sigma / pixel_size), 
            bounds[1] if bounds[1] is not None else np.round( 6 * sigma / pixel_size)
        )
        self.pixels = int(self.bounds[1] - self.bounds[0])

    def pdf(self, x, s=0):
        return np.abs(self.psf(x, s))**2
    

    def prob(self, s=0):
        pdf = lambda x: self.pdf(x, s)
        p = []
        for j in np.arange(self.bounds[0], self.bounds[1] + 1, 1):
            p.append(quad(pdf, self.pixel_size*j - self.pixel_size/2, self.pixel_size*j + self.pixel_size/2, limit=1000)[0])
        return np.array(p)


    def gen(self, s=0, photons=1):
        p = self.prob(s)
        outcomes = np.random.choice(len(p), photons, p=p/p.sum())
        return np.histogram(outcomes, bins=self.pixels, range=(0, self.pixels))[0]


    def fit(self, data):
        raise(NotImplementedError)



class SincPSF(_PSF):
    def psf(self, x, s=0):
        return (self.sigma*np.pi)**-0.5 * np.sinc((x-s) / (self.sigma*np.pi))



class JincPSF(_PSF):
    @classmethod
    def jinc(cls, x):
        is_scalar = np.isscalar(x)
        x = np.asarray(x, dtype=np.float64)
        result = np.empty_like(x)

        mask = x != 0
        result[~mask] = 1.0
        result[mask] = (2 * j1(x[mask])) / x[mask]

        return result.item() if is_scalar else result


    def psf(self, x, s=0):
        return ((3*np.pi) / (32*self.sigma))**0.5 * self.jinc((x-s) / self.sigma)



class GausPSF(_PSF):
    def psf(self, x, s=0):
        return (2*np.pi*self.sigma**2)**-0.25 * np.exp(-((x-s)**2) / (4*self.sigma**2))




class _Modes:
    def __init__(self, q, sigma=1):
        self.q = q
        self.sigma = sigma

        self._c_term = (2*np.pi*self.sigma**2)**-0.25
        self._exp_term = lambda x: np.exp(-x**2 / (4*self.sigma**2))



class HG(_Modes):
    def __init__(self, q, sigma=1):
        if q % 1 != 0 or q < 0:
            raise ValueError('For HG modes, q must be a natural number.')
        super().__init__(q, sigma)

        if self.q == 0:
            self._term1 = 1
            self._term2 = 1
        else:
            self._term1 = (2**self.q * factorial(self.q))**-0.5
            self._H = hermite(self.q)


    def wave_function(self, x):
        _x = x / (2**0.5 * self.sigma)
        if self.q != 0:
            self._term2 = 2*_x if self.q == 1 else self._H(_x)
        return self._c_term * self._term1 * self._term2 * self._exp_term(x)



class PM(_Modes):
    def __init__(self, q, sigma=1):
        if q not in (-1, 1):
            raise ValueError('Fpr PM modes, q must -1 or 1.')
        super().__init__(q, sigma)


    def wave_function(self, x):
        self._term = (1 + self.q * x / self.sigma) * 2**-0.5
        return self._c_term * self._term * self._exp_term(x)




def Born(s, modes: _Modes, psf: _PSF):
    result = []
    for _s in np.atleast_1d(s):
        fun = lambda x: modes.wave_function(x) * psf.psf(x, _s) 
        result.append(np.abs(quad(fun, -np.inf, np.inf)[0])**2)
    return np.array(result)




def FisherInfo(s, modes: _Modes, psf: _PSF, ds=1e-8):
    p1 = Born(s+ds, modes, psf)
    p2 = Born(s-ds, modes, psf)
    dp = p1 - p2
    dv = dp/(2*ds)
    return dv**2 / p1
