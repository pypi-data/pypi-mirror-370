## [1.1.71] - 2025-08-21

### 更新

* 根据数据流3.0组件API调整更新模型定义
* 数据流3.0异步启动默认为带启停启动，同步固定为不带启停启动


## [1.1.70] - 2025-08-19

### 新增

* 消息中心推送增加抄送用户、用户组参数


## [1.1.69] - 2025-08-12

### 新增

* 消息中心推送接受发送成功规则参数


## [1.1.68] - 2025-07-29

### 更新

* DeepModel元素insert_df和update_df接受chunksize=None
* DeepModel元素insert_df和update_df组织的bulk语句优化
* 修复DataFrame.replace会引发类型推断导致的bug


## [1.1.67] - 2025-07-22

### 新增

* 财务模型元素查询支持指定透视成员列表
* 凭证模型数据更新接受指定头行操作类型

### 更新

* 兼容维度load_dataframe依据共享成员列分数据时共享成员列非bool列的处理


## [1.1.66] - 2025-07-10

### 更新

* 修复连接器连接信息密码超过16位时的aes解密逻辑


## [1.1.65] - 2025-07-09

### 更新

* 修正deepmodel元素试图set client引发的问题


## [1.1.64] - 2025-07-08

### 更新

* 更新连接器元素获取连接信息的接口和密码处理逻辑
* TaskUtil的api实例化延迟至TaskUtil实例化过程中


## [1.1.63] - 2025-07-01

### 更新

* 工作流完成任务实例方法增加附件列表
* 财务模型和DeepModel批量操作支持批次前后alert


## [1.1.62] - 2025-06-12

### 更新

* 工作流完成任务实例方法增加提供动作类型参数


## [1.1.61] - 2025-06-10

### 新增

* 财务模型元素实例化支持定制数据来源类型

### 更新

* deepmodel query_df无论有无数据都在列信息上保持一致性


## [1.1.59] - 2025-06-05

### 更新

* 更新numpy依赖版本


## [1.1.58] - 2025-06-05

### 更新

* 兼容pydantic 2.0


## [1.1.57] - 2025-05-22

### 新增

* 工作流完成任务实例方法增加完成参数
* 财务模型支持mdx_execution_with_code

### 更新

* 兼容deepmodel组件特殊版本的版本号可能以非数字结尾的情况


## [1.1.56] - 2025-04-27

### 新增

* 财务模型支持complement_save_unpivot


## [1.1.55] - 2025-04-25

### 新增
* DeepModel支持update_df
* 财务模型支持complement_save

### 变更

* DeepModel事务内设置globals不生效问题修正
* DeepModel兼容线上线下模式的json类型数据的处理，保证insert_df和query_df的读写格式一致性


## [1.1.54] - 2025-03-27

### 变更

* 根据DeepModel组件API调整更新模型定义


## [1.1.53] - 2025-02-25

### 新增

* 封装数据流3.0组件元素

### 变更

* 依赖的三方库版本升级

## [1.1.52] - 2025-01-07

### 变更

* pymysql依赖版本升级至1.1.1, aiomysql依赖版本升级至0.2.0

## [1.1.51] - 2024-12-20

### 变更

* DeepModel query_df修正返回空dataframe时frame_desc未处理的问题

## [1.1.50] - 2024-12-19

### 变更

* DeepModel query_df修正不提供shape时会返回空dataframe的问题

## [1.1.49] - 2024-11-21

### 变更

* 凭证组件元素table对象增加逻辑表数据库方言信息

## [1.1.48] - 2024-11-19

### 变更

* 维度元素兼容1.0中1.2已不存在的字段处理

## [1.1.47] - 2024-11-14

### 变更

* AccountAPI增加统一header用于绕过token校验

## [1.1.46] - 2024-11-05

### 变更

* 修复update_from_dataframe在有chunksize时读取where条件错误的bug

### 新增

* DeepModel对象查询返回增加声明信息

## [1.1.45] - 2024-10-29

### 变更

* 因漏洞修复更新aiohttp版本至3.9.0

## [1.1.44] - 2024-10-21

### 变更

* DeepModel query_df处理std::decimal类型列的cast使用float作为dtype

## [1.1.43] - 2024-10-17

### 变更

* DeepModel query_df处理Bool的cast不使用pd.BooleanDtype()

### 新增

* DeepModel start_transaction支持flatten

## [1.1.42] - 2024-09-19

### 新增

* 维度1.2 API 封装多维实体维度配置表查询和增量保存接口

## [1.1.41] - 2024-08-26

### 变更

* DeepModel get_object方法改为执行object查询语句
* DeepModel 查询和执行方法在kwargs的key缺省时自动补充None值

## [1.1.40] - 2024-07-23

### 变更

* DeepModel insert_df不排除外部对象链接

## [1.1.39] - 2024-07-16

### 新增

* 用户中心api封装用户组详情修改接口

## [1.1.38] - 2024-06-21

### 新增

* DeepModel增加获取查询语句接口

### 变更

* 无

### 文档

* 无

## [1.1.37] - 2024-06-14

### 新增

* DeepModel兼容外部库的直连

### 变更

* 无

### 文档

* 无

## [1.1.36] - 2024-06-05

### 新增

* 无

### 变更

* pg类数据表quote_char更新

### 文档

* 无


## [1.1.35] - 2024-05-28

### 变更

* pyscript中初始化redis client时的密码增加quota

### 文档

* 修复部分文档显示错误/重复的问题


## [1.1.34] - 2024-04-23

### 新增

* DeepModel增加批量插入pg底表方法

### 变更

* 财务模型元素save方法支持保存备注
* 财务模型元素save方法增加数据保存权鉴模式参数


## [1.1.33] - 2024-04-16

### 新增

* 封装消息中心

### 变更

* 无


## [1.1.32] - 2024-04-02

### 新增

* DeepModel提供设置globals方法
* DeepModel开放直连参数

### 变更

* DeepModel execute方法返回DML结果
* 支持配置多节点Eureka地址


## [1.1.31] - 2024-03-26

### 新增

* DeepUX支持作为图结构数据源

### 变更

* DeepModel修正查询返回结构字段顺序与语句不一致问题


## [1.1.30] - 2024-03-05

### 新增

* 无

### 变更

* PythonScript线下模式获取运行结果完善错误提示


## [1.1.29] - 2024-02-27

### 新增

* 无

### 变更

* 凭证元素save方法headMainId生成规则改为生成uuid


## [1.1.28] - 2024-02-20

### 新增

* DeepModel元素增加objects属性
* 服务发现的缓存增加轮询和随机策略

### 变更

* 凭证元素save方法文档更新
* 维度元素save方法DimMember兼容1.0与1.1&1.2的字段差异


## [1.1.27] - 2024-01-30

### 新增

* DeepModel元素insert_df支持upsert句式

### 变更

* DeepModel元素query_df结果增加符合列类型的cast
* 维度1.1&1.2元素使用的全量和增量保存接口更新，与前端使用的保持一致


## [1.1.26] - 2023-12-26

### 新增

* 凭证模型元素提供update方法

### 变更

* 无

## [1.1.25] - 2023-12-19

### 新增

* 财务模型元素提供delete_with_mdx方法

### 变更

* 财务模型元素delete方法提供是否使用MDX脚本实现的flag
* DeepModel序列化排除日期和UUID类型转string
* 财务模型元素delete, save, save_unpivot方法增加callback入参

## [1.1.24] - 2023-12-12

### 新增

* 无

### 变更

* 财务模型元素delete方法使用MDX脚本实现

## [1.1.23] - 2023-11-16

### 新增

* 财务模型元素新增封装权限状态upsert更新接口

### 变更

* 修正postgresql类数据表copy_rows为自增列赋默认值的问题

## [1.1.22] - 2023-11-02

### 新增

* 合并流程api封装

### 变更

* 凭证组件元素接口响应success=False时报错
* 维度元素封装修改成员父级功能

## [1.1.21] - 2023-10-26

### 变更

* 更新KingBase数据表quote char


## [1.1.20] - 2023-10-17

### 新增

* 添加DeepModel KingBase数据表
* 维度元素封装sync_data方法

### 变更

* 财务模型query方法增加对ignore列的处理


## [1.1.19] - 2023-10-10

### 变更

* 修正凭证元素save的头行df自带index时的请求体组织问题


## [1.1.18] - 2023-09-19

### 变更

* 修正DeepModel元素批量插入自链接对象时未排除计算link的问题


## [1.1.17] - 2023-09-12

### 新增

* 维度1.2支持多维度实体配置参数

### 变更

* 修正维度1.1 1.2版本增量编辑响应的数据类型


## [1.1.16] - 2023-09-05

### 新增

* Deep Connector封装获取连接信息方法

### 变更

* 维度修正共享成员维度保存的问题


## [1.1.15] - 2023-08-29

### 变更

* DeepModel 部分bug修复
* 维度修正共享成员维度保存的问题
* 优化redislock的renew lock逻辑


## [1.1.14] - 2023-08-15

### 变更

* 维度涉及ud字段的model统一扩充至60个ud
* 维度1.2 /refactor/dimension/info/save接口请求响应model更新


## [1.1.13] - 2023-08-08

### 变更

* DeepModel 部分bug修复
* pyscript redislock 延迟初始化
* 凭证元素接口字段修改 `type -> _type`（breaking）


## [1.1.12] - 2023-07-27

### 新增
* 维度同步至DeepModel对象

### 变更

* DeepModel取消元素初始化逻辑（同步组件变更）


## [1.1.11] - 2023-07-18

### 新增
* 添加DeepModel数据表


## [1.1.10] - 2023-07-13

### 新增
* DeepModel insert_df增加对multi link的支持

### 变更
* DeepModel本地执行时使用API
* 维度元素扩充DimensionMemberBean的ud数量至60
* 凭证元素已知问题修正

## [1.1.9] - 2023-07-04

### 新增
* 新增DeepModel元素
* 新增凭证元素

## [1.1.8] - 2023-06-29

### 变更
* deepux支持返回字段描述


## [1.1.7] - 2023-06-20

### 变更
* 兼容deepchart原BaseField的name成员可以被访问的逻辑
* 修复api/base中错误访问root属性的bug


## [1.1.6] - 2023-06-13

### 新增
* 支持nacos

### 变更

* 修复oracle/dameng数据表查询字段大小写不一致的问题
* dataframe中set类型的索引器改为list类型 [@李杨](https://e.gitee.com/proinnova/members/trend/ryan_li1384)
* 优化DataframeSQLConvertor的性能 [@李杨](https://e.gitee.com/proinnova/members/trend/ryan_li1384)
* 修复多线程情况下future_property的死锁问题
* eureka相关代码重构
* 统一数据表获取方式为``get_table_class``，支持服务名作为参数


## [1.1.5] - 2023-06-01

### 变更

* 将dbkits的table_cache纳入Cache Manager管理
* 去除db库内对build_api的cache_async装饰

## [1.1.4] - 2023-05-30

### 新增

* 维度1.2新增/refactor/dimension/object/sync-data接口

### 变更

* 修正试图将Oracle自增列置为null的默认逻辑

## [1.1.3] - 2023-05-11

### 变更

* 支持mysql标准以外SQL的字符串转义
* 修复 `bizmodel.set_approval_ex` 固定了审批流数据表为Mysql的问题

## [1.1.2] - 2023-05-09

### 新增

* 增加对账引擎对账集、数据集元素 [@陈文雍](https://e.gitee.com/proinnova/members/trend/calvinstk)
* 工作流新增封装批量启动流程接口
* 提供全局Cache、by space/app 级别的缓存管理

### 变更

* APIResponseError增加code属性
* 单元测试代码重构，简化元素的单元测试编写工作
* 修复sqlcondition固定quote char为"`"的问题
* 优化elementBase的实现，增加async_api/api的自动补全（Pylance only，Pycharm不支持）


## [1.1.1] - 2023-04-20

### 新增

* 支持python作为DeepUX数据源
* 支持PostgreSQL, DeepEngine数据表

### 变更

* 修复维度保存可能不返回errors的兼容性问题
* 修复多线程事务不支持的问题
* future_property失败时不再抛出BadFutureError，而是抛出实际发生的错误
* 修复单元测试用例
* 精简出现异常时打印的错误栈信息


## [1.1.0] - 2023-04-06

### 新增

* :tada: v1.1 第一次发版

### 变更

* 无

### 文档

* 无
