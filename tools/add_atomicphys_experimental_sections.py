from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE_MARKER = "ATOMICPHYS-EXPERIMENT-SECTION"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path(r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


FONT = font(24)
FONT_SMALL = font(18)
FONT_TINY = font(15)
FONT_BOLD = font(26, bold=True)


def line(draw: ImageDraw.ImageDraw, points, fill="#1d3557", width=4):
    draw.line(points, fill=fill, width=width)


def arrow(draw: ImageDraw.ImageDraw, start, end, fill="#1d3557", width=4):
    line(draw, [start, end], fill=fill, width=width)
    sx, sy = start
    ex, ey = end
    angle = math.atan2(ey - sy, ex - sx)
    head = 15
    for da in (math.pi * 0.82, -math.pi * 0.82):
        px = ex + head * math.cos(angle + da)
        py = ey + head * math.sin(angle + da)
        line(draw, [(ex, ey), (px, py)], fill=fill, width=width)


def text(draw, xy, value, fill="#14213d", size="small", anchor=None):
    selected = {"bold": FONT_BOLD, "small": FONT_SMALL, "tiny": FONT_TINY}.get(size, FONT)
    draw.text(xy, value, fill=fill, font=selected, anchor=anchor)


def save_photoelectric(path: Path):
    img = Image.new("RGB", (1000, 560), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 999, 559], fill="#fbfbf8")
    d.line([110, 470, 900, 470], fill="#222", width=3)
    d.line([110, 470, 110, 70], fill="#222", width=3)
    text(d, (500, 30), "Photoelectric effect: stopping potential vs frequency", size="bold", anchor="ma")
    text(d, (455, 520), "frequency nu", size="small", anchor="ma")
    text(d, (25, 250), "stopping potential", size="small")
    nu0_x = 300
    d.line([nu0_x, 470, nu0_x, 150], fill="#888", width=2)
    text(d, (nu0_x, 490), "threshold nu0", size="tiny", anchor="ma")
    arrow(d, (nu0_x, 470), (780, 140), fill="#d62828", width=5)
    text(d, (680, 170), "slope = h/e", fill="#d62828", size="small")
    text(d, (155, 125), "no emitted electrons", fill="#555", size="small")
    text(d, (660, 410), "Ek,max = h nu - A", fill="#14213d", size="small")
    d.ellipse([760, 100, 780, 120], fill="#d62828")
    img.save(path)


def save_compton(path: Path):
    img = Image.new("RGB", (1000, 560), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 999, 559], fill="#fbfbf8")
    d.line([120, 470, 900, 470], fill="#222", width=3)
    d.line([120, 470, 120, 70], fill="#222", width=3)
    text(d, (500, 30), "Compton scattering: wavelength shift", size="bold", anchor="ma")
    text(d, (500, 520), "scattering angle theta", size="small", anchor="ma")
    text(d, (28, 235), "Delta lambda / lambda_C", size="small")
    pts = []
    for i in range(181):
        theta = math.pi * i / 180
        x = 120 + 780 * i / 180
        y = 470 - 360 * (1 - math.cos(theta)) / 2
        pts.append((x, y))
    d.line(pts, fill="#0077b6", width=5)
    for deg in (0, 90, 180):
        x = 120 + 780 * deg / 180
        d.line([x, 466, x, 475], fill="#222", width=2)
        text(d, (x, 490), f"{deg} deg", size="tiny", anchor="ma")
    text(d, (620, 175), "Delta lambda = lambda_C (1 - cos theta)", fill="#0077b6", size="small")
    arrow(d, (210, 245), (350, 245), fill="#d62828")
    d.ellipse([390, 220, 435, 265], outline="#222", width=3)
    arrow(d, (435, 245), (610, 145), fill="#d62828")
    arrow(d, (435, 245), (615, 330), fill="#6a994e")
    text(d, (230, 215), "photon", fill="#d62828", size="tiny")
    text(d, (620, 125), "scattered photon", fill="#d62828", size="tiny")
    text(d, (625, 335), "recoil electron", fill="#6a994e", size="tiny")
    img.save(path)


def save_stern_gerlach(path: Path):
    img = Image.new("RGB", (1000, 560), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 999, 559], fill="#fbfbf8")
    text(d, (500, 30), "Stern-Gerlach experiment: two-valued spin projection", size="bold", anchor="ma")
    d.rectangle([70, 245, 150, 315], outline="#222", width=4)
    text(d, (110, 325), "Ag oven", size="tiny", anchor="ma")
    d.rectangle([215, 230, 245, 330], outline="#222", width=4)
    text(d, (230, 340), "slit", size="tiny", anchor="ma")
    d.polygon([(420, 170), (600, 215), (600, 265), (420, 265)], fill="#ced4da", outline="#222")
    d.polygon([(420, 390), (600, 345), (600, 295), (420, 295)], fill="#ced4da", outline="#222")
    text(d, (505, 150), "inhomogeneous", size="tiny", anchor="ma")
    text(d, (505, 375), "magnetic field", size="tiny", anchor="ma")
    d.rectangle([800, 165, 850, 395], outline="#222", width=4)
    text(d, (825, 405), "screen", size="tiny", anchor="ma")
    arrow(d, (150, 280), (420, 280), width=4)
    arrow(d, (600, 280), (800, 205), fill="#d62828", width=4)
    arrow(d, (600, 280), (800, 355), fill="#0077b6", width=4)
    d.ellipse([815, 195, 835, 215], fill="#d62828")
    d.ellipse([815, 345, 835, 365], fill="#0077b6")
    text(d, (875, 195), "ms = +1/2", fill="#d62828", size="small")
    text(d, (875, 345), "ms = -1/2", fill="#0077b6", size="small")
    text(d, (345, 420), "classical smear expected; two spots observed", fill="#555", size="small", anchor="ma")
    img.save(path)


def save_field_splitting(path: Path):
    img = Image.new("RGB", (1000, 560), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 999, 559], fill="#fbfbf8")
    text(d, (500, 30), "Field splitting of spectral lines", size="bold", anchor="ma")
    d.line([130, 440, 870, 440], fill="#222", width=3)
    text(d, (500, 490), "field strength", size="small", anchor="ma")
    for x, label in [(190, "0"), (500, "moderate"), (810, "strong")]:
        d.line([x, 432, x, 448], fill="#222", width=2)
        text(d, (x, 455), label, size="tiny", anchor="ma")
    for x in [190]:
        d.line([x, 130, x, 350], fill="#111", width=8)
    colors_triplet = ["#d62828", "#222222", "#0077b6"]
    for x0, spread in [(500, 65), (810, 125)]:
        for off, c in zip([-spread, 0, spread], colors_triplet):
            d.line([x0 + off, 130, x0 + off, 350], fill=c, width=8)
    text(d, (190, 100), "single line", size="small", anchor="ma")
    text(d, (500, 100), "Zeeman splitting", size="small", anchor="ma")
    text(d, (810, 100), "larger splitting", size="small", anchor="ma")
    d.arc([395, 245, 605, 390], 200, 340, fill="#6a994e", width=4)
    text(d, (500, 400), "Stark/Zeeman: degeneracy lifted by external fields", fill="#6a994e", size="small", anchor="ma")
    img.save(path)


def save_ramsauer_noble_gases(path: Path, data_path: Path) -> None:
    dataset = json.loads(data_path.read_text(encoding="utf-8"))
    process_ids = {
        "Ar": "SIGLO__Ar__Effective__00",
        "Kr": "SIGLO__Kr__Elastic__17",
        "Xe": "SIGLO__Xe__Elastic__32",
    }
    processes = {process["id"]: process for process in dataset["processes"]}
    colors = {"Ar": "#0072B2", "Kr": "#D55E00", "Xe": "#009E73"}

    img = Image.new("RGB", (1200, 760), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1199, 759], fill="#fbfbf8")
    left, top, right, bottom = 135, 90, 1130, 625
    d.rectangle([left, top, right, bottom], fill="white", outline="#333", width=2)

    x_min, x_max = math.log10(0.01), math.log10(10.0)
    y_min, y_max = math.log10(0.03), math.log10(100.0)

    def plot_x(value: float) -> float:
        return left + (math.log10(value) - x_min) / (x_max - x_min) * (right - left)

    def plot_y(value: float) -> float:
        return bottom - (math.log10(value) - y_min) / (y_max - y_min) * (bottom - top)

    for value, label in [(0.01, "0.01"), (0.1, "0.1"), (1.0, "1"), (10.0, "10")]:
        x = plot_x(value)
        d.line([(x, top), (x, bottom)], fill="#d7d7d7", width=1)
        text(d, (x, bottom + 18), label, fill="#333", size="tiny", anchor="ma")
    for value, label in [(0.03, "0.03"), (0.1, "0.1"), (0.3, "0.3"), (1, "1"), (3, "3"), (10, "10"), (30, "30"), (100, "100")]:
        y = plot_y(value)
        d.line([(left, y), (right, y)], fill="#d7d7d7", width=1)
        text(d, (left - 16, y), label, fill="#333", size="tiny", anchor="rm")

    minima = {}
    for gas, process_id in process_ids.items():
        process = processes[process_id]
        points = [
            (float(energy), float(sigma) / 1e-20)
            for energy, sigma in zip(process["energy"], process["cross_section"])
            if 0.01 <= float(energy) <= 10.0 and float(sigma) > 0
        ]
        d.line([(plot_x(energy), plot_y(sigma)) for energy, sigma in points], fill=colors[gas], width=5)
        minima[gas] = min((point for point in points if point[0] <= 5.0), key=lambda point: point[1])

    offsets = {"Ar": (-105, -58), "Kr": (72, 30), "Xe": (72, -58)}
    for gas, (energy, sigma) in minima.items():
        x, y = plot_x(energy), plot_y(sigma)
        dx, dy = offsets[gas]
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=colors[gas], outline="white", width=2)
        d.line([(x, y), (x + dx * 0.7, y + dy * 0.7)], fill=colors[gas], width=2)
        text(
            d,
            (x + dx, y + dy),
            f"{gas}: {energy:.2g} eV",
            fill=colors[gas],
            size="small",
            anchor="mm",
        )

    text(d, (600, 35), "Ramsauer-Townsend minima in noble gases", size="bold", anchor="ma")
    text(d, ((left + right) / 2, 682), "Electron energy (eV)", size="small", anchor="ma")
    axis_label = Image.new("RGBA", (430, 44), (255, 255, 255, 0))
    axis_draw = ImageDraw.Draw(axis_label)
    axis_draw.text(
        (215, 22),
        "Momentum-transfer cross section (10^-20 m^2)",
        fill="#14213d",
        font=FONT_SMALL,
        anchor="mm",
    )
    axis_label = axis_label.rotate(90, expand=True, resample=Image.Resampling.BICUBIC)
    img.paste(axis_label, (30, 145), axis_label)

    legend_y = 67
    for gas, legend_x in [("Ar", 820), ("Kr", 920), ("Xe", 1020)]:
        d.line([(legend_x, legend_y), (legend_x + 35, legend_y)], fill=colors[gas], width=5)
        text(d, (legend_x + 44, legend_y), gas, fill="#222", size="tiny", anchor="lm")
    text(d, (600, 730), "Data: LXCat SIGLO database; curves redrawn for this course", fill="#555", size="tiny", anchor="ma")
    img.save(path)


def generated_figures(fig_dir: Path) -> None:
    fig_dir.mkdir(parents=True, exist_ok=True)
    save_photoelectric(fig_dir / "fig_exp_photoelectric_threshold.png")
    save_compton(fig_dir / "fig_exp_compton_shift.png")
    save_stern_gerlach(fig_dir / "fig_exp_stern_gerlach_scheme.png")
    save_field_splitting(fig_dir / "fig_exp_field_splitting.png")


def markdown_cell(source: str) -> dict:
    if not source.endswith("\n"):
        source += "\n"
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def find_insert_after_first_heading(cells: list[dict]) -> int:
    for index, cell in enumerate(cells):
        if cell.get("cell_type") != "markdown":
            continue
        source = "".join(cell.get("source", []))
        if source.lstrip().startswith("#"):
            return index + 1
    return 0


def upsert_cell(nb_path: Path, key: str, source: str) -> bool:
    marker = f"<!-- {BASE_MARKER}: {key} -->"
    full_source = marker + "\n" + source.strip() + "\n"
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    cells = nb.get("cells", [])
    for cell in cells:
        if cell.get("cell_type") == "markdown" and marker in "".join(cell.get("source", [])):
            cell["source"] = full_source.splitlines(keepends=True)
            nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            return True
    insert_at = find_insert_after_first_heading(cells)
    cells.insert(insert_at, markdown_cell(full_source))
    nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return True


def update_ramsauer_caption(nb_path: Path) -> bool:
    old_image = '<img src="./figs/fig_Ramsauer.jpg" alt="Ефект Рамзауера-Таунсенда" width="520">'
    image = '<img src="./figs/fig_Ramsauer_ArKrXe.png" alt="Мінімуми Рамзауера-Таунсенда для Ar, Kr і Xe" width="720">'
    old_intro = (
        "Аномальна прозорість газу (аргону) для електронного пучка певної "
        "енергії ($\\sim 0.01 eV$) \n"
    )
    new_intro = (
        "В ефекті Рамзауера-Таунсенда повний переріз розсіяння повільних "
        "електронів на атомах важких інертних газів різко зменшується за енергій "
        "порядку $1\\,\\mathrm{eV}$ (точне положення мінімуму залежить від атома; "
        "для аргону воно становить приблизно $0.3\\,\\mathrm{eV}$).\n"
    )
    explanation = r"""

**Пояснення до рисунка.** Криві показують ефективні перерізи переносу імпульсу для електронів у Ar, Kr і Xe. У наборі даних SIGLO мінімуми лежать біля $0.25$, $0.59$ і $0.64\,\mathrm{eV}$ відповідно. Поблизу мінімуму домінуючий s-хвильовий фазовий зсув проходить поблизу нуля, тому внесок $\sigma_0=(4\pi/k^2)\sin^2\delta_0$ різко зменшується, а газ стає аномально прозорим для електронів цієї енергії. Точні положення і глибини мінімумів залежать від виду перерізу та конкретного набору експериментальних даних.

**Аналогія з білою плямою Пуассона-Араго.** В обох випадках класично несподіваний результат зумовлений хвильовою інтерференцією. Для плями Пуассона дифраговані світлові хвилі конструктивно складаються в центрі геометричної тіні; для ефекту Рамзауера-Таунсенда парціальні хвилі розсіяного електрона інтерферують так, що розсіяння майже гаситься і проходження пучка зростає. Це аналогія проявів хвильової природи, а не тотожність геометрії двох дослідів.

**Джерело даних:** [LXCat, SIGLO database](https://www.lxcat.net/SIGLO), записи ефективного/пружного перерізу переносу імпульсу для Ar, Kr і Xe; графік побудовано для цього курсу за табличними даними. Опис платформи: L. C. Pitchford *et al.*, *Plasma Processes and Polymers* **14**, 1600098 (2017), [DOI: 10.1002/ppap.201600098](https://doi.org/10.1002/ppap.201600098).
""".strip()

    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    changed = False
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        source = "".join(cell.get("source", []))
        if old_image not in source and image not in source:
            continue
        updated = source.replace(old_intro, new_intro)
        updated = updated.replace(old_image, image)
        if "10.1002/ppap.201600098" not in updated:
            updated = updated.replace(image, image + "\n\n" + explanation)
        if updated != source:
            cell["source"] = updated.splitlines(keepends=True)
            changed = True
    if changed:
        nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return changed


SECTIONS = {
    "atomicphys_toc.ipynb": (
        "overview",
        r"""
## Експериментальна карта курсу

<img src="./figs/fig_qmain_exprmnts.png" alt="Карта класичних квантових експериментів" width="680">

Теоретичні моделі курсу зручно читати разом із експериментами, які зробили відповідні поняття необхідними. Фотоелектричний ефект, випромінювання чорного тіла, Комптон-ефект, дослід Франка-Герца, досліди Резерфорда, Девіссона-Джермера, Штерна-Герлаха, ефекти Штарка і Зеємана та правило Мозлі утворюють історичний міст від класичної фізики до квантового опису атома.
""",
    ),
    "atomicphys_photons.ipynb": (
        "photons",
        r"""
## Експериментальні витоки: кванти світла

У цьому розділі три експериментальні факти працюють як мінімальний набір доказів частинкових властивостей світла. Випромінювання чорного тіла показує, що класичний неперервний обмін енергією призводить до ультрафіолетової катастрофи; фотоелектричний ефект вводить поріг частоти та енергію фотона $E=h\nu$; Комптон-ефект додає імпульс фотона $p=h/\lambda$ через вимірюваний зсув довжини хвилі.

<img src="./figs/fig_blackbody.png" alt="Спектри випромінювання чорного тіла" width="620">

<img src="./figs/fig_exp_photoelectric_threshold.png" alt="Фотоелектричний поріг і стала Планка" width="620">

<img src="./figs/fig_exp_compton_shift.png" alt="Комптонівський зсув довжини хвилі" width="620">

**Ідея експерименту.** У фотоелектричному досліді змінюють частоту світла і вимірюють затримуючий потенціал; нахил прямої дає $h/e$, а перетин з віссю частот задає роботу виходу. У досліді Комптона реєструють розсіяне рентгенівське випромінювання під кутом $\theta$ і знаходять $\Delta \lambda=\lambda_C(1-\cos\theta)$, що неможливо отримати без імпульсу фотона.
""",
    ),
    "atomicphys_dual.ipynb": (
        "duality",
        r"""
## Експериментальні витоки: дискретні рівні та хвилі матерії

Дослід Франка-Герца безпосередньо показує, що атоми поглинають енергію не неперервно, а порціями: струм у парі ртуті має максимуми та мінімуми з періодом, який відповідає першій енергії збудження атома. Дослід Девіссона-Джермера переносить хвильову ідею на електрони: максимум розсіяння на кристалі нікелю відповідає умові дифракції для довжини хвилі де Бройля.

<!-- <img src="./figs/fig_davissgermerexp.png" alt="Схема досліду Девіссона-Джермера" width="620"> -->

**Ідея експерименту.** Франк-Герц: прискорені електрони втрачають енергію тільки коли можуть збудити атомний рівень. Девіссон-Гермер: електронний пучок відбивається від кристала як хвиля. Рамзауер-Таунсенд: прозорість газу для повільних електронів виникає як інтерференційний ефект розсіяння.
<!--  -->
""",
    ),
    "atomicphys_atom.ipynb": (
        "rutherford",
        r"""
## Експериментальний ключ: розсіяння Резерфорда

Дослід із розсіянням $\alpha$-частинок на тонкій металевій фользі показав, що позитивний заряд і майже вся маса атома зосереджені в дуже малому ядрі. Більшість частинок проходить майже прямо, але рідкісні великі кути розсіяння несумісні з моделлю Томсона, де заряд розмазаний по всьому об'єму атома.

<img src="./figs/fig_rutherfordwiki.png" alt="Траєкторія альфа-частинки у камері та велике розсіяння" width="520">

**Ідея експерименту.** Джерело $\alpha$-частинок, тонка фольга і екран/детектор фактично вимірюють кутовий розподіл. Сам хвіст розподілу при великих кутах народжує ядерну модель атома; далі квантування Бора пояснює, чому електрон не падає класично на ядро.
""",
    ),
    "atomicphys_atomh_theor.ipynb": (
        "hydrogen_spectrum",
        r"""
## Експериментальний ключ: лінійчастий спектр водню

Лінії Бальмера та узагальнена формула Рідберга були відомі до повної квантової теорії атома. Саме регулярність спектральних частот підказує, що випромінювання відповідає переходам між дискретними рівнями енергії, а не довільним орбітальним частотам класичного електрона.

<img src="./figs/fig_hspectrum.png" alt="Серії спектра атома водню" width="620">

<img src="./figs/atphys_hspec.png" alt="Видимі лінії спектра водню" width="620">

**Ідея експерименту.** Розряд у водні створює збуджені атоми, а спектрометр розкладає випромінювання за довжинами хвиль. Емпірична регулярність $1/\lambda=R(1/n_1^2-1/n_2^2)$ стає прямим свідченням дискретного спектра гамільтоніана атома.
""",
    ),
    "atomicphys_spinpauli_theor.ipynb": (
        "stern_gerlach",
        r"""
## Експериментальний ключ: дослід Штерна-Герлаха

У неоднорідному магнітному полі на магнітний момент діє сила, тому атомний пучок має відхилятися залежно від проекції моменту. Для атомів срібла класична картина очікувала неперервну пляму, але на екрані виникають дві компоненти. Це стало прямим образом просторового квантування та привело до поняття спіну електрона.

<img src="./figs/fig_exp_stern_gerlach_scheme.png" alt="Схема досліду Штерна-Герлаха" width="680">

**Ідея експерименту.** Піч формує пучок нейтральних атомів, щілина колімує його, неоднорідний магніт розділяє компоненти з $m_s=\pm 1/2$, а екран фіксує два сліди замість неперервного розподілу.
""",
    ),
    "atomicphys_atominemfield.ipynb": (
        "fields",
        r"""
## Експериментальні витоки: розщеплення спектральних ліній у полях

Ефекти Штарка і Зеємана вимірюють, як зовнішнє електричне або магнітне поле знімає виродження атомних рівнів. Спостерігається не просто зміщення однієї лінії, а поява кількох компонент, кількість і поляризація яких кодують квантові числа та правила відбору.

<img src="./figs/fig_stark.png" alt="Схема розщеплення рівнів у ефекті Штарка" width="620">

<img src="./figs/fig_exp_field_splitting.png" alt="Схематичне розщеплення спектральної лінії у зовнішньому полі" width="620">

**Ідея експерименту.** Газ або атомний пучок розміщують між електродами чи полюсами магніту і спостерігають спектр високої роздільної здатності. Залежність положень ліній від поля прямо перевіряє матричні елементи дипольного або магнітного моменту.
""",
    ),
    "atomicphys_atomhxspectr.ipynb": (
        "moseley",
        r"""
## Експериментальний ключ: правило Мозлі та характеристичні рентгенівські спектри

Мозлі вимірював частоти характеристичних $K$- та $L$-ліній для послідовних елементів і виявив майже лінійну залежність $\sqrt{\nu}$ від атомного номера $Z$. Це показало, що саме заряд ядра, а не атомна маса, є правильною змінною для впорядкування елементів.

<img src="./figs/fig_atomphysmosley.png" alt="Закон Мозлі для характеристичних рентгенівських ліній" width="620">

<img src="./figs/fig_atomxr.png" alt="Характеристичні рентгенівські переходи" width="560">

**Ідея експерименту.** Електрони великої енергії вибивають електрони з внутрішніх оболонок, а переходи з вищих оболонок дають вузькі рентгенівські лінії. Екраювання змінює ефективний заряд, але головна залежність масштабу частот залишається $\nu \sim (Z-\sigma)^2$.
""",
    ),
    "atomicphys_mols.ipynb": (
        "molecular_spectra",
        r"""
## Експериментальний ключ: молекулярні спектри

Молекулярні спектри додають до електронних переходів коливальні та обертальні ступені свободи. Тому замість одиночних атомних ліній спостерігаються смуги з внутрішньою структурою. Саме така структура робить природним адіабатичне розділення руху електронів і ядер.

<img src="./figs/fig_molspectr.png" alt="Молекулярний спектр" width="620">

<img src="./figs/fig_rotovibr.png" alt="Коливально-обертальна структура спектра" width="620">

**Ідея експерименту.** Молекулярний газ збуджують світлом або розрядом і аналізують випромінювання чи поглинання спектрометром. Відстані між лініями відокремлюють масштаби: електронні переходи найбільші, коливальні менші, обертальні найменші.
""",
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--atomic-py", type=Path, required=True)
    parser.add_argument(
        "--notebook",
        action="append",
        choices=sorted(SECTIONS),
        help="Update only the selected notebook; may be repeated.",
    )
    args = parser.parse_args()
    atomic_py = args.atomic_py
    fig_dir = atomic_py / "figs"
    selected = args.notebook or list(SECTIONS)
    figure_notebooks = {
        "atomicphys_photons.ipynb",
        "atomicphys_spinpauli_theor.ipynb",
        "atomicphys_atominemfield.ipynb",
    }
    if args.notebook is None or figure_notebooks.intersection(selected):
        generated_figures(fig_dir)
    if "atomicphys_dual.ipynb" in selected:
        data_path = Path(__file__).resolve().parents[1] / "sources" / "lxcat_siglo.json"
        save_ramsauer_noble_gases(fig_dir / "fig_Ramsauer_ArKrXe.png", data_path)
    updated = []
    for notebook in selected:
        key, content = SECTIONS[notebook]
        nb_path = atomic_py / notebook
        if not nb_path.exists():
            raise FileNotFoundError(nb_path)
        upsert_cell(nb_path, key, content)
        if notebook == "atomicphys_dual.ipynb":
            update_ramsauer_caption(nb_path)
        updated.append(notebook)
    print("updated notebooks:")
    for name in updated:
        print(f"- {name}")
    print("generated figures:")
    if args.notebook is None or figure_notebooks.intersection(selected):
        for name in [
            "fig_exp_photoelectric_threshold.png",
            "fig_exp_compton_shift.png",
            "fig_exp_stern_gerlach_scheme.png",
            "fig_exp_field_splitting.png",
        ]:
            print(f"- figs/{name}")
    if "atomicphys_dual.ipynb" in selected:
        print("- figs/fig_Ramsauer_ArKrXe.png")


if __name__ == "__main__":
    main()
