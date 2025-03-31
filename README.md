# Instagram Profile Scraper API

A simple API to scrape Instagram profile information using Instagram's GraphQL API.

## Features

- Get user profile information
- Fetch follower and following counts
- Get business account details
- Retrieve profile picture URLs
- Get post counts and recent posts
- And much more!

## API Endpoints

### POST /scrape

Scrapes Instagram profile information for a given username.

**Request Body:**
```json
{
  "username": "instagram"
}
```

**Response:**
```json
{
  "username": "instagram",
  "fullName": "Instagram",
  "followersCount": 123456789,
  "followingCount": 123,
  "bio": "Instagram bio text",
  "externalUrl": "https://example.com",
  "isBusinessAccount": false,
  "isPrivate": false,
  "profilePicture": "https://instagram.com/profile-picture.jpg",
  "postsCount": 1234,
  "isVerified": true,
  // ... more fields
}
```

## Deployment

This API is configured to be deployed on Render. The following files are required:

- `server.js` - Main application file
- `package.json` - Project dependencies and scripts
- `.gitignore` - Git ignore rules
- `README.md` - Project documentation

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the server:
   ```bash
   npm start
   ```
4. The API will be available at `http://localhost:3000`

## Environment Variables

No environment variables are required for basic functionality.

## License

ISC 