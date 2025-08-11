# Hugo Site Deployment to Hostinger

This guide explains how to deploy your Hugo site to Hostinger using the provided Python scripts.

## Prerequisites

1. **Hugo installed** - The deployment script will check for this
2. **Python 3** with required packages installed:
   ```bash
   pip3 install paramiko scp
   ```
3. **SSH access set up** with Hostinger (either SSH key or password)

## Scripts Available

### 1. `deploy_flexible.py` - Recommended
This is the main deployment script that supports both SSH key and password authentication.

### 2. `test_ssh.py`
A simple script to test your SSH connection to Hostinger.

### 3. `deploy.py`
Original script (SSH key only) - use `deploy_flexible.py` instead.

## Usage

### Test Connection First
Always test your connection before deploying:

```bash
# Test with SSH key (if set up)
python3 deploy_flexible.py --test

# Test with password
python3 deploy_flexible.py --test --password
```

### Deploy Your Site

```bash
# Deploy with SSH key (if set up)
python3 deploy_flexible.py

# Deploy with password
python3 deploy_flexible.py --password
```

## Authentication Options

### Option 1: SSH Key (Recommended)
1. Make sure your SSH key is at `~/.ssh/id_ed25519`
2. Add your public key to Hostinger's SSH key management:
   - Copy your public key: `cat ~/.ssh/id_ed25519.pub`
   - Add it to Hostinger control panel under "SSH Access"
3. Use the deployment script without `--password` flag

### Option 2: Password Authentication
1. Use the `--password` flag
2. Enter your Hostinger password when prompted
3. This is easier to set up but less secure than SSH keys

## What the Script Does

1. **Checks requirements** - Verifies Hugo is installed and authentication is set up
2. **Tests connection** - Connects to Hostinger to verify access
3. **Builds Hugo site** - Runs `hugo --cleanDestinationDir` to build your site
4. **Clears remote directory** - Removes old files from `/public_html`
5. **Uploads new files** - Uploads all files from `/public` to `/public_html`
6. **Shows progress** - Displays upload progress for each file

## Configuration

The Hostinger connection details are configured in the script:
- Host: 82.180.172.252
- Port: 65002
- User: u344797311
- Remote path: /public_html

## Troubleshooting

### SSH Key Authentication Fails
- Make sure your SSH key is added to Hostinger
- Check key permissions: `chmod 600 ~/.ssh/id_ed25519`
- Try password authentication instead: `--password`

### Hugo Build Fails
- Make sure you're in the correct directory (project root)
- Check that `hugo.toml` exists
- Run `hugo build` manually to see detailed errors

### Upload Fails
- Check your internet connection
- Verify Hostinger credentials
- Try the test mode first: `--test`

### Permission Errors
- Make sure scripts are executable: `chmod +x deploy_flexible.py`
- Check that you have write access to the project directory

## File Structure

Your Hugo project should have this structure:
```
/your-hugo-site/
├── hugo.toml          # Hugo configuration
├── content/           # Your content
├── themes/            # Hugo themes
├── public/            # Generated site (created by Hugo)
├── deploy_flexible.py # Deployment script
└── ...
```

After running `hugo build`, the `/public` directory contains your static website files that get uploaded to Hostinger.

## Security Notes

1. **Never commit passwords** to version control
2. **Use SSH keys** when possible (more secure than passwords)
3. **Keep your SSH keys private** - never share the private key file
4. **Set correct permissions** on SSH keys (`chmod 600`)

## Support

If you encounter issues:
1. Run the test connection first: `python3 deploy_flexible.py --test`
2. Check the error messages - they usually indicate the problem
3. Try password authentication if SSH key fails
4. Verify your Hostinger account has SSH access enabled