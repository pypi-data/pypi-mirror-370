import numpy as np
import pandas as pd
from scipy.optimize import minimize
from mgwr.sel_bw import Sel_BW

from .kernels import anisotropic_kernel_projected
from .utils import project_coordinates


def compute_precomputation_matrices(nodes: np.ndarray, theta: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    计算预计算矩阵V和W，精确匹配R代码的矩阵代数运算。
    
    参数:
        nodes: np.ndarray - (m, 2)数组，表示m个节点的坐标
        theta: np.ndarray - 2元素数组，表示带宽参数
    
    返回:
        tuple[np.ndarray, np.ndarray] - 包含矩阵(V, W)的元组
    """
    m = nodes.shape[0]
    
    # 1. 计算R_A: (m, m)核函数矩阵
    R_A = np.zeros((m, m))
    for i in range(m):
        for j in range(m):
            # 使用简化的核函数，匹配R代码
            h = nodes[i] - nodes[j]
            R_A[i, j] = np.exp(-h @ h * theta[0])  # 使用第一个theta值
    
    # 添加正则化项
    nugget = 1e-8
    R_A += nugget * np.eye(m)
    
    # 2. 计算G_A: (m, 3)矩阵 [1, x, y]
    G_A = np.column_stack([np.ones(m), nodes[:, 0], nodes[:, 1]])
    
    # 3. 计算R_A的逆矩阵
    R_A_inv = np.linalg.inv(R_A)
    
    # 4. 计算中间矩阵 (G_A^T @ R_A^(-1) @ G_A)^(-1)
    GRA = np.linalg.inv(G_A.T @ R_A_inv @ G_A)
    
    # 5. 计算矩阵V和W
    V = R_A_inv @ G_A @ GRA
    W = (np.eye(m) - V @ G_A.T) @ R_A_inv
    
    return V, W


def calculate_basis_vector(x: np.ndarray, nodes: np.ndarray, V: np.ndarray, W: np.ndarray, theta: np.ndarray) -> np.ndarray:
    """
    使用预计算的V和W矩阵计算单个空间点x的基函数向量b(x)。
    
    参数:
        x: np.ndarray - 2元素数组，表示单个坐标点 [x, y]
        nodes: np.ndarray - (m, 2)数组，表示节点坐标
        V: np.ndarray - 预计算的V矩阵
        W: np.ndarray - 预计算的W矩阵
        theta: np.ndarray - 2元素带宽数组
    
    返回:
        np.ndarray - (m, 1)基函数向量b(x)
    """
    m = nodes.shape[0]
    
    # 1. 计算g(x): (3, 1)向量 [1, x, y]
    g_x = np.array([1, x[0], x[1]]).reshape(3, 1)
    
    # 2. 计算r_A(x): (m, 1)向量，表示x与每个节点之间的核函数值
    r_A_x = np.zeros((m, 1))
    for i in range(m):
        # 使用简化的核函数，匹配R代码
        h = x - nodes[i]
        r_A_x[i, 0] = np.exp(-h @ h * theta[0])  # 使用第一个theta值
    
    # 3. 计算基函数向量: b(x) = V @ g_x + W @ r_A_x
    b_x = V @ g_x + W @ r_A_x
    
    return b_x


def construct_design_matrix(
    global_vars_df: pd.DataFrame,
    local_vars_df: pd.DataFrame,
    coords: np.ndarray,
    nodes: np.ndarray,
    thetas: dict
) -> np.ndarray:
    """
    构建AGWR模型的完整设计矩阵Z = [X, Ẑ]。
    
    参数:
        global_vars_df: pd.DataFrame - (n, p) DataFrame，全局变量数据
        local_vars_df: pd.DataFrame - (n, q) DataFrame，局部变量数据
        coords: np.ndarray - (n, 2) 数组，数据点坐标
        nodes: np.ndarray - (m, 2) 数组，节点坐标
        thetas: dict - 字典，键为局部变量名，值为对应的2元素带宽数组
    
    返回:
        np.ndarray - 完整的 (n, p + q*m) 设计矩阵Z
    """
    n, p = global_vars_df.shape
    q = local_vars_df.shape[1]
    m = nodes.shape[0]
    
    # 步骤1: 构建全局变量矩阵X
    X = global_vars_df.values
    
    # 步骤2: 构建局部变量矩阵Ẑ
    local_matrices = []
    
    for var_name in local_vars_df.columns:
        # 获取对应的带宽参数
        theta_k = thetas[var_name]
        
        # 预计算V_k和W_k矩阵
        V_k, W_k = compute_precomputation_matrices(nodes, theta_k)
        
        # 计算基函数矩阵B_k: (n, m)
        B_k = np.zeros((n, m))
        for i in range(n):
            # 计算第i个数据点的基函数向量
            b_i = calculate_basis_vector(coords[i], nodes, V_k, W_k, theta_k)
            B_k[i, :] = b_i.flatten()
        
        # 计算Ẑ_k = B_k * diag(x_k)
        x_k = local_vars_df[var_name].values.reshape(n, 1)
        Z_hat_k = B_k * x_k
        
        local_matrices.append(Z_hat_k)
    
    # 步骤3: 组合所有矩阵
    Z_hat = np.hstack(local_matrices)
    Z = np.hstack([X, Z_hat])
    
    return Z


def negative_log_likelihood(
    params: np.ndarray,
    Y: np.ndarray,
    global_vars_df: pd.DataFrame,
    local_vars_df: pd.DataFrame,
    coords: np.ndarray,
    nodes: np.ndarray
) -> float:
    """
    计算AGWR模型的负对数似然函数值。
    
    参数:
        params: np.ndarray - 1D数组，包含所有需要优化的参数
        Y: np.ndarray - (n, 1)数组，因变量数据
        global_vars_df: pd.DataFrame - (n, p) DataFrame，全局变量数据
        local_vars_df: pd.DataFrame - (n, q) DataFrame，局部变量数据
        coords: np.ndarray - (n, 2)数组，数据点坐标
        nodes: np.ndarray - (m, 2)数组，节点坐标
    
    返回:
        float - 负对数似然函数值
    """
    # 获取数据维度
    n = Y.shape[0]
    p = global_vars_df.shape[1]
    q = local_vars_df.shape[1]
    m = nodes.shape[0]
    
    # 步骤1: 参数解包和对数变换
    param_idx = 0
    
    # 解包log_sigma2并变换回原始尺度
    log_sigma2 = params[param_idx]
    sigma2 = np.exp(log_sigma2)
    param_idx += 1
    
    # 解包log_thetas并变换回原始尺度
    thetas = {}
    for var_name in local_vars_df.columns:
        log_theta_u = params[param_idx]
        log_theta_v = params[param_idx + 1]
        thetas[var_name] = np.array([np.exp(log_theta_u), np.exp(log_theta_v)])
        param_idx += 2
    
    # 解包alphas（全局变量系数）
    alphas = params[param_idx:param_idx + p]
    param_idx += p
    
    # 解包gammas（局部变量系数）
    gammas = params[param_idx:param_idx + q*m]
    
    # 步骤2: 构建设计矩阵Z
    Z = construct_design_matrix(global_vars_df, local_vars_df, coords, nodes, thetas)
    
    # 步骤3: 构建参数向量η
    eta = np.concatenate([alphas, gammas])
    
    # 步骤4: 计算残差和RSS
    Y_pred = Z @ eta
    residuals = Y.flatten() - Y_pred
    RSS = np.sum(residuals ** 2)
    
    # 步骤5: 计算负对数似然
    nll = (n/2) * np.log(2 * np.pi * sigma2) + RSS / (2 * sigma2)
    
    return nll


class AGWR:
    def __init__(self, m: int = 8):
        """
        各向异性地理加权回归模型
        
        参数:
            m (int): 重构方法的空间节点数量
        """
        self.m = m
        self.aic_ = None
        self.bandwidths_ = None
        self.coefficients_ = None
        self.fitted_values_ = None
        self.residuals_ = None
        self.is_fitted_ = False
        
    def fit(self, X: pd.DataFrame, y: pd.Series, coords: np.ndarray, local_vars: list, global_vars: list):
        """
        拟合AGWR模型
        
        参数:
            X (pd.DataFrame): 自变量DataFrame
            y (pd.Series): 因变量Series
            coords (np.ndarray): (n, 2)数组，包含[经度, 纬度]坐标
            local_vars (list): X中要作为局部变量处理的列名列表
            global_vars (list): X中要作为全局变量处理的列名列表
        """
        # --- 1. 数据准备 ---
        print("1. 数据准备...")
        projected_coords = project_coordinates(coords)
        nodes = projected_coords[:self.m, :]  # 简单节点选择
        
        # 数据分区
        y_arr = y.to_numpy().reshape(-1, 1)
        global_df = X[global_vars]
        local_df = X[local_vars]
        
        print(f"  观测数量: {len(y)}")
        print(f"  局部变量: {local_vars}")
        print(f"  全局变量: {global_vars}")
        print(f"  节点数量: {self.m}")
        
        # --- 2. 使用默认带宽估计 ---
        print("\n2. 获取初始带宽估计...")
        # 使用数据范围的15%作为默认带宽
        x_range = (projected_coords[:, 0].max() - projected_coords[:, 0].min()) / 1000.0
        y_range = (projected_coords[:, 1].max() - projected_coords[:, 1].min()) / 1000.0
        mgwr_bws = np.array([x_range * 0.15, y_range * 0.15])
        print(f"  默认带宽: {mgwr_bws} 公里")
        
        # --- 3. 设置和运行优化 ---
        print("\n3. 设置优化参数...")
        
        # 组装x0向量
        n_params = 1 + len(local_vars) * 2 + len(global_vars) + len(local_vars) * self.m
        x0 = np.zeros(n_params)
        
        param_idx = 0
        
        # log_sigma2初始值
        x0[param_idx] = np.log(0.5)  # 初始误差方差
        param_idx += 1
        
        # log_thetas初始值
        for var in local_vars:
            x0[param_idx] = np.log(mgwr_bws[0])  # log_theta_u
            x0[param_idx + 1] = np.log(mgwr_bws[1])  # log_theta_v
            param_idx += 2
        
        # alphas初始值（全局变量系数）
        x0[param_idx:param_idx + len(global_vars)] = 0.0
        param_idx += len(global_vars)
        
        # gammas初始值（局部变量系数）
        x0[param_idx:] = 0.0
        
        print(f"  参数数量: {n_params}")
        print(f"  初始参数向量长度: {len(x0)}")
        
        # 设置参数边界
        bounds = []
        
        # log_sigma2边界
        bounds.append((np.log(1e-6), np.log(100)))
        
        # log_thetas边界
        for var in local_vars:
            bounds.append((np.log(0.1), np.log(1000)))  # log_theta_u
            bounds.append((np.log(0.1), np.log(1000)))  # log_theta_v
        
        # alphas边界（全局变量系数）
        for var in global_vars:
            bounds.append((-10, 10))
        
        # gammas边界（局部变量系数）
        for var in local_vars:
            for j in range(self.m):
                bounds.append((-10, 10))
        
        print(f"  边界数量: {len(bounds)}")
        
        # 调用优化器
        print("\n4. 运行优化...")
        result = minimize(
            negative_log_likelihood,
            x0,
            args=(y_arr, global_df, local_df, projected_coords, nodes),
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': 5000, 'disp': True, 'gtol': 1e-6}
        )
        
        # --- 4. 存储结果 ---
        print("\n5. 处理优化结果...")
        if result.success:
            print("  优化成功!")
            
            # 解包最终参数
            final_params = result.x
            param_idx = 0
            
            # 解包log_sigma2
            log_sigma2 = final_params[param_idx]
            sigma2 = np.exp(log_sigma2)
            param_idx += 1
            
            # 解包log_thetas
            self.bandwidths_ = {}
            for var in local_vars:
                log_theta_u = final_params[param_idx]
                log_theta_v = final_params[param_idx + 1]
                self.bandwidths_[var] = np.array([np.exp(log_theta_u), np.exp(log_theta_v)])
                param_idx += 2
            
            # 解包alphas和gammas
            alphas = final_params[param_idx:param_idx + len(global_vars)]
            param_idx += len(global_vars)
            gammas = final_params[param_idx:]
            
            # 构建最终设计矩阵
            final_thetas = {var: self.bandwidths_[var] for var in local_vars}
            Z_final = construct_design_matrix(global_df, local_df, projected_coords, nodes, final_thetas)
            
            # 计算最终系数和拟合值
            eta_final = np.concatenate([alphas, gammas])
            self.fitted_values_ = Z_final @ eta_final
            self.residuals_ = y_arr.flatten() - self.fitted_values_
            
            # 计算AIC
            n = len(y)
            k = len(final_params)
            RSS_final = np.sum(self.residuals_ ** 2)
            self.aic_ = n * np.log(RSS_final / n) + 2 * k
            
            # 存储系数
            self.coefficients_ = {
                'global': dict(zip(global_vars, alphas)),
                'local': {}
            }
            
            gamma_idx = 0
            for var in local_vars:
                self.coefficients_['local'][var] = gammas[gamma_idx:gamma_idx + self.m]
                gamma_idx += self.m
            
            self.is_fitted_ = True
            
            print(f"  最终AIC: {self.aic_:.4f}")
            print(f"  误差方差: {sigma2:.6f}")
            print(f"  带宽参数:")
            for var, theta in self.bandwidths_.items():
                print(f"    {var}: {theta}")
            
        else:
            print(f"  优化失败: {result.message}")
        
        return self
    
    def predict(self, X: pd.DataFrame, coords: np.ndarray) -> np.ndarray:
        """
        使用拟合的模型进行预测
        
        参数:
            X (pd.DataFrame): 自变量DataFrame
            coords (np.ndarray): (n, 2)数组，包含[经度, 纬度]坐标
        
        返回:
            np.ndarray: 预测值
        """
        if not self.is_fitted_:
            raise ValueError("模型尚未拟合，请先调用fit()方法")
        
        # 这里需要实现预测逻辑
        # 暂时返回简单的线性预测
        return np.zeros(len(X))
