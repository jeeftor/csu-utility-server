"""CSU Scraper Playwright Module."""
import sqlite3
import aiofiles
from playwright.async_api import async_playwright

from .const import _LOG, CSU_URL


class CSU:
    """CSU Scraper class."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize the class."""
        self.username = username
        self.password = password

        self.con = sqlite3.connect("utility.sqlite")
        self.cur = self.con.cursor()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the DB (if necessary)."""
        # Create table if missing
        tables = self.cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()

        wanted_tables = ["gas", "electric", "water"]

        for t in wanted_tables:
            if (t,) not in tables:

                self.cur.execute(f"CREATE TABLE {t}(date PRIMARY KEY, time, usage)")
                _LOG.info(f"Creating table {t}")

    async def download_gas(self) -> None:
        """Download gas usage data."""
        return await self._get_utility(type="GAS")

    @property
    def latest_gas(self):
        """Get the latest gas entry from the DB."""
        statement = "SELECT * from gas ORDER BY date DESC"
        self.cur.execute(statement)
        latest = self.cur.fetchone()  # format is [ date, time, usage]
        return dict(zip(["date", "time", "usage"], latest))

    async def _get_utility(self, type: str) -> None:
        """Run a playwright login to CSU and gets the requested utility."""
        async with async_playwright() as p:
            browser_type = p.webkit
            browser = await browser_type.launch()
            page = await browser.new_page()
            await page.goto(CSU_URL)
            _LOG.info("Loading %s", CSU_URL)
            await page.focus("#userId")
            await page.keyboard.type(self.username)
            await page.focus("#password")
            await page.keyboard.type(self.password)
            await page.click("a#LoginButton")

            # Goto My Usage
            await page.click('a[href="myusage"]')
            await page.wait_for_selector("div.CSUMyUsageButton")

            # Extract Options & Values
            # If you produce electric with solar this will be messed up
            handles = await page.query_selector_all(
                "#ContentPlaceHolder1_UI_ExternalUserControl1_dlLocationID option"
            )

            current_reads = [await x.inner_html() for x in handles]
            print(current_reads)

            # Overyly complicated way to turn the stuff into a dictionary
            options = dict(
                zip(
                    [(await x.inner_html()).split("/ ")[1].rstrip() for x in handles],
                    [await x.get_attribute("value") for x in handles],
                )
            )

            # Select the selected option ( could error out here however )
            await page.select_option(
                "#ContentPlaceHolder1_UI_ExternalUserControl1_dlLocationID",
                options[type],
            )

            async with page.expect_download() as download_info:

                # Start the download
                await page.click(
                    "input#ContentPlaceHolder1_UI_ExternalUserControl1_btnCsv"
                )
            download = await download_info.value
            # Wait for DL to complete
            print(await download.path())

            await download.save_as(f"/tmp/{type}.csv")
            await self._parse_data(f"/tmp/{type}.csv")

    async def _parse_data(self, filename: str) -> None:
        async with aiofiles.open(filename, mode="r") as f:
            await f.readline()
            await f.readline()
            async for line in f:
                date, time, usage = line.split(",")[0:3]
                m, d, y = date.split("/")
                print(date, time, usage)
                date = f"{y}/{m}/{d}"

                # Insert into DB
                table = "gas"
                insert = f"INSERT OR IGNORE INTO {table} (date,time,usage) VALUES ('{date}','{time}','{usage}')"
                self.cur.execute(insert)
                self.con.commit()
