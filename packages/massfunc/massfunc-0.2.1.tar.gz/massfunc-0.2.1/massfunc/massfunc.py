import numpy as np
from astropy import units as u
from scipy.interpolate import interp1d
from scipy.integrate import quad,quad_vec
from sympy import symbols,solve,Eq
from dataclasses import dataclass
from scipy.special import erfc


@dataclass
class CosmologySet:
    h: float = 0.674
    omegam: float = 0.315

    def __post_init__(self):
        self.omegab = 0.0224 * self.h**-2
        self.omegalam = 1 - self.omegam
        self.rhocrit = 2.775366e11 * self.h**2 * u.Msun / u.Mpc**3
        rhoc = self.rhocrit.value
        self.rhom = rhoc * self.omegam
        self.H0u = 100 * self.h * (u.km * u.s**-1 * u.Mpc**-1)
        self.mHu = 1.6726e-27 * u.kg                        # the mass of a hydrogen Unit: kg
        self.Y = 0.75                                       # the mass fraction of hydrogen
        self.nHu = self.rhocrit.to(u.kg/u.cm**3) * self.omegab * self.Y / self.mHu    # hydrogen density
        self.nH = self.nHu.value
        self.omegak = 0.0   
        self.omegar = 0.0

class Mass_func(CosmologySet):
    def __init__(self, ns=0.965, sigma8=0.811, h=0.674, omegam=0.315):
        super().__init__(h=h, omegam=omegam)
        self.n = ns
        self.sigma8 = sigma8
        self.m8 = 4.0 * np.pi * self.rhom / 3.0 * (8.0 / self.h) ** 3
        self.As = 1.0
        self.As = sigma8 ** 2 / self.sigma2(self.m8)
        self.sig2_interp_complete = False
        self.dsig2_interp_complete = False
    
    def sigma2_interpolation_set(self):
        m = np.logspace(0.0, 18.0, 1000)
        sig = np.log10(self.sigma2(m))
        self.sig_interp = interp1d(np.log10(m), sig, kind='cubic')
        self.sig2_interp_complete = True

    def sigma2_interpolation(self, M):
        if not self.sig2_interp_complete:
            self.sigma2_interpolation_set()
        logM = np.log10(M)
        ff = self.sig_interp(logM)
        return 10 ** ff

    def dsig2dm_interpolation_set(self):
        m = np.logspace(0.0, 18.0, 1000)
        dsig2dms = np.log10(-self.dsig2dm(m))
        self.dsig2dm_interp = interp1d(np.log10(m), dsig2dms, kind='cubic')
        self.dsig2_interp_complete = True
    
    def dsig2dm_interpolation(self, M):
        if not self.dsig2_interp_complete:
            self.dsig2dm_interpolation_set()
        logM = np.log10(M)
        ff = self.dsig2dm_interp(logM)
        return -10 ** ff
    
    def Ez(self, z):
        return np.sqrt(self.omegar * (1.0 + z) ** 4.0 + self.omegam * (1.0 + z) ** 3 + self.omegak * (1.0 + z) ** 2 + self.omegalam)

    def omegam_z(self, z):
        return self.omegam * (1.0 + z) ** 3 / self.Ez(z) ** 2
    
    def omegalam_z(self, z):
        return self.omegalam / self.Ez(z) ** 2

    def Dz(self, z):
        def gz(z):
            return 2.5 * self.omegam_z(z) / (self.omegam_z(z) ** (4. / 7.) - self.omegalam_z(z) + (1. + self.omegam_z(z) / 2.) * (1. + self.omegalam_z(z) / 70.))
        return gz(z) / (gz(0.0) * (1.0 + z))

    def Tk(self, k):
        q = k / (self.omegam * self.h ** 2)
        para = (1. + 3.89 * q + (16.1 * q) ** 2 + (5.46 * q) ** 3 + (6.71 * q) ** 4) ** -0.25
        return np.log(1. + 2.34 * q) / (2.34 * q) * para
  
    def Pk(self, k, z):
        return self.As * k ** self.n * (self.Tk(k)) ** 2 * self.Dz(z) ** 2
    
    # The Fourier transform of a top-hat window function with radius R in real space
    def wkr(self, M, k):
        r = (3.0 * M / (4.0 * np.pi * self.rhom)) ** (1.0 / 3.0)
        x = r * k
        return 3.0 * (np.sin(x) - x * np.cos(x)) * (x)**-3

    def sigma2dlnk(self, lnk, M):
        def sigma2dk(M, k):
            return k ** 2 * self.Pk(k, z=0.0) * self.wkr(M, k) * self.wkr(M, k) / (2.0 * np.pi ** 2)
        k = np.exp(lnk)
        return k * sigma2dk(M, k)

    # def sigma2(self, M):
    #     kslice = np.logspace(-5.0, 8.0, 12)
    #     res = np.zeros_like(M)
    #     for i in range(0, len(kslice) - 1):
    #         res += quad(self.sigma2dlnk, np.log(kslice[i]), np.log(kslice[i + 1]),epsrel=1e-6, args=(M,))[0]
    #     return res

    def sigma2(self, M):
        return quad_vec(self.sigma2dlnk, np.log(1e-5), np.log(1e8), args=(M,),epsrel=1e-6,limit=1000)[0]
    
    def dsig2dmdk(self, lnk, M):
        k = np.exp(lnk)
        r = (3.0 * M / (4.0 * np.pi * self.rhom)) ** (1. / 3.)
        drdm = 1 / (4. * np.pi * self.rhom) * (3.0 * M / (4.0 * np.pi * self.rhom)) ** (-2.0 / 3.0)
        x = k * r
        dwdx = 3.0 * k * (x ** -2 * (np.sin(x)) - 3.0 * x ** -4 * (np.sin(x) - x * np.cos(x)))
        return dwdx * drdm * k ** 3 * self.Pk(k, 0) * self.wkr(M, k) * 2.0 / (2.0 * np.pi ** 2)

    # integrate and get dsig/dM
    # def dsig2dm(self, M):
    #     kslice = np.logspace(-5., 8., 12)
    #     res = np.zeros_like(M)
    #     for i in range(0, len(kslice) - 1):
    #         res += quad(self.dsig2dmdk, np.log(kslice[i]), np.log(kslice[i + 1]),epsrel=1e-6,args=(M,))[0]
    #     return res
    
    def dsig2dm(self, M):
        return quad_vec(self.dsig2dmdk, np.log(1e-5), np.log(1e8), args=(M,),epsrel=1e-6,limit=1000)[0]

    def deltac(self, z):
        return 1.686 / self.Dz(z)
    
    def dndmps(self, m, z):
        sigm = np.sqrt(self.sigma2_interpolation(m))
        dsig_dm = abs(self.dsig2dm_interpolation(m)) / (2.0 * sigm)
        return np.sqrt(2.0 / np.pi) * self.rhom / m * self.deltac(z) / sigm * dsig_dm * np.exp(-self.deltac(z) ** 2 / (2 * sigm ** 2))

    # S-T
    def dndmst(self, M, z):
        A = .353
        a = .707
        p = .175
        sigm = np.sqrt(self.sigma2_interpolation(M))
        nu = (self.deltac(z) / sigm) ** 2
        nup = a * nu
        dsigdm = self.dsig2dm_interpolation(M) / (2.0 * sigm)
        dndm = -np.sqrt(2.0 / np.pi) * self.rhom * (M * sigm) ** -1 * dsigdm
        fsst = A * (1 + nup ** -p) * nup ** (1.0 / 2.0) * np.exp(-nup / 2.0)
        return dndm * fsst

    def delta_L(self, deltar,z):
        return (1.68647 - 1.35 / (1 + deltar) ** (2 / 3) - 1.12431 / (1 + deltar) ** (1 / 2) + 0.78785 / (1 + deltar) ** (0.58661)) / self.Dz(z)

    def dndmeps(self, M, Mr, deltar,z):
        delta_L = (1.68647 - 1.35 / (1 + deltar) ** (2 / 3) - 1.12431 / (1 + deltar) ** (1 / 2) + 0.78785 / (1 + deltar) ** (0.58661)) / self.Dz(z)
        sig1 = self.sigma2_interpolation(M) - self.sigma2_interpolation(Mr)
        del1 = self.deltac(z) - delta_L
        return self.rhom * (1 + deltar) / M / np.sqrt(2 * np.pi) * abs(self.dsig2dm_interpolation(M)) * del1 / sig1 ** (3 / 2) * np.exp(-del1 ** 2 / (2 * sig1))
    
class Collapse_fraction(Mass_func):

    def __init__(self, ns=0.965, sigma8=0.811, h=0.674, omegam=0.315): 
        super().__init__(ns=ns, sigma8=sigma8, h=h, omegam=omegam)
        
    # The df/dz interpolation
    # The virial mass
    def virialm(self, Tvir, mu, z):
        d = self.omegam_z(z) - 1.0
        deltac = 18.0 * np.pi**2 + 82.0 * d - 39.0 * d**2
        right = 1.98e4 * (mu / 0.6) * (self.omegam / self.omegam_z(z) * deltac / (18. * np.pi**2))**(1. / 3.) * (1 + z) / 10
        m = symbols('m')
        eq = Eq(right * (m / (1e8 * 1 / self.h))**(2.0 / 3.0) - Tvir, 0)
        solution = solve(eq, m)
        python_float = float(solution[0])
        numpy_float = np.float64(python_float)
        return numpy_float

    def Delta_cc(self, z):
        d = self.omegam_z(z) - 1.0
        return 18 * np.pi**2 + 82.0 * d - 39.0 * d**2
    
    def M_vir(self, mu, Tvir, z):
        a1 = (self.omegam / self.omegam_z(z) * self.Delta_cc(z) / (18 * np.pi**2))**(-1.0 / 3.0)
        a2 = a1 * (mu / 0.6)**(-1.0) * ((1.0 + z) / 10)**(-1.0) / 1.98e4 * Tvir
        return a2**(3.0 / 2.0) * 1e8 / self.h

    def fcolldiff(self, lnM, z):
        M = np.exp(lnM)
        diff = M * self.dndmst(M, z)
        return diff * M

    def fcoll(self, minmass, maxmass, z):
        resp, w = quad(self.fcolldiff, np.log(minmass), np.log(maxmass), args=(z,))
        return resp / self.rhom

    def dfcolldz(self, minmass, maxmass, z):
        zs = z - z * .01
        zl = z + z * .01
        diffz = (self.fcoll(minmass, maxmass, zl) - self.fcoll(minmass, maxmass, zs)) / (zl - zs)
        return diffz
    
    def deltaL_delta(delf,delta,z):
        deltaL_delta=1.68647-1.35/(1.0+delta)**(2./3.)-1.12431/(1.0+delta)**(5e-1)+0.78785/(1.0+delta)**(0.58661)
        return deltaL_delta/delf.Dz(z)

    def fcoll_EPS(self,z,delta_V,ss1):
        x=(self.deltac(z)-self.deltaL_delta(delta_V,z))/ss1 
        return erfc(x)

    # Change static method to instance method
    def M_Jeans(self, z, T, mu):
        return 3.96e4 * (T / mu)**(3. / 2.) * (self.omegam * self.h**2)**(-1. / 2.) * (1 + z)**(-3. / 2.)

    def M_J(self, z):
        return 5.73e3*(self.omegam*self.h**2/0.15)**(-1/2) * (self.omegab*self.h**2/0.0224)**(-3/5) * ((1+z)/10)**(3/2)

class SFRD(Collapse_fraction):

    def __init__(self, ns=0.965, sigma8=0.811, h=0.674, omegam=0.315): 
        super().__init__(ns=ns, sigma8=sigma8, h=h, omegam=omegam)

    def fstar(self, M):
        f0 = .14
        ylo = .46
        yhi = .82
        Mp = 10**12.3  # M_sun solmass
        fup = 2 * f0
        fdown = ((M / Mp)**-ylo + (M / Mp)**yhi)
        return fup / fdown

    def fduty(self, M):
        al = 1.5
        Mc = 6e7
        return (1 + (2.**(al / 3.) - 1) * (M / Mc)**-al)**(-3. / al)

    def dMdt(self, M, z):
        return 24.1 * (M / (1e12))**1.094 * (1 + 1.75 * z) * np.sqrt(self.omegam * (1 + z)**3 + self.omegalam)  # solmass/yr
    
    def rhosfrdiff(self, lnM, z):
        M = np.exp(lnM)
        diff = self.fstar(M) * self.omegab / self.omegam * self.dMdt(M, z) * self.dndmst(M, z) * self.fduty(M)
        return M * diff
    
    def rhosfr(self, T1, T2, z):
        Mmin = self.virialm(T1, 0.61, z)
        Mmax = self.virialm(T2, 0.61, z)
        ans, var = quad(self.rhosfrdiff, np.log(Mmin), np.log(Mmax), args=(z,))
        return ans

# set_cosmology(h0=0.7, omegam_0=0.3, omegab_0=0.046)
if __name__ == "__main__":
    a = SFRD(ns=1, sigma8=0.9)
    print(a.rhosfr(1e4, 1e8, 0.0))