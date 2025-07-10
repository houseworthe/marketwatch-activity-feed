#!/usr/bin/env python3
"""
Script to update frontend data from competition scraper.
Run this every 5 minutes to keep the frontend updated.
"""

import json
import shutil
import os
from datetime import datetime
from competition_scraper import CompetitionScraper
from leaderboard_scraper import scrape_leaderboard

def update_frontend_data():
    """Update the frontend JSON data file."""
    
    # Your fresh authentication cookies
    auth_cookies = 'refresh=off; letsGetMikey=enabled; refresh=off; letsGetMikey=enabled; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXQF8g; _pcid=%7B%22browserId%22%3A%22mc4yzz5cvpxw07b3%22%7D; cX_P=mc4yzz5cvpxw07b3; djcs_route=966396ea-5edb-4ce1-a7a5-26117bf651a0; TR=V2-c9d47073af3b9588751977fe4fbcf20f724a9bc94c79daba415c2eeb74a88ae0; djcs_auto=M1750367024%2FvqcMb8aJqCyDvD%2Bp4%2Fvy%2BJiAFKg5fZvadNlW5%2B6tPob1Ux%2F8CxJVZxpM3o7j2vhZOAMILVme9%2FLQlzzu9y8IKXamsLI7pQb%2FQ5M1MihrPMEk3sF9GGfMqFopxSs3%2BIt%2B1DUxn82dVaLUw7uKUk%2FiDTjS%2BzmL1XBKGa94d6bhelFEArIjIwCRNSZ2GAuc07sfEiDsMOrV8J1clJPuxicJ3dT879yl2tTfW2PxOI%2FfaIj6asUD0iUKcDIHsTi0HUv7%2F5qVvr76vbBnMftizItPBra55qpyQNAo8SNb2H0eBMD05Qkn0PRW%2Fuwi2gP2m6aO7QR%2BmMGp6HOUTU2sDzPUDB%2Bi5aJjS%2Fa0sYi0Djc446J79jy0mgplfbnJ%2BG32U%2BH0235i4ZIQdOnYwPoK5gR%2FJ%2FdJhA6Z%2BUMFTa%2FP3iYgc6Yv%2BWqeDBSaV5%2BVF%2BiTEr7sCa1uKl8JP3pg82rvoUB1gQ%3D%3DG; djcs_session=M1750430628%2F59I8D%2Bl49KcBfDxwh6Bp6FxgsnCYIPy6KL%2FM2PeI%2By7uZtzgKNyoQi6T2%2B0dCheRYYyxH29OJyBE3%2FeAX%2FjxxQoq2xitSco3%2F1Yu98h8iT1ea%2BUDtUMutK6qEqEhdTdjv8b0AAomqZw9HvBNkUIiZdc%2BFk16EsM0dYEzQaikaR7eD6HPTdt8jjVguKTFPc9mDM9bGBXKSftZN4iREbJ7prR%2Fkyy1gp3KD8WhH4jIfFBihOZRFdfcfxDLPdIL0wiPwhDWC%2BX0u75dHAQTtWBtf7ZgmKnMYBXrET4F5A3f17HQKOFNIIXERXF9RUzpxuRqHKR6CzK9dI6jElmJ9RiVuBp92HnnDglpM4RSiMyYNXyhP412z7m%2FL%2BfETluZNmbEK1j0mLOqIVkyhJbrNYjdCXDTDZmqH1BY03rXvN%2F5Hy17x%2F2BIoV9ayTyIYhVBC%2B9urxtiNHh66W1lyCqzLw8ETsxvw%2F9CvH8DrL8x1OU%2BOnM2%2FPhtdZnnbny0lmVyz%2FC3Lba8Jfhm1FCdjmIB%2F3cdvB9AoI6c6X0qixmGLJiRwz6%2FltWTlkv8bQzjrKIwSoNQ8amCyipAt4OdsJygpz7zw%3D%3DG; ab_uuid=05588ce5-0f6c-487b-8ab8-1426ce30f17d; wsjregion=na%2Cus; gdprApplies=false; ccpaApplies=false; vcdpaApplies=false; regulationApplies=gdpr%3Afalse%2Ccpra%3Afalse%2Cvcdpa%3Afalse; refresh=off; letsGetMikey=enabled; ca_rt=IXv-C9jkFcy69fAikw1gqQ._JN4amJoBEkZaLYOCmOf4FgJ_QMP9UsJgIiVG650EAEARkpvB2Uv7qoK26shrmbCz7JTQqbZw6fvODc8Gz6M1Y9DpnkxJesQ9ImPL1iXK00; datadome=~F9hNrk0f_vF7i04F4qXVPSkq5tnV4~PETGvgBlCfxSAw1uuyDsRaXhSU0Q6N0_lM1n6vcvQMjEB09yBTaKyCCe_FJjeyvXTzRIFHW50r2pjWnZ3rQG8g4QFPxcm3QkA; mw_loc=%7B%22Region%22%3A%22WI%22%2C%22Country%22%3A%22US%22%2C%22Continent%22%3A%22NA%22%2C%22ApplicablePrivacy%22%3A0%7D; ca_id=0f7b9586-b922-4403-8396-039962f63385.eJw9kFFTwjAQhP9Lnim0acolPNmRIjgKiKIjjsNc40RGSsE2UNHxvxtw9PW7vd29-yIrc1DlssSNIj2S2BxL0iIaN6Y4_tHhdl-rZlvZ3I3UBk3hoMr_6UXVpGiqrC23G6fY703mBJSikj5DL4PU95hPucdRUi8QPk8lDyHTwqlthXJ9XpAiY-BDiDpMRcQ5RIEA0IrpVGrqa6AMRSoFkyAyTJEFkaRKpcCQc1S-M6u2hapJ74UMZkkyS6680bg_ehz15_ENeW0R3Nt8ac3pqAAin4UhB2iR-hz_qSdGHxfjYjmZjrzZqoTo4SmOg9tDsTP5MHMbRz25vly_w3wa30MyeMbFnQuVlUKrsiXaky0TEdBu5GzNL4gCLrquq3vdx-4MaEj5GZjalSW5tbu61-k0TdNu6rfTFzuyMKq05PsHv4596Q.LM5NCaU8KolC1aMqQPq7IAn2KVUV412PMHi2EeqQN2c-nQLSN8DtUvYE8bkT4Ou4WUpwHm94nJVkniYt1zYG_NdGWBnOMcAruqnjVtpdRwkLRVM-ACeoPuAPL9W341xCNrDUDYOHBeMKSZRIJe7jCG3rj5zxrsHKs4qrsArOOtDWMKPqNxGNeXBYcOVoMgbTEY4Yn5RKxn2EF7IaAq9HOmP4d44l4D8ZaQ8SafuOajVTF9B5o1r7hQ8O9j4i96rVYb9Ehzk2Y6dj1UHiYXgjdUYPY5vQ4KmrjC4mIAgXMhP5pjkDH66AFIa2Mr_yJ9QLv_vY24npiKXVGjuRvkuJrA; icons-loaded=true; usr_prof_v2=eyJpYyI6NH0%3D'
    
    # Competition details
    game_uri = "baird-pwm-intern-stock-market-competition"
    
    try:
        print("Fetching leaderboard...")
        # Get all competitors from leaderboard
        competitors_info = scrape_leaderboard(game_uri, auth_cookies)
        public_ids = [comp[0] for comp in competitors_info]
        
        print(f"Found {len(public_ids)} competitors")
        
        # Create scraper
        scraper = CompetitionScraper(game_uri, auth_cookies)
        
        # Scrape all competitors
        print("Scraping competitor data...")
        competitors = scraper.scrape_all_competitors(public_ids, delay=2.0)
        
        # Create activity feed
        print("Creating activity feed...")
        activity_feed = scraper.create_activity_feed(competitors)
        
        # Prepare data for frontend
        frontend_data = {
            'competition': game_uri,
            'scraped_at': datetime.now().isoformat(),
            'competitors': [c.to_dict() for c in competitors],
            'activity_feed': activity_feed
        }
        
        # Save to competition_data.json
        with open('competition_data.json', 'w') as f:
            json.dump(frontend_data, f, indent=2)
        
        # Copy to frontend public directory
        frontend_path = 'frontend/public/competition_data.json'
        if os.path.exists('frontend/public'):
            shutil.copy('competition_data.json', frontend_path)
            print(f"Updated {frontend_path}")
        
        print(f"Successfully updated data - {len(competitors)} competitors, {len(activity_feed)} activities")
        
    except Exception as e:
        print(f"Error updating data: {e}")
        # Keep existing data if update fails
        pass

if __name__ == "__main__":
    update_frontend_data()