# 🌸 Как запустить и настроить аниме-профиль

Здесь всё, что нужно сделать руками на сайте GitHub. Код и картинки уже готовы.

---

## Шаг 1. Переименовать репозиторий в `wobuzhidaoq` (обязательно)

GitHub показывает README на странице профиля, **только если репозиторий называется так же, как твой ник**.
Сейчас он называется `README.md`, поэтому на профиле ничего не видно.

1. Открой https://github.com/wobuzhidaoq/README.md
2. Вверху нажми вкладку **⚙️ Settings**.
3. В разделе **General** найди поле **Repository name**.
4. Сотри `README.md`, впиши `wobuzhidaoq` и нажми **Rename**.
5. GitHub покажет плашку «✨ wobuzhidaoq/wobuzhidaoq is a ✨special✨ repository» — значит всё правильно.

Репозиторий должен быть **Public** (публичным). Проверить: Settings → General → в самом низу «Danger Zone» →
там написано «This repository is currently public».

> Если репозиторий `wobuzhidaoq` у тебя уже есть — удали его или переименуй, а потом переименуй этот.

## Шаг 2. Сделать основной ветку `main`

Всё лежит в ветке `claude/pensive-tesla-l5e5nf`. Профиль показывает README из **основной (default) ветки**.

**Вариант А — если репозиторий был пустой** (ветка `claude/...` стала основной сама):

1. Settings → General → блок **Default branch**.
2. Нажми ✏️ (Rename branch) рядом с названием ветки.
3. Впиши `main` → **Rename branch**.

**Вариант Б — если основная ветка уже `main`:**

1. Вкладка **Pull requests** → **New pull request**.
2. base: `main` ← compare: `claude/pensive-tesla-l5e5nf` → **Create pull request** → **Merge pull request** → **Confirm merge**.

## Шаг 3. Включить GitHub Actions (живая статистика)

Карточки статистики, змейка, 3D-календарь, «окно статуса» и цитата дня обновляются роботом каждые 6 часов.

1. **Разрешить роботу сохранять картинки:**
   Settings → слева **Actions** → **General** → внизу блок **Workflow permissions** →
   выбери **Read and write permissions** → **Save**.
2. Открой вкладку **Actions**. Если видишь жёлтую плашку
   «Workflows aren’t being run on this repository» — нажми
   **I understand my workflows, go ahead and enable them**.
3. Слева выбери **🌸 Обновить аниме-профиль** → справа **Run workflow** → ветка `main` → зелёная кнопка **Run workflow**.
4. Подожди 2–3 минуты, пока кружок станет зелёной галочкой ✅.
5. Открой https://github.com/wobuzhidaoq — профиль готов!

Дальше всё работает само: каждые 6 часов и после каждого твоего изменения в репозитории.

> Картинки на GitHub кешируются на несколько минут. Если не видишь изменений — обнови страницу через Ctrl+F5.

## Шаг 4. Вписать своё

Все файлы можно редактировать прямо на сайте: открой файл → ✏️ (Edit) → внеси правки → **Commit changes**.
После каждого коммита робот сам пересоберёт картинки (~2 минуты).

### `config/profile.json` — тексты на картинках

| Поле | Что это |
|---|---|
| `header.greeting` | маленькая надпись над ником в шапке (сейчас «こんにちは、旅人さん！» — «Привет, путник!») |
| `header.title` | большой ник в шапке |
| `header.subtitle` | строка под ником |
| `status_window.race` | «Раса» в окне статуса |
| `status_window.class` | «Класс». Пусто → выбирается сам по твоему главному языку (Python → «Змеиный заклинатель» и т.д.) |
| `status_window.title` | «Титул». Пусто → выдаётся сам за достижения (стрик, звёзды, коммиты…) |
| `status_window.equipment` | «Снаряжение» — список приколов через запятую |
| `exclude_languages` | языки, которые не показывать в навыках, например `["HTML", "Jupyter Notebook"]` |
| `anime_list.*` | карточка «Сейчас смотрю» (см. шаг 5) |
| `footer.title`, `footer.subtitle` | надписи в подвале |
| `style` | стиль профиля: `"manga"` или `"sakura-day"` (подробнее — [STYLES.md](STYLES.md)) |
| `typing_lines` | строки печатающегося текста под шапкой |
| `skills` | навыки в разделе «Арсенал» (названия как на https://skillicons.dev, например `python`, `js`, `cpp`) |
| `socials` | соцсети: впиши ссылку в `url`, и бейдж появится; пустые ссылки не показываются |
| `images` | картинки для панелей стиля манги (см. [STYLES.md](STYLES.md)) |
| `credits` | подписи авторов артов под счётчиком просмотров |

### `README.md` — места с пометкой ✏️

- **Обо мне** — список строк под окном статуса.
- Навыки, соцсети и строки печатающегося текста теперь задаются в `config/profile.json`
  (`skills`, `socials`, `typing_lines`) — README обновится сам.

### `data/quotes.json` — цитаты дня

Добавляй свои: `{"text": "Цитата", "who": "Персонаж", "anime": "Аниме"}`. Каждый день показывается новая.

## Шаг 5. Карточка «Сейчас смотрю» из AniList или Shikimori (по желанию)

Показывает обложки аниме, которые ты сейчас смотришь, прогресс по сериям и общую статистику.
Токены не нужны — данные берутся из публичного профиля.

**AniList:**
1. Зарегистрируйся на https://anilist.co
2. Найди аниме → **Add to List** → статус **Watching**, укажи, сколько серий посмотрел.
3. В `config/profile.json` впиши: `"service": "anilist"`, `"username": "твой_ник_на_anilist"`.

**Shikimori:**
1. Зарегистрируйся на https://shikimori.one
2. Добавь аниме в список со статусом **Смотрю**.
3. В `config/profile.json` впиши: `"service": "shikimori"`, `"username": "твой_ник_на_shikimori"`.

После коммита в README сам появится раздел «📺 Сейчас смотрю».

## Шаг 6. Аниме-гифки (по желанию)

1. Найди гифку (Tenor, Giphy, Pinterest) и скачай её как `.gif`. Лучше до 5 МБ и шириной 300–500 px.
2. В репозитории открой папку `assets` → **Add file** → **Upload files** → перетащи гифку → **Commit changes**.
3. В `README.md` найди комментарий «✏️ Аниме-гифка», убери вокруг строки `<!--` и `-->`
   и поставь имя своего файла: `./assets/имя.gif`.

Можно вставить гифку куда угодно строкой `<p align="center"><img src="./assets/имя.gif" width="360"/></p>`.

## Шаг 7. Довести профиль до идеала (по желанию)

- **Аватарка:** Settings → Public profile → Profile picture → Edit → Upload a photo.
- **Био и имя:** Settings → Public profile → Name / Bio.
- **Статус с эмодзи:** на странице профиля нажми на аватарку → **Set status** → например 🌸 «смотрю аниме».
- **Закреплённые репозитории:** на странице профиля **Customize your pins** → выбери до 6 штук.
- **Приватные вклады в календаре:** на профиле над графиком вкладов **Contribution settings** →
  включи **Private contributions**.
- **Ачивки GitHub:** Settings → Public profile → включи **Show Achievements on my profile**.

### Учитывать приватные репозитории в статистике

По умолчанию робот видит только публичные репозитории. Чтобы считать и приватные:

1. https://github.com/settings/tokens → **Generate new token (classic)** → отметь `repo` и `read:user` →
   срок можно поставить No expiration → **Generate token** → скопируй токен.
2. В репозитории: Settings → **Secrets and variables** → **Actions** → **New repository secret** →
   Name: `GH_PAT`, Secret: вставь токен → **Add secret**.
3. В `.github/workflows/anime-profile.yml` замени все `secrets.GITHUB_TOKEN` на `secrets.GH_PAT`.

## Сохранённые стили

Готовые стили (дневная и ночная сакура) сохранены тегами — как вернуть любой из них и как безопасно
пробовать новый стиль, описано в [docs/STYLES.md](STYLES.md).

## Если что-то не работает

- **Красный крестик в Actions.** Открой запуск → упавший шаг → прочитай лог.
  `Permission denied` / `403` при `git push` → проверь шаг 3.1 (Read and write permissions).
- **Картинка показывает «появится после первого запуска Actions».** Робот ещё не запускался — шаг 3.3.
- **Расписание перестало работать.** GitHub выключает расписание в публичных репозиториях,
  где 60 дней нет активности. Зайди в Actions → workflow → **Enable workflow**.
- **Счётчик просмотров, печатающийся текст, график активности и серия** — это внешние сервисы
  (count.getloli.com, demolab.com, vercel.app). Если один из них временно лежит, просто подожди.

## Как это устроено

```
.github/workflows/anime-profile.yml  ← робот: запускается каждые 6 часов
config/profile.json                  ← твои тексты и настройки
config/3d-sakura.json                ← цвета 3D-календаря
data/quotes.json                     ← цитаты дня
scripts/build.py                     ← собирает баннер, окно статуса, цитату, список аниме
scripts/anime_profile/               ← сами генераторы картинок (Python, без зависимостей)
assets/generated/                    ← готовые картинки (не редактируй руками — перезапишутся)
```

Локальный запуск (если захочешь): `GITHUB_TOKEN=ghp_... python3 scripts/build.py`.
