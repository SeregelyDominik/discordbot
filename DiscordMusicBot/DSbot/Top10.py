import requests
from bs4 import BeautifulSoup


class Top10:

    def get_top_10_songs(self):
        """Top 10 zeneszám letöltése külső oldalról"""
        url = "https://tophit.com/chart/top/youtube/hits/global/weekly"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        songnames = soup.find_all("a", {"class": "Name_name__1sQZg"})[0:10]
        top_songs = []
        top_links = []
        top_eloadok = []
        for a in songnames:
            songurl = "https://tophit.com" + a["href"]
            response2 = requests.get(songurl)
            soup2 = BeautifulSoup(response2.text, 'html.parser')
            link = soup2.find_all("a", {"aria-label": "Google Music"})
            div = soup2.find_all("div",
                                 {"class": "truncate text-lg text-gray-500"})
            eloadok = div[0].find_all("a",
                                      {"class": "text-tophit-"
                                                "blue dark:opacity-95"})
            lista = []
            for e in eloadok:
                lista.append(e.text)
            top_eloadok.append(lista)
            top_links.append(link[0]["href"])
            span = a.find("span")
            song_name = span.get_text(strip=True)
            top_songs.append(song_name)

        # fájlba kiírás
        with open('top_10_songs.txt', 'w', encoding='utf-8') as file:
            for i in range(10):
                eload = ""
                for e in top_eloadok[i]:
                    eload += e + " & "
                eload = eload.removesuffix("& ").strip()
                if top_links[i].startswith('https://music.youtube.com/'):
                    file.write(f"{top_songs[i]}, {eload}, {top_links[i]}\n")
                else:
                    file.write(f"{top_songs[i]}, {eload} -\n")
