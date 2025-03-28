from flask import Flask, jsonify
import instaloader
import re
import random
import time

# Initialize Flask app and Instaloader
app = Flask(__name__)
L = instaloader.Instaloader()

# List of User-Agents to rotate through
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def setup_instaloader():
    # Set up headers to mimic a real browser
    L.context._session.headers.update({
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    })

@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    try:
        # Set up headers before each request
        setup_instaloader()
        
        # Add a small random delay to avoid rate limiting
        time.sleep(random.uniform(1, 3))
        
        # Fetch the Instagram profile
        profile = instaloader.Profile.from_username(L.context, username)
        
        # Extract email from bio using regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, profile.biography)
        email = emails[0] if emails else None

        # Extract profile information
        data = {
            'username': profile.username,
            'full_name': profile.full_name,
            'bio': profile.biography,
            'external_url': profile.external_url,
            'email': email,
            'follower_count': profile.followers,
            'following_count': profile.followees,
            'post_count': profile.mediacount,
            'profile_pic_url': profile.profile_pic_url,
            'is_private': profile.is_private,
            'is_verified': profile.is_verified,
            'can_dm': not profile.is_private
        }
        
        return jsonify(data)
    
    except instaloader.exceptions.ProfileNotExistsException:
        return jsonify({'error': 'Profile does not exist'}), 404
    
    except instaloader.exceptions.TooManyRequestsException:
        return jsonify({'error': 'Rate limit exceeded, try again later'}), 429
    
    except instaloader.exceptions.ConnectionException as e:
        return jsonify({'error': f'Connection error: {str(e)}'}), 503
    
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
