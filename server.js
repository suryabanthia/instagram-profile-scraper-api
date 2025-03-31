const express = require('express');
const axios = require('axios');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const app = express();
const port = process.env.PORT || 3000;

// Enable CORS for all routes
app.use(cors());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

app.use(express.json());

// Instagram API endpoints
const INSTAGRAM_API_URL = 'https://i.instagram.com/api/v1/users/web_profile_info/';
const INSTAGRAM_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
  'Accept': '*/*',
  'Accept-Language': 'en-US,en;q=0.9',
  'X-IG-App-ID': '936619743392459',
  'X-ASBD-ID': '198387',
  'X-IG-WWW-Claim': '0',
  'Origin': 'https://www.instagram.com',
  'Connection': 'keep-alive',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache'
};

// Instagram session cookie from environment variable
if (!process.env.INSTAGRAM_SESSION_ID) {
  throw new Error('INSTAGRAM_SESSION_ID environment variable is required');
}

// Validate username format
function isValidUsername(username) {
  return /^[a-zA-Z0-9._]{1,30}$/.test(username);
}

async function scrapeInstagramProfile(username) {
  try {
    // Get user profile data using Instagram's API
    const userResponse = await axios.get(`${INSTAGRAM_API_URL}?username=${username}`, {
      headers: {
        ...INSTAGRAM_HEADERS,
        'Cookie': `sessionid=${process.env.INSTAGRAM_SESSION_ID};`,
        'Referer': `https://www.instagram.com/${username}/`
      },
      timeout: 30000,
      validateStatus: function (status) {
        return status >= 200 && status < 500;
      }
    });

    if (!userResponse.data || !userResponse.data.data || !userResponse.data.data.user) {
      throw new Error('User not found or profile is private');
    }

    const userData = userResponse.data.data.user;

    // Extract the data
    const profileData = {
      username: userData.username,
      fullName: userData.full_name,
      followersCount: userData.edge_followed_by.count,
      followingCount: userData.edge_follow.count,
      bio: userData.biography,
      externalUrl: userData.external_url,
      isBusinessAccount: userData.is_business_account,
      isPrivate: userData.is_private,
      profilePicture: userData.profile_pic_url_hd || userData.profile_pic_url,
      postsCount: userData.edge_owner_to_timeline_media.count,
      isVerified: userData.is_verified,
      businessCategory: userData.business_category_name,
      businessEmail: userData.business_email,
      businessPhone: userData.business_phone_number,
      businessAddress: userData.business_address_json,
      connectedFacebookPage: userData.connected_facebook_page,
      countryBlock: userData.country_block,
      hasArEffects: userData.has_ar_effects,
      hasClips: userData.has_clips,
      hasGuides: userData.has_guides,
      hasChannel: userData.has_channel,
      hasBlockedViewer: userData.has_blocked_viewer,
      highlightReelCount: userData.highlight_reel_count,
      isJoinedRecently: userData.is_joined_recently,
      businessContactMethod: userData.business_contact_method,
      category: userData.category,
      categoryName: userData.category_name,
      mutualFollowersCount: userData.edge_mutual_followed_by.count,
      pronouns: userData.pronouns,
      restrictedByViewer: userData.restricted_by_viewer,
      shouldShowCategory: userData.should_show_category,
      shouldShowPublicContacts: userData.should_show_public_contacts,
      showAccountTransparencyDetails: userData.show_account_transparency_details,
      transparencyProduct: userData.transparency_product,
      transparencyProductEnabled: userData.transparency_product_enabled,
      userID: userData.id,
      website: userData.external_url,
      createdAt: new Date(userData.edge_owner_to_timeline_media.edges[0]?.node?.taken_at_timestamp * 1000).toISOString(),
      lastPostTimestamp: userData.edge_owner_to_timeline_media.edges[0]?.node?.taken_at_timestamp,
      lastPostShortcode: userData.edge_owner_to_timeline_media.edges[0]?.node?.shortcode,
      recentPosts: userData.edge_owner_to_timeline_media.edges.slice(0, 12).map(edge => ({
        id: edge.node.id,
        shortcode: edge.node.shortcode,
        takenAt: new Date(edge.node.taken_at_timestamp * 1000).toISOString(),
        displayUrl: edge.node.display_url,
        isVideo: edge.node.is_video,
        videoUrl: edge.node.video_url,
        likesCount: edge.node.edge_liked_by.count,
        commentsCount: edge.node.edge_media_to_comment.count
      }))
    };

    return profileData;
  } catch (error) {
    console.error('Scraping error:', error);
    if (error.response) {
      if (error.response.status === 404) {
        throw new Error('Profile not found');
      } else if (error.response.status === 429) {
        throw new Error('Rate limit exceeded. Please try again later.');
      } else if (error.response.status === 401) {
        throw new Error('Authentication required. Please check your session ID.');
      } else if (error.response.status === 403) {
        throw new Error('Access forbidden. The request was blocked.');
      }
    }
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please try again.');
    }
    throw new Error(`Failed to scrape Instagram profile: ${error.message}`);
  }
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

app.post('/scrape', async (req, res) => {
  try {
    const { username } = req.body;
    
    // Validate request body
    if (!username) {
      return res.status(400).json({ 
        success: false,
        error: 'Username is required',
        details: 'Please provide a username in the request body'
      });
    }

    // Validate username format
    if (!isValidUsername(username)) {
      return res.status(400).json({ 
        success: false,
        error: 'Invalid username format',
        details: 'Username can only contain letters, numbers, dots, and underscores'
      });
    }

    const data = await scrapeInstagramProfile(username);
    res.json({
      success: true,
      data: data
    });
  } catch (error) {
    console.error('API error:', error);
    res.status(500).json({ 
      success: false,
      error: error.message
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    success: false,
    error: 'Internal server error',
    details: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

const server = app.listen(port, () => {
  console.log(`Server running on port ${port}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});

// Set server timeout
server.timeout = 30000; // 30 seconds
