from flask import Flask, jsonify
import instaloader
import re

# Initialize Flask app and Instaloader
app = Flask(__name__)
L = instaloader.Instaloader()

# Set a User-Agent to mimic a browser and reduce blocking risk
L.context._session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    try:
        # Fetch the Instagram profile
        profile = instaloader.Profile.from_username(L.context, username)
        
        # Extract email from bio using regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, profile.biography)
        email = emails[0] if emails else None  # Take the first email found, or None if none

        # Extract profile information
        data = {
            'username': profile.username,
            'full_name': profile.full_name,
            'bio': profile.biography,
            'external_url': profile.external_url,  # Add external URL
            'email': email,  # Add extracted email (if any)
            'follower_count': profile.followers,
            'following_count': profile.followees,
            'post_count': profile.mediacount,
            'profile_pic_url': profile.profile_pic_url,
            'is_private': profile.is_private,
            'is_verified': profile.is_verified
        }
        
        # Return data as JSON
        return jsonify(data)
    
    except instaloader.exceptions.ProfileNotExistsException:
        # Handle non-existent profiles
        return jsonify({'error': 'Profile does not exist'}), 404
    
    except instaloader.exceptions.TooManyRequestsException:
        # Handle rate limit errors
        return jsonify({'error': 'Rate limit exceeded, try again later'}), 429
    
    except instaloader.exceptions.ConnectionException as e:
        # Handle network-related issues
        return jsonify({'error': f'Connection error: {str(e)}'}), 503
    
    except Exception as e:
        # Catch all other errors
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)