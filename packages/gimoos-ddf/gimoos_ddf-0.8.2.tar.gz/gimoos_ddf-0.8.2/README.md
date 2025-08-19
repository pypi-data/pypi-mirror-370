# Gimccs Driver Development

极墨思驱动开发框架

## 一、安装

`pip install gimoos_ddf`

## 二、使用

1. 创建驱动 `gimoos_ddf create <name> <type>`
   - **name**: 驱动名称，如 ***"my driver"***，名称中包含空格请使用英文引号包裹
   - **type**: 驱动类型，可以为 ***"水位感应, 遥控器, 灯, 投影仪, 电源时序器, 门感应, 媒体播放机, 摄像头, 按键, DVD机, 继电器, 窗帘, 人体感应, 温控, 功放, 电视"***
2. 上传驱动 `gimoos_ddf update <host>`
   - **host**: 驱动上传地址，如 "192.168.1.1:8000"
