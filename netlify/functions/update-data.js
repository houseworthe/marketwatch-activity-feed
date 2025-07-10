const https = require('https');
const fs = require('fs').promises;
const path = require('path');

// Competition configuration
const GAME_URI = 'baird-pwm-intern-stock-market-competition';
const AUTH_COOKIES = 'refresh=off; letsGetMikey=enabled; refresh=off; letsGetMikey=enabled; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXQF8g; _pcid=%7B%22browserId%22%3A%22mc4yzz5cvpxw07b3%22%7D; cX_P=mc4yzz5cvpxw07b3; djcs_route=966396ea-5edb-4ce1-a7a5-26117bf651a0; TR=V2-c9d47073af3b9588751977fe4fbcf20f724a9bc94c79daba415c2eeb74a88ae0; djcs_auto=M1750367024%2FvqcMb8aJqCyDvD%2Bp4%2Fvy%2BJiAFKg5fZvadNlW5%2B6tPob1Ux%2F8CxJVZxpM3o7j2vhZOAMILVme9%2FLQlzzu9y8IKXamsLI7pQb%2FQ5M1MihrPMEk3sF9GGfMqFopxSs3%2BIt%2B1DUxn82dVaLUw7uKUk%2FiDTjS%2BzmL1XBKGa94d6bhelFEArIjIwCRNSZ2GAuc07sfEiDsMOrV8J1clJPuxicJ3dT879yl2tTfW2PxOI%2FfaIj6asUD0iUKcDIHsTi0HUv7%2F5qVvr76vbBnMftizItPBra55qpyQNAo8SNb2H0eBMD05Qkn0PRW%2Fuwi2gP2m6aO7QR%2BmMGp6HOUTU2sDzPUDB%2Bi5aJjS%2Fa0sYi0Djc446J79jy0mgplfbnJ%2BG32U%2BH0235i4ZIQdOnYwPoK5gR%2FJ%2FdJhA6Z%2BUMFTa%2FP3iYgc6Yv%2BWqeDBSaV5%2BVF%2BiTEr7sCa1uKl8JP3pg82rvoUB1gQ%3D%3DG; djcs_session=M1750430628%2F59I8D%2Bl49KcBfDxwh6Bp6FxgsnCYIPy6KL%2FM2PeI%2By7uZtzgKNyoQi6T2%2B0dCheRYYyxH29OJyBE3%2FeAX%2FjxxQoq2xitSco3%2F1Yu98h8iT1ea%2BUDtUMutK6qEqEhdTdjv8b0AAomqZw9HvBNkUIiZdc%2BFk16EsM0dYEzQaikaR7eD6HPTdt8jjVguKTFPc9mDM9bGBXKSftZN4iREbJ7prR%2Fkyy1gp3KD8WhH4jIfFBihOZRFdfcfxDLPdIL0wiPwhDWC%2BX0u75dHAQTtWBtf7ZgmKnMYBXrET4F5A3f17HQKOFNIIXERXF9RUzpxuRqHKR6CzK9dI6jElmJ9RiVuBp92HnnDglpM4RSiMyYNXyhP412z7m%2FL%2BfETluZNmbEK1j0mLOqIVkyhJbrNYjdCXDTDZmqH1BY03rXvN%2F5Hy17x%2F2BIoV9ayTyIYhVBC%2B9urxtiNHh66W1lyCqzLw8ETsxvw%2F9CvH8DrL8x1OU%2BOnM2%2FPhtdZnnbny0lmVyz%2FC3Lba8Jfhm1FCdjmIB%2F3cdvB9AoI6c6X0qixmGLJiRwz6%2FltWTlkv8bQzjrKIwSoNQ8amCyipAt4OdsJygpz7zw%3D%3DG; ab_uuid=05588ce5-0f6c-487b-8ab8-1426ce30f17d; wsjregion=na%2Cus; gdprApplies=false; ccpaApplies=false; vcdpaApplies=false; regulationApplies=gdpr%3Afalse%2Ccpra%3Afalse%2Cvcdpa%3Afalse; refresh=off; letsGetMikey=enabled; ca_rt=IXv-C9jkFcy69fAikw1gqQ._JN4amJoBEkZaLYOCmOf4FgJ_QMP9UsJgIiVG650EAEARkpvB2Uv7qoK26shrmbCz7JTQqbZw6fvODc8Gz6M1Y9DpnkxJesQ9ImPL1iXK00; datadome=~F9hNrk0f_vF7i04F4qXVPSkq5tnV4~PETGvgBlCfxSAw1uuyDsRaXhSU0Q6N0_lM1n6vcvQMjEB09yBTaKyCCe_FJjeyvXTzRIFHW50r2pjWnZ3rQG8g4QFPxcm3QkA; mw_loc=%7B%22Region%22%3A%22WI%22%2C%22Country%22%3A%22US%22%2C%22Continent%22%3A%22NA%22%2C%22ApplicablePrivacy%22%3A0%7D; ca_id=0f7b9586-b922-4403-8396-039962f63385.eJw9kFFTwjAQhP9Lnim0acolPNmRIjgKiKIjjsNc04RGSsE2UNHxvxtw9PW7vd29-yIrc1DlssSNIj2S2BxL0iIaN6Y4_tHhdl-rZlvZ3I3UBk3hoMr_6UXVpGiqrC23G6fY703mBJSikj5DL4PU95hPucdRUi8QPk8lDyHTwqlthXJ9XpAiY-BDiDpMRcQ5RIEA0IrpVGrqa6AMRSoFkyAyTJEFkaRKpcCQc1S-M6u2hapJ74UMZkkyS6680bg_ehz15_ENeW0R3Nt8ac3pqAAin4UhB2iR-hz_qSdGHxfjYjmZjrzZqoTo4SmOg9tDsTP5MHMbRz25vly_w3wa30MyeMbFnQuVlUKrsiXaky0TEdBu5GzNL4gCLrquq3vdx-4MaEj5GZjalSW5tbu61-k0TdNu6rfTFzuyMKq05PsHv4596Q.LM5NCaU8KolC1aMqQPq7IAn2KVUV412PMHi2EeqQN2c-nQLSN8DtUvYE8bkT4Ou4WUpwHm94nJVkniYt1zYG_NdGWBnOMcAruqnjVtpdRwkLRVM-ACeoPuAPL9W341xCNrDUDYOHBeMKSZRIJe7jCG3rj5zxrsHKs4qrsArOOtDWMKPqNxGNeXBYcOVoMgbTEY4Yn5RKxn2EF7IaAq9HOmP4d44l4D8ZaQ8SafuOajVTF9B5o1r7hQ8O9j4i96rVYb9Ehzk2Y6dj1UHiYXgjdUYPY5vQ4KmrjC4mIAgXMhP5pjkDH66AFIa2Mr_yJ9QLv_vY24npiKXVGjuRvkuJrA; icons-loaded=true; usr_prof_v2=eyJpYyI6NH0%3D';

// Competitor data - names and IDs only, ranks calculated dynamically
const COMPETITORS = [
  { "public_id": "-Ct8JFv9TYip", "name": "cj deslongchamps" },
  { "public_id": "_8Wq2c1c3_KU", "name": "Sam Klein" },
  { "public_id": "PC71jGgKlLH-", "name": "Will Hemauer" },
  { "public_id": "DZIwD2ECcFRC", "name": "Sebastian Babu" },
  { "public_id": "HRBmKqN6Syly", "name": "Ryan Carew" },
  { "public_id": "BB-z-hSCXbOT", "name": "Ethan Houseworth" },
  { "public_id": "4uvjV2dXQ4SZ", "name": "Jack DePrey" },
  { "public_id": "WArCf7i9ryyb", "name": "Luke Sagone" },
  { "public_id": "eHQgXe9W7f8M", "name": "Steve Perkins" },
  { "public_id": "iIDZxw5xNBMY", "name": "Lily Valimont" },
  { "public_id": "XArvdHeUXb1q", "name": "Griffin Fanger" },
  { "public_id": "9BaDE7wJmTD2", "name": "Milla MacLeod" },
  { "public_id": "zvZv24UsJIFb", "name": "Eileen Carey" },
  { "public_id": "LXCJkeLdPbuA", "name": "Caroline Gundersen" },
  { "public_id": "lzmy429KW9qb", "name": "Jack Pinsky" },
  { "public_id": "HmJ0d8Dzu6nT", "name": "Leah Wong" },
  { "public_id": "eDoajzvdSnYh", "name": "Katie Perritt" },
  { "public_id": "lSznByCwYnaw", "name": "Sam LoCoco" },
  { "public_id": "3zPM3BlrtN6C", "name": "Shega Case" }
];

// Make HTTP request
function makeRequest(options) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          resolve(data);
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

// Fetch portfolio data for a competitor
async function getPortfolioData(publicId) {
  const options = {
    hostname: 'vse-api.marketwatch.com',
    path: `/v1/statistics/portfolioPerformance?gameUri=${GAME_URI}&publicId=${publicId}`,
    method: 'GET',
    headers: {
      'accept': 'application/json',
      'accept-language': 'en-US,en;q=0.9',
      'cookie': AUTH_COOKIES,
      'dnt': '1',
      'origin': 'https://www.marketwatch.com',
      'referer': `https://www.marketwatch.com/games/${GAME_URI}`,
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }
  };

  try {
    const data = await makeRequest(options);
    return data;
  } catch (error) {
    console.error(`Error fetching portfolio data for ${publicId}:`, error);
    return null;
  }
}

// Main scraping function
async function scrapeCompetitionData() {
  console.log('Starting competition data scrape...');
  
  const competitors = [];
  const nameMap = {};
  
  // Create name mapping
  COMPETITORS.forEach(comp => {
    nameMap[comp.public_id] = comp.name;
  });

  // Scrape each competitor
  for (let i = 0; i < COMPETITORS.length; i++) {
    const comp = COMPETITORS[i];
    console.log(`Scraping competitor ${i + 1}/${COMPETITORS.length}: ${comp.public_id}`);
    
    try {
      const portfolioData = await getPortfolioData(comp.public_id);
      
      if (portfolioData && portfolioData.data && portfolioData.data.values) {
        const values = portfolioData.data.values;
        const latest = values[values.length - 1];
        
        const competitor = {
          public_id: comp.public_id,
          name: nameMap[comp.public_id] || 'Unknown Player',
          rank: 0, // Will be calculated after sorting
          portfolio_value: latest.w || 0.0,
          return_percentage: latest.p || 0.0,
          return_dollars: latest.g || 0.0,
          transactions: [], // We'll skip transaction scraping for now as it's complex
          last_updated: new Date().toISOString()
        };
        
        competitors.push(competitor);
        console.log(`  ✓ ${competitor.name} - $${competitor.portfolio_value.toLocaleString()}`);
      } else {
        console.log(`  ✗ Failed to get data for ${comp.public_id}`);
      }
      
      // Small delay to be respectful
      await new Promise(resolve => setTimeout(resolve, 500));
      
    } catch (error) {
      console.error(`Error processing ${comp.public_id}:`, error);
    }
  }

  // Sort by portfolio value (highest first) and assign ranks
  competitors.sort((a, b) => b.portfolio_value - a.portfolio_value);
  competitors.forEach((competitor, index) => {
    competitor.rank = index + 1;
  });

  console.log('Final standings:');
  competitors.slice(0, 5).forEach(comp => {
    console.log(`  ${comp.rank}. ${comp.name} - $${comp.portfolio_value.toLocaleString()}`);
  });

  // Create final data structure
  const competitionData = {
    competition: GAME_URI,
    scraped_at: new Date().toISOString(),
    competitors: competitors,
    activity_feed: [] // We'll skip activity feed for now
  };

  return competitionData;
}

// Netlify Function handler
exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  try {
    console.log('Netlify Function: update-data started');
    
    // Scrape fresh data
    const competitionData = await scrapeCompetitionData();
    
    // In a real deployment, you'd save this to a file or database
    // For now, we'll just return it so it can be manually saved
    console.log(`Scraped ${competitionData.competitors.length} competitors`);
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        message: `Successfully scraped ${competitionData.competitors.length} competitors`,
        data: competitionData,
        timestamp: new Date().toISOString()
      })
    };
    
  } catch (error) {
    console.error('Error in update-data function:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      })
    };
  }
};