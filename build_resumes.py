"""Builds 5 resume variants (4 Arity roles + combined) as .tex, .pdf (pdflatex) and .docx from one content source.

Run:  python build_resumes.py
Edit content below; markup in text: **bold**, *italic*.
"""
import re
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.text import WD_TAB_ALIGNMENT, WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Inches, RGBColor

OUT = Path(__file__).parent
GITHUB = "github.com/easha003"

VARIANTS = {
    "dae": "DataAnalyticsEngineer",
    "ds": "DataScience_CoreTelematics",
    "swe": "SoftwareEngineer",
    "ux": "ExperienceDesign",
    "combined": "Combined",
}

ORDER = {
    "dae": ["summary", "education", "skills", "projects", "research", "work", "pubs", "certs"],
    "ds": ["summary", "education", "skills", "research", "projects", "work", "pubs", "certs"],
    "swe": ["summary", "education", "skills", "projects", "research", "work", "pubs", "certs"],
    "ux": ["summary", "education", "skills", "projects", "research", "work", "pubs", "certs"],
    "combined": ["summary", "education", "skills", "research", "projects", "work", "pubs", "certs"],
}

TITLES = {
    "summary": "Summary", "education": "Education", "skills": "Technical Skills", "projects": "Projects",
    "research": "Research Experience", "work": "Professional Experience", "pubs": "Publications",
    "certs": "Certifications & Service",
}

NAME = "EASHRAQUE JAHAN EASHA"
CONTACT = ["Denver, CO", "+1 (303) 520-7748", "EashraqueJahan.Easha@du.edu", "linkedin.com/in/easha003"]

HEADLINE = {
    "dae": "Data Analytics Engineering | Python · SQL · BigQuery · Airflow · PySpark · Tableau / Looker",
    "ds": "Data Science | Sensor & Time-Series Analytics · Signal Processing · Machine Learning · Python",
    "swe": "Software Engineering | Java · Python · Spring Boot · AWS / GCP · CI/CD · Test-Driven Development",
    "ux": "Experience Design | Human-Centered Research · Figma Prototyping · Data Visualization · Front-End",
    "combined": "Data Science & Engineering for Connected Mobility | Python · SQL · Java · Cloud · ML · Figma",
}

SUMMARY = {
    "dae": "Ph.D. student in Electrical and Computer Engineering (GPA 3.92/4.00) at the University of Denver, researching "
           "vehicle-to-vehicle communication for road safety. Builds reproducible Python data pipelines at scale (a "
           "20.9M-packet evaluation, Parquet traces, versioned artifact manifests, automated tests) and turns the results "
           "into clear visualizations. Hands-on with **SQL, GCP BigQuery, Apache Airflow, PySpark, Git/GitHub, Linux/bash "
           "and Tableau / Looker Studio**; 4+ years of industry and teaching experience working with engineers, managers "
           "and students.",
    "ds": "Ph.D. student in Electrical and Computer Engineering (GPA 3.92/4.00) at the University of Denver, modeling "
          "vehicle-to-vehicle (V2V) communication on realistic urban traffic. Trained in **signal processing, detection "
          "and estimation, and random processes**, and applies them with **Python (pandas, NumPy, SciPy, scikit-learn, "
          "PyTorch)** to time-series forecasting, classification, bootstrap statistics and reinforcement learning on "
          "simulated driving data (20.9M packets). Presents findings clearly to technical and non-technical audiences.",
    "swe": "Ph.D. student in Electrical and Computer Engineering (GPA 3.92/4.00) at the University of Denver who builds "
           "research software: a 226-commit Python simulation framework with a CLI, validated configs and pytest/Hypothesis "
           "test suites under strict mypy typing, plus a PyTorch reinforcement-learning extension. Writes **Python, Java "
           "and C++**, and is building a **Spring Boot** telematics service with PostgreSQL, OAuth2/JWT, JUnit/Mockito TDD, "
           "Docker, GitHub Actions CI/CD and Terraform on AWS. Comfortable in Linux/bash and quick to learn new languages.",
    "ux": "Ph.D. student in Electrical and Computer Engineering at the University of Denver whose research centers on "
          "driver and road safety. Turns complex technical systems and data into clear visual stories, a skill built over "
          "4+ years of teaching engineering and mathematics to diverse learners. Practices **human-centered design** end "
          "to end: user interviews, synthesis, user flows, wireframes and interactive prototypes in **Figma**, usability "
          "testing, design systems, and front-end builds in **HTML/CSS, React and TypeScript**.",
    "combined": "Ph.D. student in Electrical and Computer Engineering (GPA 3.92/4.00) researching vehicle-to-vehicle "
                "communication for safer transportation, backed by a 226-commit simulation framework and a 20.9M-packet "
                "evaluation. Combines **signal processing, statistics and ML/RL** (PyTorch) with **data engineering** (SQL, "
                "BigQuery, Airflow, PySpark), **software engineering** (typed Python, Java/Spring Boot, AWS, CI/CD) and "
                "**human-centered design** (Figma, React). IEEE-published; 4+ years of industry and teaching experience.",
}

COURSEWORK = {
    "default": "Random Signals and Processes, Digital Signal Processing, Signals and Systems, Communication Theory, "
               "Mobile Cellular Communication, Telecommunication Engineering",
}

EDUCATION = [
    dict(title="Doctor of Philosophy (Ph.D.), Electrical and Computer Engineering", date="Sep 2023 – Present",
         sub="Ritchie School of Engineering and Computer Science, University of Denver", loc="Denver, CO",
         bullets=["**GPA:** 3.92/4.00  |  **Advisor:** Dr. Mohammad Abdul Matin",
                  "**Dissertation:** *Modeling a hybrid system using Visible Light Communication and 5G New Radio*"]),
    dict(title="Master of Science (M.S.), Renewable Energy Technology", date="May 2018 – Feb 2020",
         sub="Institute of Energy, University of Dhaka", loc="Dhaka, Bangladesh",
         bullets=["**GPA:** 3.88/4.00  |  **Thesis:** *Fabrication of CdZnSe thin-film buffer layer by Chemical Bath "
                  "Deposition and its compositional, structural, optical and morphological characterization*"]),
    dict(title="Bachelor of Science (B.Sc.), Electrical and Electronic Engineering", date="Feb 2013 – Sep 2017",
         sub="Bangladesh University of Engineering and Technology (BUET)", loc="Dhaka, Bangladesh",
         bullets=["Major in Communication, Minor in Power  |  **Thesis:** *Enhancement of noisy speech based on "
                  "decision-directed Wiener approach in perceptual wavelet packet domain* (published, IEEE TENCON 2017)"]),
]

SKILLS = {
    "dae": [
        ("Languages", "Python, SQL, Bash, Java"),
        ("Data Engineering", "GCP (BigQuery, Cloud Storage), Apache Airflow, PySpark, Parquet / PyArrow, ETL/ELT "
                             "pipeline design, data modeling, data-quality testing (pytest, Hypothesis)"),
        ("Analytics & Statistics", "pandas, NumPy, SciPy, statsmodels, scikit-learn, bootstrap inference, exploratory "
                                   "data analysis, time-series analysis, geospatial analysis (Shapely, Folium)"),
        ("Visualization", "Tableau, Looker Studio, Matplotlib, seaborn, Plotly, Excel (Power Query, Power Pivot), SPSS"),
        ("Engineering Practice", "Git/GitHub, GitHub Actions, Linux, Pydantic, mypy, ruff, YAML configuration, "
                                 "reproducible artifacts, technical documentation, LaTeX"),
    ],
    "ds": [
        ("Programming", "Python (pandas, NumPy, SciPy, statsmodels), SQL, MATLAB, Bash, Jupyter"),
        ("Machine Learning", "scikit-learn, PyTorch, TensorFlow/Keras, Gymnasium, PPO and constrained (primal-dual) RL, "
                             "feature engineering, cross-validation, OpenCV"),
        ("Signal & Time Series", "Kalman / AR(1) forecasting, digital filtering (Wiener, Butterworth), spectral and "
                                 "wavelet analysis, OFDM, channel modeling, detection and estimation theory"),
        ("Statistics & Visualization", "Bootstrap inference, isotonic regression, Matplotlib, seaborn, Plotly, Folium, "
                                       "Tableau"),
        ("Data & Tools", "Git/GitHub, Linux, pytest, Hypothesis, Parquet / PyArrow, PySpark, Google BigQuery, LaTeX"),
    ],
    "swe": [
        ("Languages", "Python, Java, C++, SQL, Bash, MATLAB, HTML/CSS"),
        ("Python Engineering", "Typed packages (strict mypy), Typer CLIs, Pydantic, pytest, Hypothesis property tests, "
                               "ruff, PyTorch"),
        ("Backend", "Spring Boot, Spring Security (OAuth2 / JWT), REST API design, PostgreSQL, Docker, "
                    "OWASP secure-coding practices"),
        ("Testing & CI/CD", "JUnit 5, Mockito, Testcontainers, Gradle, GitHub Actions, test-driven development"),
        ("Cloud & Infrastructure", "AWS (S3, Lambda, EC2, IAM), GCP (BigQuery), Terraform, Linux/Unix"),
        ("Fundamentals", "Object-oriented design, data structures and algorithms, numerical simulation, embedded "
                         "hardware design (EasyEDA, PSpice)"),
    ],
    "ux": [
        ("Design Practice", "Human-centered design, user interviews, affinity mapping, personas, journey maps, user "
                            "flows, wireframing, interactive prototyping, usability testing, design systems, "
                            "accessibility (WCAG)"),
        ("Design Tools", "Figma, FigJam, Figma Make, MURAL, AI-assisted development (Cursor)"),
        ("Front-End", "HTML, CSS, React, TypeScript"),
        ("Data & Visualization", "Python, SQL, Tableau, Matplotlib, seaborn, Plotly, Excel data visualization"),
        ("Communication", "Teaching, technical presentations, research writing (IEEE), LaTeX"),
    ],
    "combined": [
        ("Languages", "Python, SQL, Java, C++, MATLAB, Bash, HTML/CSS, TypeScript"),
        ("Data Science & ML", "pandas, NumPy, SciPy, scikit-learn, PyTorch, TensorFlow, Gymnasium; time-series and "
                              "signal processing, bootstrap statistics, reinforcement learning"),
        ("Data Engineering & Cloud", "GCP (BigQuery), Apache Airflow, PySpark, Parquet / PyArrow, AWS (S3, Lambda, EC2), "
                                     "Terraform, Docker, PostgreSQL"),
        ("Software Engineering", "Typed Python (mypy, Pydantic, Typer), pytest, Hypothesis, Spring Boot, REST, OAuth2/JWT, "
                                 "JUnit, Mockito, Git/GitHub, GitHub Actions CI/CD, Linux, TDD"),
        ("Visualization & Design", "Tableau, Looker Studio, Matplotlib, Plotly, Folium, Excel, Figma, MURAL, React"),
    ],
}

# PhD bullets, sourced from github.com/easha003 (Manhattan-RF-VLC-eV2X = GRAIL-V, Reinforcement_Learning_V2X_RF_VLC,
# nr_urllc_*). Each variant picks a subset by key.
PHD = dict(
    A="Built **GRAIL-V**, a Python framework (226 commits) evaluating hybrid **5G NR sidelink + vehicular VLC** links on "
      "a microscopic Manhattan-grid traffic model (car-following, 40 signalized junctions, mixed car/van/truck fleet); "
      "IEEE WCNC 2027 paper in preparation.",
    B="Ran **20.9M-packet** evaluations across three traffic densities with a 20,000-replicate trajectory-block "
      "bootstrap; showed that the shared radio resource pool, not the link budget, limits reliability, and that "
      "load-aware optical offloading meets a 1-in-100,000 miss target that neither link meets alone.",
    C="Designed a causal link selector from observable features (vehicle separation, field-of-view margin) that reaches "
      "**99.94% precision**; solved the coupled allocation as a damped fixed-point problem.",
    D="Structured it as a typed Python package: Typer CLI, Pydantic-validated layered YAML configs, Parquet (PyArrow) "
      "traces, and artifact manifests (commit, config hash, seeds, SHA-256 per file) for reproducibility; tested with "
      "pytest and Hypothesis (unit, integration, regression, statistical), strict mypy and ruff.",
    D_dae="Built **reproducible data pipelines** for it: Parquet (PyArrow) trace storage, Pydantic-validated layered "
          "configs, artifact manifests (commit, config hash, seeds, SHA-256 per file), and automated data and "
          "statistical checks with pytest and Hypothesis.",
    E="Extending it to **constrained mean-field reinforcement learning**: PPO with primal-dual (Lagrangian) updates in "
      "**PyTorch / Gymnasium**, action masking, GAE, resumable checkpointed training and deterministic seeded "
      "rollouts, backed by 100+ test modules.",
    F="Wrote a **5G NR link-level simulator** from scratch in NumPy (OFDM, pilot-based channel estimation and "
      "equalization, LDPC coding, 3GPP CDL/TDL-C fading) plus a DCO-OFDM visible-light physical layer for BLER and "
      "URLLC latency sweeps.",
    G="Designed a **predictive hybrid RF/VLC controller** (AR(1)/Kalman SNR forecasting, Markov blockage model, "
      "isotonic-regression reliability lookup tables), evaluated over 5 channel scenarios with 100 runs each; journal "
      "paper **under review in IEEE Transactions on Vehicular Technology**.",
)
PHD_PICK = {
    "dae": ["A", "B", "D_dae", "G"],
    "ds": ["A", "B", "C", "G", "E"],
    "swe": ["A", "D", "E", "F", "G"],
    "combined": ["A", "B", "E", "G"],
}
PHD_UX = [
    "Researching hybrid **5G NR + visible light** vehicle-to-vehicle communication for collision avoidance on a "
    "realistic Manhattan-grid traffic model (GRAIL-V, 226 commits); IEEE WCNC 2027 paper in preparation.",
    "Distilled 20.9M simulated packets into three clear claims with supporting figures, traffic-scene visuals and "
    "supervisor briefing decks; journal paper **under review in IEEE Transactions on Vehicular Technology**.",
    "Design decision logic around what a vehicle can actually observe, kept separate from ground truth, a discipline "
    "that carries over directly to user research.",
]

RESEARCH = [
    dict(title="Graduate Researcher, Hybrid 5G NR and VLC for Vehicle-to-Vehicle Safety", date="Sep 2023 – Present",
         sub="Ritchie School of Engineering and Computer Science, University of Denver", loc="Denver, CO",
         bullets={"ux": PHD_UX, "default": [], **{v: [PHD[k] for k in ks] for v, ks in PHD_PICK.items()}}),
    dict(title="Graduate Researcher, Thin-Film Solar Cell Buffer Layers", date="Oct 2019 – Nov 2020",
         sub="Institute of Energy, University of Dhaka", loc="Dhaka, Bangladesh",
         bullets={"default": [
             "Fabricated CdZnSe thin-film buffer layers by chemical bath deposition, characterized them with XRD, SEM, "
             "EDAX and UV-Vis, and compared measurements with CIGS solar-cell simulations in wxAMPS."]}),
    dict(title="Undergraduate Researcher, Speech Enhancement", date="Oct 2016 – Jul 2017",
         sub="Bangladesh University of Engineering and Technology (BUET)", loc="Dhaka, Bangladesh",
         bullets={
             "default": ["Enhanced noisy speech with a decision-directed Wiener filtering approach in the perceptual "
                         "wavelet-packet domain (MATLAB); **published at IEEE TENCON 2017**."],
             "ds": ["Designed a decision-directed **Wiener filter** in the perceptual wavelet-packet domain (MATLAB) to "
                    "suppress noise in real-world speech signals; **published at IEEE TENCON 2017**."],
         }),
]

WORK = [
    dict(title="Graduate Service Assistant", date="Sep 2023 – Dec 2025",
         sub="Department of Electrical and Computer Engineering, University of Denver", loc="Denver, CO",
         bullets={"default": ["Graded Circuits I & II, Instrumentation & Data Acquisition, Optoelectronics, and Intro to "
                              "Power & Energy."]}),
    dict(title="Adjunct Faculty", date="Sep 2022 – May 2023",
         sub="Department of Mathematics and Natural Sciences, BRAC University", loc="Dhaka, Bangladesh",
         bullets={"default": ["Taught Differential & Integral Calculus and Linear Algebra."],
                  "ux": ["Taught Differential & Integral Calculus and Linear Algebra, explaining abstract concepts "
                         "to students from varied backgrounds."]}),
    dict(title="Senior Deputy Assistant Director, Electric Vehicle Conversion Project", date="Aug 2021 – Sep 2022",
         sub="Walton Hi-Tech Industries PLC", loc="Dhaka, Bangladesh",
         bullets={"default": [
             "Sized and optimized the EV battery pack by modeling energy demand over the **WLTP drive cycle** "
             "(speed-time data).",
             "Analyzed Li-ion battery market data for Bangladesh and Southeast Asia; prepared technical "
             "specifications and benchmarked motor and battery options.",
             "Developed a Battery Management System (BMS) circuit design in EasyEDA.",
         ]}),
    dict(title="Lecturer", date="Apr 2019 – Nov 2019",
         sub="Department of Electrical and Electronic Engineering, City University", loc="Dhaka, Bangladesh",
         bullets={"default": ["Taught seven undergraduate courses: Energy Conversion I, Mobile Cellular Communication, "
                              "Analog Integrated Circuits, Electric Circuits I & II, Telecommunication Engineering, "
                              "and Signal & Linear System Analysis."]}),
]

P_DS = dict(name="Smartphone Telematics: Driving-Event Detection",
            tech="Python, pandas, SciPy, scikit-learn, TensorFlow, Plotly, Folium, Git", date="Nov 2026",
            bullets=[
                "Cleaned and explored 500+ minutes of naturalistic smartphone driving data (UAH-DriveSet: accelerometer, "
                "GPS); found and fixed sampling-rate jitter, sensor dropouts and timestamp misalignment.",
                "Applied signal processing (Butterworth low-pass filtering, gravity removal, sliding-window statistical "
                "and spectral features) to engineer features for **harsh braking, rapid acceleration and sharp turns**.",
                "Trained and compared Random Forest, gradient boosting and a **1D-CNN (TensorFlow)** event detector with "
                "driver-grouped cross-validation; reported per-event precision, recall and F1.",
                "Mapped detected events along trip routes with **Folium** and built Plotly summaries; documented "
                "methodology, findings and recommendations in the project report.",
            ])
P_DAE = dict(name="Mobility Analytics Pipeline on Google Cloud",
             tech="Python, SQL, BigQuery, Apache Airflow, PySpark, Looker Studio, GitHub Actions", date="Nov 2026",
             bullets=[
                 "Built an **Airflow** DAG that pulls Chicago taxi-trip records (BigQuery public dataset) into partitioned, "
                 "clustered **BigQuery** staging and analytics tables on a daily schedule.",
                 "Wrote modular **SQL** transformations that produce trip-, zone- and hour-level datasets for analysts, "
                 "with automated data-quality tests (nulls, ranges, duplicates, freshness) in pytest.",
                 "Reproduced the heaviest aggregation in **PySpark** to compare distributed processing with BigQuery.",
                 "Published a **Looker Studio / Tableau** dashboard of demand, trip duration and speed patterns; GitHub "
                 "Actions runs linting and tests on every pull request.",
             ])
P_SWE = dict(name="Telematics Trip Ingestion Service",
             tech="Java 17, Spring Boot, PostgreSQL, JUnit 5, Mockito, Docker, GitHub Actions, Terraform, AWS",
             date="Nov 2026",
             bullets=[
                 "Built a **Spring Boot REST API** that ingests trip telemetry events, validates payloads, stores them in "
                 "**PostgreSQL**, and serves per-trip summaries (distance, duration, harsh-event counts).",
                 "Secured endpoints with **OAuth2 / JWT** (Spring Security) and applied OWASP practices: input "
                 "validation, parameterized queries, and least-privilege IAM.",
                 "Developed **test-first** with JUnit 5 and Mockito plus Testcontainers integration tests; a **GitHub "
                 "Actions CI/CD** pipeline builds with Gradle, runs tests and publishes a Docker image.",
                 "Provisioned **AWS** resources (S3 raw-event archive, Lambda processor, IAM roles) with **Terraform**; "
                 "added health and metrics endpoints with Spring Actuator for monitoring.",
             ])
P_UX = dict(name="Driver Safety Insights: UX Case Study", tech="Figma, FigJam, MURAL, React, TypeScript",
            date="Nov 2026",
            bullets=[
                "Interviewed 5 drivers and 2 fleet managers; synthesized findings into an affinity map, personas and a "
                "journey map for a driving-safety feedback product.",
                "Explored concepts through sketching and Crazy 8s, then built **user flows, wireframes and an "
                "interactive Figma prototype** of a mobile safety-score app and a fleet analytics dashboard.",
                "Ran two rounds of moderated **usability testing** (5 participants each) and iterated; checked "
                "accessibility against WCAG AA (contrast, touch targets, color-independent charts).",
                "Created a small **design system** (tokens, components) in Figma and implemented the dashboard in "
                "**React + TypeScript**, using data from the telematics event-detection project.",
            ])

# (project, number of its bullets to show) or (project, [custom bullets])
PROJECTS = {
    "dae": [(P_DAE, 4), (P_DS, 2)],
    "ds": [(P_DS, 4), (P_DAE, 2)],
    "swe": [(P_SWE, 4)],
    "ux": [(P_UX, 4), (P_DS, [
        "Analyzed smartphone driving-sensor data in Python and turned detected harsh-driving events into "
        "interactive **Folium** route maps and Plotly charts for non-technical audiences."])],
    "combined": [(P_DS, [
        "Cleaned 500+ minutes of real smartphone accelerometer/GPS driving data, engineered filtered sliding-window "
        "features, and compared Random Forest, gradient boosting and a **1D-CNN** detector for harsh driving events."]),
                 (P_DAE, [
        "Built an **Airflow** DAG loading Chicago taxi trips into partitioned **BigQuery** tables, with modular SQL "
        "transforms, pytest data-quality checks, a PySpark comparison and a Looker Studio dashboard."]),
                 (P_SWE, [
        "Built a **Spring Boot** REST API (PostgreSQL, OAuth2/JWT) test-first with JUnit 5 and Mockito, shipped through "
        "GitHub Actions and Docker, with S3/Lambda infrastructure in **Terraform**."]),
                 (P_UX, [
        "Ran driver and fleet-manager interviews and two rounds of usability tests; built user flows, wireframes, "
        "an interactive **Figma** prototype and a small design system, then implemented the dashboard in **React**."])],
}

PUBS = [
    "Islam, M.T., Shaan, M.N., **Easha, E.J.**, Minhaz, A.T., Shahnaz, C., & Fattah, S.A. (2017). Enhancement of noisy "
    "speech based on decision-directed Wiener approach in perceptual wavelet packet domain. *IEEE Region 10 Conference "
    "(TENCON)*. DOI: 10.1109/TENCON.2017.8228313",
    "**Easha, E.J.**, et al. Journal manuscript on a hybrid VLC and 5G NR system for vehicle-to-vehicle communication. "
    "*IEEE Transactions on Vehicular Technology*, under review.",
    "**Easha, E.J.**, et al. Conference paper on pool-constrained optical offloading for hybrid NR sidelink and "
    "vehicular VLC networks. In preparation for *IEEE WCNC 2027*.",
]

CERTS = [
    ("Supervised Machine Learning: Regression and Classification", "DeepLearning.AI & Stanford University, Coursera", "2023"),
    ("Excel Fundamentals, Data Visualization & Power Tools for Data Analysis", "Macquarie University, Coursera",
     "2022 – 23"),
    ("Amateur Radio Service Certificate", "Bangladesh Telecommunication Regulatory Commission (BTRC)", "2019"),
]

SERVICE = [
    ("Volunteer", "IEEE ICC 2024, Denver, CO; Mojar School (education for street children), Dhaka", "2017 – 2024"),
]


def pick(d, v):
    return d.get(v, d["default"]) if isinstance(d, dict) else d


def projects_for(v):
    return [(p, n if isinstance(n, list) else p["bullets"][:n]) for p, n in PROJECTS[v]]


def contact_items():
    return CONTACT + ([GITHUB] if GITHUB else [])


# ---------------------------------------------------------------- LaTeX
def tex_esc(s):
    s = s.replace("\\", r"\textbackslash{}")
    for a, b in [("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
                 ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"\*(.+?)\*", r"\\textit{\1}", s)
    return s.replace("·", r"\textperiodcentered{}").replace("  |  ", r" \quad|\quad ")


TEX_HEAD = r"""\documentclass[10pt,letterpaper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{charter}
\usepackage[margin=0.5in]{geometry}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage[hidelinks]{hyperref}
\definecolor{accent}{RGB}{31,56,100}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\titleformat{\section}{\color{accent}\large\bfseries\scshape}{}{0pt}{}[{\color{accent}\titlerule}]
\titlespacing*{\section}{0pt}{5pt}{3pt}
\setlist[itemize]{leftmargin=1.3em,itemsep=0.5pt,topsep=1pt,parsep=0pt,label=\textbullet}
\newcommand{\entry}[4]{\textbf{#1}\hfill #2\\\textit{#3}\hfill\textit{#4}\par}
\newcommand{\project}[3]{\textbf{#1}\hfill #3\\\textit{#2}\par}
\begin{document}
"""


def build_tex(v):
    L = [TEX_HEAD]
    L.append(r"\begin{center}{\LARGE\bfseries\color{accent} %s}\\[3pt]" % tex_esc(NAME))
    L.append(r"%s\\[2pt]" % r" \textbar{} ".join(tex_esc(c) for c in contact_items()))
    L.append(r"\textit{%s}\end{center}\vspace{-6pt}" % tex_esc(HEADLINE[v]))

    def entries(items):
        for e in items:
            L.append(r"\entry{%s}{%s}{%s}{%s}" % tuple(tex_esc(e[k]) for k in ("title", "date", "sub", "loc")))
            b = pick(e["bullets"], v)
            if b:
                L.append(r"\begin{itemize}" + "".join(r"\item " + tex_esc(x) for x in b) + r"\end{itemize}")
            L.append(r"\vspace{2pt}")

    for sec in ORDER[v]:
        L.append(r"\section*{%s}" % tex_esc(TITLES[sec]))
        if sec == "summary":
            L.append(tex_esc(SUMMARY[v]))
        elif sec == "education":
            entries(EDUCATION)
            L.append(r"\textbf{Relevant Coursework:} " + tex_esc(pick(COURSEWORK, v)))
        elif sec == "skills":
            L.append(r"\begin{itemize}" + "".join(
                r"\item \textbf{%s:} %s" % (tex_esc(a), tex_esc(b)) for a, b in SKILLS[v]) + r"\end{itemize}")
        elif sec == "projects":
            for p, b in projects_for(v):
                L.append(r"\project{%s}{%s}{%s}" % (tex_esc(p["name"]), tex_esc(p["tech"]), tex_esc(p["date"])))
                L.append(r"\begin{itemize}" + "".join(r"\item " + tex_esc(x) for x in b) + r"\end{itemize}\vspace{2pt}")
        elif sec == "research":
            entries(RESEARCH)
        elif sec == "work":
            entries(WORK)
        elif sec == "pubs":
            L.append(r"\begin{itemize}" + "".join(r"\item " + tex_esc(x) for x in PUBS) + r"\end{itemize}")
        elif sec == "certs":
            L.append("".join(r"\textbf{%s}, \textit{%s}\hfill %s\par" % tuple(map(tex_esc, c)) for c in CERTS + SERVICE))
    L.append(r"\end{document}")
    return "\n".join(L)


# ---------------------------------------------------------------- DOCX
ACCENT = RGBColor(31, 56, 100)
TEXT_W = Inches(8.5 - 1.0)


def add_runs(par, text, italic=False, size=None):
    for part in re.split(r"(\*\*.+?\*\*|\*.+?\*)", text):
        if not part:
            continue
        b = part.startswith("**")
        i = italic or (part.startswith("*") and not b)
        r = par.add_run(part.strip("*") if part.startswith("*") else part)
        r.bold, r.italic = b or None, i or None
        if size:
            r.font.size = size


def tight(par, before=0, after=0):
    pf = par.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), 1.0
    return par


def right_tab(par):
    par.paragraph_format.tab_stops.add_tab_stop(TEXT_W, WD_TAB_ALIGNMENT.RIGHT)


def bottom_border(par):
    pPr = par._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    for k, val in (("val", "single"), ("sz", "6"), ("space", "1"), ("color", "1F3864")):
        b.set(qn("w:" + k), val)
    bdr.append(b)
    pPr.append(bdr)


def build_docx(v, path):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Inches(8.5), Inches(11)
    s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Inches(0.5)
    st = doc.styles["Normal"]
    st.font.name, st.font.size = "Cambria", Pt(10)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Cambria")

    p = tight(doc.add_paragraph(), after=2)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(NAME)
    r.bold, r.font.size, r.font.color.rgb = True, Pt(18), ACCENT
    p = tight(doc.add_paragraph(" | ".join(contact_items())), after=1)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = tight(doc.add_paragraph(), after=2)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_runs(p, HEADLINE[v], italic=True)

    def heading(t):
        h = tight(doc.add_paragraph(), before=6, after=3)
        r = h.add_run(t.upper())
        r.bold, r.font.size, r.font.color.rgb = True, Pt(11.5), ACCENT
        h.paragraph_format.keep_with_next = True
        bottom_border(h)

    def bullet(text):
        b = tight(doc.add_paragraph(style="List Bullet"), after=0.5)
        b.paragraph_format.left_indent, b.paragraph_format.first_line_indent = Inches(0.2), Inches(-0.15)
        add_runs(b, text)

    def line(left, right, italic_left=False, bold_left=True):
        q = tight(doc.add_paragraph())
        right_tab(q)
        q.paragraph_format.keep_with_next = True
        add_runs(q, ("**%s**" % left) if bold_left else left, italic=italic_left)
        add_runs(q, "\t" + right, italic=italic_left)
        return q

    def entries(items):
        for e in items:
            line(e["title"], e["date"]).paragraph_format.space_before = Pt(2)
            line(e["sub"], e["loc"], italic_left=True, bold_left=False)
            for x in pick(e["bullets"], v):
                bullet(x)

    for sec in ORDER[v]:
        heading(TITLES[sec])
        if sec == "summary":
            add_runs(tight(doc.add_paragraph()), SUMMARY[v])
        elif sec == "education":
            entries(EDUCATION)
            add_runs(tight(doc.add_paragraph(), before=2), "**Relevant Coursework:** " + pick(COURSEWORK, v))
        elif sec == "skills":
            for a, b in SKILLS[v]:
                bullet("**%s:** %s" % (a, b))
        elif sec == "projects":
            for p_, bl in projects_for(v):
                line(p_["name"], p_["date"]).paragraph_format.space_before = Pt(2)
                add_runs(tight(doc.add_paragraph()), p_["tech"], italic=True)
                for x in bl:
                    bullet(x)
        elif sec == "research":
            entries(RESEARCH)
        elif sec == "work":
            entries(WORK)
        elif sec == "pubs":
            for x in PUBS:
                bullet(x)
        elif sec == "certs":
            for a, b, c in CERTS + SERVICE:
                q = tight(doc.add_paragraph())
                right_tab(q)
                add_runs(q, "**%s**, *%s*\t%s" % (a, b, c))
    doc.save(path)


def main():
    for v, label in VARIANTS.items():
        stem = "Easha_Resume_Arity_" + label
        (OUT / f"{stem}.tex").write_text(build_tex(v), encoding="utf-8")
        build_docx(v, OUT / f"{stem}.docx")
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{stem}.tex"],
                           cwd=OUT, capture_output=True, text=True, errors="replace")
        if r.returncode:
            raise SystemExit(f"pdflatex failed for {stem}:\n{r.stdout[-2500:]}")
        pages = re.search(r"Output written on .*?\((\d+) page", r.stdout)
        print(f"{stem}: {pages.group(1) if pages else '?'} page(s)")
        for ext in (".aux", ".log", ".out"):
            (OUT / f"{stem}{ext}").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
