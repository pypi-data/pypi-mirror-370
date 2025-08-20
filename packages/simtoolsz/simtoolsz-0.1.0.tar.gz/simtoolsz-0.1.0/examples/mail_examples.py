#!/usr/bin/env python3
"""
邮件功能使用示例

这个文件展示了如何使用优化后的send_email和fetch_emails函数
"""

from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simtoolsz.mail import send_email, fetch_emails

def example_send_simple_email():
    """示例1: 发送简单文本邮件"""
    print("=== 示例1: 发送简单文本邮件 ===")
    
    result = send_email(
        email_account="your_email@qq.com",  # 替换为你的邮箱
        password="your_password",           # 替换为你的密码/授权码
        subject="测试邮件 - 简单文本",
        content="这是一封测试邮件，使用send_email函数发送。",
        recipients="recipient@example.com"  # 替换为收件人邮箱
    )
    
    print(f"发送结果: {result}")
    print()

def example_send_html_email():
    """示例2: 发送HTML格式邮件"""
    print("=== 示例2: 发送HTML格式邮件 ===")
    
    result = send_email(
        email_account="your_email@gmail.com",
        password="your_app_password",
        subject="测试邮件 - HTML格式",
        content="""
        <h1>欢迎使用邮件发送功能</h1>
        <p>这是一封<strong>HTML格式</strong>的测试邮件。</p>
        <ul>
            <li>支持HTML标签</li>
            <li>支持样式</li>
            <li>支持内嵌图片</li>
        </ul>
        """,
        recipients=["user1@example.com", "user2@example.com"],
        html_mode=True,
        sender_name="邮件机器人"
    )
    
    print(f"发送结果: {result}")
    print()

def example_send_with_attachments():
    """示例3: 发送带附件的邮件"""
    print("=== 示例3: 发送带附件的邮件 ===")
    
    # 创建测试文件
    test_file = Path("test_attachment.txt")
    test_file.write_text("这是一个测试附件文件的内容", encoding='utf-8')
    
    try:
        result = send_email(
            email_account="your_email@163.com",
            password="your_auth_code",
            subject="测试邮件 - 带附件",
            content="请查收附件中的测试文件。",
            recipients="boss@company.com",
            attachments=[str(test_file)],
            cc_recipients=["colleague@company.com"],
            signature="\n\n此致\n张三"
        )
        
        print(f"发送结果: {result}")
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()
    print()

def example_send_with_inline_images():
    """示例4: 发送带内嵌图片的邮件"""
    print("=== 示例4: 发送带内嵌图片的邮件 ===")
    
    # 创建测试图片文件（实际使用时替换为真实图片）
    # 这里只是示例，实际使用时需要提供真实图片路径
    
    result = send_email(
        email_account="your_email@qq.com",
        password="your_password",
        subject="产品展示邮件",
        content='''
        <h2>最新产品展示</h2>
        <p>请查看我们的最新产品图片：</p>
        <img src="cid:product_image" style="max-width: 500px;">
        <p>产品特点：</p>
        <ul>
            <li>高质量材料</li>
            <li>精美设计</li>
            <li>优惠价格</li>
        </ul>
        ''',
        recipients="client@example.com",
        html_mode=True,
        inline_images={
            "product_image": "path/to/your/product.jpg"  # 替换为实际图片路径
        },
        sender_name="销售部门"
    )
    
    print(f"发送结果: {result}")
    print()

def example_fetch_all_emails():
    """示例5: 获取所有邮件"""
    print("=== 示例5: 获取所有邮件 ===")
    
    result = fetch_emails(
        email_account="your_email@qq.com",
        password="your_password",
        max_emails=5
    )
    
    if result["success"]:
        print(f"成功获取 {result['email_count']} 封邮件")
        for i, email in enumerate(result["emails"], 1):
            print(f"邮件 {i}:")
            print(f"  主题: {email['subject']}")
            print(f"  发件人: {email['from']}")
            print(f"  日期: {email['date']}")
            print(f"  大小: {email['size']} bytes")
            print()
    else:
        print(f"获取失败: {result['message']}")
    print()

def example_fetch_by_subject():
    """示例6: 按主题搜索邮件"""
    print("=== 示例6: 按主题搜索邮件 ===")
    
    result = fetch_emails(
        email_account="your_email@gmail.com",
        password="your_app_password",
        subject="会议通知",
        search_mode="fuzzy",
        date_range=(datetime.now() - timedelta(days=30), datetime.now())
    )
    
    if result["success"] and result["emails"]:
        print(f"找到 {result['email_count']} 封匹配邮件")
        for email in result["emails"]:
            print(f"主题: {email['subject']}")
            print(f"正文预览: {email['text_body'][:100]}...")
            print()
    else:
        print("没有找到匹配的邮件")
    print()

def example_fetch_with_attachments():
    """示例7: 下载邮件附件"""
    print("=== 示例7: 下载邮件附件 ===")
    
    result = fetch_emails(
        email_account="your_email@163.com",
        password="your_auth_code",
        sender="reports@company.com",
        download_attachments=True,
        attachment_dir="./downloaded_reports"
    )
    
    if result["success"] and result["emails"]:
        print(f"成功获取 {result['email_count']} 封邮件")
        for email in result["emails"]:
            if email["attachments"]:
                print(f"邮件 "{email['subject']}" 包含 {len(email['attachments'])} 个附件:")
                for att in email["attachments"]:
                    print(f"  - {att['filename']} ({att['size']} bytes)")
                    print(f"    保存路径: {att['filepath']}")
    else:
        print("没有找到带附件的邮件")
    print()

def main():
    """运行所有示例"""
    print("邮件功能使用示例")
    print("=" * 50)
    
    # 注意：运行前请替换示例中的邮箱和密码为实际值
    
    # 示例1: 简单文本邮件
    # example_send_simple_email()
    
    # 示例2: HTML格式邮件
    # example_send_html_email()
    
    # 示例3: 带附件邮件
    # example_send_with_attachments()
    
    # 示例4: 带内嵌图片邮件
    # example_send_with_inline_images()
    
    # 示例5: 获取所有邮件
    # example_fetch_all_emails()
    
    # 示例6: 按主题搜索邮件
    # example_fetch_by_subject()
    
    # 示例7: 下载邮件附件
    # example_fetch_with_attachments()
    
    print("示例代码已准备就绪！")
    print("请根据注释替换邮箱地址和密码后运行相应示例。")
    print("\n注意事项:")
    print("1. QQ邮箱、163邮箱等需要使用授权码而非登录密码")
    print("2. Gmail需要使用应用专用密码")
    print("3. 确保网络连接正常")
    print("4. 附件路径需使用绝对路径或相对于脚本的路径")

if __name__ == "__main__":
    main()