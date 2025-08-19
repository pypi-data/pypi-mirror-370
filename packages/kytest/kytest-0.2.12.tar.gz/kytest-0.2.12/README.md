# 介绍

[Gitee](https://gitee.com/bluepang2021/kytest_project)

Android/IOS/HarmonyOS NEXT/Web/API automation testing framework based on pytest.

> 基于pytest的安卓/IOS/HarmonyOS NEXT/Web/API平台自动化测试框架。

## 特点

* 提供丰富的断言
* 支持生成随机测试数据
* 提供强大的`数据驱动`，支持json、yaml
* 集成`allure`, 支持HTML格式的测试报告
* 集成`requests`/`playwright`/`facebook-wda`/`uiautomator2`/`hmdriver2`
* 支持多种执行模式（单设备、多设备并发执行全部用例、多设备并发轮询执行用例）
* 支持本地设备执行、开源云平台Sonic的远程设备执行



## 三方依赖

* [测试报告：Allure](https://github.com/allure-framework/allure2)
    * 依赖：java8及以上版本
    * 安装方式：
        * macos：brew install allure
        * windows（powershell）：scoop install allure
        * 其它方式：下载zip包解压到本地，然后配置环境变量即可
* [拾取元素：weditor](https://github.com/alibaba/web-editor)
    * 安装方式：安装kytest后自动安装
* [查看安卓设备id：adb](https://formulae.brew.sh/cask/android-platform-tools)
    * 安装方式：
        * macos：brew install android-platform-tools
        * windows（powershell）：scoop install android-platform-tools
        * 其它方式：下载zip包解压到本地，然后配置环境变量即可
* [查看IOS设备id：sib](https://github.com/SonicCloudOrg/sonic-ios-bridge/releases/tag/v1.3.20)
    * 安装方式：直接放在本地任何地方，在调用远程设备时候把sib的路径传入即可
* [IOS端代理：WebDriverAgent](https://github.com/appium/WebDriverAgent)
    * 安装方式：使用xcode编译后安装至手机

## Install

```shell
> pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ktest
```

## 🔬 Demo

[demo](/demo) 提供了丰富实例，帮你快速了解ktest的用法。

