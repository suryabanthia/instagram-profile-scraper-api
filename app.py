from flask import Flask, jsonify
import instaloader
import os

# Initialize Flask app and Instaloader
app = Flask(__name__)
L = instaloader.Instaloader()

# Get Instagram credentials from environment variables
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Log in to Instagram if credentials are provided, otherwise proceed without auth
if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
    try:
        L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    except Exception as e:
        print(f"Login failed: {str(e)}")

# Set a User-Agent to mimic a browser
L.context._session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        data = {
            'username': profile.username,
            'full_name': profile.full_name,
            'bio': profile.biography,
            'external_url': profile.external_url,
            'follower_count': profile.followers,
            'following_count': profile.followees,
            'post_count': profile.mediacount,
            'profile_pic_url': profile.profile_pic_url,
            'is_private': profile.is_private,
            'is_verified': profile.is_verified
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
