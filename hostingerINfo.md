Below is a step‑by‑step checklist that matches the details in your screenshots (IP 82.180.172.252, port 65002, user u344797311). Follow it once and you’ll be able to work locally in VS Code, hit **git push**, and have Hostinger pull and publish the site.

---

## 1. Generate and register an SSH key

```bash
# in your VS Code terminal
ssh-keygen -t ed25519 -C "hostinger-site"
# press Enter three times to accept defaults
cat ~/.ssh/id_ed25519.pub          # copy the full key
```

1. hPanel › **Advanced › SSH Access › Add SSH key** → paste the key and save. ([Hostinger][1])
2. Test it:

```bash
ssh -p 65002 u344797311@82.180.172.252
```

If you see a welcome banner, the key works.

---

## 2. Create the Git deployment slot in hPanel

1. hPanel › **Advanced › Git**
2. **Repository address** → paste the SSH URL of your GitHub repo (for example `git@github.com:yourname/site.git`).
3. **Branch** → `main` (or whichever you use).
4. **Installation path** → leave blank to deploy into `/public_html`.
5. Click **Create** then toggle **Auto‑deployment**. Copy the webhook URL that appears. ([Hostinger Help Center][2])

---

## 3. Wire up the webhook on GitHub

1. GitHub › Your repo › **Settings › Webhooks › Add webhook**.
2. Payload URL → paste the Hostinger webhook.
3. Content‑type → `application/json`.
4. Events → “Just the push event”. Save.

Now each push will trigger Hostinger to pull and publish automatically.

---

## 4. Everyday workflow in VS Code

```bash
# inside your project folder
git add .
git commit -m "update footer"
git push origin main    # goes to GitHub
# Hostinger receives the webhook, pulls, and updates the live site
```

No manual uploads, no extra extensions.

---

### Need to edit files directly on the server?

Install the **Remote‑SSH** extension in VS Code and add this to `~/.ssh/config`:

```
Host hostinger
    HostName 82.180.172.252
    Port 65002
    User u344797311
    IdentityFile ~/.ssh/id_ed25519
```

Then: **F1 › Remote‑SSH: Connect to Host… › hostinger**. You can open and save files on the server as if they were local. ([Visual Studio Code][3])

---

### Prefer an SFTP sync instead of Git?

1. Install the **“SFTP”** extension by liximomo.
2. Create `.vscode/sftp.json`:

```json
{
  "name": "Hostinger",
  "host": "82.180.172.252",
  "protocol": "sftp",
  "port": 65002,
  "username": "u344797311",
  "remotePath": "/public_html",
  "privateKeyPath": "~/.ssh/id_ed25519",
  "uploadOnSave": true,
  "ignore": [".git/**", "node_modules/**", ".vscode/**"]
}
```

Save a file and it syncs instantly. ([Hostinger Help Center][4])

---

## Final checklist

1. SSH key added and tested.
2. Git deployment slot created with auto‑deploy enabled.
3. GitHub webhook added.
4. First `git push` triggers the build; check hPanel › Git for logs and confirm the site updates.

With these pieces in place, your VS Code workflow is now “edit → commit → push → live”.

[1]: https://www.hostinger.com/tutorials/how-to-set-up-ssh-keys?utm_source=chatgpt.com "How to Set Up SSH Keys and Manage Them Effectively in 2025"
[2]: https://support.hostinger.com/en/articles/1583302-how-to-deploy-a-git-repository?utm_source=chatgpt.com "How to Deploy a Git Repository - Hostinger Help Center"
[3]: https://code.visualstudio.com/docs/remote/ssh?utm_source=chatgpt.com "Remote Development using SSH - Visual Studio Code"
[4]: https://support.hostinger.com/en/articles/5972689-how-to-connect-to-your-hosting-using-sftp?utm_source=chatgpt.com "How to Connect to Your Hosting Using SFTP - Hostinger Help Center"
