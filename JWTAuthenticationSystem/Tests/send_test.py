import resend

# 1. Set your API Key (USE YOUR NEW API KEY HERE)
resend.api_key = "my api key"

# 2. Define the email details with HTML styling and an image
html_content = """
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
                <!-- Main Card -->
                <table width="100%" max-width="600px" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    
                    <!-- Image Header -->
                    <tr>
                        <td align="center" style="padding: 0;">
                            <!-- Using a reliable placeholder image. You can replace this URL with your own logo later -->
                            <img src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?q=80&w=600&auto=format&fit=crop" alt="Security Banner" width="100%" style="display: block; max-width: 600px; height: auto; border: 0;" />
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px 0; color: #1a202c; font-size: 24px; font-weight: 600; text-align: center;">Secure Login Verification</h2>
                            
                            <p style="margin: 0 0 24px 0; color: #4a5568; font-size: 16px; line-height: 1.6; text-align: center;">
                                Please use the following One-Time Password (OTP) to complete your login. This code is highly confidential.
                            </p>

                            <!-- OTP Box -->
                            <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td align="center">
                                        <div style="background-color: #f7fafc; border: 2px dashed #cbd5e0; border-radius: 8px; padding: 20px; display: inline-block;">
                                            <span style="font-family: 'Courier New', Courier, monospace; font-size: 32px; font-weight: bold; color: #2b6cb0; letter-spacing: 8px;">849201</span>
                                        </div>
                                    </td>
                                </tr>
                            </table>

                            <p style="margin: 24px 0 0 0; color: #e53e3e; font-size: 14px; text-align: center; font-weight: 500;">
                                ⏳ This code will expire in 2 minutes.
                            </p>
                            
                            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;" />

                            <p style="margin: 0; color: #a0aec0; font-size: 13px; text-align: center; line-height: 1.5;">
                                If you didn't request this code, you can safely ignore this email.<br>
                                Someone may have typed your email address by mistake.
                            </p>
                        </td>
                    </tr>
                </table>
                
                <!-- Footer -->
                <table width="100%" max-width="600px" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; margin-top: 20px;">
                    <tr>
                        <td align="center" style="color: #a0aec0; font-size: 12px;">
                            © 2024 Patients Management System. All rights reserved.
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

params: resend.Emails.SendParams = {
    # While testing, you MUST use onboarding@resend.dev as the sender
    "from": "Patients Management System <onboarding@resend.dev>", 
    
    # IMPORTANT: While testing, this MUST be the exact email address you used to sign up for Resend
    "to": ["murtaza.tanveer488@gmail.com"], 
    
    "subject": "Your Secure OTP Code",
    "html": html_content,
}

# 3. Send the email
try:
    print("Sending email...")
    email = resend.Emails.send(params)
    print("Success! Email sent.")
    print(f"Message ID: {email['id']}")
except Exception as e:
    print(f"Failed to send email. Error: {e}")