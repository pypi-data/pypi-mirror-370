'''
计算全息图 (CGH) 生成工具模块
================================

该模块提供用于生成计算全息图 (Computer-Generated Hologram, CGH) 的面向对象工具集.

模块结构
--------
核心类:
    - `CGH`      : CGH 生成器, 管理模式叠加与全息图计算. 
    - `HG`       : Hermite-Gaussian 模式表示类. 
    - `PM`       : 两个模式的线性组合 (加/减). 
    - `SLM`      : 空间光调制器 (Spatial Light Modulator, SLM) 参数与坐标网格定义. 
    - `CGHutils` : 常用模式分布与批量生成工具函数. 

尚未实现:
    - `LG`       : Laguerre-Gaussian 模式 (占位符, 暂不支持). 

基本使用流程
------------
1. 创建 CGH 实例, 指定光束腰参数：
       >>> cgh = CGH(sigma=100)
2. 添加一个或多个模式及其空间频率：
       >>> cgh.add_modes(HG(0, 1), nx_list=500, ny_list=0)
3. 计算并生成 CGH 图像：
       >>> cgh.cal()
4. 获取或保存结果：
       >>> img_array = cgh.result()
       >>> cgh.save('my_cgh.png')

依赖
----
- numpy
- scipy
- pillow (PIL)

'''

import numpy as np
from numpy import pi

from math import factorial

from scipy.special import hermite, laguerre
from scipy.interpolate import interp1d

from os import path
from PIL import Image

import importlib.resources as resources

__all__ = ['SLM', 'HG', 'LG', 'PM', 'CGH', 'CGHutils']



class SLM:
    device = 'HoloEye, PLUTO-2-NIR-011'

    pixel_size = 8
    resolution = (1920, 1080)
    
    x, y = np.meshgrid(
           np.arange(-resolution[0]/2, resolution[0]/2) * pixel_size,
          -np.arange(-resolution[1]/2, resolution[1]/2) * pixel_size)
    
    rho = x**2 + y**2

    norm_x = x / (resolution[0] * pixel_size)
    norm_y = y / (resolution[1] * pixel_size)



class _Mode:
    @staticmethod
    def check(inputs):
        if not isinstance(inputs, (HG, LG, PM)):
            raise ValueError('invalid mode')
        return inputs
    
    def __add__(self, other):
        return PM(self, other, '+')
    
    def __sub__(self, other):
        return PM(self, other, '-')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.order1}, {self.order2})'



class PM(_Mode):
    def __init__(self, mode1, mode2, pm):
        self.mode1 = _Mode.check(mode1)
        self.mode2 = _Mode.check(mode2)
        self.pm = pm
        self.norm = self.mode1.norm + self.mode2.norm

    def wave_function(self, sigma):
        wf1 = self.mode1.wave_function(sigma)
        wf2 = self.mode2.wave_function(sigma)
        if self.pm == '+':
            return (wf1 + wf2) / np.sqrt(self.norm)
        elif self.pm == '-':
            return (wf1 - wf2) / np.sqrt(self.norm)
        else:
            raise ValueError("invalid 'pm' option")

    def __repr__(self):
        return f'{self.mode1} {self.pm} {self.mode2}'



class HG(_Mode):
    def __init__(self, n, m):
        if all(isinstance(x, int) and x >= 0 for x in (n, m)):
            self.order1 = n
            self.order2 = m
            self.norm = 1
        else:
            raise ValueError('orders must be positive integers')


    def wave_function(self, sigma):
        w0 = 2*sigma
        n, m = self.order1, self.order2

        N = np.sqrt(2**(1-n-m) / (pi * factorial(m) * factorial(n))) / w0
        hx, hy= hermite(n)(2**.5 * SLM.x / w0), hermite(m)(2**.5 * SLM.y / w0)
        ca = N * hx * hy * np.exp(-SLM.rho/(w0**2))
        a, phi = np.abs(ca), np.angle(ca)

        return a * np.exp(1j * phi)



class LG(_Mode):
    def __init__(self):
        raise NotImplementedError('LG mode is not supported yet')



class CGH:
    def __init__(self, sigma):
        self.sigma = sigma
        self.mode_list, self.nx_list, self.ny_list = [], [], []
        self.cgh = None


    def _check_cgh(self):
        if not self.mode_list:
            raise RuntimeError('No modes added. Use add_modes() to add at least one mode.')
        if self.cgh is None:
            print('CGH not generated. Running cal() automatically...')
            self.cal()


    def add_modes(self, mode_list, nx_list, ny_list):
        mode_list = np.atleast_1d(mode_list)
        nx_list = np.atleast_1d(nx_list)
        ny_list = np.atleast_1d(ny_list)

        for mode in mode_list:
            _Mode.check(mode)

        if not (len(mode_list) == len(nx_list) == len(ny_list)):
            raise ValueError("mode_list, nx_list, and ny_list must have the same length")
        
        self.mode_list.extend(mode_list)
        self.nx_list.extend(nx_list)
        self.ny_list.extend(ny_list)


    @staticmethod
    def fx2(x):
        with resources.files('hduq.assets').joinpath('fx2.npy').open('rb') as f:
            _fx2 = interp1d(np.linspace(0, 1, 801), np.load(f))
        return _fx2(x)


    def cal(self):
        V = 0
        for i, mode in enumerate(self.mode_list):
            V = V + (mode.wave_function(self.sigma) * np.exp(2j*pi * (SLM.norm_x*self.nx_list[i] + SLM.norm_y*self.ny_list[i])))

        a = np.abs(V) / np.abs(V).max()
        phi = np.angle(V)

        _temp = self.fx2(a) * np.sin(phi)
        _temp = ((_temp - _temp.min()) / (_temp.max() - _temp.min())) * 255

        self.cgh = _temp.astype(np.uint8)
        self.img = Image.fromarray(self.cgh)


    def result(self):
        self._check_cgh()
        return self.cgh


    def show(self):
        self._check_cgh()
        self.img.show()


    def save(self, file, override=False):
        self._check_cgh()
        file = path.expanduser(file)
        if not path.exists(file) or override:
            self.img.save(file)
        else:
            raise FileExistsError(f'{file} already exists')




class CGHutils:
    @staticmethod
    def line(modes_num, x_scale=1, y_scale=1):
        nx = np.array([500] * modes_num).ravel() if modes_num != 1 else 500
        ny = np.linspace(-50, 50, modes_num) if modes_num != 1 else 0
        return np.array([nx * x_scale, ny * y_scale])


    @staticmethod
    def arc(modes_num, x_scale=1, y_scale=1):
        angle_rad = np.deg2rad(45)
        theta = np.linspace(-angle_rad/2, angle_rad/2, modes_num)
        radius = 500
        nx = radius * np.cos(theta)
        ny = radius * np.sin(theta) 
        return np.array([nx * x_scale, ny * y_scale])


    @staticmethod
    def hg_mat(max_n, max_m):
        modes = np.empty((max_n+1, max_m+1), dtype=object)
        for n in range(max_n):
            for m in range(max_m):
                modes[n, m] = HG(n, m)
        return modes


    @staticmethod
    def pm_mat(max_n, max_m):
        modes = [HG(n, m) for n in range(max_n+1) for m in range(max_m+1)]
        size = len(modes)
        pm_modes = np.empty((size, size), dtype=object)
        for i in range(size):
            for j in range(i, size):
                if i != j:
                    pm_modes[i, j] = modes[i] + modes[j]
                    pm_modes[j, i] = modes[i] - modes[j]
        return pm_modes


    @classmethod
    def preset_cgh(cls, *modes, sigma, dist, x_scale=1, y_scale=1):
        cgh = CGH(sigma)
        if dist == 'v_line':
            cgh.add_modes(modes, *cls.line(len(modes), x_scale, y_scale))
        elif dist == 'h_line':
            cgh.add_modes(modes, *cls.line(len(modes), x_scale, y_scale)[::-1, ...])
        elif dist == 'v_arc':
            cgh.add_modes(modes, *cls.arc(len(modes), x_scale, y_scale))
        elif dist == 'h_arc':
            cgh.add_modes(modes, *cls.arc(len(modes), x_scale, y_scale)[::-1, ...])

        cgh.cal()
        return cgh
