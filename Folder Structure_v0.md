# PID温度控制仿真系统 - 项目目录结构

## 根目录结构

```
G:\SimControl/                          # 项目根目录
│
├── src/                                 # 源代码目录
│   ├── main.py                          # 程序入口：初始化→登录→主界面
│   ├── config.py                        # 全局配置（路径、参数、权限常量）
│   ├── exception.py                     # 全局异常捕获与处理
│   │
│   ├── control/                         # 控制算法模块
│   │   ├── __init__.py
│   │   ├── pid_controller.py            # PID控制器（位置式、增量式、抗饱和）
│   │   ├── cascade_control.py           # 串级控制器（外环+内环）
│   │   ├── feedforward_control.py       # 前馈控制器（静态+动态补偿）
│   │   └── control_strategy.py          # 控制策略管理器（5种策略切换）
│   │
│   ├── model/                           # 系统模型模块
│   │   ├── __init__.py
│   │   ├── two_inertia_model.py         # 双惯性环节串联模型
│   │   ├── feedback_model.py            # 反馈环节模型（传感器模拟）
│   │   └── disturbance.py               # 干扰信号发生器（方波）
│   │
│   ├── ui/                              # 用户界面模块
│   │   ├── __init__.py
│   │   ├── main_window.py               # 主界面（菜单、控制面板、波形显示）
│   │   ├── plot_widget.py               # 实时波形显示组件（pyqtgraph）
│   │   ├── history_window.py            # 历史数据查询窗口
│   │   ├── user_manager_ui.py           # 用户管理界面（管理员专用）
│   │   ├── change_pwd_ui.py             # 修改密码对话框
│   │   └── widgets.py                   # 自定义控件（PID参数面板等）
│   │
│   ├── user/                            # 用户管理模块
│   │   ├── __init__.py
│   │   ├── user_manager.py              # 用户管理逻辑（增删改查）
│   │   ├── login_window.py              # 登录界面
│   │   ├── user_data.py                 # 用户数据存储（JSON加密）
│   │   └── permission.py                # 权限校验（角色、权限常量）
│   │
│   └── utils/                           # 工具类模块
│       ├── __init__.py
│       ├── data_logger.py               # 数据记录器（历史数据存储）
│       ├── excel_exporter.py            # Excel导出功能
│       ├── validator.py                 # 参数校验工具
│       ├── time_format.py               # 时间格式化工具
│       └── exception_handler.py         # 异常处理工具类
│
├── data/                                # 数据目录（运行时自动生成）
│   ├── history_data/                    # 历史仿真数据（JSON格式）
│   ├── users/                           # 用户数据
│   │   └── users.json                   # 用户账号密码（加密存储）
│   └── logs/                            # 日志文件
│       └── error.log                    # 错误日志
│
├── tests/                               # 测试代码
│   ├── test_pid.py                      # PID控制器测试
│   ├── test_model.py                    # 被控对象模型测试
│   ├── test_disturbance.py              # 干扰信号测试
│   ├── test_ui.py                       # UI组件测试
│   └── test_user.py                     # 用户管理测试
│
├── assets/                              # 静态资源
│   ├── icons/                           # 图标文件（.ico, .png）
│   ├── images/                          # 图片资源
│   └── style.qss                        # Qt样式表
│
├── dist/                                # 打包输出目录（自动生成）
│   └── PID温度控制仿真系统.exe          # 可执行文件（单文件）
│
├── build/                               # 打包临时目录（自动生成）
│
├── Plan_v0.md                           # 软件开发计划（本文件）
├── Folder Structure_v0.md               # 项目目录结构说明
├── README.md                            # 项目简介与使用说明
├── plan.md                              # 开发过程记录
├── requirements.txt                     # Python依赖清单
│
├── build_exe.py                         # 一键打包脚本（PyInstaller）
├── PID仿真系统.spec                     # PyInstaller配置文件
├── 打包说明.md                          # 打包发布详细指南
│
└── .vscode/                             # VS Code配置
    └── settings.json                    # 编辑器设置
```

## 模块详细说明

### 1. 控制算法模块 (src/control/)

| 文件 | 职责 | 关键类/函数 |
|------|------|------------|
| pid_controller.py | PID控制器实现 | `PIDController`（带抗饱和）、`SimplePIDController`（纯PID） |
| cascade_control.py | 串级控制实现 | `CascadeController`（双回路）、`CascadeWithFeedforward`（串级+前馈） |
| feedforward_control.py | 前馈控制实现 | `FeedforwardController`（干扰补偿）、`FeedforwardFeedbackController`（复合控制） |
| control_strategy.py | 策略管理 | `ControlStrategyManager`（5种策略切换、手动/自动模式） |

### 2. 系统模型模块 (src/model/)

| 文件 | 职责 | 关键类 |
|------|------|--------|
| two_inertia_model.py | 被控对象 | `TwoInertiaModel`（双惯性串联）、`FirstOrderLag`（一阶惯性） |
| feedback_model.py | 传感器模型 | `FeedbackModel`（一阶低通滤波）、`SensorWithNoise`（带噪声） |
| disturbance.py | 干扰信号 | `SquareWaveDisturbance`（方波干扰）、`DisturbanceGenerator`（干扰管理） |

### 3. 用户界面模块 (src/ui/)

| 文件 | 职责 | 关键类 |
|------|------|--------|
| main_window.py | 主界面 | `MainWindow`（菜单、工具栏、状态栏、仿真控制） |
| plot_widget.py | 实时波形 | `PlotWidget`（pyqtgraph实时绘图）、`HistoryPlotWidget`（历史曲线） |
| history_window.py | 历史数据 | `HistoryWindow`（数据查询、导出、缩放平移） |
| user_manager_ui.py | 用户管理 | `UserManagerWindow`（增删改用户、权限设置） |
| change_pwd_ui.py | 修改密码 | `ChangePasswordDialog`（密码修改对话框） |
| widgets.py | 自定义控件 | `PIDParamGroup`（PID参数面板）、`StatusBar`（状态栏） |

### 4. 用户管理模块 (src/user/)

| 文件 | 职责 | 关键类/函数 |
|------|------|------------|
| user_manager.py | 用户管理逻辑 | `UserManager`（用户CRUD、密码加密） |
| login_window.py | 登录界面 | `LoginWindow`（登录验证、记住密码） |
| user_data.py | 数据持久化 | `UserDataManager`（JSON读写、加密解密） |
| permission.py | 权限系统 | `CurrentUser`（当前用户上下文）、`Permissions`（权限常量） |

### 5. 工具类模块 (src/utils/)

| 文件 | 职责 | 关键类/函数 |
|------|------|------------|
| data_logger.py | 数据记录 | `DataLogger`（仿真数据记录、历史数据查询） |
| excel_exporter.py | Excel导出 | `export_to_excel()`（数据导出Excel） |
| validator.py | 参数校验 | `validate_pid_params()`、参数范围检查 |
| time_format.py | 时间处理 | `get_current_time_str()`（格式化时间字符串） |
| exception_handler.py | 异常工具 | `show_error_dialog()`、异常日志记录 |

## 关键文件说明

### 入口文件
- **src/main.py**: 程序入口，初始化顺序：
  1. 安装全局异常处理器
  2. 创建数据目录
  3. 显示登录窗口
  4. 验证通过后启动主界面

### 配置文件
- **src/config.py**: 全局配置
  - `TempConfig`: 温度控制参数（范围、默认值）
  - `ControlStrategy`: 控制策略枚举
  - `UserRole`/`Permissions`: 角色权限常量
  - `Paths`: 路径配置（自适应开发和打包环境）

### 异常处理
- **src/exception.py**: 全局异常处理
  - 自定义异常类（`CalculationException`、`ParameterException`）
  - 全局异常钩子（`install_exception_handler`）
  - 对话框函数（`show_error_dialog`、`show_info_dialog`）

## 数据流示意图

### 自动模式仿真流程
```
┌─────────────┐    SV     ┌─────────────────┐    u     ┌──────────────┐    y+干扰   ┌──────────────┐
│  设定值输入  │ ─────────→ │  控制策略管理器  │ ───────→ │   被控对象    │ ─────────→ │   反馈环节   │
│  (用户输入)  │            │  (PID/串级/前馈) │          │ (双惯性环节)  │            │  (传感器模拟)  │
└─────────────┘            └─────────────────┘          └──────────────┘            └──────────────┘
                                    ↑                                                      │
                                    └────────────────── PV ←───────────────────────────────┘
```

### 手动模式仿真流程
```
┌─────────────┐    手动值   ┌─────────────────┐    u     ┌──────────────┐    y+干扰   ┌──────────────┐
│  手动输出框  │ ─────────→ │  开环控制器     │ ───────→ │   被控对象    │ ─────────→ │   反馈环节   │
│  (用户输入)  │            │  (直接输出设定值)│          │ (双惯性环节)  │            │  (传感器模拟)  │
└─────────────┘            └─────────────────┘          └──────────────┘            └──────────────┘
```

## 开发与打包

### 开发运行
```bash
cd G:\SimControl
G:\pytorch\python.exe src\main.py
```

### 打包发布
```bash
cd G:\SimControl
G:\pytorch\python.exe build_exe.py
```

打包输出：`dist/PID温度控制仿真系统.exe`

---

**文档版本**: v1.0
**最后更新**: 2024年
**维护者**: SimControl Team
