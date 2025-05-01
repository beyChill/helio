from cmd2 import CommandSet, categorize
from argparse import Namespace
from stardust.utils.applogging import HelioLogger

log = HelioLogger()


class MyFreeCams(CommandSet):
    # prompt = "MFC-->"
    def __init__(self):
        super().__init__()

    def do_get(self,streamer:Namespace):
        """Capture a streamer

        example:
        MFC--> get <streamer's_name>
        """
        pass
        name_ = streamer.name[0]

    # def make_dl_url():
    #     query_url_data(["streamer_"])
    #     get_user_profile(["streamer_"])
    #     rand_val = random.random()
    #     url=f"ffprobe -i https://edgevideo.myfreecams.com/llhls/NxServer/408/ngrp:mfc_a_122478911.f4v_cmaf/playlist_sfm4s.m3u8?nc={rand_val}&v=1.97.24"
        # url2=f"https://previews.myfreecams.com/hls/NxServer/1147/ngrp:mfc_a_139203630.f4v_mobile_mhp1080_previewurl/playlist.m3u8"
        # https://previews.myfreecams.com/hls/NxServer/1147/ngrp:mfc_a_139203630.f4v_mobile_mhp1080_previewurl/chunklist_rhGk0Kcgw4C_previewurl_b5000000.m3u8
        # https://edgevideo.myfreecams.com/llhls/NxServer/1147/ngrp:mfc_a_139203630.f4v_cmaf/playlist_sfm4s.m3u8?nc=0.20980551166925328&v=1.97.24
        # chunklist_rhGk0Kcgw4C_previewurl_b5000000.m3u8


        url3=f"https://edgevideo.myfreecams.com/llhls/NxServer/{1104}/ngrp:mfc_{a_113478259}.f4v_mobile/playlist.m3u8?nc={rand_val}&v=1.97.23"


    def do_stop(self,ns:Namespace):
        """Stop Streamer Capture

        example:
        MFC--> stop <streamer's_name>
        """
        pass

    def do_block(self,ns:Namespace):
        """Block streamer from long captures
        MFC--> get my_fav_girl
        """
        pass

    categorize((do_get, do_stop, do_block), "MyFreeCams Streamer")