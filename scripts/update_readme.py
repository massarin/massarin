#!/usr/bin/env python3
import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def load_leaderboard():
    leaderboard_path = Path('leaderboard.json')
    if leaderboard_path.exists():
        with open(leaderboard_path, 'r') as f:
            return json.load(f)
    return {
        "leaderboard": {},
        "current_user": None,
        "last_updated": None
    }

def save_leaderboard(data):
    with open('leaderboard.json', 'w') as f:
        json.dump(data, f, indent=2)

def update_leaderboard(username):
    data = load_leaderboard()
    
    if username not in data["leaderboard"]:
        data["leaderboard"][username] = 0
    
    data["leaderboard"][username] += 1
    data["current_user"] = username
    data["last_updated"] = datetime.now().isoformat()
    
    save_leaderboard(data)
    return data

def generate_gif(username):
    gif_path = Path('assets/current_user.gif')
    gif_path.parent.mkdir(exist_ok=True)
    
    try:
        result = subprocess.run(
            ['gugs', username, '--reverse'],
            capture_output=True,
            text=True,
            check=True
        )
        
        generated_gif = Path(f'{username}.gif')
        if generated_gif.exists():
            generated_gif.rename(gif_path)
            print(f"Generated GIF for {username}")
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating GIF: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
    return False

def format_leaderboard(data):
    if not data["leaderboard"]:
        return "No participants yet!"
    
    sorted_users = sorted(
        data["leaderboard"].items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    table = "| Rank | User | Display Count |\n"
    table += "|------|------|---------------|\n"
    
    for i, (user, count) in enumerate(sorted_users[:10], 1):
        medal = ""
        if i == 1:
            medal = "🥇 "
        elif i == 2:
            medal = "🥈 "
        elif i == 3:
            medal = "🥉 "
        
        table += f"| {medal}{i} | @{user} | {count} |\n"
    
    return table

def update_readme(data):
    readme_path = Path('README.md')
    
    # Check if README exists
    if not readme_path.exists():
        print("README.md not found - skipping update")
        return False
    
    # Read existing README
    with open(readme_path, 'r') as f:
        readme_content = f.read()
    
    # Define markers
    start_marker = "<!-- GUGS_START -->"
    end_marker = "<!-- GUGS_END -->"
    
    # Check if markers exist
    if start_marker not in readme_content or end_marker not in readme_content:
        print(f"Markers not found in README.md")
        print(f"Please add the following markers where you want the GUGS content:")
        print(f"  {start_marker}")
        print(f"  {end_marker}")
        return False
    
    # Prepare the content to insert
    current_user = data.get("current_user", "massarin")
    last_updated = data.get("last_updated", datetime.now().isoformat())
    leaderboard_table = format_leaderboard(data)
    
    gugs_content = f"""## 🎮 Interactive GitHub Profile

### Current Featured User: @{current_user}

![Current User GIF](assets/current_user.gif)

*Last updated: {last_updated}*

### Want to be featured?

➡️ **[Click here](https://github.com/massarin/massarin/issues/new?title=Feature%20me!&body=I%20want%20to%20be%20featured%20on%20your%20profile!)**
 to create an issue and see your username as the initial conditions of a gravity simulation!


### 🏆 Leaderboard

{leaderboard_table}

---

*This README is powered by [GUGS](https://github.com/massarin/gugs) - GitHub Username Gravity Simulation*"""
    
    # Find the positions of the markers
    start_pos = readme_content.find(start_marker)
    end_pos = readme_content.find(end_marker)
    
    if start_pos == -1 or end_pos == -1 or start_pos >= end_pos:
        print("Invalid marker positions in README.md")
        return False
    
    # Replace content between markers
    new_readme = (
        readme_content[:start_pos + len(start_marker)] + 
        "\n\n" + gugs_content + "\n\n" +
        readme_content[end_pos:]
    )
    
    # Write updated README
    with open(readme_path, 'w') as f:
        f.write(new_readme)
    
    print(f"README updated successfully!")
    return True

def main():
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = os.environ.get('GITHUB_ACTOR', 'massarin')
    
    print(f"Processing update for user: {username}")
    
    data = update_leaderboard(username)
    
    if generate_gif(username):
        print("GIF generated successfully")
    else:
        print("Failed to generate GIF, using default")
    
    update_readme(data)
    
    print("Update complete!")

if __name__ == "__main__":
    main()