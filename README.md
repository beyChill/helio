<meta property="og:site_name" content="Helio"/>
<meta property="og:title" content="Helio: Python Web interactions" />
<meta property="og:description" content="Fast, easy, and reliable CLI/UI" />
<meta property="og:keywords" content="Python, stream, ffmpeg, download, record, video, chaturbate, adult, cmd2, stripchat, curl_cffi, screenshots, jpgs, images"/>
<link rel="stylesheet" href="github-markdown.css">



<p id="top" align="center">
    <b><h1 align="center">Helio</h1></b>
</p>

<p align="center">An educational app for testing and comprehending python
    <br/> and rust capabilities to interact, monitor, and capture stream
    <br/> data for a small number of specific internet sites.
    <br/> (primarliy mature / adult sites)
</p>

<p align="center">
    <b><h2 align="center">Helio ...new direction (2025-06-30)</h2></b>
</p>

<p align="center">Having recently viewed some rust code. I decided on impulse to take Helio into rusty land.</br> Therefore, a pure python Helio is lower on the time allocation list.</br>Follow as I learn and implement rust.

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
    <!-- <img alt="GitHub Downloads (all assets, all releases)" src="https://img.shields.io/github/downloads/beyChill/helio/total?style=for-the-badge&labelColor=blue"> -->
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
    - Helio can capture as many streams as your system can handle
- Whatever long term storage for videos

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

- Rust
  - <a title="Rust" href="https://www.rust-lang.org/tools/install">Rust install instructions</a>

- uv - An ultra fast project and package manager.
  - <a title="uv by Astral" href="https://docs.astral.sh/uv/getting-started/installation/">uv install instructions</a>

\*\*Optional, populate .env with applicable strings.

An example is in the root directory.

- env_example

Expect Helio to create folders and databases.  

<h3>Clone Helio from github</h3>
<h4>Recommended install steps</h4>


- Note: The uv cache location impacts performance.

    - A cache on a drive separate from the project may generate uv errors

```bash
export UV_CACHE_DIR=<place on same drive as project>
git clone https://github.com/beyChill/helio.git
cd helio
uv venv .venv --prompt Helio
source .venv/bin/activate
uv sync
uv pip install -e .
uv run stardust/setup_dirs.py
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
    Windows compatibility: <b style="color:red">ZERO interest</b>.<br/> Any user is free to modify this software for use on platforms outside of Linux
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
    <li><a href="https://github.com/0x676e67/rnet">rnet: </a>TLS/HTTP2 client</li>
    <li><a href="https://github.com/PyGithub/PyGithub">pygithub: </a>Access GitHub api</li>
    <li><a href="https://github.com/theskumar/python-dotenv">python-dotenv: </a>Environment variables</li>

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
        <li>MyFreeCams: active</li>
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

# use help command to access features
Helio--> help

# use load command to switch sites
Helio--> load cb
chaturbate interactions are ready
CB-->  get ann456
22:02:56 [CAPTURING]: ann456 [CB]
CB-->  load mfc
myfreecams interactions are ready
MFC--> get emma_hot
05:49:56 [CAPTURING]: emma_hot [MFC]
MFC--> unload mfc
Helio--> quit
```

**_IMPORTANT_**

<p>The different sites cli (cb, mfc, sc, etc.) use commands with identical names.</br>
Issue the 'load' command for the specific site to obtain the desired results.</p>

```python
helio--> load mfc
myfreecams interactions are ready
MFC--> get adysweet
05:18:56 [CAPTURING]: adysweet [MFC]

```

