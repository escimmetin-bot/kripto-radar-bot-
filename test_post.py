from playwright.sync_api import sync_playwright
import time
import os
import config

print("Starting Playwright X test...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800}
    )
    ctx.add_cookies([
        {"name": "auth_token", "value": config.TWITTER_AUTH_TOKEN, "domain": ".x.com", "path": "/", "secure": True, "httpOnly": True},
        {"name": "ct0", "value": config.TWITTER_CT0, "domain": ".x.com", "path": "/", "secure": True, "httpOnly": False}
    ])

    page = ctx.new_page()
    page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)

    page.screenshot(path="output/step1_compose_modal.png")
    print("Step 1 screenshot saved")

    editor = page.locator('div[role="textbox"][data-testid="tweetTextarea_0"]')
    if not editor.count():
        editor = page.locator('div[role="textbox"]')
    print("Editor count:", editor.count())

    test_text = "🚨 Kripto & Finans Radarı Test Yayını\n\nBitcoin ve altcoin piyasalarında sıcak gelişmeler anlık olarak burada.\n\n#Kripto #Bitcoin"
    editor.first.click()
    editor.first.fill(test_text)
    time.sleep(2)

    card_p = os.path.abspath("output/crypto_binance-hacker-altcoin-sa.jpg")
    if os.path.exists(card_p):
        file_input = page.locator('input[data-testid="fileInput"]').first
        print("FileInput count:", file_input.count())
        if file_input.count():
            file_input.set_input_files(card_p)
            time.sleep(4)

    page.screenshot(path="output/step2_filled.png")
    print("Step 2 screenshot saved")

    post_btn = page.locator('button[data-testid="tweetButton"]').first
    if not post_btn.count():
        post_btn = page.locator('button[data-testid="tweetButtonInline"]').first
    print("Post button count:", post_btn.count(), "disabled:", post_btn.get_attribute("aria-disabled"))

    # Close any autocomplete dropdown (Hashtags/Mentions)
    page.keyboard.press("Escape")
    time.sleep(1)

    # Press Control+Enter to publish
    editor.first.focus()
    page.keyboard.press("Control+Enter")
    print("Pressed Control+Enter")
    time.sleep(4)

    # If still visible, click the visible post button with force=True
    visible_btn = page.locator('button[data-testid="tweetButton"]').last
    if visible_btn.count():
        try:
            visible_btn.click(force=True)
            print("Clicked visible Post button with force=True")
            time.sleep(5)
        except Exception as e:
            print("Click error:", e)

    page.screenshot(path="output/step3_after_click.png")
    print("Step 3 screenshot saved")
    browser.close()
