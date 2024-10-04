# HKA Email Scraper

Automated Email Scraper for the HKA OWA system.
Send emails to a webhook for further processing.


## Usage

1. Extract your TOTP secret from your authenticator app.
We recommend using [extract_otp_secrets](https://github.com/scito/extract_otp_secrets)

2. Copy the .env.example file to .env and fill in the required fields.
```bash
cp .env.example .env
```
```
OWA_USERNAME: Your Username
OWA_PASSWORD: Your Password
TOTP_SECRET: Extracted TOTP Secret
WEBHOOK_URL: Webhook URL to send the emails to
```

3. Run the docker container
```bash
docker compose up -d
```
