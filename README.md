# MailerLite client to send automated e-mails

This project is an AWS Lambda function that sends emails to multiple users using the [MailerLite API](https://developers.mailerlite.com/). It automates the creation of user groups, adds users to the group, and sends a campaign email using the MailerLite platform.

## Features

- Creates new subscriber groups dynamically
- Adds users to MailerLite and assigns them to a group
- Creates and sends HTML email campaigns
- Checks and handles existing users and groups
- Uses AWS Secrets Manager for secure API key management

## How It Works

1. Receives an event with a list of users (email and name).
2. Generates a unique group name.
3. Adds each user to MailerLite (only if not already added).
4. Subscribes users to the new group.
5. Creates a campaign with a predefined HTML content.
6. Sends the campaign to the group.

## File Structure

- `app.py`: AWS Lambda handler that manages the flow of creating users, groups, and campaigns.
- `mailer_client.py`: MailerLite API client wrapper to simplify interactions with MailerLite's API.

## Environment Configuration

The MailerLite API key must be stored in AWS Secrets Manager under the secret name `test/email/Mailer`. It should contain the following key-value pair:

```json
{
  "MAILER_KEY": "your-mailerlite-api-key"
}
```

## Request Format

The Lambda function expects a `POST` request with a JSON body like the following:

```json
{
  "users": [
    { "email": "marco@example.com", "name": "Marco" },
    { "email": "juan@example.com", "name": "Juan" }
  ]
}
```

Each user must contain a `name` and a valid `email`.

## Email Template

The email content is a hardcoded HTML template embedded in the campaign creation request. You can customize it in the `app.py` file under the `content` variable.

## Limitations

- This example sends one-time campaigns only.
- You cannot resend a campaign once it has been sent via the API.
- Campaigns must contain a valid unsubscribe link and use a verified sender address in your MailerLite account.
