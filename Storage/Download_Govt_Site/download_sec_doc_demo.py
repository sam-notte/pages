import notte
from notte_storage.local import LocalStorage

output_filename = "NVIDIA_SEC_FILING.csv"
output_dir = "NVIDIA_SEC_FILING/"
storage = LocalStorage(download_dir=output_dir)

with notte.Session(storage=storage, browser_type="chrome", headless=False, chrome_args=[]) as session:
    agent = notte.Agent(session=session, reasoning_model="vertex_ai/gemini-2.0-flash")
    response = agent.run(
        task=f"""Navigate to the SEC site and search for Nvidia
Click on the first result and then click on 'View Filings'
Download the full CSV as {output_filename}.""",
        url="https://www.sec.gov/",
    )

    print(response)
