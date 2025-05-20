<meta property="og:site_name" content="Helio"/>
<meta property="og:title" content="Helio: Python Web interactions" />
<meta property="og:description" content="Fast, easy, and reliable CLI/UI" />
<meta property="og:keywords" content="Python, stream, ffmpeg, download, record, video, chaturbate, adult, cmd2, stripchat, curl_cffi, screenshots, jpgs, images"/>
<link rel="stylesheet" href="github-markdown.css">

<p id="top" align="center">
    <b><h1 align="center">Helio</h1></b>
</p>

<p align="center">An educational app for testing and comprehending python's
    <br/> capabilities to interact, monitor, and capture stream data
    <br/> for a small number of specific internet sites.
    <br/> (primarliy mature / adult sites)
</p>

<p align='center' >
    <a href="#considerations">Considerations</a> |
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

<div id="toc" align="center">
    <ul style="list-style: none;">
    <summary>
        <h2 id="considerations">Considerations</h2>
    </summary>
    </ul>
</div>

- Fast storage (SSD) for real-time access
- Whatever long term storage for videos
- mitmproxy (for web browser intercepts) provides the certificates for <b style="color:orange;">https</b> access when active
    - <a title="mitmproxy" href="https://docs.mitmproxy.org/stable/concepts-certificates/">mitmproxy</a>

<!-- <ul>
    <li>Fast storage (SSD) for real-time access</li>
    <li>Whatever long term storage for videos</li>
    <li>mitmproxy provides the certificates for <b style="color:orange;">https</b> access</li>
    <span><a title="mitmproxy" href="https://docs.mitmproxy.org/stable/concepts-certificates/">mitmproxy</a></span>            
</ul> -->

<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>

<hr style="height:2px;border-width:0;color:gray;">


<div id="toc" align="center">
    <ul style="list-style: none;">
    <summary>
        <h2 id="installation">Installation</h2>
    </summary>
    </ul>
</div>


<h3>Prerequisite</h3>

- uv - An ultra fast project and package manager.
    - <a title="uv by Atrfal" href="https://docs.astral.sh/uv/getting-started/installation/">uv Astral</a>
- Some versions of linux (Fedora) require Xvfb install to use Seleniumbase without display error messages in the console
```bash
sudo dnf install xorg-x11-server-Xvfb
```
    

<p>Clone from github</p>

```bash
git clone https://github.com/beyChill/helio.git <project name>
cd <project name>
uv run main.py
source .venv/bin/activate
uv pip install -e .
uv sync
```

**Update ``Helio`` from a GitHub clone:**

```bash
git pull
uv pip install -e .
```


<p>
    After the inital run security certificates will be install in ~/.mitmproxy
</p>

<span>Ubuntu/Debian</span>
<span> <a title="Install a root CA certificate in the trust store" href="https://documentation.ubuntu.com/server/how-to/security/install-a-root-ca-certificate-in-the-trust-store/index.html">(Detailed instructions)</a></span>

```bash
mv mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt
sudo update-ca-certificates
```

<span>Fedora</span>
<span> <a title="Using Shared System Certificates" href="https://docs.fedoraproject.org/en-US/quick-docs/using-shared-system-certificates/#proc_adding-new-certificates">(Detailed instructions)</a></span>

```bash
mv mitmproxy-ca-cert.pem /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust
```

<span>Arch Linux</span><span> <a title="Transport Layer Security" href="https://wiki.archlinux.org/title/Transport_Layer_Security#Add_a_certificate_to_a_trust_store">(Detailed instructions)</a></span>

```bash
sudo trust anchor mitmproxy-ca-cert.pem
```


<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>
<hr style="height:2px;border-width:0;color:gray;">

<div id="toc" align="center">
    <ul style="list-style: none;">
    <summary>
        <h2 id="config">Config</h2>
    </summary>
    </ul>
</div>

<div>
    <p>
        Managed setting are located in settings.py file. ( Path: stardust/config/settings.py )
        The thought was simple in the beginning.  However, as Helio grows so does the size of settings.py.  Perhaps beyChill will look into other options. 
        Consideration is being made for live config changes.
    </p>
</div>

<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>
<hr style="height:2px;border-width:0;color:gray;">

<div id="toc" align="center">
    <ul style="list-style: none;">
    <summary>
        <h2 id="dev_notes">Dev Notes</h2>
    </summary>
    </ul>
</div>


<p>
    Windows compatibility: <b style="color:red">ZERO interest</b>.<br/> Any user is free to modify this software for use on platforms outside of Linus
</p>

<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>
<hr style="height:2px;border-width:0;color:gray;">

<div id="toc" align="center">
    <ul style="list-style: none;">
    <summary>
        <h2 id="Requirements">Tech</h2>
    </summary>
    </ul>
</div>

<div >
<p>
Knowledge share for some packages in Helio's tech stack
<ul>
    <li><a href="https://github.com/python-cmd2/cmd2">cmd2: </a>Cli</li>
    <li><a href="https://github.com/0x676e67/rnet">rnet: </a>internet stuff</li>
    <li><a href="https://github.com/PyGithub/PyGithub">pygithub: </a>github api</li>
    <li><a href="https://github.com/theskumar/python-dotenv">python-dotenv: </a>.env stuff</li>
    <li><a href="https://mitmproxy.org">mitmproxy: </a>browser stuff</li>
    <li><a href="https://mitmproxy.org">mitmproxy: </a>Seleniumbase automated browser</li>
</ul>
</p>
</div>
<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>
<hr style="height:2px;border-width:0;color:gray;">

<div id="toc" align="center">
    <ul style="list-style: none;">
    <summary>
        <h2 id="sites">Sites</h2>
    </summary>
    </ul>
</div>


<div>
    <ul>
        <li>Chaturbate: active</li>
        <li>StripChat: planning</li>
        <li>MyFreeCams: 83%</li>
        <li>StreaMate: planning</li>
    </ul>
</div>

<p style="font-size:30px">
    <a href="#top" title="Move to page top">⬆️</a>
</p>

<hr style="height:2px;border-width:0;color:gray;">

<div id="toc" align="center">
    <ul style="list-style: none;">
    <summary>
        <h2 id="disclaimer">Disclaimer</h2>
    </summary>
    </ul>
</div>


<div >
<p>beyChill <b style="color:red">does not</b> provide any warranty of any kind, expressed or implied, relating to the open-source Helio and its use.  beyChill <b style="color:red">disclaims</b> all expressed and/or implied warranties and conditions pertaining in any way to any open-source integrated into Helio code. beyChill <b style="color:red">does not</b> warrant that Helio will integrate error-free with other software running on any machine. Helio may become <b style="color:red">abandoned</b> at any time. beyChill <b style="color:red">is not</b> required to provide prior notice for Helio <b style="color:red">depreciated support</b>. Use of Helio will <b style="color:red">never</b> require any monetary exchange. beyChill will <b style="color:red">never</b> request any donation and/or compensation for Helio.</p></div>
<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>
<hr style="height:2px;border-width:0;color:gray;">

<div id="toc" align="center">
    <ul style="list-style: none;">
    <summary>
        <h2 id="usage">Usage</h2>
    </summary>
    </ul>
</div>

<p>Make sure the .venv is active.</p>

```bash
$ source .venv/bin/activate
(helio) $
```
<p>Run setup_dirs.py from stardust directory prior to accessing cli.</p>

Run start script from stardust directory.<br/>
( help screen is visible after entering the help command )

```bash
(helio) $ uv run stardust/start.py
Helio--> help
Helio--> app cb
chaturbate interactions are ready
CB--> help
CB--> unapp cb
Helio--> app mfc
myfreecams interactions are ready
MFC--> help
MFC--> unapp mfc
Helio--> quit
```
***IMPORTANT***
<p>The different sites cli (cb, mfc, sc, etc.) use commands with identical names.</br>
Issue the 'unapp' command before activating another site to prevent an error.</p>

***IMPORTANT***
<p>Capitalization is very important with MyFreeCams streamer's names. The MFC app has lowercased streamer names.</br>
Please ensure correct capitalization otherwise database will contain duplicate streamers</p>
<p style="font-size:30px"><a href="#top" title="Move to page top">⬆️</a></p>
