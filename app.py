import json
import re
import time
from typing import Dict

def get_instagram_profile(username: str) -> Dict:
    """
    Scrape Instagram profile information without authentication.
    Uses only Pyodide-compatible libraries for n8n code node.
    """
    try:
        # Set up headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

        # Get the profile page using fetch
        profile_url = f'https://www.instagram.com/{username}/'
        response = fetch(profile_url, headers=headers)
        
        if not response.ok:
            return {'error': f'Failed to fetch profile. Status code: {response.status}'}

        # Get the response text
        html_content = response.text()

        # Extract shared data from the page
        shared_data = re.search(r'window\._sharedData\s*=\s*({.+?});', html_content)
        if not shared_data:
            return {'error': 'Could not find profile data'}

        try:
            profile_data = json.loads(shared_data.group(1))
            user_data = profile_data['entry_data']['ProfilePage'][0]['graphql']['user']
        except (json.JSONDecodeError, KeyError):
            return {'error': 'Failed to parse profile data'}

        # Extract email from bio if present
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, user_data.get('biography', ''))
        email = emails[0] if emails else None

        # Compile essential profile information
        profile_info = {
            'username': user_data.get('username'),
            'full_name': user_data.get('full_name'),
            'bio': user_data.get('biography'),
            'external_url': user_data.get('external_url'),
            'email': email,
            'follower_count': user_data.get('edge_followed_by', {}).get('count', 0),
            'following_count': user_data.get('edge_follow', {}).get('count', 0),
            'post_count': user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
            'profile_pic_url': user_data.get('profile_pic_url'),
            'profile_pic_url_hd': user_data.get('profile_pic_url_hd'),
            'is_private': user_data.get('is_private', False),
            'is_verified': user_data.get('is_verified', False),
            'is_business_account': user_data.get('is_business_account', False),
            'business_category_name': user_data.get('business_category_name'),
            'website': user_data.get('website')
        }

        return profile_info

    except Exception as e:
        return {'error': f'An unexpected error occurred: {str(e)}'}

# Example usage for n8n
if __name__ == '__main__':
    username = "example_username"  # Replace with actual username
    result = get_instagram_profile(username)
    print(json.dumps(result, indent=2)) 
