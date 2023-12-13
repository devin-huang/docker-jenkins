> Jenkins是一个开源软件项目，是基于Java开发的一种持续集成工具，用于代码编译、部署、测试等工作。 Jenkins也是一个跨平台的，大多数主流的平台都支持，而且安装很简单，我们这里以docker部署war包方式安装它。
> 官网下载地址： https://jenkins.io/download/

- 主要在官方版本之上增加了一些常用的依赖生产可用（详情可见plugins/jenkins）
- 免去了初始化账号密码的麻烦（默认账号/密码：jenkins/1235678）
- 镜像地址：https://hub.docker.com/repository/docker/kamalyes/jenkins/tags

```bash
# 添加提前安装好的plugins https://github.com/jenkinsci/docker/blob/master/README.md
ADD --chown=jenkins:jenkins plugins/jenkins/2.387.3/  /usr/share/jenkins/ref/plugins/

# 添加初始化脚本,用户提前设置用户名和密码, 需注意：如果你设置了JENKINS_USER变量=admin时会自动修改密码为admin
COPY --chown=jenkins:jenkins scripts/set_user_password.groovy /usr/share/jenkins/ref/init.groovy.d/set_user_password.groovy

# 安装常用软件
RUN apt-get update && \
    apt-get install -y --no-install-recommends make wget vim sshpass net-tools ansible inetutils-ping telnet git openssh-server openssh-client
```
### 详细部署流程
![Image text](https://devin-huang.github.io/img/pubilc/github/docker-jenkins-steps.png)

- 基于centos（CentOS Linux release 7.9.2009 (Core)）、docker（docker-ce-24.0.6）、git（1.8.3.1）、docker-compose方式启动
- 第一步：安装docker、docker仓库下载镜像 `kamalyes/jenkins:2.387.3-lts-jdk11-slim`
- 第二步：安装docker-compose，查看是否安装：`docker-compose --version`
```
1. 下载（必须github连接）：`curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose`
2. 权限设置：`chmod +x /usr/local/bin/docker-compose`
3. 查看安装成功否：`docker-compose -v`
```
- 第三步：使用`docker-compose`方式启动，centos（任意目录）执行命令： `/opt docker-compose up -d` 创建容器（初始化jenkins）
- 第四步：jenkins全局配置凭据拉取git项目，最终pipeline变量中写入 jenkins ->「系统管理(Manage Jenkins)」-> [凭据(credentials)] -> [系统(system)] -> [全局凭据(global credentials)] -> [新增凭据]
- 第五步：SSH 配置（服务器凭证配置）
```
一、【获取秘钥】： 进入centos（任意目录）执行命令：ssh-keygen -m PEM -t rsa -b 4096 或 ssh-keygen -t rsa -P '' -f '/root/.ssh/id_rsa' （一直回车，如存在就重写）
二、【复制id_rsa.pub内容到当前目录authorized_keys文件】：centos（任意目录）执行命令：cd /root/.ssh/ && cat id_rsa.pub >> authorized_keys (需要注意的是root代表是用户名)
三、【jenkins依赖，默认已安装当前可忽略】：jenkins下载jar:ssh-steps.hpi.2.0.0, 源码地址：https://github.com/jenkinsci/ssh-steps-plugin/tree/ssh-steps-2.0.0
四:、重启jenkins并把「系统管理」-> [凭据] -> [系统] -> [全局凭据] -> [新增凭据]
```
凭据配置步骤：【 
	1.「类型」：选择 SSH private Key  
	2.「ID」填入 pipeline 配置的 SSH_CREDENTIALS_ID（自定义即可）
	3.「Private Key」填入（第二步）id_rsa 中内容即可
	4.「描述」 备注服务器IP 
	5.「用户」 root 
】
```
- 第六步：区分环境项目：我的视图 -> 新建视图 -> 我的视图 -> 选择项目 -> sit、prod
- 第七步：使用流水线方式创建项目并写入pipeline script：具体参考： `/**/pipeline`

### 命令式快速开始

```bash
docker run -d --name kamalyes-jenkins -p 18080:8080 -p 15001:50000 kamalyes/jenkins:2.387.3-lts-jdk11-slim
# 实例
[root@k8s-master docker-jenkins]# docker run -d --name kamalyes-jenkins -p 18080:8080 -p 15001:50000 kamalyes/jenkins:2.387.3-lts-jdk11-slimUnable to find image 'kamalyes/jenkins:2.387.3-lts-jdk11-slim' locally
2.387.3-lts-jdk11-slim: Pulling from kamalyes/jenkins
b0248cf3e63c: Already exists 
62f383c3c765: Already exists 
67400627246a: Already exists 
b3351de6687f: Already exists 
85f1bf17d08b: Already exists 
2a3961df564a: Already exists 
1c4b1dd83b8f: Already exists 
941d0a3e91b6: Already exists 
f07d5591ca96: Already exists 
d1e9c8dee430: Already exists 
48724caf6170: Already exists 
95ce98d61add: Already exists 
057e4a19bf34: Already exists 
c5713ae2b88e: Pull complete 
e74e2291730a: Pull complete 
2d7fd3320c6a: Pull complete 
2d0f840a7ddf: Pull complete 
ce0807f41cc1: Pull complete 
312af55cc32d: Pull complete 
06dad93a1e69: Pull complete 
Digest: sha256:f47c0f8d5b8721cf9bddad57ee47b349a25b362f1a70337777db3c82ce99bf89
Status: Downloaded newer image for kamalyes/jenkins:2.387.3-lts-jdk11-slim
930eaaffd2f10588dd0817562540a5529329e3cc6b3d9141b1d5da322409da53

[root@k8s-master docker-jenkins]# docker ps -a | grep kamalyes-jenkins
930eaaffd2f1   kamalyes/jenkins:2.387.3-lts-jdk11-slim    "/usr/bin/tini -- /u…"   5 seconds ago   Up 5 seconds          0.0.0.0:18080->8080/tcp, :::18080->8080/tcp, 0.0.0.0:15001->50000/tcp, :::15001->50000/tcp                     kamalyes-jenkins
```

### docker-compose方式启动

**1. 创建挂载目录**

```bash
sudo sudo mkdir -p /opt/jenkins && chmod 777 -R /opt/jenkins && cd /opt/jenkins # 目录设置为 777 权限，避免权限问题
```
**2. 创建 docker-compose.yml 文件**
```bash
version: '3.1'
services:
 jenkins:
  restart: always
  privileged: true
  user: root
  container_name: jenkins
  image: kamalyes/jenkins:2.387.3-lts-jdk11-slim
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8080"]
    interval: 6s
    timeout: 5s
    retries: 10
  volumes:
   - /root/.ssh:/root/.ssh
   - /opt/jenkins/:/var/jenkins_home
   - /opt/jenkins/workspace/:/root/.jenkins/workspace
   - /var/run/docker.sock:/var/run/docker.sock
   - /usr/bin/docker:/usr/bin/docker
   - /usr/bin/buildctl:/usr/local/bin/buildctl
   - /usr/local/go:/usr/local/go
   - /usr/lib/x86_64-linux-gnu/libltdl.so.7:/usr/lib/x86_64-linux-gnu/libltdl.so.7
   - /usr/local/gradle-7.3.3:/usr/local/gradle-7.3.3
   - /usr/local/gradle-7.6:/usr/local/gradle-7.6
   - /usr/local/jdk11.0.1:/usr/local/jdk11.0.1
   - /usr/local/jdk1.8.0_141:/usr/local/jdk1.8.0_141
   - /usr/local/node-v16.19.1-linux-x64:/usr/local/node-v16.19.1-linux-x64
   - /usr/local/python3:/usr/local/python3
   - /usr/local/android-sdk-linux:/usr/local/android-sdk-linux
  ports:
   - 18080:8080
   - 15001:50000
```

**说明**

```bash
以下软件均需提前安装好（若不需要则可以去掉）
- /usr/bin/buildctl:/usr/local/bin/buildctl
- /usr/local/go:/usr/local/go
- /usr/lib/x86_64-linux-gnu/libltdl.so.7:/usr/lib/x86_64-linux-gnu/libltdl.so.7
- /usr/local/gradle-7.3.3:/usr/local/gradle-7.3.3
- /usr/local/gradle-7.6:/usr/local/gradle-7.6
- /usr/local/jdk11.0.1:/usr/local/jdk11.0.1
- /usr/local/jdk1.8.0_141:/usr/local/jdk1.8.0_141
- /usr/local/node-v16.19.1-linux-x64:/usr/local/node-v16.19.1-linux-x64
- /usr/local/python3:/usr/local/python3
- /usr/local/android-sdk-linux:/usr/local/android-sdk-linux
```

**3. 启动 docker-compose**
```bash
docker-compose up -d
```

**4. 访问**
```bash
# 默认账号/密码：jenkins/1235678
localhost:18080/manage/pluginManager/installed # 查看pluginInstalled
localhost:18080/manage/configureSecurity/ # （因默认开启了游客状态可访问）、需登录下（/login?from=%2F）重新设置安全组
```
