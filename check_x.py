from playwright.sync_api import sync_playwright
import time
import json
import config

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    c = b.new_context()
    c.add_cookies([
        {'name': 'auth_token', 'value': config.TWITTER_AUTH_TOKEN, 'domain': '.x.com', 'path': '/'},
        {'name': 'ct0', 'value': config.TWITTER_CT0, 'domain': '.x.com', 'path': '/'}
    ])
    page = c.new_page()
    page.goto('https://x.com/home', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)
    
    # URL ve başlık
    print("Page URL:", page.url)
    print("Page title:", page.title())

    # Profil linki
    user_elem = page.locator('a[data-testid="AppTabBar_Profile_Link"]')
    if user_elem.count():
        print("Profile href:", user_elem.get_attribute('href'))

    # Account switcher
    btn = page.locator('div[data-testid="SideNav_AccountSwitcher_Button"]')
    if btn.count():
        print("Account info:", btn.inner_text().replace('\n', ' | '))

    page.goto('https://x.com/kriptofinansa', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)
    page.screenshot(path='output/kriptofinansa_profile.png')
    print("Profile screenshot saved to output/kriptofinansa_profile.png")
    b.close()
