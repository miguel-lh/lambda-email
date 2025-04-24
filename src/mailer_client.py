import requests


class MailerLiteClient:
    def __init__(self, api_key: str):
        self.api_key: str = api_key
        self.headers: dict = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        self._status_codes: dict = {
            200: "Ok",
            201: "Created",
            422: "Unprocessable Entity",
        }

    def check_status_code(self, status_code: int):
        """
        Checks the provided HTTP status code against predefined status codes.

        If the status code is not defined in the _status_codes dictionary,
        it prints an undefined status message and exits the program.

        If the status code is 422, it prints the corresponding status message
        and exits the program.

        For all other defined status codes, it prints the status code and
        its corresponding message.

        Args:
            status_code (int): The HTTP status code to check.
        """

        status = self._status_codes.get(status_code)

        if not status:
            print(f"Status code not defined: {status}")
            # NOTE: Return status code in json
            exit(0)

        print(f"{status_code}: {self._status_codes[status_code]}")

        if status_code == 422:
            # NOTE: Return status code in json
            exit(0)

    def post(self, url: str, data: dict) -> tuple[int, dict]:
        """
        Sends a POST request to the specified URL with the provided JSON data.

        This method utilizes the `requests` library to send an HTTP POST
        request to the given URL, including the specified data as a JSON
        payload.

        Parameters:
            url (str): The endpoint URL to which the POST request will be sent.
            data (dict): A dictionary representing the JSON payload to include
                         in the request body.

        Returns:
            tuple:
                - int: The HTTP status code returned by the server.
                - dict: The JSON-decoded response content from the server.

        Example:
        status_code, response_data = self.post("https://api.example.com/data", {"key": "value"})
        """

        try:
            response = requests.post(url, headers=self.headers, json=data)
        except Exception as error:
            print(f"{error=}")
            # NOTE: return a status code if server has an error? 3xx

        return response.status_code, response.json()

    def user_exists(self, email: str) -> tuple[int, dict] | None:
        """
        Checks if a user (subscriber) exists by their email address.

        Sends a GET request to the MailerLite API with the given email.
        If the request is successful (HTTP 200), returns the status code and
        the user data as JSON.
        If the user does not exist or an error occurs, returns None.

        Args:
            email (str): The email address of the subscriber to check.

        Returns:
            tuple[int, dict] | None: A tuple containing the status code and
                                     user data if found, otherwise None.
        """

        try:
            response = requests.get(
                f"https://connect.mailerlite.com/api/subscribers/{email}",
                headers=self.headers,
            )
        except Exception as error:
            print(f"{error=}")
            # NOTE: return a status code if server has an error? 3xx

        if response.status_code == 200:
            return response.status_code, response.json()

        return None

    def add_user(self, email: str, name: str, last_name=None) -> tuple[int, dict]:
        """
        Parameters:
            email (str): The subscriber's email address.
            groups (list): A group IDs (strings) to which the subscriber should
                           be added. The groups must exist in the
                           MailerLite account.

        Returns:
            tuple:
                - int: The HTTP status code returned by the server.
                - dict: The JSON-decoded response content from the server.

        Reference:
            MailerLite API Documentation:
            https://developers.mailerlite.com/docs/subscribers
        """

        user_available = self.user_exists(email)

        if user_available:
            return user_available

        data = {}
        data["email"] = email
        data["fields"] = {"name": name, "last_name": last_name}

        return self.post("https://connect.mailerlite.com/api/subscribers", data)

    def user_suscribed_to_group(self, user_id: str, group_id) -> dict | None:
        """
        Checks if a specific user is subscribed to a given group.

        Sends a GET request to the MailerLite API to retrieve all subscribers
        of the specified group.
        Iterates through the subscriber list to check if the user ID exists in
        the group's data.
        Returns the subscriber's data if found, otherwise returns None.

        Args:
            user_id (str): The ID of the user to check.
            group_id (str): The ID of the group to search within.

        Returns:
            dict | None: A dictionary with the subscriber's data if they are
                         in the group, otherwise None.
        """

        try:
            response = requests.get(
                f"https://connect.mailerlite.com/api/groups/{
                    group_id}/subscribers",
                headers=self.headers,
            )
        except Exception as error:
            print(f"{error=}")
            # NOTE: return a status code if server has an error? 3xx

        result = response.json()

        for item in result["data"]:
            if item.get("id") == user_id:
                return item  # dict

        return None

    def subscribe_user(self, user_id: str, group_id) -> int:
        """
        Subscribes a user to a specific group.

        Sends a POST request to the MailerLite API to add the specified user
        to the given group.
        Handles exceptions during the request and prints the error
        if one occurs.
        Returns the HTTP status code of the response.

        Args:
            user_id (str): The ID of the user to subscribe.
            group_id (str): The ID of the group to subscribe the user to.

        Returns:
            int: The HTTP status code of the API response.
        """

        try:
            response = requests.post(
                f"https://connect.mailerlite.com/api/subscribers/{user_id}/groups/{
                    group_id
                }",
                headers=self.headers,
            )
        except Exception as error:
            print(f"{error=}")
            # NOTE: return a status code if server has an error? 3xx

        return response.status_code

    def delete_user(self, user_id: str) -> int:
        """
        Deletes a subscriber from your MailerLite account.

        This method sends a DELETE request to the MailerLite API to
        remove a subscriber identified by their unique ID.

        Parameters:
            user_id (str): The unique identifier of the
                           subscriber to be deleted.

        Returns:
            int: The HTTP status code returned by the MailerLite API.

        Reference:
            MailerLite API Documentation:
            https://developers.mailerlite.com/docs/subscribers
        """

        try:
            response = requests.delete(
                f"https://connect.mailerlite.com/api/subscribers/{user_id}",
                headers=self.headers,
            )
        except Exception as error:
            print(f"{error=}")
            # NOTE: return a status code if server has an error? 3xx

        return response.status_code

    def group_exists(self, group_name: str):
        """
        Checks if a group with the specified name exists.

        Sends a GET request to the MailerLite API to retrieve all groups.
        Iterates through the groups and compares their names with the provided
        group name.
        Handles request exceptions and prints any errors.
        Returns the group data as a dictionary if found,
        otherwise returns None.

        Args:
            group_name (str): The name of the group to search for.

        Returns:
            dict or None: The group data if found, otherwise None.
        """

        try:
            response = requests.get(
                "https://connect.mailerlite.com/api/groups",
                headers=self.headers,
            )
        except Exception as error:
            print(f"{error=}")
            # NOTE: return a status code if server has an error? 3xx

        result = response.json()

        for item in result["data"]:
            if item.get("name") == group_name:
                return item  # dict

        return None

    def create_group(self, name: str) -> tuple[int, dict]:
        """
        Creates a new subscriber group in the MailerLite account.

        This method sends a POST request to the MailerLite API
        to create a new group with the specified name. Groups are used to
        organize subscribers and target specific users for certains cases.

        Parameters:
            name (str): The name of the group to be created.
                        Must be a non-empty string.

        Returns:
            tuple:
                - int: The HTTP status code returned by the MailerLite API.
                - dict: The JSON-decoded response content from the server,
                        containing details of the newly created group or
                        error information.

        Reference:
            MailerLite API Documentation:
            https://developers.mailerlite.com/docs/groups
        """

        data = {}
        data["name"] = name

        return self.post("https://connect.mailerlite.com/api/groups", data=data)

    def delete_group(self, group_id: str) -> int:
        """
        Deletes a subscriber group from your MailerLite account.

        This method sends a DELETE request to the MailerLite API to remove a
        subscriber group identified by its unique ID. Deleting a group does not
        delete the subscribers within it; it only removes the group itself.

        Parameters:
            group_id (str): The unique identifier of the group to be deleted.

        Returns:
            int: The HTTP status code returned by the MailerLite API.
                 Typically, a 204 No Content status indicates a
                 successful deletion.

        Reference:
            MailerLite API Documentation:
            https://developers.mailerlite.com/docs/groups
        """
        try:
            response = requests.delete(
                f"https://connect.mailerlite.com/api/groups/{group_id}",
                headers=self.headers,
            )
        except Exception as error:
            print(f"{error=}")
            # NOTE: return a status code if server has an error? 3xx

        return response.status_code

    def create_campaign(
        self,
        name: str,
        groups,
        from_email: str,
        from_name: str,
        subject: str,
        content: str,
    ) -> tuple[int, dict]:
        """
        Creates a new email campaign in your MailerLite account.

        This method sends a POST request to the MailerLite API to create a new
        email campaign with the specified parameters.
        The campaign includes details such as the campaign name, type,
        target groups, sender information, subject line, and email content.

        Parameters:
            name (str): The internal name of the campaign. This is used for
                        identification within the account.
            groups (list): A list of group IDs to which the campaign
                           will be sent.
            from_email (str): The sender's email address. Must be a verified
                              email in your MailerLite account.
            from_name (str): The name that will appear as the sender.
            subject (str): The subject line of the email.
            content (str): The HTML content of the email. This should be a
                           well-formed HTML string.

        Returns:
            tuple:
                - int: The HTTP status code returned by the MailerLite API.
                - dict: The JSON-decoded response content from the server,
                        containing details of the newly created campaign or
                        error information.

        Notes:
            - Ensure that the 'from_email' is a verified sender in the
              MailerLite account.
            - The 'content' should include all necessary HTML elements,
              including an unsubscribe link.

        Reference:
            MailerLite API Documentation:
            https://developers.mailerlite.com/docs/campaigns
        """

        type = "regular"

        data = {
            "name": name,
            "type": type,
            "groups": groups,
            "emails": [
                {
                    "subject": subject,
                    "from": from_email,
                    "from_name": from_name,
                    "content": content,
                }
            ],
        }

        return self.post("https://connect.mailerlite.com/api/campaigns", data=data)

    def get_campaign(self, campaign_id: str) -> dict:
        """
        Retrieves the details of a specific campaign by its ID.

        Sends a GET request to the MailerLite API to
        retrieve the campaign information.
        Handles request exceptions and prints any errors encountered
        during the request.
        Returns the JSON response containing campaign details.

        Args:
            campaign_id (str): The ID of the campaign to retrieve.

        Returns:
            dict: The JSON response containing the campaign details.
        """

        try:
            response = requests.get(
                f"https://connect.mailerlite.com/api/campaigns/{campaign_id}",
                headers=self.headers,
            )
        except Exception as error:
            print(f"{error=}")

        return response.json()

    def update_campaign_group(self, campaign_id: str, group_id: str):
        """
        Updates the group of a specific campaign.

        Retrieves the current campaign data and updates the campaign
        with a new group ID.
        The method maintains other campaign details such as name,
        email content, and subject.
        Handles request exceptions and prints any errors encountered
        during the request.
        Returns the JSON response with the updated campaign data.

        Args:
            campaign_id (str): The ID of the campaign to update.
            group_id (str): The new group ID to associate with the campaign.

        Returns:
            dict: The JSON response containing the updated campaign details.
        """

        old_data = self.get_campaign(campaign_id)["data"]
        # TODO: Check if campaign_id exists
        # TODO: Check if overwritten groups

        data = {
            "name": old_data["name"],
            # "type": type,
            "groups": [group_id],
            "emails": [
                {
                    "subject": "prueba campaña",
                    "from": "contacto@valledelosangeles.com",
                    "from_name": "Valle de los Ángeles",
                    # "content": old_data["emails"][0]["content"],
                    # HACK:
                    "content": '<!doctype html>\n<html lang dir="ltr" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office"><head><!--{$head_top}-->\n    <meta charset="utf-8">\n    \n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=yes">\n    <meta name="format-detection" content="telephone=no, date=no, address=no, email=no, url=no">\n    <meta name="x-apple-disable-message-reformatting">\n    <!--[if !mso]>\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <![endif]-->\n    <!--[if mso]>\n    <style>\n        * { font-family: sans-serif !important; }\n    </style>\n    <noscript>\n        <xml>\n            <o:OfficeDocumentSettings>\n                <o:PixelsPerInch>96</o:PixelsPerInch>\n            </o:OfficeDocumentSettings>\n        </xml>\n    </noscript>\n    <![endif]-->\n    <style type="text/css">\n        /* Outlines the grids, remove when sending */\n        /*table td { border: 1px solid cyan; }*/\n        /* RESET STYLES */\n        html, body { margin: 0 !important; padding: 0 !important; width: 100% !important; height: 100% !important; }\n        body { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; text-rendering: optimizeLegibility;}\n        .document { margin: 0 !important; padding: 0 !important; width: 100% !important; }\n        img { border: 0; outline: none; text-decoration: none;  -ms-interpolation-mode: bicubic; }\n        table { border-collapse: collapse; }\n        table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }\n        body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }\n        h1, h2, h3, h4, h5, p { margin:0; word-break: break-word;}\n        /* iOS BLUE LINKS */\n        a[x-apple-data-detectors] {\n            color: inherit !important;\n            text-decoration: none !important;\n            font-size: inherit !important;\n            font-family: inherit !important;\n            font-weight: inherit !important;\n            line-height: inherit !important;\n        }\n        /* ANDROID CENTER FIX */\n        div[style*="margin: 16px 0;"] { margin: 0 !important; }\n        /* MEDIA QUERIES */\n        @media all and (max-width:639px){\n            .wrapper{ width:100%!important; }\n            .container{ width:100%!important; min-width:100%!important; padding: 0 !important; }\n            .row{padding-left: 20px!important; padding-right: 20px!important;}\n            .col-mobile {width: 20px!important;}\n            .table-between-col-mobile {width:100%!important;}\n            .col{display: block!important; width: 100%!important;}\n            .col-feature{display: block!important; width: 100%!important;}\n            .mobile-center{text-align: center!important; float: none!important;}\n            .mobile-mx-auto {margin: 0 auto!important; float: none!important;}\n            .mobile-left{text-align: center!important; float: left!important;}\n            .mobile-hide{display: none!important;}\n            .img{ width:100% !important; height:auto !important; }\n            .ml-btn { width: 100% !important; max-width: 100%!important;}\n            .ml-btn-container { width: 100% !important; max-width: 100%!important;}\n            *[class="mobileOff"] { width: 0px !important; display: none !important; }\n            *[class*="mobileOn"] { display: block !important; max-height:none !important; }\n            .mlContentTable{ width: 100%!important; min-width: 10%!important; margin: 0!important; float: none!important; }\n            .mlContentButton a { display: block!important; width: auto!important; }\n            .mlContentOuter { padding-bottom: 0px!important; padding-left: 15px!important; padding-right: 15px!important; padding-top: 0px!important; }\n            .mlContentSurvey { float: none!important; margin-bottom: 10px!important; width:100%!important; }\n            .multiple-choice-item-table { width: 100% !important; min-width: 10% !important; float: none !important; }\n            .ml-default, .ml-card, .ml-fullwidth { width: 100%; min-width: 100%; }\n        }\n\n        @media screen and (max-width: 600px) {\n            .col-feature {\n                margin-bottom: 30px;\n            }\n        }\n\n        /* Carousel style */\n        @media screen and (-webkit-min-device-pixel-ratio: 0) {\n            .webkit {\n                display: block !important;\n            }\n        }  @media screen and (-webkit-min-device-pixel-ratio: 0) {\n            .non-webkit {\n                display: none !important;\n            }\n        }  @media screen and (-webkit-min-device-pixel-ratio: 0) {\n            /* TARGET OUTLOOK.COM */\n            [class="x_non-webkit"] {\n                display: block !important;\n            }\n        }  @media screen and (-webkit-min-device-pixel-ratio: 0) {\n            [class="x_webkit"] {\n                display: none !important;\n            }\n        }\n    </style>\n    \n    <style type="text/css">@import url("https://assets.mlcdn.com/fonts-v2.css?version=1745332");</style>\n<style type="text/css">\n            @media screen {\n                body {\n                    font-family: \'Inter\', sans-serif;\n                }\n            }\n        </style><meta name="robots" content="noindex, nofollow">\n<title>prueba campaña</title>\n<!--{$head_bottom}--></head>\n<body style="margin: 0 !important; padding: 0 !important; background-color:#F4F7FA;"><!--{$body_top}-->\n\n    \n        \n        \n    \n\n    \n\n        \n            \n\n            \n            \n            \n            \n            \n            \n        \n\n        \n            \n\n            \n        \n\n        \n            \n\n            \n        \n\n    \n\n    \n\n        \n\n        \n\n        \n            \n            \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n        \n\n        \n            \n            \n        \n\n        \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n            \n            \n            \n            \n            \n            \n        \n\n        \n            \n            \n            \n            \n            \n            \n            \n            \n            \n            \n        \n\n        \n\n            \n                \n                \n                \n                \n                \n            \n\n            \n                \n                \n                \n            \n\n            \n                \n                \n                \n                \n                \n            \n\n            \n                \n                \n                \n                \n                \n            \n\n            \n                \n                \n                \n                \n                \n            \n\n            \n                \n                \n                \n                \n            \n\n            \n                \n                \n            \n\n            \n                \n                \n            \n\n        \n    \n\n    <div class="document" role="article" aria-roledescription="email" aria-label lang dir="ltr" style="background-color:#F4F7FA; line-height: 100%; font-size:medium; font-size:max(16px, 1rem);">\n\n        <!--[if gte mso 9]>\n        <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t" if="variable.bodyBackgroundImage.value">\n            <v:fill type="tile" src="" color="#F4F7FA"/>\n        </v:background>\n        <![endif]-->\n\n        \n\n        <table width="100%" align="center" cellspacing="0" cellpadding="0" border="0">\n            <tr>\n                <td class background bgcolor="#F4F7FA" align="center" valign="top" style="padding: 0 8px;">\n\n                    <table class="container" align="center" width="640" cellpadding="0" cellspacing="0" border="0" style="max-width: 640px;">\n    <tr>\n        <td align="center">\n            \n\n                \n\n                <table align="center" width="100%" cellpadding="0" cellspacing="0" border="0">\n                    <tr>\n                        <td colspan="2" height="20" style="line-height: 20px"></td>\n                    </tr>\n                    <tr>\n                        \n                        <td align="left" style="font-family: \'Inter\', sans-serif; color: #111111; font-size: 12px; line-height: 18px;">\n                            \n                            \n                        </td>\n                        \n                        <td align="right" style="font-family: \'Inter\', sans-serif; color: #111111; font-size: 12px; line-height: 18px;">\n                            <a style="color: #111111; font-weight: normal; font-style: normal; text-decoration: underline;" href="{$url}" data-link-id="152432757093434783" data-link-type="webview">View in browser</a>&nbsp;\n                        </td>\n                    </tr>\n                    <tr>\n                        <td colspan="2" height="20" style="line-height: 20px;"></td>\n                    </tr>\n                </table>\n\n                \n\n                \n                    \n                    \n                    \n                \n\n                \n                    \n                    \n                \n\n            \n        </td>\n    </tr>\n</table>\n\n\n                    <table width="640" class="wrapper" align="center" border="0" cellpadding="0" cellspacing="0" style="\n                        max-width: 640px;\n                        border:1px solid #E5E5E5;\n                        border-radius:8px; border-collapse: separate!important; overflow: hidden;\n                        ">\n                        <tr>\n                            <td align="center">\n\n                                \n    <!-- {% if true %} -->\n<table class="ml-default" width="100%" bgcolor border="0" cellspacing="0" cellpadding="0">\n    <tr>\n        <td style>\n            \n                \n                \n\n                \n                \n\n                <table class="container ml-4 ml-default-border" width="640" bgcolor="#ffffff" align="center" border="0" cellspacing="0" cellpadding="0" style="\n                width: 640px; min-width: 640px;\n                ;\n                \n                ">\n                    <tr>\n                        <td class="ml-default-border container" height="40" style="line-height: 40px; min-width: 640px;"></td>\n                    </tr>\n                    <tr>\n                        <td>\n\n    \n    \n    \n    \n\n\n<table align="center" width="100%" border="0" cellspacing="0" cellpadding="0">\n    <tr>\n        <td class="row mobile-center" align="center" style="padding: 0 50px;">\n            \n\n    \n\n\n\n\n\n\n<img src="https://storage.mlcdn.com/account_image/1043022/VmjzhOMrYV5tCc5ld0UYBqeBLWRCTaDhNdYB8CjL.png" border="0" alt width="120" class="logo" style="max-width: 120px; display: inline-block;">\n\n\n\n\n\n\n\n\n        </td>\n    </tr>\n    <tr>\n        <td height="25" style="line-height: 25px;"></td>\n    </tr>\n    \n    <tr>\n        <td class="row mobile-center" style="padding: 0 50px;" align="center">\n            \n\n    \n\n\n<table class="menu mobile-mx-auto" width cellpadding="0" cellspacing="0" border="0">\n    <tr>\n        <td align="center" class="menu-item" style="padding: 0 20px 0 0;">\n            <a href="https://" target="blank" style="font-family: \'Inter\', sans-serif; font-size: 14px; line-height: 150%; color: #2C438D; font-weight: normal; font-style: normal; text-decoration: none;" data-link-id="152432757100774816">\n                <span style="color: #2C438D;">About</span>\n            </a>\n        </td><td align="center" class="menu-item" style="padding: 0 20px 0 20px;">\n            <a href="https://" target="blank" style="font-family: \'Inter\', sans-serif; font-size: 14px; line-height: 150%; color: #2C438D; font-weight: normal; font-style: normal; text-decoration: none;" data-link-id="152432757106017698">\n                <span style="color: #2C438D;">New!</span>\n            </a>\n        </td><td align="center" class="menu-item" style="padding: 0 0 0 20px;">\n            <a href="https://" target="blank" style="font-family: \'Inter\', sans-serif; font-size: 14px; line-height: 150%; color: #2C438D; font-weight: normal; font-style: normal; text-decoration: none;" data-link-id="152432757109163427">\n                <span style="color: #2C438D;">Shop</span>\n            </a>\n        </td>\n    </tr>\n</table>\n\n\n\n\n        </td>\n    </tr>\n    \n</table>\n\n\n    \n    \n    \n    \n    \n\n\n\n    \n    \n\n\n\n\n                            </td>\n                    </tr>\n                    <tr>\n                        <td height="40" style="line-height: 40px;"></td>\n                    </tr>\n                </table>\n                \n                    \n                    \n                \n            \n        </td>\n    </tr>\n</table>\n<!-- {% endif %} -->\n\n\n    <!-- {% if true %} -->\n<table class="ml-default" width="100%" bgcolor border="0" cellspacing="0" cellpadding="0">\n    <tr>\n        <td style>\n            \n                \n                \n                \n                \n                \n                \n                \n                \n\n                <table class="ml-default-border" width="100%" align="center" bgcolor="#ffffff" border="0" cellspacing="0" cellpadding="0" style="\n                ;\n                \n                ">\n                    <tr>\n                        <td class="ml-default-border" background style="background-size: cover; background-position: center center;" valign="top" align="center">\n\n                            \n                            <table class="container ml-9" width="640" align="center" border="0" cellpadding="0" cellspacing="0" style="color: #242424; width: 640px; min-width: 640px;">\n                                <tr>\n                                    <td class="container" height="20" style="line-height: 20px; min-width: 640px;"></td>\n                                </tr>\n                                <tr>\n                                    <td>\n\n    \n    \n\n\n\n\n\n\n    <table class="container" width="640" border="0" cellspacing="0" cellpadding="0">\n        <tr>\n            <td class="row" align="center" style="padding: 0 50px" colspan="3">\n                \n\n    \n    <img src="https://storage.mlcdn.com/account_image/1043022/tlW3EOUmz0rNUT4J9PILS6KXxubqO4LNUAxWKS79.png" border="0" alt class="img" width="540" style="display: block;">\n\n\n\n            </td>\n        </tr>\n        <tr>\n            <td class="col-mobile" width="50" height="0" style="line-height: 0;"></td>\n            <td>\n                <table class="table-between-col-mobile" width="540" border="0" cellspacing="0" cellpadding="0">\n                    <tr>\n                        <td height="30" style="line-height:30px;"></td>\n                    </tr>\n                    <tr>\n                        <td>\n                            <h1 style="font-family: \'Inter\', sans-serif; color: #2C438D; font-size: 36px; line-height: 125%; font-weight: bold; font-style: normal; text-decoration: none; ;margin-bottom: 10px; text-align: center;">Cotización</h1>\n<p style="font-family: \'Inter\', sans-serif; color: #242424; font-size: 16px; line-height: 165%; margin-top: 0; margin-bottom: 0; text-align: center;">{$name} ha recibido una nueva cotización</p>\n                        </td>\n                    </tr>\n                    <tr>\n                        <td height="30" style="line-height:30px;"></td>\n                    </tr>\n                    <tr>\n                        <td align="center">\n                            \n\n    \n    \n    \n    \n\n    \n\n\n\n\n\n\n                        </td>\n                    </tr>\n                    \n                    \n                </table>\n            </td>\n            <td class="col-mobile" width="50" height="0" style="line-height: 0;"></td>\n        </tr>\n    </table>\n\n\n\n\n    \n    \n    \n    \n    \n\n\n\n    \n    \n    \n    \n    \n\n\n\n    \n    \n    \n    \n    \n\n\n\n    \n    \n    \n    \n    \n\n\n\n    \n    \n    \n    \n\n\n\n    \n    \n\n\n\n\n\n\n    \n    \n    \n    \n    \n    \n    \n    \n    \n    \n    \n\n\n\n\n\n\n\n\n    \n    \n    \n    \n    \n    \n    \n    \n    \n    \n\n\n\n\n\n\n\n                                        </td>\n                                </tr>\n                                <tr>\n                                    <td height="40" style="line-height: 40px;"></td>\n                                </tr>\n                            </table>\n\n                            \n                            \n                                \n                            \n\n                        </td>\n                    </tr>\n                </table>\n\n            \n        </td>\n    </tr>\n</table>\n<!-- {% endif %} -->\n\n\n    <!-- {% if true %} -->\n<table class="ml-default" width="100%" bgcolor border="0" cellspacing="0" cellpadding="0">\n    <tr>\n        <td style>\n            \n\n                \n                \n\n                \n                \n\n                <table class="container ml-11 ml-default-border" width="640" bgcolor="#ffffff" align="center" border="0" cellspacing="0" cellpadding="0" style="\n                width: 640px; min-width: 640px;\n                ;\n                \n                ">\n                    <tr>\n                        <td class="ml-default-border container" height="40" style="line-height: 40px; min-width: 640px;"></td>\n                    </tr>\n                    <tr>\n                        <td class="row" style="padding: 0 50px;">\n\n\n    \n    \n\n<table align="center" width="100%" cellpadding="0" cellspacing="0" border="0">\n    <tr>\n        <td class="col" align="left" width="250" valign="top" style="text-align: left!important;">\n            \n                <h5 style="font-family: \'Inter\', sans-serif; color: #2C438D; font-size: 15px; line-height: 125%; font-weight: bold; font-style: normal; text-decoration: none; margin-bottom: 6px;">Valle de los Ángeles</h5>\n            \n            <p style="font-family: \'Inter\', sans-serif; color: #242424; font-size: 14px; line-height: 150%; margin-bottom: 6px;"><strong>Valle de los Ángeles</strong></p>\n<p style="font-family: \'Inter\', sans-serif; color: #242424; font-size: 14px; line-height: 150%; margin-bottom: 6px;">T. 222 237 4455</p>\n<p style="font-family: \'Inter\', sans-serif; color: #242424; font-size: 14px; line-height: 150%; margin-bottom: 6px;">Av. Manuel Espinosa Yglesias 1212, Puebla<br>Col. Ladrillera de Benítez,&nbsp;Puebla, Puebla,&nbsp;México</p>\n\n            <table width="100%" cellpadding="0" cellspacing="0" border="0">\n                <tr>\n                    <td height="16" style="line-height: 16px;"></td>\n                </tr>\n                <tr>\n                    <td>\n                        \n\n\n\n\n<table class="**$class**" role="presentation" cellpadding="0" cellspacing="0" border="0">\n    <tr>\n        <td align="center" valign="middle" width="18" ng-show="slink.link != \'\'" style="padding: 0 5px 0 0;">\n            <a href="https://www.facebook.com/grupovalledelosangeles" target="blank" style="text-decoration: none;" data-link-id="152432757113357733">\n                <img src="https://assets.mlcdn.com/ml/images/icons/default/rounded_corners/black/facebook.png" width="18" alt="facebook">\n            </a>\n        </td><td align="center" valign="middle" width="18" ng-show="slink.link != \'\'" style="padding: 0 0 0 5px;">\n            <a href="https://www.instagram.com/funerariavalledelosangeles/" target="blank" style="text-decoration: none;" data-link-id="152432757117552038">\n                <img src="https://assets.mlcdn.com/ml/images/icons/default/rounded_corners/black/instagram.png" width="18" alt="instagram">\n            </a>\n        </td>\n    </tr>\n</table>\n\n                        \n                    </td>\n                </tr>\n            </table>\n        </td>\n        <td class="col" width="40" height="30" style="line-height: 30px;"></td>\n        <td class="col" align="left" width="250" valign="top" style="text-align: left!important;">\n            \n                <p style="font-family: \'Inter\', sans-serif; color: #242424; font-size: 14px; line-height: 150%; margin-bottom: 6px;">You received this email because you signed up on our website or made a purchase from us.</p>\n            \n\n            <table width="100%" cellpadding="0" cellspacing="0" border="0">\n                <tr>\n                    <td height="8" style="line-height: 8px;"></td>\n                </tr>\n                <tr>\n                    <td align="left">\n                        <p style="font-family: \'Inter\', sans-serif; color: #242424; font-size: 14px; line-height: 150%; margin-bottom: 0;">\n                            <a href="{$unsubscribe}" style="color: #242424; font-weight: normal; font-style: normal; text-decoration: underline;" data-link-id="152432757120697769" data-link-type="unsubscribe">Unsuscribe</a>\n                            \n                            \n                            \n                        </p>\n                    </td>\n                </tr>\n            </table>\n        </td>\n    </tr>\n</table>\n\n\n\n\n\n\n\n\n    \n    \n    \n    \n    \n\n\n\n    \n    \n    \n    \n\n\n\n    \n    \n\n\n\n\n\n    \n    \n    \n\n\n\n                            </td>\n                    </tr>\n                    <tr>\n                        <td height="40" style="line-height: 40px;"></td>\n                    </tr>\n                </table>\n                \n                    \n                    \n                \n            \n        </td>\n    </tr>\n</table>\n<!-- {% endif %} -->\n\n\n\n                            </td>\n                        </tr>\n                    </table>\n\n                    <table cellpadding="0" cellspacing="0" border="0" align="center" width="640" style="max-width: 640px; width: 100%;">\n    <tr class="ml-hide-branding">\n        <td height="40" style="line-height: 40px;"></td>\n    </tr>\n    <tr class="ml-hide-branding">\n        <td align="center">\n            <a href="https://www.mailerlite.com" target="_blank" style="text-decoration: none;" data-link-id="152432757125940650">\n                <img width="100" border="0" alt="Sent by MailerLite" src="https://assets.mlcdn.com/ml/logo/sent-by-mailerlite.png" style="display: block;">\n            </a>\n        </td>\n    </tr>\n    <tr class="ml-hide-branding">\n        <td height="40" style="line-height: 40px;"></td>\n    </tr>\n</table>\n\n\n                </td>\n            </tr>\n        </table>\n\n    </div>\n\n    \n\n    \n\n<!--{$body_bottom}--></body>\n</html>',
                }
            ],
        }

        try:
            response = requests.put(
                f"https://connect.mailerlite.com/api/campaigns/{campaign_id}",
                headers=self.headers,
                json=data,
            )
        except Exception as error:
            print(f"{error=}")

        return response.json()

    def send_campaign(self, campaign_id) -> tuple[int, dict]:
        """
        Schedules a campaign for immediate sending in your MailerLite account.

        This method sends a POST request to the MailerLite API to schedule
        a campaign for immediate delivery. The campaign must be in a 'draft'
        or 'ready' state before it can be scheduled.

        Parameters:
            campaign_id (str): The unique identifier of the campaign
                               to be sent.

        Returns:
            tuple:
                - int: The HTTP status code returned by the MailerLite API.
                - dict: The JSON-decoded response content from the server,
                        containing details of the scheduled campaign or
                        error information.

        Notes:
            - Ensure that the campaign has all required settings completed
              before scheduling.
            - A 422 Unprocessable Entity error indicates missing campaign
              settings.
            - A 404 Not Found error indicates that the campaign ID does not
              exist in the account.

        Reference:
            MailerLite API Documentation:
            https://developers.mailerlite.com/docs/campaigns
        """

        data = {}
        data["delivery"] = "instant"

        return self.post(
            f"https://connect.mailerlite.com/api/campaigns/{
                campaign_id}/schedule",
            data=data,
        )

    def delete_campaign(self, campaign_id) -> int:
        """
        Deletes a campaign from your MailerLite account.

        This method sends a DELETE request to the MailerLite API to
        remove a campaign identified by its unique ID. Note that only
        campaigns that are in 'draft' or 'ready' status can be deleted.

        Parameters:
            campaign_id (str): The unique identifier of the campaign
                               to be deleted.

        Returns:
            int: The HTTP status code returned by the MailerLite API.
                 A 204 No Content status indicates a successful deletion.
                 A 404 Not Found status indicates that the campaign ID
                 does not exist.

        Reference:
            MailerLite API Documentation:
            https://developers.mailerlite.com/docs/campaigns
        """

        try:
            response = requests.delete(
                f"https://connect.mailerlite.com/api/campaigns/{campaign_id}",
                headers=self.headers,
            )
        except Exception as error:
            print(f"{error=}")
            # NOTE: return a status code if server has an error? 3xx

        return response.status_code
