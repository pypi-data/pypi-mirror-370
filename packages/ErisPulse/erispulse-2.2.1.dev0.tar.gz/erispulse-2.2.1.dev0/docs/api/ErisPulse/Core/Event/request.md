# `ErisPulse.Core.Event.request` 模块

<sup>更新时间: 2025-08-18 22:00:40</sup>

---

## 模块概述


ErisPulse 请求处理模块

提供基于装饰器的请求事件处理功能

<div class='admonition tip'><p class='admonition-title'>提示</p><p>1. 支持好友请求、群邀请等不同类型请求
2. 可以通过返回特定值来同意或拒绝请求</p></div>

---

## 类列表

### `class RequestHandler`

    RequestHandler 类提供相关功能。

    
#### 方法列表

##### `on_request(priority: int = 0)`

    通用请求事件装饰器

:param priority: 处理器优先级
:return: 装饰器函数

    ---
    
##### `remove_request_handler(handler: Callable)`

    取消注册通用请求事件处理器

:param handler: 要取消注册的处理器
:return: 是否成功取消注册

    ---
    
##### `on_friend_request(priority: int = 0)`

    好友请求事件装饰器

:param priority: 处理器优先级
:return: 装饰器函数

    ---
    
##### `remove_friend_request_handler(handler: Callable)`

    取消注册好友请求事件处理器

:param handler: 要取消注册的处理器
:return: 是否成功取消注册

    ---
    
##### `on_group_request(priority: int = 0)`

    群邀请请求事件装饰器

:param priority: 处理器优先级
:return: 装饰器函数

    ---
    
##### `remove_group_request_handler(handler: Callable)`

    取消注册群邀请请求事件处理器

:param handler: 要取消注册的处理器
:return: 是否成功取消注册

    ---
    
<sub>文档最后更新于 2025-08-18 22:00:40</sub>