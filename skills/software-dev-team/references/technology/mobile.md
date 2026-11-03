# 手机 App 技术与交付

先确认 Android/iOS/平板、目标系统、是否必须上架、相机/蓝牙/定位等设备 SDK、离线、通知/后台、用户设备和开发者账户。不能从“做个 App”推断全部平台条件。

| 工作与目标 | 候选技术 | 工具和取舍 |
|---|---|---|
| 同时覆盖 Android/iOS，统一业务 UI | Flutter / Dart | Flutter SDK、Android Studio/Xcode；核查插件和原生扩展覆盖，Dart 随 SDK 配套 |
| 已有 React/TypeScript 团队 | React Native + Expo | Expo SDK 与原生模块配套；区分 Expo Go、开发构建与商店制品 |
| Android 专用或深度平台能力 | Kotlin + Jetpack Compose | Android Studio、Gradle、Android SDK；设备 API 与系统版本范围 |
| iOS 专用及系统体验 | Swift + SwiftUI，必要时 UIKit | Xcode、签名、Apple SDK；目标系统和开发/发布资源 |

跨平台能复用业务与部分界面，不意味着所有原生能力零成本。要求高性能时先明确滚动、启动、图像/音视频处理或网络瓶颈，再决定原生模块或 Rust 核心是否有价值。

分层区分视图、应用状态、数据访问、设备适配与服务端。处理弱网、超时、重试、缓存、重复提交、同步冲突、权限拒绝及前后台生命周期；秘密不能放进客户端当作可保密凭据。

测试选择 Flutter 的单元/widget/integration_test、Android 原生测试、iOS XCTest/XCUITest，或跨栈 Appium。浏览器的手机模拟视口不能当真实原生 App 验收。实际签名制品应在目标模拟器/真机验证关键链，上架结果单独报告。

官方依据：[Flutter](https://docs.flutter.dev/)、[Flutter 测试](https://docs.flutter.dev/testing/overview)、[Expo](https://docs.expo.dev/get-started/create-a-project/)、[Android Compose](https://developer.android.com/compose)、[SwiftUI](https://developer.apple.com/swiftui/)、[Appium](https://appium.io/docs/en/latest/)。
