# stlitepack

[<img src="https://img.shields.io/pypi/v/stlitepack?label=pypi%20package">](https://pypi.org/project/stlitepack/)

stlitepack is a Python utility that helps you turn your existing Streamlit apps into [stlite apps — lightweight, browser-only Streamlit apps that run entirely in the client without a server](https://github.com/whitphx/stlite).

With stlitepack, you can:

- 📦 Pack your Streamlit app into a stlite-ready format (current functionality).
- 🚀 (Upcoming) Generate GitHub Actions workflows to auto-deploy your app to GitHub Pages.
- 🗂️ (Planned) Add support for multi-page apps, external resources, and more.

## 📦 Installation

```bash
pip install stlitepack
```

## 🚀 Usage

```python
from stlitepack import pack

# Pack your Streamlit app (e.g., "app.py") into a stlite bundle
pack("app.py", output_dir="docs")
```

This will create a docs/ folder containing your stlite-ready app files, which you can serve as static files.

## 🔮 Roadmap

- ✅ v0.1: Single-page app packing
- ✅ v0.2: Helper functions for GitHub Pages auto-deploy (via GitHub Actions workflow generation)
- ✅ v0.3: Multi-page app support (for [`pages/` subfolder](https://webapps.hsma.co.uk/multipage.html#method-2-pages-subfolder) method)
- v0.4: Better support for resource bundling (images, CSVs, assets, etc.) of local or web-based files
- v0.5: Better multi-page app support (for [`st.navigation()`](https://webapps.hsma.co.uk/multipage.html#method-1-st.page-and-st.navigation) method)
- v0.6: Auto-handling of stlite-specific features (e.g. asyncio vs sleep)
- v0.7: Add support for generating the required package.json for [desktop app bundling](https://github.com/whitphx/stlite/tree/main/packages/desktop)
- v0.8: Add helpers for generating files for additional deployment options e.g. Docker, Caddy, Nginx, Apache
- v0.9: TOML or YAML file support as optional alternative to the packing function
- v1.0: Full toolkit for packaging, deploying, and managing stlite apps

## 🤝 Contributing
Contributions, feature requests, and feedback are welcome!
Open an issue or submit a pull request to help improve stlitepack.

## 📜 License
Apache 2.0 License. See LICENSE for details.

## Acknowledgements

- [whitphx](https://github.com/whitphx) for creating the amazing [stlite](https://github.com/whitphx/stlite) framework!

## Generative AI Use Disclosure

This package was developed with the assistance of ChatGPT (OpenAI’s GPT-5 model) as a coding and documentation partner.
All code and design decisions were reviewed and finalized by a human, and ChatGPT’s output was used as a foundation rather than a final product.
