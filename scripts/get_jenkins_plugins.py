#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Use: python get_jenkins_plugins.py
            -url http://192.168.0.66:8080/
            -u admin -p admin
            -o jenkins
            --repo_url "https://mirror.tuna.tsinghua.edu.cn/jenkins/plugins/"    # 添加repo_url 就代表,
            -d   # 添加-d就下载
python get_jenkins_plugins.py -url http://192.168.0.66:8080/ -u admin -p 1235678  -o jenkins --repo_url "https://mirror.tuna.tsinghua.edu.cn/jenkins/plugins/" -d
# 该脚本为下载问件事未使用多线程,后续改进
# 该脚本 可以做成jenkins工程,然后将生成的plugin_version.txt 和 plugin_download_url.txt 存放到jenkins构建中,打包成制品,
# 默认只要下载,就默认使用gz进行打包,并删除下载的文件夹。
# 该方式 需要基础环境中 有jenkins-python包,requests包,然后需要知道 jenkins的账号和密码
'''

import jenkins
import os
import sys
import argparse
import requests
import tarfile
import shutil
requests.packages.urllib3.disable_warnings()


def getArgs():
    parse = argparse.ArgumentParser()
    parse.add_argument('-u', type=str, help='jenkins的用户名')
    parse.add_argument('-p', type=str, help='jenkins的密码')
    parse.add_argument('-url', type=str, help="jenkins的地址")
    parse.add_argument('-o', type=str, help='输出文件夹')
    parse.add_argument('-d', action='store_true', help='下载所有jenkins版本插件')
    parse.add_argument('--repo_url', type=str,
                       default='https://updates.jenkins-ci.org/download/plugins', help='插件仓库的地址')
    args = parse.parse_args()
    return vars(args)

# 创建空文件,如果之前存在先删除


def touch_empty_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

# 写入内容到文件,追加写入


def write_line_in_file(file_path, content):
    with open(file_path, 'a') as f:
        f.write(content)

# 下载文件,没有使用多线程,单线程下载


def download_file(file_path, download_url):
    proxies = {"http": None, "https": None}
    res = requests.get(url=download_url, proxies=proxies, verify=False)
    with open(file_path, 'wb') as f:
        f.write(res.content)

# 筛选数据并写入文件,如果需要下载也下载文件


def filter_data_and_write_file(InstanceJenkins, output_dir, plugin_dir_name, plugin_version_file_name, plugin_download_file_name,
                               download_is_ok, repo_url):

    # 使用这种方式来创建空文件,如果之前存在就删除
    plugin_version_file_path = os.path.join(
        output_dir, plugin_version_file_name)
    plugin_download_file_path = os.path.join(
        output_dir, plugin_download_file_name)
    touch_empty_file(plugin_version_file_path)
    touch_empty_file(plugin_download_file_path)
    # 遍历数据,循环写入数据
    plugins = InstanceJenkins.get_plugins(depth=1)
    for one_plugin_detail in plugins.values():
        plugin_name_version = "{0}:{1}".format(one_plugin_detail.get(
            'shortName'), one_plugin_detail.get('version'))
        download_url = "{0}/{1}/{2}/{1}.hpi".format(
            repo_url, one_plugin_detail.get('shortName'), one_plugin_detail.get('version'))
        write_line_in_file(plugin_version_file_path, plugin_name_version+'\n')
        write_line_in_file(plugin_download_file_path, download_url+'\n')
        if download_is_ok == True:
            file_name = download_url.split('/')[-1]
            if not os.path.exists(os.path.join(output_dir, plugin_dir_name)):
                os.makedirs(os.path.join(output_dir, plugin_dir_name))
            file_path = os.path.join(output_dir, "plugins", file_name)
            if os.path.exists(file_path):
                print('{0}:已经存在'.format(file_name))
            else:
                download_file(file_path, download_url)
                print('{0}:下载成功'.format(file_name))


def exec_gzip_plugin_dir(output_dir, plugin_dir_name, jenkins_version, mode):
    os.chdir(output_dir)
    plugin_dir_path = plugin_dir_name
    plugin_gz_path = "{0}_{1}.tar.{2}".format(
        plugin_dir_name, jenkins_version, mode)
    with tarfile.open(name=plugin_gz_path, mode='w:{0}'.format(mode)) as tf:
        tf.add(plugin_dir_path)
    if os.path.exists(plugin_gz_path):
        print('{0}压缩succeed'.format(plugin_gz_path))
    else:
        print('{0}压缩 Failed'.format(plugin_gz_path))
        sys.exit(1)
    if os.path.exists(plugin_dir_name):
        shutil.rmtree(plugin_dir_name)


if __name__ == '__main__':
    args = getArgs()
    jenkins_url = args['url'][:-1] if args['url'][-1] == "/" else args['url']
    username = args['u']
    password = args['p']
    output_dir = args['o']
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    download_is_ok = args['d']  # 是否下载文件
    repo_url = args['repo_url'][:-
                                1] if args['repo_url'] == '/' else args['repo_url']

    # 获取jenkins实例
    InstanceJenkins = jenkins.Jenkins(jenkins_url, username, password)
    # 获取jenkinsVersion
    jenkins_version = InstanceJenkins.get_version()

    plugin_version_file_name = "plugin_version_{0}.txt".format(
        jenkins_version)
    plugin_download_file_name = "plugin_download_url_{0}.txt".format(
        jenkins_version)
    plugin_dir_name = "plugins"

    # 筛选数据并写入文件,并下载插件
    filter_data_and_write_file(InstanceJenkins, output_dir, plugin_dir_name, plugin_version_file_name, plugin_download_file_name,
                               download_is_ok, repo_url)
    # 压缩插件目录
    # http://www.juzicode.com/python-tutorial-zip-unzip-tarfile/#5
    # gz bz2 xz
    if download_is_ok:
        exec_gzip_plugin_dir(output_dir, plugin_dir_name,
                             jenkins_version, 'gz')
