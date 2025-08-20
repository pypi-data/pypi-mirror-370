from astropy.constants import c,sigma_T
from scipy.interpolate import interp1d
import massfunc as mf 
from scipy.integrate import quad
import numpy as np
import astropy.units as u
from dataclasses import dataclass
import matplotlib.pyplot as plt
import os

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
        self.X = 0.75                                       # the mass fraction of hydrogen
        self.nHu = self.rhocrit.to(u.kg/u.cm**3) * self.omegab * self.X / self.mHu    # hydrogen density
        self.nH = self.nHu.value
        self.omegak = 0.0   
        self.omegar = 0.0

class OpticalDepth(CosmologySet):

    def __init__(self,z: np.ndarray, ionf: np.ndarray, ns=0.965, sigma8=0.811, h=0.674, omegam=0.315):
        super().__init__(h=h, omegam=omegam)
        self.ionf_interp_init = False
        self.z = np.array(z)
        self.ionf = np.array(ionf)
        self.cosmo = mf.SFRD(ns=ns, sigma8=sigma8, h=h, omegam=omegam)
        self.nH = self.cosmo.nHu

    def IonFraction_Init(self,z: np.ndarray, ionf: np.ndarray):
        z = np.array(z)
        ionf = np.array(ionf)
        self.ionf_interp = interp1d(z, ionf)
        self.ionf_interp_init = True

    def IonFraction(self, z: np.ndarray):
        if self.ionf_interp_init == False:
            self.IonFraction_Init(self.z, self.ionf)
        z = np.array(z)
        z1 = z[z < self.z[0]]
        zm = z[(z >= self.z[0]) & (z <= self.z[-1])]
        z2 = z[z > self.z[-1]]
        z1_out = np.ones(len(z1)) if len(z1) > 0 else np.array([])
        z2_out = np.zeros(len(z2)) if len(z2) > 0 else np.array([])
        return np.concatenate([z1_out,self.ionf_interp(zm),z2_out])

    def OpticalDepth_diff(self, z: float) -> float:
        Y = 0.25
        X = 0.75
        eta = 2 if z <=4 else 1
        Hz = self.cosmo.Ez(z) * self.cosmo.H0u
        x_HII = self.IonFraction(z)
        return (c*(1+z)**2 /Hz * x_HII * self.nH* sigma_T*(1+eta*Y/(4*X))).to(u.dimensionless_unscaled).value
    
    def OpticalDepth(self, z: float) -> float:
        """
        Add the Integrate grid for better result
        """
        zlist = np.linspace(0, z, 12)
        ans = 0
        for i in range(len(zlist)-1):
            ans += quad(self.OpticalDepth_diff, zlist[i], zlist[i+1], epsrel=1e-7, limit=200)[0]
        return ans

class XXIPowerSpectrum(CosmologySet):
    def __init__(self,h=0.674, omegam=0.315):
        super().__init__(h=h, omegam=omegam)

    def XXI_Field(self,z: float, deltaR: np.ndarray, ionf: np.ndarray):
        xHI = 1-ionf
        bracket1 = self.omegab*self.h**2/0.023
        bracket2 = (0.15/(self.omegam*self.h**2) *(1+z)/10)**(1/2)
        bracket3 = (1+deltaR)*xHI
        return 27*bracket1*bracket2*bracket3

    def PowerSpectrum(self, field: np.ndarray,
                    box_length: int, num_bins: int = 50) -> np.ndarray: 
        
        DIM = field.shape[0]
        field_ffted = np.fft.rfftn(field, norm="forward")
        Power_Field = np.abs(field_ffted)**2 * box_length**3

        sampling_interval = box_length / DIM
        kx = 2 * np.pi * np.fft.fftfreq(DIM, d=sampling_interval)
        ky = 2 * np.pi * np.fft.fftfreq(DIM, d=sampling_interval)
        kz = 2 * np.pi * np.fft.rfftfreq(DIM, d=sampling_interval)

        Kx, Ky, Kz = np.meshgrid(kx, ky, kz, indexing='ij')
        K_magnitude = np.sqrt(Kx**2 + Ky**2 + Kz**2)

        k_min = np.min(K_magnitude[K_magnitude > 0])
        k_max = np.max(K_magnitude)

        k_bins = np.logspace(np.log10(k_min), np.log10(k_max), num_bins + 1)
        k_flat = K_magnitude.flatten()
        power_flat = Power_Field.flatten()

        #分bins统计
        n_modes, _ = np.histogram(k_flat, bins=k_bins)
        power_sum, _ = np.histogram(k_flat, bins=k_bins, weights=power_flat)

        P_k = np.divide(power_sum, n_modes,out=np.zeros_like(power_sum),where=(n_modes != 0))
        k_sum, _ = np.histogram(k_flat, bins=k_bins, weights=k_flat)
        k_ave = np.divide(k_sum, n_modes,out=np.zeros_like(k_sum),where=(n_modes != 0))

        del k_flat, power_flat, K_magnitude, Power_Field

        delta_sq_k = k_ave**3 * P_k / (2 * np.pi**2)
        valid_indices = np.where(n_modes > 0)

        P_k_valid = P_k[valid_indices]
        k_ave_valid = k_ave[valid_indices]
        n_modes_valid = n_modes[valid_indices]

        #  计算无量纲功率谱和误差棒
        delta_sq_k = k_ave_valid**3 * P_k_valid / (2 * np.pi**2)
        error_P_k = P_k_valid / np.sqrt(n_modes_valid)
        error_delta_sq_k = k_ave_valid**3 * error_P_k / (2 * np.pi**2)
    
        return k_ave_valid, delta_sq_k, error_delta_sq_k

    def PowerSpectrumPlot(self, field: np.ndarray,
                    box_length: int, num_bins: int = 50,
                    label: str = 'Power Spectrum' ,figLabel: str = '21cm') -> None:

        k_ave_valid, delta_sq_k, error_delta_sq_k = self.PowerSpectrum(field, box_length, num_bins)

        plt.figure(figsize=(10, 8),dpi=300)
        plt.errorbar(k_ave_valid, delta_sq_k, yerr=error_delta_sq_k,
                    marker='o',         
                    linestyle='-',      
                    capsize=3,          
                    color='royalblue',
                    ecolor='lightgray', 
                    label=f'{figLabel}')

        plt.xscale('log')
        plt.yscale('log')

        plt.xlabel(r'$k \quad [\mathrm{Mpc}^{-1}]$', fontsize=14)
        plt.ylabel(r'$\Delta^2_{21}(k) \quad [mK^2]$', fontsize=14)
        plt.title(f'{label}', fontsize=16)
        # plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.legend(fontsize=12)
        os.makedirs('figure_deltaTb', exist_ok=True)
        plt.savefig(f'figure_deltaTb/PowerSpectrum_{label}.png', dpi=300)       


    def XXIFandXXIP(self,z: float, deltaR: np.ndarray, ionf: np.ndarray, box_length: int,
                    label: str = '21cm Field', percentage_number: float = 99,
                    ):
        DIM = deltaR.shape[0]
        XXI_field = self.XXI_Field(z, deltaR, ionf)
        # get the 21cm signal field slice and the ionization field slice
        xxi_slice = XXI_field[:,:,int(DIM/2)]
        ion_slice = ionf[:,:,int(DIM/2)]

        # 创建坐标网格
        n1, n2 = xxi_slice.shape
        x = np.linspace(0, box_length, n1)
        y = np.linspace(0, box_length, n2)
        XX, YY = np.meshgrid(x, y)
        # --- 2. 创建 1x2 子图 ---

        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 6), dpi=150)
        fig.suptitle(f'{label}', fontsize=16)

        # 为电离场设置颜色范围 (0到1之间)
        v_ion = np.linspace(0, 1, 21, endpoint=True)

        # 为21cm信号场设置颜色范围
        cmin_xxi = xxi_slice.min()
        cmax_xxi = np.percentile(xxi_slice, percentage_number)
        v_xxi = np.linspace(cmin_xxi, cmax_xxi, 21, endpoint=True)


        # --- 3. 绘制左边的子图 (电离场) ---
        ax1 = axes[0]
        CS1 = ax1.contourf(XX, YY, ion_slice, v_ion, cmap=plt.cm.Blues_r, extend='max')
        ax1.set_title(f'Ionization Field', fontsize=14)
        ax1.set_xlabel('Mpc')
        ax1.set_ylabel('Mpc')
        ax1.set_aspect('equal', 'box') # 保持 x,y 轴比例一致

        # 为左图添加颜色条
        cbar1 = fig.colorbar(CS1, ax=ax1, fraction=0.046, pad=0.04, format='%.2f')
        cbar1.set_label(r'Ionization Fraction', fontsize=12)


        # --- 4. 绘制右边的子图 (21cm信号场) ---
        ax2 = axes[1]
        CS2 = ax2.contourf(XX, YY, xxi_slice, v_xxi, cmap=plt.cm.jet, extend='max')
        ax2.set_title(f'21cm Signal Field', fontsize=14)
        ax2.set_xlabel('Mpc')
        ax2.set_ylabel('') # 隐藏右图的y轴标签，避免重复
        ax2.set_yticklabels([]) # 隐藏y轴刻度标签
        ax2.set_aspect('equal', 'box') # 保持 x,y 轴比例一致

        # 为右图添加颜色条
        cbar2 = fig.colorbar(CS2, ax=ax2, fraction=0.046, pad=0.04, format='%.2f')
        cbar2.set_label(r'$\delta T_b~[\mathrm{mK}]$', fontsize=12)


        # --- 5. 调整布局并显示 ---
        # 自动调整子图间距，防止标题和标签重叠
        plt.tight_layout(pad=1.5)
        os.makedirs('figure_deltaTb', exist_ok=True)
        plt.savefig(f'figure_deltaTb/ionization_and_21cm_z={z},percentile={percentage_number}.png')

