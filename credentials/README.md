# Local Credentials

Do not store real server credentials, database passwords, SSH keys, API keys, or tokens in this repository.

Use environment variables or local files that are excluded by `.gitignore`.

## Suggested local configuration

Store application settings in a local `.env` file based on the repository's `.env.example`:

```text
FLASK_SECRET_KEY=your_local_secret
MYSQL_USER=your_database_user
MYSQL_PASSWORD=your_database_password
MYSQL_DB=your_database_name
MYSQL_HOST=your_database_host
```

For SSH access, keep private key files outside the repository or in an ignored local path.

If credentials were ever committed to Git, removing them from the current file is not enough. Rotate or revoke the exposed credentials and rewrite history if the repository must be distributed without the old values.
