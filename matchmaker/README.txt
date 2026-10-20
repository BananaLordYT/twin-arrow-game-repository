TWIN ARROW ARENA MATCHMAKER
===========================

The server pairs two connected clients and relays game inputs/state. It uses
Python's websockets package and Render's PORT environment variable.

FREE RENDER SETUP
  1. Create a GitHub repository. Upload render.yaml at the repository root,
     then create a matchmaker folder with server.py and requirements.txt.
     You can also add this README.
  2. In Render, click Skip on the Create a new Service screen to return to the
     dashboard. Choose New > Blueprint and connect the GitHub repository.
  3. Review the service plan and deploy the Blueprint.
  4. Copy the deployed service URL, changing https:// to wss://.
  5. Put the wss:// URL in server_url.txt for each game installation.

Render Free Web Services accept WebSocket connections, but sleep after 15
minutes without incoming traffic. The first connection after sleep may take
about a minute to wake. Matchmaking state is held in memory and clears on a
service restart, which is fine for this small hobby game.
