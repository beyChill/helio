import m3u8

from stardust.utils.applogging import HelioLogger

log=HelioLogger()
def get_m3u8_bandwidth(m3u8_url):
    m3u8_ =m3u8.load(m3u8_url)
    if not m3u8_.is_variant:
        log.error("The m3u8 does not contain variant playlists")
        return(m3u8_url)

    top_bandwidth = max(
                m3u8_.playlists,
                key=lambda x: x.stream_info.bandwidth
                if isinstance(x.stream_info.bandwidth, int) else False
            )
    return top_bandwidth


# Example Usage
# m3u8_url = "YOUR_M3U8_URL_HERE"
m="https://edge3-chi.live.mmcdn.com/live-hls/amlst:eli_sun-sd-a1c1b8405cdc1bc90143ed71a224466e40d1fb090827ee5e5f1ff97dfbb8050d_trns_h264/playlist.m3u8"
best_quality_url = get_m3u8_bandwidth(m)

if best_quality_url:
    print(f"Best quality URL: {best_quality_url}")
else:
    print("Failed to get best quality URL.")
