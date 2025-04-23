<meta property="og:site_name" content="Helio">
<meta property="og:title" content="Helio: Python Web interactions" />
<meta property="og:description" content="Fast, easy, and reliable CLI/UI" />
<meta property="og:keywords" content="Python, stream, ffmpeg, download, record, video, chaturbate, adult, cmd2, stripchat, curl_cffi, screenshots, jpgs, images">
<!-- <link rel="stylesheet" href="github-markdown.css"> -->

<p id="top" align="center"><b>
    <h1 align="center">Helio</h1></b>
</p>

<p align="center">An educational app for testing and comprehending python's
    <br/> capabilities to interact, monitor, and capture stream data
    <br/> for a small number of specific internet sites.
    <br/> (primarliy mature / adult sites)
</p>

<p align='center' >
    <a href="#requirements">Requirements</a> |
    <a href="#installation">Installation</a> |
    <a href="#config">Config</a> |
    <a href="#dev_notes">Dev Notes</a> |
    <br/>
    <a href="#tech">Tech</a> |
    <a href="#sites">Sites</a> |
    <a href="#disclaimer">Disclaimer</a> |
    <a href="#usage">Usage</a> |
</p>

<p align="center">Platform: Linux</p>

<div align="center">
    <img style="margin-right:15px;" alt="Static Badge" src="https://img.shields.io/badge/MIT-orange?style=for-the-badge&label=license&labelColor=blue">
    <img style="margin-right:15px;" alt="GitHub last commit" src="https://img.shields.io/github/last-commit/beyChill/helio?style=for-the-badge&labelColor=blue">
    <img style="margin-right:15px;" alt="GitHub Release Date" src="https://img.shields.io/github/release-date/beyChill/helio?style=for-the-badge&labelColor=blue">
    <img alt="GitHub Downloads (all assets, all releases)" src="https://img.shields.io/github/downloads/beyChill/helio/total?style=for-the-badge&labelColor=blue">
</div>

<hr style="height:2px;border-width:0;color:gray;">

<div align="center">
    <h3 id="Requirements">Considerations</h3>
</div>

<ul>
    <li>Fast storage (SSD) for real-time access</li>
    <li>Whatever long term storage for videos</li>
    <li>mitmproxy provides <b style="color:orange">https</b> access install the mitmproxy security certificates</li>
    <li><a>https://docs.mitmproxy.org/stable/concepts-certificates/</a></li>            
</ul>

<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>

<hr style="height:2px;border-width:0;color:gray;">

<div align="center">
    <h3 id="installation">Installation</h3>
</div>

<h5>Prerequisite</h5>

<p>uv - An ultra fast project and package manager.<br/>
    https://docs.astral.sh/uv/getting-started/installation/<br/>
</p>

<p>Clone from github</p>

```bash
git clone https://github.com/beyChill/helio.git <project name>
cd <project name>
uv init .
uv run main.py
source /bin/.venv/activate
```

<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>
<hr style="height:2px;border-width:0;color:gray;">
<div align="center">
    <h3 id="config">Config</h3>
</div>

<div >
    <p>
        Managed setting are located in settings.py file. ( Path: stardust/config/settings.py )
        The thought was simple in the beginning.  However, as Helio grows so does the size of settings.py.  Perhaps beyChill will look into other options. 
        Consideration is being made for live config changes.
    </p>
</div>
<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>
<hr style="height:2px;border-width:0;color:gray;">
<div align="center">
    <h3 id="dev_notes">Dev Notes</h3></div>
<div style="margin-left:15px">
<p>
    Windows compatibility: <b style="color:red">ZERO interest</b>. Any user is free to modify this software for use on platforms outside of Linus
</p>
</div>
<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>
<hr style="height:2px;border-width:0;color:gray;">
<div align="center">
    <h3 id="tech">Tech</h3>
</div>
<div >
<p>
Knowledge share for some packages in Helio's tech stack
<ul>
    <li><a href=https://github.com/python-cmd2/cmd2>cmd2: Cli</a></li>
    <li><a href=https://github.com/0x676e67/rnet>rnet: internet stuff</a></li>
    <li><a href=https://github.com/PyGithub/PyGithub>pygithub: github api</a></li>
    <li><a href=https://github.com/theskumar/python-dotenv>python-dotenv: .env stuff</a></li>
</ul>
</p>
</div>
<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>
<hr style="height:2px;border-width:0;color:gray;">
<div align="center">
    <h3 id="sites">Sites</h3>
</div>
<div>
    <ul>
        <li>Chaturbate: active</li>
        <li>StripChat: planning</li>
        <li>MyFreeCams: planning</li>
        <li>StreaMate: planning</li>
    </ul>
</div>
<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>
<hr style="height:2px;border-width:0;color:gray;">
<div align="center">
    <h3 id="disclaimer">Disclaimer</h3>
</div>

<div >
<p>beyChill <b style="color:red">does not</b> provide any warranty of any kind, expressed or implied, relating to the open-source Helio and its use.  beyChill <b style="color:red">disclaims</b> all expressed and/or implied warranties and conditions pertaining in any way to any open-source integrated into Helio code. beyChill <b style="color:red">does not</b> warrant that Helio will integrate error-free with other software running on any machine. Helio may become <b style="color:red">abandoned</b> at any time. beyChill <b style="color:red">is not</b> required to provide prior notice for Helio <b style="color:red">depreciated support</b>. Use of Helio will <b style="color:red">never</b> require any monetary exchange. beyChill will <b style="color:red">never</b> request any donation and/or compensation for Helio.</p></div>
<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>
<hr style="height:2px;border-width:0;color:gray;">
<div align="center">
    <h3 id="usage">Usage</h3>
</div>
<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>
