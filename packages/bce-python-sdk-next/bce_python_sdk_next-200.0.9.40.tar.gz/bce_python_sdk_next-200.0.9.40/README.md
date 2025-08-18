# bce-python-sdk三方版

## 简介

bce-python-sdk三方版，适配官方尚未支持的某些产品API，例如AIHC

## 使用说明

1. AIHC 二次开发说明参考文档 [baidubce/services/aihc/README.md](baidubce/services/aihc/README.md)

2. AIHC 示例代码参考文档 [sample/aihc/README.md](sample/aihc/README.md)

## 快速开始（AIHC）

- 配置认证与端点：编辑 `sample/aihc/aihc_sample_conf.py`，将 `HOST`、`AK`、`SK` 替换为你的值

- 运行示例（推荐，模块方式，优先使用本地源码）：

```
python -m sample.aihc.aihc_model_sample
```

- 其他示例入口：

```
python -m sample.aihc.aihc_dataset_sample
python -m sample.aihc.aihc_job_sample
python -m sample.aihc.aihc_service_sample
python -m sample.aihc.aihc_devinstance_sample
python -m sample.aihc.aihc_base_sample
```

- 备用运行方式（显式指定本地源码优先级）：

```
export PYTHONPATH=$(pwd)
python sample/aihc/aihc_model_sample.py
```

- 可编辑安装（可选）：

```
pip install -e .
```

- 常见问题：
  - ImportError: cannot import name 'AihcClient' → 通常命中了环境中的旧版 `baidubce` 包。请使用“模块方式运行”或设置 `PYTHONPATH=$(pwd)`；或卸载旧版包后重试：

```
pip uninstall baidubce
```

## 安装

- 本地安装

```
python setup.py install
```

- pip安装

```
pip install bce-python-sdk-next
```
