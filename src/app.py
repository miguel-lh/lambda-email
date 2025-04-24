import json
from mailer_client import MailerLiteClient
import boto3
from botocore.exceptions import ClientError
from datetime import datetime


def get_secret(secret_name):
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager", region_name="us-west-1")

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name)
    except ClientError as e:
        raise e

    secret = get_secret_value_response["SecretString"]
    return secret


def lambda_handler(event, context):
    api_key = get_secret("test/email/Mailer")["MAILER_KEY"]

    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON in request body"}),
        }

    if "users" not in body:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'users' in request body"}),
        }

    users = body.get("users")
    if not users:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "'users' must be a non-empty list"}),
        }

    for i, user in enumerate(users):
        if not isinstance(user, dict) or "email" not in user or "name" not in user:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {
                        "error": f"Each user must be a dict with 'email' and 'name'. Error at index {i}"
                    }
                ),
            }

    if api_key is None:
        print("MAILER_KEY is not set in enviroment variables")
        # NOTE: return a status code if server has an error? 3xx
        exit(1)

    client = MailerLiteClient(api_key)

    users: list = event["users"]

    # unique name
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
    group_name = f"code group {timestamp}"

    # Check group exists
    group_available = client.group_exists(group_name)

    group_id: str

    if not group_available:
        # Create group
        status_code, result = client.create_group(group_name)
        client.check_status_code(status_code)
        group_id = result["data"]["id"]
    else:
        group_id = group_available["id"]

    print(f"{group_id=}")

    # Create users and add to group
    users_id: list[str] = []
    for user in users:
        status_code, result = client.add_user(
            email=user["email"], name=user["name"])
        client.check_status_code(status_code)
        user_id = result["data"]["id"]

        # HACK:
        user_is_subscribed = client.user_suscribed_to_group(user_id, group_id)
        if not user_is_subscribed:
            client.subscribe_user(user_id, group_id)

        users_id.append(user_id)

    print(f"{users_id=}")

    # # Create users and add to group
    # users_id: list[str] = []
    # for email, name in emails.items():
    #     status_code, result = client.add_user(email=email, name=name)
    #     client.check_status_code(status_code)
    #     user_id = result["data"]["id"]
    #
    #     # HACK:
    #     user_is_subscribed = client.user_suscribed_to_group(user_id, group_id)
    #     if not user_is_subscribed:
    #         client.subscribe_user(user_id, group_id)
    #
    #     users_id.append(user_id)
    #
    # print(f"{users_id=}")

    # NOTE: If a campaign is sent, it can not sent again (status: sent),
    # it can not change via API

    # Send existing campaign

    # campaign_id = "152433680782984339"  # campaign
    #
    # result = client.update_campaign_group(campaign_id, group_id)
    #
    # print(result)
    #
    # input()
    #
    # client.send_campaign(campaign_id)

    # Create campaign
    content = '<!doctype html>\n<html lang dir="ltr" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office"><head><!--{$head_top}-->\n    <meta charset="utf-8">\n    \n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=yes">\n    <meta name="format-detection" content="telephone=no, date=no, address=no, email=no, url=no">\n    <meta name="x-apple-disable-message-reformatting">\n    <!--[if !mso]>\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <![endif]-->\n    <!--[if mso]>\n    <style>\n        * { font-family: sans-serif !important; }\n    </style>\n    <noscript>\n        <xml>\n            <o:OfficeDocumentSettings>\n                <o:PixelsPerInch>96</o:PixelsPerInch>\n            </o:OfficeDocumentSettings>\n        </xml>\n    </noscript>\n    <![endif]-->\n    <style type="text/css">\n        /* Outlines the grids, remove when sending */\n        /*table td { border: 1px solid cyan; }*/\n        /* RESET STYLES */\n        html, body { margin: 0 !important; padding: 0 !important; width: 100% !important; height: 100% !important; }\n        body { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; text-rendering: optimizeLegibility;}\n        .document { margin: 0 !important; padding: 0 !important; width: 100% !important; }\n        img { border: 0; outline: none; text-decoration: none;  -ms-interpolation-mode: bicubic; }\n        table { border-collapse: collapse; }\n        table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }\n        body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }\n        h1, h2, h3, h4, h5, p { margin:0; word-break: break-word;}\n        /* iOS BLUE LINKS */\n        a[x-apple-data-detectors] {\n            color: inherit !important;\n            text-decoration: none !important;\n            font-size: inherit !important;\n            font-family: inherit !important;\n            font-weight: inherit !important;\n            line-height: inherit !important;\n        }\n        /* ANDROID CENTER FIX */\n        div[style*="margin: 16px 0;"] { margin: 0 !important; }\n        /* MEDIA QUERIES */\n        @media all and (max-width:639px){\n            .wrapper{ width:100%!important; }\n            .container{ width:100%!important; min-width:100%!important; padding: 0 !important; }\n            .row{padding-left: 20px!important; padding-right: 20px!important;}\n            .col-mobile {width: 20px!important;}\n            .table-between-col-mobile {width:100%!important;}\n            .col{display: block!important; width: 100%!important;}\n            .col-feature{display: block!important; width: 100%!important;}\n            .mobile-center{text-align: center!important; float: none!important;}\n            .mobile-mx-auto {margin: 0 auto!important; float: none!important;}\n            .mobile-left{text-align: center!important; float: left!important;}\n            .mobile-hide{display: none!important;}\n            .img{ width:100% !important; height:auto !important; }\n            .ml-btn { width: 100% !important; max-width: 100%!important;}\n            .ml-btn-container { width: 100% !important; max-width: 100%!important;}\n            *[class="mobileOff"] { width: 0px !important; display: none !important; }\n            *[class*="mobileOn"] { display: block !important; max-height:none !important; }\n            .mlContentTable{ width: 100%!important; min-width: 10%!important; margin: 0!important; float: none!important; }\n            .mlContentButton a { display: block!important; width: auto!important; }\n            .mlContentOuter { padding-bottom: 0px!important; padding-left: 15px!important; padding-right: 15px!important; padding-top: 0px!important; }\n            .mlContentSurvey { float: none!important; margin-bottom: 10px!important; width:100%!important; }\n            .multiple-choice-item-table { width: 100% !important; min-width: 10% !important; float: none !important; }\n            .ml-default, .ml-card, .ml-fullwidth { width: 100%; min-width: 100%; }\n        }\n\n        @media screen and (max-width: 600px) {\n            .col-feature {\n                margin-bottom: 30px;\n            }\n        }\n\n        /* Carousel style */\n        @media screen and (-webkit-min-device-pixel-ratio: 0) {\n            .webkit {\n                display: block !important;\n            }\n        }  @media screen and (-webkit-min-device-pixel-ratio: 0) {\n            .non-webkit {\n                display: none !important;\n            }\n        }  @media screen and (-webkit-min-device-pixel-ratio: 0) {\n            /* TARGET OUTLOOK.COM */\n            [class="x_non-webkit"] {\n                display: block !important;\n            }\n        }  @media screen and (-webkit-min-device-pixel-ratio: 0) {\n            [class="x_webkit"] {\n                display: none !important;\n            }\n        }\n    </style>\n    \n    <style type="text/css">@import url("https://assets.mlcdn.com/fonts-v2.css?version=1745332");</style>\n<style type="text/css">\n            @media screen {\n                body {\n                    font-family: \'Inter\', sans-serif;\n                }\n            }\n        </style><meta name="robots" content="noindex, nofollow">\n<title>prueba campaña</title>\n<!--{$head_bottom}--></head>\n<body style="margin: 0 !important; padding: 0 !important; background-color:#F4F7FA;"><!--{$body_top}-->\n\n    \n        \n        \n    \n\n    \n\n        \n            \n\n            \n            \n            \n            \n            \n            \n        \n\n        \n            \n\n            \n        \n\n        \n            \n\n            \n        \n\n    \n\n    \n\n        \n\n        \n\n        \n            \n            \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n        \n\n        \n            \n            \n        \n\n        \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n            \n            \n            \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n            \n            \n            \n            \n            \n            \n        \n\n        \n\n            \n                \n                \n                \n                \n                \n            \n\n            \n                \n                \n                \n            \n\n            \n                \n                \n                \n                \n                \n            \n\n            \n                \n                \n                \n                \n                \n            \n\n            \n                \n                \n                \n                \n                \n            \n\n            \n                \n                \n                \n                \n            \n\n            \n                \n                \n            \n\n            \n                \n                \n            \n\n        \n    \n\n    <div class="document" role="article" aria-roledescription="email" aria-label lang dir="ltr" style="background-color:#F4F7FA; line-height: 100%; font-size:medium; font-size:max(16px, 1rem);">\n\n        <!--[if gte mso 9]>\n        <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t" if="variable.bodyBackgroundImage.value">\n            <v:fill type="tile" src="" color="#F4F7FA"/>\n        </v:background>\n        <![endif]-->\n\n        \n\n        <table width="100%" align="center" cellspacing="0" cellpadding="0" border="0">\n            <tr>\n                <td class background bgcolor="#F4F7FA" align="center" valign="top" style="padding: 0 8px;">\n\n                    <table class="container" align="center" width="640" cellpadding="0" cellspacing="0" border="0" style="max-width: 640px;">\n    <tr>\n        <td align="center">\n            \n\n                \n\n                <table align="center" width="100%" cellpadding="0" cellspacing="0" border="0">\n                    <tr>\n                        <td colspan="2" height="20" style="line-height: 20px"></td>\n                    </tr>\n                    <tr>\n                        \n                        <td align="left" style="font-family: \'Inter\', sans-serif; color: #111111; font-size: 12px; line-height: 18px;">\n                            \n                            \n                        </td>\n                        \n                        <td align="right" style="font-family: \'Inter\', sans-serif; color: #111111; font-size: 12px; line-height: 18px;">\n                            <a style="color: #111111; font-weight: normal; font-style: normal; text-decoration: underline;" href="{$url}" data-link-id="152432757093434783" data-link-type="webview">View in browser</a>&nbsp;\n                        </td>\n                    </tr>\n                    <tr>\n                        <td colspan="2" height="20" style="line-height: 20px;"></td>\n                    </tr>\n                </table>\n\n                \n\n                \n                    \n                    \n                    \n                \n\n                \n                    \n                    \n                \n\n            \n        </td>\n    </tr>\n</table>\n\n\n                    <table width="640" class="wrapper" align="center" border="0" cellpadding="0" cellspacing="0" style="\n                        max-width: 640px;\n                        border:1px solid #E5E5E5;\n                        border-radius:8px; border-collapse: separate!important; overflow: hidden;\n                        ">\n                        <tr>\n                            <td align="center">\n\n                                \n    <!-- {% if true %} -->\n<table class="ml-default" width="100%" bgcolor border="0" cellspacing="0" cellpadding="0">\n    <tr>\n        <td style>\n            \n                \n                \n\n                \n                \n\n                <table class="container ml-4 ml-default-border" width="640" bgcolor="#ffffff" align="center" border="0" cellspacing="0" cellpadding="0" style="\n                width: 640px; min-width: 640px;\n                ;\n                \n                ">\n                    <tr>\n                        <td class="ml-default-border container" height="40" style="line-height: 40px; min-width: 640px;"></td>\n                    </tr>\n                    <tr>\n                        <td>\n\n    \n    \n    \n    \n\n\n<table align="center" width="100%" border="0" cellspacing="0" cellpadding="0">\n    <tr>\n        <td class="row mobile-center" align="center" style="padding: 0 50px;">\n            \n\n    \n\n\n\n\n\n\n<img src="https://storage.mlcdn.com/account_image/1043022/VmjzhOMrYV5tCc5ld0UYBqeBLWRCTaDhNdYB8CjL.png" border="0" alt width="120" class="logo" style="max-width: 120px; display: inline-block;">\n\n\n\n\n\n\n\n\n        </td>\n    </tr>\n    <tr>\n        <td height="25" style="line-height: 25px;"></td>\n    </tr>\n    \n    <tr>\n        <td class="row mobile-center" style="padding: 0 50px;" align="center">\n            \n\n    \n\n\n<table class="menu mobile-mx-auto" width cellpadding="0" cellspacing="0" border="0">\n    <tr>\n        <td align="center" class="menu-item" style="padding: 0 20px 0 0;">\n            <a href="https://" target="blank" style="font-family: \'Inter\', sans-serif; font-size: 14px; line-height: 150%; color: #2C438D; font-weight: normal; font-style: normal; text-decoration: none;" data-link-id="152432757100774816">\n                <span style="color: #2C438D;">About</span>\n            </a>\n        </td><td align="center" class="menu-item" style="padding: 0 20px 0 20px;">\n            <a href="https://" target="blank" style="font-family: \'Inter\', sans-serif; font-size: 14px; line-height: 150%; color: #2C438D; font-weight: normal; font-style: normal; text-decoration: none;" data-link-id="152432757106017698">\n                <span style="color: #2C438D;">New!</span>\n            </a>\n        </td><td align="center" class="menu-item" style="padding: 0 0 0 20px;">\n            <a href="https://" target="blank" style="font-family: \'Inter\', sans-serif; font-size: 14px; line-height: 150%; color: #2C438D; font-weight: normal; font-style: normal; text-decoration: none;" data-link-id="152432757109163427">\n                <span style="color: #2C438D;">Shop</span>\n            </a>\n        </td>\n    </tr>\n</table>\n\n\n\n\n        </td>\n    </tr>\n    \n</table>\n\n\n    \n    \n    \n    \n    \n\n\n\n    \n    \n\n\n\n\n                            </td>\n                    </tr>\n                    <tr>\n                        <td height="40" style="line-height: 40px;"></td>\n                    </tr>\n                </table>\n                \n                    \n                    \n                \n            \n        </td>\n    </tr>\n</table>\n<!-- {% endif %} -->\n\n\n    <!-- {% if true %} -->\n<table class="ml-default" width="100%" bgcolor border="0" cellspacing="0" cellpadding="0">\n    <tr>\n        <td style>\n            \n                \n                \n                \n                \n                \n                \n                \n                \n\n                <table class="ml-default-border" width="100%" align="center" bgcolor="#ffffff" border="0" cellspacing="0" cellpadding="0" style="\n                ;\n                \n                ">\n                    <tr>\n                        <td class="ml-default-border" background style="background-size: cover; background-position: center center;" valign="top" align="center">\n\n                            \n                            <table class="container ml-9" width="640" align="center" border="0" cellpadding="0" cellspacing="0" style="color: #242424; width: 640px; min-width: 640px;">\n                                <tr>\n                                    <td class="container" height="20" style="line-height: 20px; min-width: 640px;"></td>\n                                </tr>\n                                <tr>\n                                    <td>\n\n    \n    \n\n\n\n\n\n\n    <table class="container" width="640" border="0" cellspacing="0" cellpadding="0">\n        <tr>\n            <td class="row" align="center" style="padding: 0 50px" colspan="3">\n                \n\n    \n    <img src="https://storage.mlcdn.com/account_image/1043022/tlW3EOUmz0rNUT4J9PILS6KXxubqO4LNUAxWKS79.png" border="0" alt class="img" width="540" style="display: block;">\n\n\n\n            </td>\n        </tr>\n        <tr>\n            <td class="col-mobile" width="50" height="0" style="line-height: 0;"></td>\n            <td>\n                <table class="table-between-col-mobile" width="540" border="0" cellspacing="0" cellpadding="0">\n                    <tr>\n                        <td height="30" style="line-height:30px;"></td>\n                    </tr>\n                    <tr>\n                        <td>\n                            <h1 style="font-family: \'Inter\', sans-serif; color: #2C438D; font-size: 36px; line-height: 125%; font-weight: bold; font-style: normal; text-decoration: none; ;margin-bottom: 10px; text-align: center;">Cotización</h1>\n<p style="font-family: \'Inter\', sans-serif; color: #242424; font-size: 16px; line-height: 165%; margin-top: 0; margin-bottom: 0; text-align: center;">{$name} ha recibido una nueva cotización</p>\n                        </td>\n                    </tr>\n                    <tr>\n                        <td height="30" style="line-height:30px;"></td>\n                    </tr>\n                    <tr>\n                        <td align="center">\n                            \n\n    \n    \n    \n    \n\n    \n\n\n\n\n\n\n                        </td>\n                    </tr>\n                    \n                    \n                </table>\n            </td>\n            <td class="col-mobile" width="50" height="0" style="line-height: 0;"></td>\n        </tr>\n    </table>\n\n\n\n\n    \n    \n    \n    \n    \n\n\n\n    \n    \n    \n    \n    \n\n\n\n    \n    \n    \n    \n    \n\n\n\n    \n    \n    \n    \n    \n\n\n\n    \n    \n    \n    \n\n\n\n    \n    \n\n\n\n\n\n\n    \n    \n    \n    \n    \n    \n    \n    \n    \n    \n    \n\n\n\n\n\n\n\n\n    \n    \n    \n    \n    \n    \n    \n    \n    \n    \n\n\n\n\n\n\n\n                                        </td>\n                                </tr>\n                                <tr>\n                                    <td height="40" style="line-height: 40px;"></td>\n                                </tr>\n                            </table>\n\n                            \n                            \n                                \n                            \n\n                        </td>\n                    </tr>\n                </table>\n\n            \n        </td>\n    </tr>\n</table>\n<!-- {% endif %} -->\n\n\n    <!-- {% if true %} -->\n<table class="ml-default" width="100%" bgcolor border="0" cellspacing="0" cellpadding="0">\n    <tr>\n        <td style>\n            \n\n                \n                \n\n                \n                \n\n                <table class="container ml-11 ml-default-border" width="640" bgcolor="#ffffff" align="center" border="0" cellspacing="0" cellpadding="0" style="\n                width: 640px; min-width: 640px;\n                ;\n                \n                ">\n                    <tr>\n                        <td class="ml-default-border container" height="40" style="line-height: 40px; min-width: 640px;"></td>\n                    </tr>\n                    <tr>\n                        <td class="row" style="padding: 0 50px;">\n\n\n    \n    \n\n<table align="center" width="100%" cellpadding="0" cellspacing="0" border="0">\n    <tr>\n        <td class="col" align="left" width="250" valign="top" style="text-align: left!important;">\n            \n                <h5 style="font-family: \'Inter\', sans-serif; color: #2C438D; font-size: 15px; line-height: 125%; font-weight: bold; font-style: normal; text-decoration: none; margin-bottom: 6px;">Valle de los Ángeles</h5>\n            \n            <p style="font-family: \'Inter\', sans-serif; color: #242424; font-size: 14px; line-height: 150%; margin-bottom: 6px;"><strong>Valle de los Ángeles</strong></p>\n<p style="font-family: \'Inter\', sans-serif; color: #242424; font-size: 14px; line-height: 150%; margin-bottom: 6px;">T. 222 237 4455</p>\n<p style="font-family: \'Inter\', sans-serif; color: #242424; font-size: 14px; line-height: 150%; margin-bottom: 6px;">Av. Manuel Espinosa Yglesias 1212, Puebla<br>Col. Ladrillera de Benítez,&nbsp;Puebla, Puebla,&nbsp;México</p>\n\n            <table width="100%" cellpadding="0" cellspacing="0" border="0">\n                <tr>\n                    <td height="16" style="line-height: 16px;"></td>\n                </tr>\n                <tr>\n                    <td>\n                        \n\n\n\n\n<table class="**$class**" role="presentation" cellpadding="0" cellspacing="0" border="0">\n    <tr>\n        <td align="center" valign="middle" width="18" ng-show="slink.link != \'\'" style="padding: 0 5px 0 0;">\n            <a href="https://www.facebook.com/grupovalledelosangeles" target="blank" style="text-decoration: none;" data-link-id="152432757113357733">\n                <img src="https://assets.mlcdn.com/ml/images/icons/default/rounded_corners/black/facebook.png" width="18" alt="facebook">\n            </a>\n        </td><td align="center" valign="middle" width="18" ng-show="slink.link != \'\'" style="padding: 0 0 0 5px;">\n            <a href="https://www.instagram.com/funerariavalledelosangeles/" target="blank" style="text-decoration: none;" data-link-id="152432757117552038">\n                <img src="https://assets.mlcdn.com/ml/images/icons/default/rounded_corners/black/instagram.png" width="18" alt="instagram">\n            </a>\n        </td>\n    </tr>\n</table>\n\n                        \n                    </td>\n                </tr>\n            </table>\n        </td>\n        <td class="col" width="40" height="30" style="line-height: 30px;"></td>\n        <td class="col" align="left" width="250" valign="top" style="text-align: left!important;">\n            \n                <p style="font-family: \'Inter\', sans-serif; color: #242424; font-size: 14px; line-height: 150%; margin-bottom: 6px;">You received this email because you signed up on our website or made a purchase from us.</p>\n            \n\n            <table width="100%" cellpadding="0" cellspacing="0" border="0">\n                <tr>\n                    <td height="8" style="line-height: 8px;"></td>\n                </tr>\n                <tr>\n                    <td align="left">\n                        <p style="font-family: \'Inter\', sans-serif; color: #242424; font-size: 14px; line-height: 150%; margin-bottom: 0;">\n                            <a href="{$unsubscribe}" style="color: #242424; font-weight: normal; font-style: normal; text-decoration: underline;" data-link-id="152432757120697769" data-link-type="unsubscribe">Unsuscribe</a>\n                            \n                            \n                            \n                        </p>\n                    </td>\n                </tr>\n            </table>\n        </td>\n    </tr>\n</table>\n\n\n\n\n\n\n\n\n    \n    \n    \n    \n    \n\n\n\n    \n    \n    \n    \n\n\n\n    \n    \n\n\n\n\n\n    \n    \n    \n\n\n\n                            </td>\n                    </tr>\n                    <tr>\n                        <td height="40" style="line-height: 40px;"></td>\n                    </tr>\n                </table>\n                \n                    \n                    \n                \n            \n        </td>\n    </tr>\n</table>\n<!-- {% endif %} -->\n\n\n\n                            </td>\n                        </tr>\n                    </table>\n\n                    <table cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="max-width: 640px; width: 100%;">\n    <tr class="ml-hide-branding">\n        <td height="40" style="line-height: 40px;"></td>\n    </tr>\n    <tr class="ml-hide-branding">\n        <td align="center">\n            <a href="https://www.mailerlite.com" target="_blank" style="text-decoration: none;" data-link-id="152432757125940650">\n                <img width="100" border="0" alt="Sent by MailerLite" src="https://assets.mlcdn.com/ml/logo/sent-by-mailerlite.png" style="display: block;">\n            </a>\n        </td>\n    </tr>\n    <tr class="ml-hide-branding">\n        <td height="40" style="line-height: 40px;"></td>\n    </tr>\n</table>\n\n\n                </td>\n            </tr>\n        </table>\n\n    </div>\n\n    \n\n    \n\n<!--{$body_bottom}--></body>\n</html>'

    status_code, result = client.create_campaign(
        name="lambda campaña",
        groups=[group_id],
        subject="prueba campaña",
        from_email="contacto@valledelosangeles.com",
        from_name="Valle de los Ángeles",
        content=content,
    )

    # TODO: Check status code
    print(f"Create campaign status code: {status_code}")

    campaign_id = result["data"]["id"]

    print(f"{campaign_id=}")

    # Send campaign
    status_code, result = client.send_campaign(campaign_id)

    print(f"Send campaign status code: {status_code}")

    # NOTE: If delete campaign and group immediately, it does not send emails

    # # Delete campaign
    # # TODO: status code and result
    # status_code = client.delete_campaign(campaign_id)
    #
    # print(f"{status_code}")

    # # Delete group
    # # TODO: status code and result
    # status_code = client.delete_group(group_id)
    #
    # print(f"{status_code}")

    return {"statusCode": 200, "body": json.dumps({"message": "mails are being sent"})}
