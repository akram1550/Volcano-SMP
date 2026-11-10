# VOLCANO SMP Bot - Railway Setup

1. Open this folder in VS Code.
2. Do NOT add a `.env` file containing your Discord token to GitHub.
3. Initialize a Git repository and publish it as a Private GitHub repository.
4. In Railway, deploy the GitHub repository.
5. Add `DISCORD_TOKEN` in Railway Variables.
6. The bot starts with `python main.py`.

If Railway detects the Procfile, it can run the bot as a worker.
