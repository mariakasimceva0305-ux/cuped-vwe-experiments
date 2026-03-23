# cuped-vwe-experiments

Минимальный воспроизводимый **research companion**: две симуляции на синтетике, где отдельно смотрят на чувствительность **CUPED** и на **VWE** (variance-weighted estimation). Разбор для статьи — в `article_draft.md`; числа там сверены с CSV в `figures/`. Это не библиотека под прод и не пакет для пайплайна — только прозрачный код и заранее сохранённые результаты.

## What this repo is

- две явные постановки (корреляция pre/post и сценарий с долей «шумных» пользователей);
- оценки plain diff, CUPED, VWE и CUPED+VWE;
- скрипт, который заново строит те же CSV/PNG;
- сохранённые результаты в `figures/`, чтобы графики открывались без прогона.

## What this repo is not

- не новый метод и не сравнение на реальных логах продукта;
- не руководство «что включать в каждый тест»;
- не production-grade пакет: без релизов, CI и публичного API.

## Repository structure

```text
cuped-vwe-experiments/
  README.md
  LICENSE
  requirements.txt
  pyproject.toml
  article_draft.md
  src/
    estimators.py
    simulate.py
  scripts/
    make_figures.py
  figures/
    *.csv
    *.png
```

## How to run

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# Windows (PowerShell): .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python scripts/make_figures.py
```

Появятся файлы в `figures/` (CSV и четыре PNG). По умолчанию: `n_units=4000`, `n_sims=300`, `pre_repeats=10`, `seed=42`, истинный эффект `0`.

![Снижение дисперсии CUPED относительно plain diff по корреляции pre/post](figures/cuped_variance_reduction.png)

![Std оценок в сценарии с 12% «шумных» пользователей (см. CSV)](figures/power_users_sd.png)

## Limitations

- выводы привязаны к **нашей симуляции** и не переносятся автоматически на любой продуктовый эксперимент;
- **VWE** здесь упрощён: дисперсии по юнитам оцениваются с повторных pre-наблюдений, как в `src/estimators.py`;
- сравнение по RMSE/SD оценки эффекта — не полный учёт bias, стоимости внедрения и интерпретируемости на проде.
