# PID温度控制仿真系统

基于Python + PyQt6 + pyqtgraph的温度控制仿真教学软件。

## 功能特性

- **5种控制策略**：普通PID、单回路PID（抗饱和）、前馈+反馈、串级PID、串级+前馈
- **用户权限管理**：管理员/普通用户角色，权限分级
- **实时波形显示**：SV、PV、控制量u、干扰、误差曲线
- **历史数据查询与导出**：支持Excel格式导出
- **方波干扰模拟**：可配置振幅和持续时间
- **手动/自动模式切换**：无扰动切换

## 快速开始

### 环境要求
- Python 3.10+
- Windows 10/11

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行程序
```bash
python src/main.py
```

### 默认账号
| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 普通用户 | user | user123 |

## 项目结构

详见 `Folder Structure_v0.md` 和 `Plan_v0.md`。

## 打包发布

```bash
python build_exe.py
```

## 版本

v1.0 - 正式版
