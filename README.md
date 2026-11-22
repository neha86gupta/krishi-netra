# Krishi Netra - crop leaf disease detector (educational prototype)

Predicts crop + disease (or healthy) from a leaf photo, shows confidence, a Grad-CAM heatmap, and static
reference advice. It says "not sure" when confidence is low. Not professional agricultural advice.

## Data and licences
- **PlantVillage** (training data) via Hugging Face `mohanty/PlantVillage`, `color` config. Licence:
  **CC BY-SA 3.0**, as stated by the original authors, who also state that algorithms trained on the data fall
  under the same licence. Some third-party mirrors list CC0 1.0 for a separately uploaded Mendeley copy; this
  project follows the stricter statement. Model weights trained here should be shared under CC BY-SA 3.0.
- **PlantDoc** (field TEST set only, never trained on): CC BY 4.0 for the compilation; images are web-scraped.

## Citations
```
@article{Mohanty_Hughes_Salathe_2016, title={Using deep learning for image-based plant disease detection},
  volume={7}, DOI={10.3389/fpls.2016.01419}, journal={Frontiers in Plant Science},
  author={Mohanty, Sharada P. and Hughes, David P. and Salath{\'e}, Marcel}, year={2016}, month={Sep}}
@article{DBLP:journals/corr/HughesS15, author={David P. Hughes and Marcel Salath{\'e}},
  title={An open access repository of images on plant health to enable the development of mobile disease
  diagnostics through machine learning and crowdsourcing}, journal={CoRR}, volume={abs/1511.08060}, year={2015}}
@inproceedings{10.1145/3371158.3371196, author={Singh, Davinder and Jain, Naman and Jain, Pranjali and Kayal, Pratik
  and Kumawat, Sudhakar and Batra, Nipun}, title={PlantDoc: A Dataset for Visual Plant Disease Detection},
  year={2020}, doi={10.1145/3371158.3371196}, booktitle={Proceedings of the 7th ACM IKDD CoDS and 25th COMAD}}
```

## Windows quick start (VS Code PowerShell, CPU only)
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1          # if blocked: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
python -m pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

python -m src.model                              # times the 3 backbones on your CPU
python -m src.download_data                      # add --pv-limit 3000 for a tiny trial first
python -m src.preprocess                         # then review data\field_test\class_map.json, set "reviewed": true
python -m src.train --subset 40 --epochs 1       # quick pipeline test
python -m src.evaluate --split test
python -m src.train --subset 300 --epochs 4 --ft-epochs 3   # feasible full-pipeline run (omit --subset for all data)
python -m src.baseline --subset 300
python -m src.evaluate --split all --ood-dir "C:\path\to\non_leaf_photos"
python -m src.predict --folder "C:\path\to\phone_photos"    # subfolders named like a class are scored
python -m src.make_kb                            # then add VERIFIED symptoms and sources by hand
python check_setup.py                            # presentation health check
python run_demo.py                               # starts app + website together
# (or just the app: streamlit run app.py)
```
Run every command from the project root with `python -m src.xxx`. Keep `--num-workers 0` on Windows.

## Layout and presentation
- `app.py` + `krishi/` = upgraded Streamlit UI (old one kept in `legacy/app_original.py`); `src/` = training/inference, unchanged except one line in `src/predict.py` exposing the raw Grad-CAM map as `cam`.
- `website/index.html` = project website. Its Launch buttons open `http://localhost:8501`; use `?app=<url>` to point at a hosted app.
- `run_demo.py` starts both (website on :8080, app on :8501). Pip-install `plotly reportlab opencv-python-headless` once (see `requirements.txt`).
- Page fonts load from Google Fonts; offline it falls back to system fonts.

## Honest-use notes
- Lab-photo accuracy does not predict field accuracy; report both.
- "Not sure" thresholds are tuned on lab-style validation data and are probably too lenient for field photos.
- The knowledge base symptom and source fields are empty until you add verified entries; Hindi text is a draft.
- This code was written without being executed against the real datasets; expect to fix small issues on first run.
