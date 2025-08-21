'''
Author: 凌逆战 | Never
Date: 2025-02-13 20:06:07
Description: 请填写文件描述
'''
# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/2/1
"""
通过邮件发送通知
"""
import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart


def send_QQEmail(title, content, from_name, from_email, from_password, to_email):
    """
    Args:
        title: 邮件标题
        content: 邮件内容
        from_email: 设置发件人邮箱地址 "xxxx@qq.com"
        from_password: SMTP 授权码
        to_email: 设置收件人邮箱地址 "xxxx@qq.com"
    """
    # 设置邮箱的域名
    HOST = "smtp.qq.com"

    # 设置邮件正文
    message = MIMEText(content, "plain", "utf-8")
    message["Subject"] = Header(title, charset="utf-8")
    message["From"] = formataddr((from_name, from_email))
    # message["From"] = Header(from_email)
    message["To"] = Header(to_email)

    try:
        # 使用SSL连接
        server = smtplib.SMTP_SSL(HOST)
        server.connect(HOST, 465)
        server.login(from_email, from_password)  # 登录邮箱
        server.sendmail(from_email, to_email, message.as_string())  # 发送邮件
        server.quit()  # 关闭SMTP服务器
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败：{e}")


def send_QQEmail_with_images(title, content, from_name, from_email, from_password, to_email, image_paths):
    """
    发送包含多张PNG图片附件的QQ邮件
    :param title: 邮件标题
    :param content: 邮件正文内容（支持HTML格式）
    :param from_email: 发件人邮箱
    :param from_password: 发件人邮箱SMTP授权码
    :param to_email: 收件人邮箱
    :param image_paths: 图片文件路径列表, 应为PNG格式
    """
    # 设置邮箱的域名
    HOST = "smtp.qq.com"
    # 创建一个MIMEMultipart对象来包含邮件的各个部分
    message = MIMEMultipart()
    message["Subject"] = Header(title, charset="utf-8")
    message["From"] = formataddr((from_name, from_email))
    message["To"] = Header(to_email)

    # 准备HTML内容
    html_content = content + "<br>"

    # 循环处理每张图片
    for index, image_path in enumerate(image_paths):
        try:
            # 生成图片的Content-ID
            image_id = f'image{index + 1}'
            cid = f"<{image_id}>"

            # 在HTML内容中添加图片引用
            html_content += f'<br><img src="cid:{image_id}" style="max-width:100%; max-height:100%;"><br>'

            # 打开图片文件并将其添加到邮件中
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()

            # 使用 MIMEImage 添加图片
            image_part = MIMEImage(img_data)

            # 设置Content-ID, 以便在正文中引用图片
            image_part.add_header('Content-ID', cid)

            # 设置为 inline 显示, 避免附件处理
            image_part.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))

            # 添加图片到邮件
            message.attach(image_part)
        except Exception as e:
            print(f"添加图片 {image_path} 失败: {e}")

    # 添加邮件正文
    text_part = MIMEText(html_content, "html", "utf-8")
    message.attach(text_part)

    try:
        # 使用SSL连接
        server = smtplib.SMTP_SSL(HOST)
        server.connect(HOST, 465)
        server.login(from_email, from_password)  # 登录邮箱
        server.sendmail(from_email, to_email, message.as_string())  # 发送邮件
        server.quit()  # 关闭SMTP服务器
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败：{e}")


if __name__ == "__main__":
    send_QQEmail("实验跑完", "实验跑完了, 快去看看吧！",
                 from_email="1786088386@qq.com", from_password="xxxx",
                 to_email="1786088386@qq.com")
    pass
