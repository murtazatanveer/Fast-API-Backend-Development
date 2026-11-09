import asyncio

import resend

from Configuration.config import settings

resend.api_key = settings.resend_api_key


def maskEmail(email: str) -> str:
    local_part, domain = email.split("@", 1)
    visible = local_part[:1] if len(local_part) <= 2 else local_part[:2]
    return f"{visible}***@{domain}"


def buildOtpEmailHtml(otp: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f4f7f6; padding: 40px 0;">
        <tr>
            <td align="center">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px 0; color: #1a202c; font-size: 24px; font-weight: 600; text-align: center;">Secure Login Verification</h2>
                            <p style="margin: 0 0 24px 0; color: #4a5568; font-size: 16px; line-height: 1.6; text-align: center;">
                                Please use the following One-Time Password (OTP) to complete your login. This code is highly confidential.
                            </p>
                            <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td align="center">
                                        <div style="background-color: #f7fafc; border: 2px dashed #cbd5e0; border-radius: 8px; padding: 20px; display: inline-block;">
                                            <span style="font-family: 'Courier New', Courier, monospace; font-size: 32px; font-weight: bold; color: #2b6cb0; letter-spacing: 8px;">{otp}</span>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            <p style="margin: 24px 0 0 0; color: #e53e3e; font-size: 14px; text-align: center; font-weight: 500;">
                                This code will expire in {settings.otp_expire_minutes} minutes.
                            </p>
                            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;" />
                            <p style="margin: 0; color: #a0aec0; font-size: 13px; text-align: center; line-height: 1.5;">
                                If you didn't request this code, you can safely ignore this email.<br>
                                Someone may have typed your email address by mistake.
                            </p>
                        </td>
                    </tr>
                </table>
                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; margin-top: 20px;">
                    <tr>
                        <td align="center" style="color: #a0aec0; font-size: 12px;">
                            &copy; 2026 Patients Management System. All rights reserved.
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


async def sendOtpEmail(email: str, otp: str) -> None:
    params = {
        "from": f"Patients Management System <{settings.otp_from_email}>",
        "to": [email],
        "subject": "Your Secure OTP Code",
        "html": buildOtpEmailHtml(otp),
    }
    await asyncio.to_thread(resend.Emails.send, params)
