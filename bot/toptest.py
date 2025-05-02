import requests
from bs4 import BeautifulSoup


def get_top_10_songs():
    url = "https://tophit.com/chart/top/youtube/hits/global/weekly"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    songnames = soup.find_all("a", {"class": "Name_name__1sQZg"})[0:10]
    top_songs = []
    top_links = []
    for a in songnames:
        songurl = "https://tophit.com" + a["href"]
        response2 = requests.get(songurl)
        soup2 = BeautifulSoup(response2.text, 'html.parser')
        link = soup2.find_all("a", {"aria-label": "Google Music"})
        top_links.append(link[0]["href"])
        span = a.find("span")
        song_name = span.get_text(strip=True)
        top_songs.append(song_name)

    # Save the top 10 songs into a text file
    with open('top_10_songs.txt', 'w', encoding='utf-8') as file:
        for i in range(10):
            if top_links[i].startswith('https://music.youtube.com/'):
                file.write(f"{top_songs[i]}, {top_links[i]}\n")
            else:
                file.write(f"{top_songs[i]}, -\n")

    print("Top 10 songs saved to 'top_10_songs.txt'.")


# Call the function
get_top_10_songs()
