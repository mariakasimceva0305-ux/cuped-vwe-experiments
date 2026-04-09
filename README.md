# CUPED vs VWE Experiments

[Русская версия](#ru) | [English version](#en)

## RU

### О проекте
Минимальный воспроизводимый исследовательский проект по снижению дисперсии в A/B-оценке: сравнение `plain diff`, `CUPED`, `VWE` и `CUPED+VWE` на синтетических данных.

### Цель
Проверить, в каких режимах предэкспериментальные сигналы и variance weighting дают статистически более стабильные оценки эффекта.

### Гипотезы
1. CUPED системно снижает дисперсию при достаточной pre/post корреляции.
2. VWE лучше работает в сценариях с гетерогенной шумностью юнитов.
3. Комбинация CUPED+VWE даёт более устойчивый RMSE в mixed-сценариях.

### Экспериментальный протокол
- множественные симуляции с фиксированными seed;
- истинный эффект по умолчанию: `0`;
- сравнение по SD/RMSE оценок, таблицы в `figures/*.csv`, графики в `figures/*.png`.

### Метрики
- `std(estimate)`
- `rmse(estimate)`
- относительное снижение дисперсии к baseline

### Запуск
```bash
python -m venv .venv
pip install -r requirements.txt
python scripts/make_figures.py
```

## EN

### Overview
A reproducible simulation benchmark for variance reduction in experiment measurement: `plain diff` vs `CUPED` vs `VWE` vs `CUPED+VWE`.

### Research objective
Quantify when pre-experiment covariates and variance weighting improve estimator stability under controlled synthetic settings.

### Evaluation
Repeated Monte-Carlo runs with fixed seeds and comparison by estimator SD/RMSE.
