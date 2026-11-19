# Projects to build: they back the resume bullets

Every bullet under **Projects** on the resumes describes one of these four builds. Build each one so that every
bullet is literally true. If you change scope (a different dataset, model, or number), edit the matching bullet in
`build_resumes.py` and run `python build_resumes.py` again.

Put each project in its own public GitHub repo with a README (problem, data, approach, results, screenshots,
how to run). Then set `GITHUB = "github.com/<you>"` at the top of `build_resumes.py` and rebuild.

Suggested order: P1 → P2 → P3 → P4. P1 is closest to your signal-processing background, and P4 reuses P1's output.

| # | Project | Backs | Effort |
|---|---------|-------|--------|
| P1 | Smartphone Telematics: Driving-Event Detection | Data Science (main), DAE, UX, Combined | 2 days |
| P2 | Mobility Analytics Pipeline on Google Cloud | Data Analytics Eng (main), DS, SWE, Combined | 2 days |
| P3 | Telematics Trip Ingestion Service | Software Eng (main), Combined | 3 days |
| P4 | Driver Safety Insights: UX Case Study | Experience Design (main), Combined | 2–3 days + interviews |

---

## P1: Smartphone Telematics: Driving-Event Detection
**Stack:** Python, pandas, NumPy, SciPy, scikit-learn, TensorFlow/Keras, Plotly, Folium, Jupyter, Git

**Data:** UAH-DriveSet (search "UAH-DriveSet robesafe"). It has 500+ minutes of naturalistic smartphone driving
from 6 drivers on 2 roads, with normal, drowsy and aggressive behavior, raw accelerometer and GPS logs, and
inertial event files (braking, acceleration, turning).

Steps:
1. Load the `RAW_ACCELEROMETERS`, `RAW_GPS` and inertial-event files for each trip into pandas. Note the sampling rates.
2. Data quality: check timestamp gaps or jitter, dropouts, and duplicate rows. Resample to a fixed rate and align GPS with accel. **Write down what you found** (the resume claims jitter, dropouts and misalignment, so confirm them or reword).
3. Signal processing: Butterworth low-pass (`scipy.signal.butter` + `filtfilt`) and gravity removal (or use the dataset's already-filtered columns and say so).
4. Features: sliding windows (e.g., 2 s windows with 50% overlap) giving mean, std, min, max, jerk, and FFT band energy per axis. Label windows from the event files (braking, acceleration, turn, none).
5. Models: Random Forest, gradient boosting (sklearn `HistGradientBoosting` or XGBoost), and a small 1D-CNN in Keras on the raw windows. Use **GroupKFold by driver** for "driver-grouped cross-validation". Report per-class precision, recall and F1, plus a confusion matrix.
6. Visualization: a Folium map of one trip with events as colored markers, and Plotly time-series plots with event overlays.
7. A README report covering methodology, results table, limitations, and recommendations.

Interview prep: why grouped CV (prevents a driver's own style leaking into the test set), class imbalance, how the filter cutoff was chosen.

## P2: Mobility Analytics Pipeline on Google Cloud
**Stack:** Python, SQL, BigQuery, Apache Airflow, PySpark, Looker Studio (or Tableau Public), pytest, GitHub Actions

**Data:** BigQuery public dataset `bigquery-public-data.chicago_taxi_trips.taxi_trips`.

Cost: use the BigQuery sandbox or the GCP $300 free trial, and **set a budget alert**. Run Airflow locally (the
official `docker-compose` or the Astro CLI); Cloud Composer itself is expensive. The resume's skills line lists
Composer, so either try it briefly on free credits or delete "Cloud Composer" from the DAE and combined skills.

Steps:
1. Airflow DAG (`@daily`): a staging task that copies one day of trips into your dataset (`stg_trips`, **partitioned by date, clustered by pickup community area**), then the transform tasks.
2. SQL transforms (keep them as `.sql` files in the repo): `fct_trips` (cleaned, with derived speed and duration), `agg_zone_hour` (demand by zone and hour), `agg_daily`.
3. Data-quality tests in pytest that query BigQuery: no null keys, duration and speed within sane ranges, no duplicate `unique_key`, and freshness (latest partition is at least yesterday).
4. PySpark: reproduce the `agg_zone_hour` aggregation locally on an exported month (Parquet). Compare the results and runtime with BigQuery and write that up in the README.
5. A Looker Studio dashboard covering demand heatmap by hour and day, trip duration, and average speed by zone. Put screenshots in the README.
6. GitHub Actions: `ruff` plus unit tests on every PR (mock the BigQuery client in CI, or mark the live tests to skip).

## P3: Telematics Trip Ingestion Service
**Stack:** Java 17, Spring Boot 3, Spring Security (OAuth2 resource server/JWT), Spring Data JPA, PostgreSQL,
JUnit 5, Mockito, Testcontainers, Gradle, Docker, GitHub Actions, Terraform, AWS (S3, Lambda, IAM)

Steps:
1. start.spring.io: Web, Validation, Security, OAuth2 Resource Server, Data JPA, PostgreSQL, Actuator (Gradle).
2. Endpoints: `POST /trips/{id}/events` (batch of `{ts, lat, lon, speed, accelX, accelY, accelZ}`, validated with `@Valid`), `GET /trips/{id}/summary` (distance by haversine, duration, and harsh-event count where |accel| exceeds a threshold).
3. Security: JWT validation (a local issuer such as Keycloak in Docker, or a test signing key). Scope-based access, no string-built SQL, request size limits. Write down which OWASP Top 10 items you addressed in the README.
4. TDD: write the tests first. Mockito for service logic, `@WebMvcTest` for controllers, Testcontainers Postgres for repository and integration tests.
5. CI/CD: GitHub Actions runs `./gradlew test` and builds and pushes a Docker image to GHCR.
6. Terraform: an S3 bucket for raw event archives, a Python Lambda triggered on object create that writes a summary, and IAM roles with least privilege. Run `terraform destroy` when done (free tier).
7. Actuator `/health` and `/metrics` endpoints.

Interview prep: OOP and design choices (layers, DTOs vs entities), how the JWT is verified, and how the tests are structured. Arity's posting stresses CS fundamentals, so review data structures, algorithms, and object-oriented design as well.

## P4: Driver Safety Insights: UX Case Study
**Stack:** Figma (free education plan), FigJam or MURAL, React + TypeScript (Vite), optional Cursor or Figma Make

Steps (the resume numbers are **5 drivers, 2 fleet managers, 2 usability rounds × 5 participants**, so hit them or edit the bullets):
1. Interviews (20–30 min each) about how people feel about driving feedback, safety scores, and privacy. Fleet managers: what they need on a dashboard.
2. Synthesis in FigJam/MURAL: affinity map, 2 personas (driver, fleet manager), and a journey map.
3. Ideation: Crazy 8s sketches, then pick concepts. User flows, low-fi wireframes, then a hi-fi interactive Figma prototype (mobile safety-score app plus a fleet dashboard).
4. Usability tests: two rounds of 5, using tasks and success rates, and note what changed between rounds.
5. Accessibility: contrast at WCAG AA, 44 px touch targets, charts that don't rely on color alone.
6. A design system page: color, type, and spacing tokens, plus button, card, chart and nav components.
7. Build the dashboard in React + TS using P1's event output (JSON). Deploy free on Vercel or GitHub Pages.
8. A case-study write-up (Figma page, Notion, or a portfolio site) with problem, research, insights, iterations, and outcome. UX recruiters will ask for a portfolio link, so add it to the header next to GitHub.

---


## PhD bullets now come from your GitHub (github.com/easha003)
| Resume claim | Source repo |
|---|---|
| GRAIL-V, 226 commits, Manhattan grid (40 signals, car/van/truck), 20.9M packets, 20,000-replicate bootstrap, resource pool is the binding constraint, 99.94% selector precision, fixed-point allocation | `Manhattan-RF-VLC-eV2X` (README, `pyproject.toml`, `paper/`) |
| Typer CLI, Pydantic configs, Parquet/PyArrow, manifests with SHA-256, pytest + Hypothesis, strict mypy, ruff | `Manhattan-RF-VLC-eV2X` (`pyproject.toml`, `tests/`) |
| Constrained mean-field RL, PPO with primal-dual updates, PyTorch/Gymnasium, masking, GAE, checkpointing, 100+ test modules (109 files in `tests/unit`) | `Reinforcement_Learning_V2X_RF_VLC` |
| 5G NR simulator in NumPy (OFDM, pilots, equalization, LDPC, CDL/TDL-C), DCO-OFDM VLC | `nr_urllc_S3` / `nr_urllc_S4_autoramp` |
| AR(1)/Kalman predictive controller, Markov blockage, isotonic LUTs, 5 scenarios x 100 runs | `nr_urllc_S7` |

**Check these, which I inferred:**
- The **TVT manuscript is the `nr_urllc_S7` work**, and the **conference paper is GRAIL-V targeting WCNC 2027** (from the `paper/wcnc2027/` folder and the "pool_constrained_optical_offloading" deck). If that's wrong, fix `PHD`, `PHD_UX` and `PUBS` in `build_resumes.py`. Also add the real paper titles and co-authors if you can.
- Your old CV said the conference paper uses reinforcement learning. The GRAIL-V README says the PPO policy was dropped, and RL now lives in the separate extension repo. The resumes follow the repos.
- The repos credit "GRAIL-V Research Team". Make sure you can explain every part (mobility model, bootstrap, fixed point, PPO primal-dual) in an interview, because interviewers *will* open the repo.
- **C++** and **data structures & algorithms** are still listed on the SWE and combined resumes. Remove them if you can't discuss them.
- Removed from the original: GRE/IELTS, references, and the B.Sc. GPA (3.43).

## Quick wins on the existing repos (do these first; under an hour total)
1. **Pin** `Manhattan-RF-VLC-eV2X`, `Reinforcement_Learning_V2X_RF_VLC` and `nr_urllc_S7` on your profile, and add a profile README (`easha003/easha003`) with 3 lines on each.
2. **Add GitHub Actions CI** to GRAIL-V and the RL repo (`ruff check`, `mypy`, `pytest` on push). The tooling is already configured in `pyproject.toml`, so it's one small `.github/workflows/ci.yml`. Then the DAE and SWE resumes can honestly say "CI on GitHub Actions" about real research code.
3. **Clean up:** `nr_urllc_S7`, `S5_S6` and `s2_v2` have `__pycache__/`, `.DS_Store` and `*.egg-info` committed, so add them to `.gitignore` and remove them. `Manhattan-Grid_Synthetic_V2V` duplicates the GRAIL-V README, and the `nr_urllc_m2/s2/S3/S4` repos are snapshots of one codebase. Archive the old ones, or say in their READMEs which one is current.
4. Give `nr_urllc_S3`, `nr_urllc_s2_v2`, `e2e_RL_init` and `RL_Huggy` real READMEs (right now they're a title or empty).
5. `nr_urllc_S7`'s README says "industrial IoT" while the resume frames the work as V2V. Make them agree.
6. Some of these repos hold a manuscript that is under review. If the venue is double-blind, check whether a public repo with the paper source is allowed.
