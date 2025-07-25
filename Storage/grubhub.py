import notte

# ENTER YOUR DETAILS HERE
first_name = "Andrea"
last_name = "Pinto"
phone_number = "+14154305422"
address = "730 clayton st, sf"

# THE PROMPT - KEEP THIS AS IS
prompt = f"""
1. Go to https://www.grubhub.com/
2. Search food for delivery at {address}
3. Search for "McDonald's" on the top right corner text box and click on the closest McDonald's restaurant
4. Find and add a Big Mac Meal to your cart - select Medium size for the meal, French Fries as the side, \
and Coke as the drink, then click Add to Bag
5. Go to the cart and click on proceed to checkout
7. Fill the recipient details - First name: {first_name}, Last name: {last_name}, Phone number: {phone_number}
"""

# TODO make it a vault example

with notte.Session(headless=False, proxies=False, browser_type="chrome", solve_captchas=False) as session:
    agent = notte.Agent(session=session, max_steps=25, reasoning_model="vertex_ai/gemini-2.5-flash")
    response = agent.run(task=prompt)
    response.replay(screenshot_type="last_action").save("out/agent.webp")
