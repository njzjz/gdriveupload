# gdriveupload

众所周知，由于种种原因，从国内传文件到国外是非常痛苦的。笔者尝试了种种办法后，均告失败。后来，笔者无意中发现了maple3142的[GDIndex](https://github.com/maple3142/GDIndex)项目，发现可以通过Cloudflare直接传输到Google Drive上。

美中不足的是，Cloudflare限制上传100MB以内的文件。不过，我们可以用分拆文件的方法绕过限制。于是，这个项目诞生了。

# 前期准备

配置[GDIndex](https://github.com/maple3142/GDIndex)。在GDIndex的目录下创建tmp目录（此为默认的临时目录）。

# 在国内机器上传文件

安装gdriveupload：
```
pip install git+https://github.com/njzjz/gdriveupload
```

在`~/.bashrc`中配置`GDRIVEUPLOAD_WEBSITE`、`GDRIVEUPLOAD_USERNAME`、`GDRIVEUPLOAD_PASSWORD`三个环境变量，分别为GDIndex网站地址、用户名和密码。

现在，此处有一个1009MB的`20180628qm9nn.tgz`，想把它传到Google Drive中的`Undergraduate_Work/Deep_Learning/Dataset/20180628qm9nn.tgz`中去。

```bash
gdriveupload upload -f 20180628qm9nn.tgz -t Undergraduate_Work/Deep_Learning/Dataset/20180628qm9nn.tgz
```

现在，`20180628qm9nn.tgz`已经分为11个子文件上传到了`tmp`文件夹中。在上海教育网环境下，共耗时3分钟，即5.5MB/s，速度尚可接受。

# 合并文件

这里推荐使用Google Colab合并文件，装载Google Drive后，在代码框输入：
```bash
!pip install git+https://github.com/njzjz/gdriveupload
!GDRIVEUPLOAD_ROOT=/content/drive/My\ Drive gdriveupload combine
```

大约耗时2分钟。现在，`20180628qm9nn.tgz`已经在Google Drive的`Undergraduate_Work/Deep_Learning/Dataset/`目录下了。
