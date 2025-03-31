from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv
import time
from functools import wraps
import random
import json
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)

# List of user agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
]

def get_random_headers():
    """Generate random headers to mimic different browsers"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

def extract_shared_data(html_content):
    """Extract shared data from Instagram page"""
    shared_data = re.search(r'window\._sharedData\s*=\s*({.+?});', html_content)
    if not shared_data:
        return None
    try:
        return json.loads(shared_data.group(1))
    except json.JSONDecodeError:
        return None

def extract_email(bio):
    """Extract email from biography if present"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, bio or '')
    return emails[0] if emails else None

@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    try:
        # Add random delay between requests (0.5 to 2 seconds)
        time.sleep(random.uniform(0.5, 2))
        
        # Get the profile page
        profile_url = f'https://www.instagram.com/{username}/'
        response = requests.get(profile_url, headers=get_random_headers())
        
        if response.status_code != 200:
            return jsonify({
                'error': f'Failed to fetch profile. Status code: {response.status_code}'
            }), response.status_code
            
        # Extract shared data
        shared_data = extract_shared_data(response.text)
        if not shared_data:
            return jsonify({
                'error': 'Could not find profile data'
            }), 404
            
        try:
            user_data = shared_data['entry_data']['ProfilePage'][0]['graphql']['user']
        except (KeyError, IndexError):
            return jsonify({
                'error': 'Failed to parse profile data'
            }), 500
            
        # Extract email from bio
        email = extract_email(user_data.get('biography'))
        
        # Compile profile information
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
            'website': user_data.get('website'),
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(profile_info)
        
    except Exception as e:
        return jsonify({
            'error': f'An unexpected error occurred: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
