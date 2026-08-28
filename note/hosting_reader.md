Render Free Tier Keep-Alive Solution

Render’s Free Tier automatically puts Flask web applications to sleep (Spin Down / Cold Start) after 15 minutes of inactivity, causing a 30–60 second loading delay on subsequent requests.

How to Fix (Free Method)
Use a free monitoring service like UptimeRobot to send dynamic HTTP pings and keep your app active 24/7.

Sign Up: Create a free account at uptimerobot.com.

Create Monitor: Click Add New Monitor.

Configure Settings:

Monitor Type: HTTP(s)

Friendly Name: My Flask App (or any preferred name)

URL: [https://your-app.onrender.com](https://your-app.onrender.com)

Interval: Every 5 minutes or Every 10 minutes

Save: Click Create Monitor.