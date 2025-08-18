import numpy as np
import massfunc as mf
import astropy.units as u
from scipy.interpolate import interp1d
from scipy.integrate import quad,quad_vec
from scipy.optimize import fsolve,root_scalar
from . import PowerSpectrum as ps
import os 

cosmo = mf.SFRD()
m_H = (cosmo.mHu.to(u.M_sun)).value #M_sun
omega_b = cosmo.omegab
omega_m = cosmo.omegam
rhom = cosmo.rhom

class Barrier:

    def __init__(self,fesc=0.2, qion=7000.0,z_v=10.0,nrec=3,xi=10.0,A2byA1=0.1,kMpc_trans=420,alpha=2.0,beta=0.0):
        self.A2byA1,self.kMpc_trans,self.alpha,self.beta = A2byA1,kMpc_trans,alpha,beta
        self.fesc = fesc
        self.qion = qion
        self.z = z_v
        self.nrec = nrec
        self.xi = xi
        self.M_min = cosmo.M_vir(0.61,1e4,self.z)  # Minimum halo mass for ionization
        self.M_Jz = cosmo.M_J(self.z)
        self.powspec = ps.MassFunctions(A2byA1=A2byA1,kMpc_trans=kMpc_trans,alpha=alpha,beta=beta)
        self.deltaR_interp = np.concatenate((np.linspace(-0.999,2,1000), np.linspace(2.001,25,1000)))
        self.ratio = self.Modify_Ratio()  # Ratio for partial ionization
    
    def Nion_Pure(self,Mv,deltaR):
        def Nion_Pure_diff(m,Mv,deltaR):
            fstar = cosmo.fstar(m)
            return fstar*m*self.dndmeps(m,Mv,deltaR,self.z)/ m_H * omega_b / omega_m
        mslice = np.logspace(np.log10(self.M_min), np.log10(Mv), 12)
        ans = np.zeros_like(deltaR)
        for i in range(len(mslice)-1):
            ans += quad_vec(Nion_Pure_diff, mslice[i], mslice[i+1],args=(Mv,deltaR), epsrel=1e-6)[0]
        return ans
    
    def Nxi_Pure(self,Mv,deltaR):
        def Nxi_Pure_diff(m,Mv,deltaR):
            return m*self.dndmeps(m,Mv,deltaR,self.z)/ m_H * omega_b / omega_m
        mslice = np.logspace(np.log10(self.M_Jz), np.log10(self.M_min), 12)
        ans = np.zeros_like(deltaR)
        for i in range(len(mslice)-1):
            ans += quad_vec(Nxi_Pure_diff, mslice[i], mslice[i+1],args=(Mv,deltaR), epsrel=1e-6)[0]
        return ans

    # Interpolation for Nion
    def Nion_interp(self, Mv,deltaR):
        try:
            Nion_arr = np.load(f'.Nion_Interp_init/NionAtz{self.z:.2f}/Nion_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        except FileNotFoundError:
            os.makedirs(f'.Nion_Interp_init/NionAtz{self.z:.2f}', exist_ok=True)
            nion_pure = self.Nion_Pure(Mv, self.deltaR_interp)
            np.save(f'.Nion_Interp_init/NionAtz{self.z:.2f}/Nion_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy', nion_pure)
            Nion_arr = np.load(f'.Nion_Interp_init/NionAtz{self.z:.2f}/Nion_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        self.Nion_interp_Mv = interp1d(self.deltaR_interp, Nion_arr, kind='cubic')
        return self.Nion_interp_Mv(deltaR) * self.fesc * self.qion 

    # Interpolation for N_xi
    def N_xi_interp(self, Mv, deltaR):
        try:
            Nxi_arr = np.load(f'.Nxi_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        except FileNotFoundError:
            os.makedirs(f'.Nxi_Interp_init/NxiAtz{self.z:.2f}', exist_ok=True)
            nxi_pure = self.Nxi_Pure(Mv, self.deltaR_interp)
            np.save(f'.Nxi_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy', nxi_pure)
            Nxi_arr = np.load(f'.Nxi_Interp_init/NxiAtz{self.z:.2f}/Nxi_arr_Mv_{Mv:.3f}at_z={self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        self.Nxi_interp_Mv = interp1d(self.deltaR_interp, Nxi_arr, kind='cubic')
        return self.Nxi_interp_Mv(deltaR) * self.xi 

    #patch
    def Nion_ST(self):
        def Nion_ST_diff(m):
            fstar = cosmo.fstar(m)
            return (1 / m_H * fstar * omega_b / omega_m * m * self.powspec.dndmst(m, self.z))
        mslice = np.logspace(np.log10(self.M_min), np.log10(cosmo.M_vir(0.61,1e8,self.z)), 100)
        ans = 0
        for i in range(len(mslice)-1):
            ans += quad(Nion_ST_diff, mslice[i], mslice[i+1], epsrel=1e-7)[0]
        return ans

    def Nion_PS(self):
        def Nion_PS_diff(m):
            fstar = cosmo.fstar(m)
            return (1 / m_H * fstar * omega_b / omega_m * m * self.powspec.dndmps(m, self.z))
        mslice = np.logspace(np.log10(self.M_min), np.log10(cosmo.M_vir(0.61,1e8,self.z)), 100)
        ans = 0
        for i in range(len(mslice)-1):
            ans += quad(Nion_PS_diff, mslice[i], mslice[i+1], epsrel=1e-7)[0]
        return ans
 
    def Modify_Ratio(self):
        try:
            ratio = np.load(f'.ratio_init/ratio_at_z{self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy')
        except FileNotFoundError:
            os.makedirs('.ratio_init', exist_ok=True)
            ratio = self.Nion_ST() / self.Nion_PS()
            np.save(f'.ratio_init/ratio_at_z{self.z:.2f}_A{self.A2byA1}_k{self.kMpc_trans}_alpha{self.alpha}_beta{self.beta}.npy', ratio)
        return ratio

    def delta_L(self, deltar):
        return (1.68647 - 1.35 / (1 + deltar) ** (2 / 3) - 1.12431 / (1 + deltar) ** (1 / 2) + 0.78785 / (1 + deltar) ** (0.58661)) / cosmo.Dz(self.z)
    
    def dndmeps(self,M,Mr,deltar,z):
        deltaL = self.delta_L(deltar)
        sig1 = self.powspec.sigma2_interp(M) - self.powspec.sigma2_interp(Mr)
        del1 = cosmo.deltac(z) - deltaL
        return cosmo.rhom * (1 + deltar) / M / np.sqrt(2 * np.pi) * abs(self.powspec.dsigma2_dm_interp(M)) * del1 / sig1 ** (3 / 2) * np.exp(-del1 ** 2 / (2 * sig1))

    def Nion_diff(self,m,Mv,deltaR):
        fstar = cosmo.fstar(m)
        return self.fesc*self.qion/m_H *fstar* omega_b/omega_m *m*self.dndmeps(m,Mv,deltaR,self.z)

    def Nion(self,Mv,delta_R):
        return quad_vec(self.Nion_diff, self.M_min, Mv, args=(Mv,delta_R),epsrel=1e-5)[0]

    def N_H(self,deltaR):
        return 1/m_H * omega_b/omega_m * rhom *(1+deltaR) 

    def N_xi_diff(self,M,Mv,deltaR):
        return self.xi/m_H * omega_b/omega_m *M*self.dndmeps(M,Mv,deltaR,self.z)
    
    def N_xi(self,Mv,delta_R):
        return quad_vec(self.N_xi_diff, self.M_Jz,self.M_min, args=(Mv,delta_R),epsrel=1e-5)[0]
    
    def Calcul_deltaVM_EQ(self,deltaR,Mv):
        return self.ratio *self.Nion(Mv,deltaR) - (1+self.nrec)*self.N_H(deltaR)

    def Calcul_deltaVM(self,Mv):
        result = root_scalar(self.Calcul_deltaVM_EQ, args=(Mv,), bracket=[-0.99, 1.5], method='bisect')
        return result.root
    
    def Calcul_deltaVM_Minihalo_EQ(self,deltaR,Mv):
        return self.ratio *self.Nion(Mv,deltaR) - (1+self.nrec)*self.N_H(deltaR) - self.ratio * self.N_xi(Mv,deltaR)

    def Calcul_deltaVM_Minihalo(self,Mv):
        result = root_scalar(self.Calcul_deltaVM_Minihalo_EQ, args=(Mv,), bracket=[-0.99, 1.67], method='bisect')
        return result.root
    