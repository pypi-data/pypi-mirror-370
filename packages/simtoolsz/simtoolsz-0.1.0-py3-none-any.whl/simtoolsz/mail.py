import imaplib
import email
import os
import smtplib
import mimetypes
from pathlib import Path
from typing import List, Dict, Union, Optional, Tuple, Any
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.utils import formataddr
from email.header import Header
from email.header import decode_header
from datetime import datetime, timedelta



def send_email(
    email_account: str,
    password: str,
    subject: str,
    content: str,
    recipients: Union[str, List[str], List[Tuple[str, str]]],
    attachments: Optional[List[Union[Path, str]]] = None,
    cc_recipients: Optional[Union[str, List[str], List[Tuple[str, str]]]] = None,
    bcc_recipients: Optional[Union[str, List[str], List[Tuple[str, str]]]] = None,
    html_mode: bool = False,
    sender_name: Optional[str] = None,
    signature: Optional[str] = None,
    inline_images: Optional[Dict[str, Union[Path, str]]] = None,
    smtp_config: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    简单易用的邮件发送函数（支持附件、HTML、内嵌图片等高级功能）
    
    使用示例:
        # 基础用法 - 发送纯文本邮件
        result = send_email(
            email_account="your@qq.com",
            password="your_password",
            subject="测试邮件",
            content="这是一封测试邮件",
            recipients="friend@example.com"
        )
        
        # 高级用法 - 发送HTML邮件带附件
        result = send_email(
            email_account="your@gmail.com",
            password="app_password",
            subject="项目报告",
            content="<h1>本月工作报告</h1><p>详见附件</p>",
            recipients=["boss@company.com", "同事<colleague@company.com>"],
            cc_recipients=["assistant@company.com"],
            attachments=["report.pdf", "data.xlsx"],
            html_mode=True,
            sender_name="张三",
            signature="<br><em>此致<br>张三</em>"
        )
        
        # 使用内嵌图片
        result = send_email(
            email_account="your@163.com",
            password="auth_code",
            subject="产品展示",
            content='<img src="cid:product1"><p>最新产品图片</p>',
            recipients="client@example.com",
            inline_images={"product1": "product.jpg"},
            html_mode=True
        )

    Args:
        email_account: 发件人邮箱地址
        password: 邮箱密码或授权码（QQ/163等需要授权码）
        subject: 邮件主题
        content: 邮件正文内容（支持HTML或纯文本）
        recipients: 收件人，可以是：
            - 单个邮箱字符串: "user@example.com"
            - 邮箱列表: ["user1@example.com", "user2@example.com"]
            - 带名称的格式: ["张三<user@example.com>"] 或 [("张三", "user@example.com")]
        attachments: 附件文件路径列表，支持Path对象或字符串
        cc_recipients: 抄送人，格式同recipients
        bcc_recipients: 密送人，格式同recipients
        html_mode: 是否使用HTML格式发送
        sender_name: 发件人显示名称
        signature: 邮件签名内容（自动添加在正文后）
        inline_images: 内嵌图片字典，格式: {"cid名称": "图片路径"}
        smtp_config: 自定义SMTP配置，格式: {"smtp_server": "smtp.xxx.com", "port": 587, "use_ssl": True}
        timeout: 连接超时时间（秒）

    Returns:
        Dict[str, Any]: 发送结果信息
            {
                "success": bool,  # 是否成功
                "message": str,   # 结果消息
                "recipient_count": int,  # 成功发送的收件人数量
                "smtp_server": str  # 使用的SMTP服务器
            }

    Raises:
        ValueError: 参数验证失败
        RuntimeError: 邮件发送失败
    """
    # 参数验证和预处理
    if not recipients:
        raise ValueError("必须指定至少一个收件人")
    
    # 标准化参数格式
    attachments = attachments or []
    cc_recipients = cc_recipients or []
    bcc_recipients = bcc_recipients or []
    
    def parse_recipients(recipients):
        """解析收件人参数为标准化格式"""
        if isinstance(recipients, str):
            return [recipients]
        elif isinstance(recipients, (list, tuple)):
            return list(recipients)
        return []
    
    all_recipients = parse_recipients(recipients)
    all_cc = parse_recipients(cc_recipients)
    all_bcc = parse_recipients(bcc_recipients)
    
    # 创建邮件对象
    msg = MIMEMultipart()
    msg.set_charset("utf-8")
    
    # 设置发件人
    if sender_name:
        sender_name = Header(sender_name, "utf-8").encode()
    msg["From"] = formataddr((sender_name, email_account)) if sender_name else email_account
    
    def format_recipient_list(recipient_list):
        """格式化收件人列表"""
        formatted = []
        for recipient in recipient_list:
            if isinstance(recipient, tuple) and len(recipient) == 2:
                name, addr = recipient
                name = Header(name, "utf-8").encode()
                formatted.append(formataddr((name, addr)))
            else:
                # 处理字符串格式如 "张三<user@example.com>"
                recipient_str = str(recipient)
                if "<" in recipient_str and ">" in recipient_str:
                    name_part = recipient_str.split("<")[0].strip()
                    addr_part = recipient_str.split("<")[1].split(">")[0].strip()
                    if name_part:
                        name_part = Header(name_part, "utf-8").encode()
                        formatted.append(formataddr((name_part, addr_part)))
                    else:
                        formatted.append(addr_part)
                else:
                    formatted.append(recipient_str)
        return formatted
    
    # 设置收件人
    msg["Subject"] = Header(subject, "utf-8")
    msg["To"] = ", ".join(format_recipient_list(all_recipients))
    if all_cc:
        msg["Cc"] = ", ".join(format_recipient_list(all_cc))
    
    # 处理邮件正文和签名
    full_content = content
    if signature:
        if html_mode:
            full_content += f"<br><br>{signature}"
        else:
            full_content += f"\n\n{signature}"
    
    # 添加邮件正文
    if html_mode:
        msg.attach(MIMEText(full_content, "html", "utf-8"))
    else:
        msg.attach(MIMEText(full_content, "plain", "utf-8"))
    
    # 添加内嵌图片
    if inline_images:
        mimetypes.init()
        for cid, img_path in inline_images.items():
            img_path = Path(img_path)
            if not img_path.exists():
                raise FileNotFoundError(f"内嵌图片文件不存在: {img_path}")
            
            mime_type, _ = mimetypes.guess_type(img_path.name)
            if not mime_type or not mime_type.startswith("image/"):
                raise ValueError(f"文件类型不支持或不是图片: {img_path}")
            
            try:
                with open(img_path, "rb") as img_file:
                    img_data = img_file.read()
                
                _, subtype = mime_type.split("/", 1)
                img_part = MIMEImage(img_data, _subtype=subtype)
                img_part.add_header("Content-ID", f"<{cid}>")
                img_part.add_header("Content-Disposition", "inline", 
                                  filename=Header(img_path.name, "utf-8").encode())
                msg.attach(img_part)
            except Exception as e:
                raise RuntimeError(f"处理内嵌图片失败 {img_path}: {e}")
    
    # 添加附件
    for attachment in attachments:
        file_path = Path(attachment)
        if not file_path.exists():
            raise FileNotFoundError(f"附件文件不存在: {file_path}")
        
        try:
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            part = MIMEApplication(file_data, Name=Header(file_path.name, "utf-8").encode())
            part.add_header("Content-Disposition", "attachment", 
                          filename=Header(file_path.name, "utf-8").encode())
            msg.attach(part)
        except Exception as e:
            raise RuntimeError(f"处理附件失败 {file_path}: {e}")
    
    # 自动配置SMTP服务器
    domain = email_account.split("@")[-1].lower()
    default_smtp_config = {
        "gmail.com": {"smtp_server": "smtp.gmail.com", "port": 587, "use_ssl": False},
        "qq.com": {"smtp_server": "smtp.qq.com", "port": 465, "use_ssl": True},
        "163.com": {"smtp_server": "smtp.163.com", "port": 465, "use_ssl": True},
        "126.com": {"smtp_server": "smtp.126.com", "port": 465, "use_ssl": True},
        "outlook.com": {"smtp_server": "smtp-mail.outlook.com", "port": 587, "use_ssl": False},
        "hotmail.com": {"smtp_server": "smtp-mail.outlook.com", "port": 587, "use_ssl": False},
        "chinaott.net": {"smtp_server": "smtp.exmail.qq.com", "port": 465, "use_ssl": True},
    }
    
    # 使用自定义配置或自动配置
    if smtp_config:
        smtp_server = smtp_config.get("smtp_server")
        port = smtp_config.get("port", 587)
        use_ssl = smtp_config.get("use_ssl", False)
    else:
        if domain not in default_smtp_config:
            raise ValueError(f"不支持的邮箱服务商: {domain}，请提供自定义smtp_config")
        config = default_smtp_config[domain]
        smtp_server = config["smtp_server"]
        port = config["port"]
        use_ssl = config["use_ssl"]
    
    # 收集所有收件人
    def extract_emails(recipient_list):
        """提取邮箱地址"""
        emails = []
        for recipient in recipient_list:
            if isinstance(recipient, tuple) and len(recipient) == 2:
                emails.append(recipient[1])
            else:
                recipient_str = str(recipient)
                if "<" in recipient_str and ">" in recipient_str:
                    addr = recipient_str.split("<")[1].split(">")[0].strip()
                    emails.append(addr)
                else:
                    emails.append(recipient_str)
        return emails
    
    all_emails = extract_emails(all_recipients) + extract_emails(all_cc) + extract_emails(all_bcc)
    
    try:
        # 建立SMTP连接
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, port, timeout=timeout)
        else:
            server = smtplib.SMTP(smtp_server, port, timeout=timeout)
            server.starttls()
        
        # 登录并发送
        server.login(email_account, password)
        server.sendmail(email_account, all_emails, msg.as_string())
        server.quit()
        
        return {
            "success": True,
            "message": f"邮件发送成功，共发送给{len(all_emails)}个收件人",
            "recipient_count": len(all_emails),
            "smtp_server": smtp_server
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"邮件发送失败: {str(e)}",
            "recipient_count": 0,
            "smtp_server": smtp_server
        }

def fetch_emails(
    email_account: str,
    password: str,
    subject: Optional[str] = None,
    sender: Optional[str] = None,
    date_range: Optional[Tuple[datetime, datetime]] = None,
    mailbox: str = 'INBOX',
    download_attachments: bool = False,
    attachment_dir: str = 'attachments',
    max_emails: Optional[int] = None,
    imap_config: Optional[Dict[str, Any]] = None,
    search_mode: str = 'exact'  # 'exact', 'fuzzy', 'regex'
) -> Dict[str, Any]:
    """
    简单易用的邮件获取函数（支持按主题、发件人搜索，附件下载等）
    
    使用示例:
        # 基础用法 - 获取所有邮件
        result = fetch_emails(
            email_account="your@qq.com",
            password="your_password",
            max_emails=10
        )
        
        # 按主题搜索邮件
        result = fetch_emails(
            email_account="your@gmail.com",
            password="app_password",
            subject="项目报告",
            search_mode="fuzzy",
            date_range=(datetime(2024, 1, 1), datetime(2024, 12, 31))
        )
        
        # 下载附件
        result = fetch_emails(
            email_account="your@163.com",
            password="auth_code",
            sender="boss@company.com",
            download_attachments=True,
            attachment_dir="./downloads"
        )
        
        # 使用自定义IMAP配置
        result = fetch_emails(
            email_account="user@company.com",
            password="password",
            imap_config={"server": "imap.company.com", "port": 993, "use_ssl": True}
        )

    Args:
        email_account: 邮箱账号
        password: 邮箱密码或授权码
        subject: 邮件主题关键词（可选）
        sender: 发件人邮箱（可选）
        date_range: 日期范围元组(start_date, end_date)，默认最近7天
        mailbox: 邮箱文件夹，默认'INBOX'
        download_attachments: 是否下载附件，默认False
        attachment_dir: 附件保存目录，默认'attachments'
        max_emails: 最大返回邮件数量（可选）
        imap_config: 自定义IMAP配置，格式: {"server": "imap.xxx.com", "port": 993, "use_ssl": True}
        search_mode: 搜索模式: 'exact'(精确), 'fuzzy'(模糊), 'regex'(正则)

    Returns:
        Dict[str, Any]: 获取结果
            {
                "success": bool,           # 是否成功
                "message": str,            # 结果消息
                "email_count": int,        # 获取的邮件数量
                "emails": List[Dict],      # 邮件列表
                "attachments_dir": str   # 附件保存目录
            }
        
        邮件格式:
        {
            "subject": str,              # 邮件主题
            "from": str,                 # 发件人
            "to": str,                   # 收件人
            "date": str,                 # 发送日期
            "text_body": str,            # 纯文本正文
            "html_body": str,            # HTML正文
            "attachments": List[Dict],   # 附件列表
            "size": int                  # 邮件大小(字节)
        }
    """
    try:
        # 设置默认日期范围
        if date_range is None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            date_range = (start_date, end_date)
        
        # 创建附件目录
        if download_attachments:
            os.makedirs(attachment_dir, exist_ok=True)
        
        # 自动配置IMAP服务器
        domain = email_account.split("@")[-1].lower()
        default_imap_config = {
            "qq.com": {"server": "imap.qq.com", "port": 993, "use_ssl": True},
            "gmail.com": {"server": "imap.gmail.com", "port": 993, "use_ssl": True},
            "163.com": {"server": "imap.163.com", "port": 993, "use_ssl": True},
            "126.com": {"server": "imap.126.com", "port": 993, "use_ssl": True},
            "outlook.com": {"server": "imap-mail.outlook.com", "port": 993, "use_ssl": True},
            "hotmail.com": {"server": "imap-mail.outlook.com", "port": 993, "use_ssl": True},
            "aliyun.com": {"server": "imap.aliyun.com", "port": 993, "use_ssl": True},
            "chinaott.net": {"server": "imap.exmail.qq.com", "port": 993, "use_ssl": True},
        }
        
        # 使用自定义配置或自动配置
        if imap_config:
            imap_server = imap_config.get("server")
            port = imap_config.get("port", 993)
            use_ssl = imap_config.get("use_ssl", True)
        else:
            if domain not in default_imap_config:
                raise ValueError(f"不支持的邮箱服务商: {domain}，请提供自定义imap_config")
            config = default_imap_config[domain]
            imap_server = config["server"]
            port = config["port"]
            use_ssl = config["use_ssl"]
        
        # 连接IMAP服务器
        if use_ssl:
            mail = imaplib.IMAP4_SSL(imap_server, port)
        else:
            mail = imaplib.IMAP4(imap_server, port)
        
        try:
            mail.login(email_account, password)
            
            # 选择邮箱文件夹
            try:
                mail.select(mailbox)
            except:
                # 如果指定文件夹不存在，使用INBOX
                mail.select('INBOX')
            
            # 构建搜索条件
            search_criteria = []
            
            # 日期范围
            start_str = date_range[0].strftime("%d-%b-%Y")
            end_str = date_range[1].strftime("%d-%b-%Y")
            search_criteria.append(f'(SINCE "{start_str}" BEFORE "{end_str}")')
            
            # 主题搜索
            if subject:
                if search_mode == 'exact':
                    search_criteria.append(f'(SUBJECT "{subject}")')
                elif search_mode == 'fuzzy':
                    search_criteria.append(f'(SUBJECT "{subject}")')  # IMAP原生支持部分匹配
                elif search_mode == 'regex':
                    # 正则搜索需要在获取后处理
                    search_criteria.append(f'(SUBJECT "{subject}")')
            
            # 发件人搜索
            if sender:
                search_criteria.append(f'(FROM "{sender}")')
            
            # 组合搜索条件
            if len(search_criteria) > 1:
                search_query = ' '.join(search_criteria)
            else:
                search_query = search_criteria[0] if search_criteria else 'ALL'
            
            # 搜索邮件
            status, messages = mail.search(None, search_query)
            if status != 'OK' or not messages[0]:
                return {
                    "success": True,
                    "message": "没有找到匹配的邮件",
                    "email_count": 0,
                    "emails": [],
                    "attachments_dir": attachment_dir if download_attachments else None
                }
            
            mail_ids = messages[0].split()
            if max_emails:
                mail_ids = mail_ids[-max_emails:]  # 获取最新的邮件
            
            emails = []
            for mail_id in reversed(mail_ids):  # 从新到旧排序
                try:
                    status, data = mail.fetch(mail_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    msg = email.message_from_bytes(data[0][1])
                    
                    # 解码邮件主题
                    subject_header = decode_header(msg.get('Subject', ''))
                    subject_str = ""
                    for part, encoding in subject_header:
                        if isinstance(part, bytes):
                            try:
                                subject_str += part.decode(encoding or 'utf-8', errors='replace')
                            except:
                                subject_str += part.decode('gbk', errors='replace')
                        else:
                            subject_str += str(part)
                    
                    # 检查主题匹配（对于正则模式进行二次过滤）
                    if subject and search_mode == 'regex':
                        import re
                        if not re.search(subject, subject_str, re.IGNORECASE):
                            continue
                    elif subject and search_mode == 'fuzzy':
                        if subject.lower() not in subject_str.lower():
                            continue
                    
                    # 提取正文内容
                    text_body = ""
                    html_body = ""
                    attachments_list = []
                    total_size = 0
                    
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            
                            # 获取邮件大小
                            if part.get('Content-Length'):
                                try:
                                    total_size += int(part.get('Content-Length'))
                                except:
                                    pass
                            
                            # 处理正文
                            if "attachment" not in content_disposition:
                                try:
                                    if content_type == "text/plain":
                                        text_body += part.get_payload(decode=True).decode(
                                            part.get_content_charset() or 'utf-8', errors='replace'
                                        )
                                    elif content_type == "text/html":
                                        html_body += part.get_payload(decode=True).decode(
                                            part.get_content_charset() or 'utf-8', errors='replace'
                                        )
                                except:
                                    pass
                            
                            # 处理附件
                            elif download_attachments and part.get_filename():
                                try:
                                    filename = decode_header(part.get_filename())[0][0]
                                    if isinstance(filename, bytes):
                                        filename = filename.decode('utf-8', errors='replace')
                                    
                                    filepath = os.path.join(attachment_dir, filename)
                                    with open(filepath, 'wb') as f:
                                        f.write(part.get_payload(decode=True))
                                    
                                    attachments_list.append({
                                        'filename': filename,
                                        'filepath': os.path.abspath(filepath),
                                        'size': len(part.get_payload(decode=True))
                                    })
                                except Exception as e:
                                    print(f"处理附件失败: {e}")
                    else:
                        # 单部分邮件
                        try:
                            text_body = msg.get_payload(decode=True).decode(
                                msg.get_content_charset() or 'utf-8', errors='replace'
                            )
                            total_size = len(msg.get_payload(decode=True))
                        except:
                            pass
                    
                    emails.append({
                        'subject': subject_str,
                        'from': msg.get('From', ''),
                        'to': msg.get('To', ''),
                        'date': msg.get('Date', ''),
                        'text_body': text_body.strip(),
                        'html_body': html_body.strip(),
                        'attachments': attachments_list,
                        'size': total_size
                    })
                    
                except Exception as e:
                    print(f"处理邮件 {mail_id} 失败: {e}")
                    continue
            
            mail.close()
            mail.logout()
            
            return {
                "success": True,
                "message": f"成功获取 {len(emails)} 封邮件",
                "email_count": len(emails),
                "emails": emails,
                "attachments_dir": attachment_dir if download_attachments else None
            }
            
        except Exception as e:
            mail.logout()
            return {
                "success": False,
                "message": f"邮件获取失败: {str(e)}",
                "email_count": 0,
                "emails": [],
                "attachments_dir": None
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"连接失败: {str(e)}",
            "email_count": 0,
            "emails": [],
            "attachments_dir": None
        }

# 别名 - 与pytoolsz的相关函数兼容
def quicksendemail(*args, **kwargs):
    """兼容旧版本的send_email函数别名"""
    return send_email(*args, **kwargs)

def quickemail(*args, **kwargs):
    """兼容旧版本的send_email函数别名"""
    return send_email(*args, **kwargs)

def load_email_by_subject(*args, **kwargs):
    """兼容旧版本的fetch_emails函数别名"""
    return fetch_emails(*args, **kwargs)