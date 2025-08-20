# 邮件功能使用指南

本指南介绍如何使用优化后的邮件发送和接收功能。

## 📧 发送邮件 - send_email

### 基本功能
- 发送纯文本或HTML格式邮件
- 支持多个收件人、抄送、密送
- 支持附件和内嵌图片
- 自动识别主流邮箱SMTP配置
- 详细的错误处理和返回信息

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| email_account | str | ✅ | 邮箱账号（如：user@qq.com） |
| password | str | ✅ | 邮箱密码或授权码 |
| subject | str | ✅ | 邮件主题 |
| content | str | ✅ | 邮件正文内容 |
| recipients | str/list | ✅ | 收件人邮箱（支持单个邮箱字符串或多个邮箱列表） |
| attachments | list | ❌ | 附件文件路径列表 |
| cc_recipients | list | ❌ | 抄送邮箱列表 |
| bcc_recipients | list | ❌ | 密送邮箱列表 |
| sender_name | str | ❌ | 发件人显示名称 |
| html_mode | bool | ❌ | 是否使用HTML格式（默认False） |
| inline_images | dict | ❌ | 内嵌图片（{cid: filepath}格式） |
| signature | str | ❌ | 邮件签名 |
| smtp_config | dict | ❌ | 自定义SMTP配置 |
| timeout | int | ❌ | 超时时间（秒，默认30） |

### 返回值格式

```python
{
    "success": bool,           # 是否成功
    "message": str,            # 状态信息
    "recipient_count": int,    # 成功发送的收件人数量
    "failed_recipients": list  # 发送失败的收件人列表
}
```

### 使用示例

#### 1. 发送简单文本邮件
```python
from simtoolsz.mail import send_email

result = send_email(
    email_account="user@qq.com",
    password="your_password",
    subject="测试邮件",
    content="这是一封测试邮件",
    recipients="recipient@example.com"
)
```

#### 2. 发送带附件的邮件
```python
result = send_email(
    email_account="user@163.com",
    password="auth_code",
    subject="工作报告",
    content="请查收本周工作报告",
    recipients=["boss@company.com", "colleague@company.com"],
    attachments=["report.pdf", "data.xlsx"],
    cc_recipients=["manager@company.com"]
)
```

#### 3. 发送HTML格式邮件
```python
result = send_email(
    email_account="user@gmail.com",
    password="app_password",
    subject="产品通知",
    content="""
    <h1>新产品发布</h1>
    <p>我们很高兴地通知您，新产品已上线！</p>
    <img src="cid:product_image" style="width: 300px;">
    """,
    recipients="client@example.com",
    html_mode=True,
    inline_images={"product_image": "product.jpg"}
)
```

#### 4. 使用自定义SMTP配置
```python
result = send_email(
    email_account="user@company.com",
    password="password",
    subject="系统通知",
    content="系统维护通知",
    recipients="all@company.com",
    smtp_config={
        "server": "smtp.company.com",
        "port": 587,
        "use_ssl": True
    }
)
```

## 📥 获取邮件 - fetch_emails

### 基本功能
- 按条件搜索和获取邮件
- 支持下载邮件附件
- 支持多种搜索模式（精确、模糊、正则）
- 自动识别主流邮箱IMAP配置
- 详细的邮件信息返回

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| email_account | str | ✅ | 邮箱账号 |
| password | str | ✅ | 邮箱密码或授权码 |
| subject | str | ❌ | 搜索主题关键词 |
| sender | str | ❌ | 发件人邮箱 |
| date_range | tuple | ❌ | 日期范围（(start_date, end_date)） |
| search_mode | str | ❌ | 搜索模式：exact/fuzzy/regex |
| max_emails | int | ❌ | 最大获取邮件数量 |
| download_attachments | bool | ❌ | 是否下载附件 |
| attachment_dir | str | ❌ | 附件保存目录 |
| imap_config | dict | ❌ | 自定义IMAP配置 |

### 返回值格式

```python
{
    "success": bool,           # 是否成功
    "message": str,            # 状态信息
    "email_count": int,        # 获取的邮件数量
    "emails": [                # 邮件列表
        {
            "subject": str,        # 主题
            "from": str,           # 发件人
            "to": str,             # 收件人
            "date": str,           # 日期
            "text_body": str,      # 纯文本内容
            "html_body": str,      # HTML内容
            "size": int,           # 邮件大小（字节）
            "attachments": [       # 附件列表
                {
                    "filename": str,     # 文件名
                    "size": int,        # 文件大小
                    "filepath": str     # 保存路径
                }
            ]
        }
    ],
    "attachments_dir": str     # 附件保存目录
}
```

### 使用示例

#### 1. 获取最新邮件
```python
from simtoolsz.mail import fetch_emails
from datetime import datetime, timedelta

result = fetch_emails(
    email_account="user@qq.com",
    password="password",
    max_emails=10
)

if result["success"]:
    for email in result["emails"]:
        print(f"主题: {email['subject']}")
        print(f"发件人: {email['from']}")
        print(f"日期: {email['date']}")
```

#### 2. 按主题搜索邮件
```python
result = fetch_emails(
    email_account="user@163.com",
    password="auth_code",
    subject="工作报告",
    search_mode="fuzzy",
    date_range=(datetime.now() - timedelta(days=7), datetime.now())
)
```

#### 3. 获取特定发件人的邮件
```python
result = fetch_emails(
    email_account="user@gmail.com",
    password="app_password",
    sender="reports@company.com",
    max_emails=5
)
```

#### 4. 下载邮件附件
```python
result = fetch_emails(
    email_account="user@company.com",
    password="password",
    subject="数据报告",
    download_attachments=True,
    attachment_dir="./downloads",
    max_emails=3
)

if result["success"]:
    for email in result["emails"]:
        if email["attachments"]:
            print(f"邮件 '{email['subject']}' 包含附件:")
            for att in email["attachments"]:
                print(f"  - {att['filename']} -> {att['filepath']}")
```

## 🔧 邮箱配置参考

### 常用邮箱SMTP/IMAP设置

| 邮箱服务商 | SMTP服务器 | SMTP端口 | IMAP服务器 | IMAP端口 | 备注 |
|---|---|---|---|---|---|
| QQ邮箱 | smtp.qq.com | 465/587 | imap.qq.com | 993 | 需使用授权码 |
| 163邮箱 | smtp.163.com | 465/994 | imap.163.com | 993 | 需使用授权码 |
| Gmail | smtp.gmail.com | 465/587 | imap.gmail.com | 993 | 需使用应用专用密码 |
| Outlook | smtp-mail.outlook.com | 587 | imap-mail.outlook.com | 993 | 需使用应用密码 |
| 126邮箱 | smtp.126.com | 465/994 | imap.126.com | 993 | 需使用授权码 |

### 获取授权码方法

#### QQ邮箱授权码
1. 登录QQ邮箱网页版
2. 进入 设置 > 账户
3. 找到 "POP3/SMTP服务" 并开启
4. 生成授权码

#### 163邮箱授权码
1. 登录163邮箱网页版
2. 进入 设置 > POP3/SMTP/IMAP
3. 开启SMTP/IMAP服务
4. 获取授权码

#### Gmail应用专用密码
1. 登录Google账户
2. 进入 安全性 > 两步验证
3. 找到 "应用专用密码"
4. 生成用于邮件的密码

## ⚠️ 注意事项

1. **安全性**
   - 不要将密码硬编码在代码中
   - 使用环境变量或配置文件存储敏感信息
   - 定期更换授权码

2. **性能**
   - 大量邮件获取时设置合理的max_emails值
   - 大附件下载时注意磁盘空间
   - 设置合适的timeout值避免网络超时

3. **错误处理**
   - 始终检查返回值的success字段
   - 查看message字段获取详细错误信息
   - 网络异常时重试机制

4. **兼容性**
   - 旧函数名quick_send_email和load_email_by_subject仍可使用
   - 新函数提供更好的错误处理和返回值

## 🚀 快速开始

1. 安装依赖：确保已安装所需Python包
2. 获取授权码：根据邮箱类型获取相应的授权码
3. 运行示例：参考examples/mail_examples.py中的示例代码
4. 集成项目：将函数集成到你的项目中

## 📞 技术支持

如遇到问题，请检查：
- 网络连接是否正常
- 邮箱账号和密码是否正确
- 邮箱服务是否已开启SMTP/IMAP
- 防火墙是否阻止了相应端口