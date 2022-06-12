# jinja2 template

## 转换说明

按需求填写[etc/config.yaml](etc/config.yaml) 文件内容

config.yaml 文件说明:

```yaml
app:
  name: foo # 应用名称
namespace: rcrai # kubernetes 命名空间, 公有云生产环境命名空间为rcrai

containerPorts:
  http: 8080 # http 端口
  grpc: 1024 # grpc 端口

metrics:
  enabled: true # 是否开启监控
  port: 18089 # 监控端口

##
image:
  registry: rcrai.tencentcloudcr.com # 镜像仓库地址
  namespace: recurrent-customize # 镜像仓库命名空间
  tag: r_1.0.0 # 镜像tag

# 自定义command, 暂时注释
# command: []

extraEnvVars: # 环境变量, 以列表形式提供
  - name: APP_NAME
    value: bar
  - name: HTTP_PORT
    value: '8080'
  - name: CLUSTER_URL
    value: http://qux

staticSiteConfigmap: # configmap 配置, configmap 文件需要单独部署
  enabled: true # 是否开启configmap
  config: # 支持多个configmap 挂载
    - mountPath: /app/huskar.yaml # 在容器内部挂载路径, 形式为 /path 或 /path/filename
      configName: huskar.yaml # 配置文件名称
      appName: foo # 服务名称, 默认为app.name

replicaCount: 20 # 副本数

resources: # 资源分配
  ##
  ## limits:
  ##   cpu: 100m
  ##   memory: 128Mi
  ## requests:
  ##   cpu: 100m
  ##   memory: 128Mi


# 健康检查
livenessProbe: # 存活性检查
  enabled: false # 是否开启, 默认关闭
  initialDelaySeconds: 30
  timeoutSeconds: 5
  periodSeconds: 10
  failureThreshold: 6
  successThreshold: 1
  # 目前只接受httpGet 方式
  httpGet:
    path: /healthz # 健康检查接口
    port: 8080 # 健康检查端口

readinessProbe: # 就绪性检查
  enabled: false # 是否开启, 默认关闭
  initialDelaySeconds: 5
  timeoutSeconds: 3
  periodSeconds: 5
  failureThreshold: 3
  successThreshold: 1
  # 目前只接受httpGet 方式
  httpGet:
    path: /healthz # 健康检查接口
    port: 8080 # 健康检查端口

# service
service:
  type: ClusterIP # service 类型
  port: 80 # service 端口, 要求为80
  grpc: false # grpc 是否开启, 开启后端口为1024

# ingress
ingress:
  enabled: false # 是否存在ingress 外部路由
  hosts:
    - hostname: foo.example.com #  ingress 域名
      path: /api/(.*) # 路由路径
      tls: false # 是否开启tls
      rewrite: true # 是否需要rewrite, 如果存在, 需要填写rewriteTargetPath
      rewriteTargetPath: /api/$1 # rewrite 目标路径
    # 一个服务存在多个外部路由，可以依次填写
    ## - hostname: xyz.example.com # ingress 域名
    ##  path: /open/call/ # 路由路径
    ##  tls: true # 是否开启tls
    ##  rewrite: false  是否需要rewrite, 如果存在, 需要填写rewriteTargetPath
    ##  rewriteTargetPath:
```

填写完成之后, 执行[main.py](main.py) 脚本, 如无任何输出表示执行成功. 目标文件放置于[target](./target) 目录下.

```shell
python main.py

```
