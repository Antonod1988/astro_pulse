# -------------------------------------
# DATA & INTERPRETATIONS (База знаний)
# -------------------------------------

# Ключевые слова для авто-генерации
KEYWORDS = {
    "ru": {
        "Sun": "Сила воли, Эго, Жизненная энергия",
        "Moon": "Эмоции, Душа, Подсознание",
        "Mercury": "Мышление, Документы, Общение",
        "Venus": "Любовь, Деньги, Комфорт",
        "Mars": "Действие, Агрессия, Спорт",
        "Jupiter": "Удача, Расширение, Авторитет",
        "Saturn": "Ограничение, Дисциплина, Уроки",
        "Uranus": "Внезапность, Революция, Свобода",
        "Neptune": "Иллюзии, Вдохновение, Хаос",
        "Pluto": "Трансформация, Власть, Кризис"
    },
    "en": {
        "Sun": "Willpower, Ego, Vital Energy",
        "Moon": "Emotions, Soul, Subconscious",
        "Mercury": "Thinking, Documents, Communication",
        "Venus": "Love, Money, Comfort",
        "Mars": "Action, Aggression, Sport",
        "Jupiter": "Luck, Expansion, Authority",
        "Saturn": "Restriction, Discipline, Lessons",
        "Uranus": "Suddenness, Revolution, Freedom",
        "Neptune": "Illusions, Inspiration, Chaos",
        "Pluto": "Transformation, Power, Crisis"
    }
}

HOUSE_KEYWORDS = {
    "ru": {
        1: "Личность/Имидж (1 дом)",
        2: "Деньги/Ресурсы (2 дом)",
        3: "Контакты/Обучение (3 дом)",
        4: "Дом/Семья (4 дом)",
        5: "Творчество/Любовь/Дети (5 дом)",
        6: "Работа/Здоровье (6 дом)",
        7: "Партнерство/Брак (7 дом)",
        8: "Кризис/Чужие ресурсы (8 дом)",
        9: "Путешествия/Мировоззрение (9 дом)",
        10: "Карьера/Статус (10 дом)",
        11: "Друзья/Планы (11 дом)",
        12: "Подсознание/Тайны (12 дом)"
    },
    "en": {
        1: "Identity/Image (1st House)",
        2: "Money/Resources (2nd House)",
        3: "Contacts/Learning (3rd House)",
        4: "Home/Family (4th House)",
        5: "Creativity/Love/Children (5th House)",
        6: "Work/Health (6th House)",
        7: "Partnership/Marriage (7th House)",
        8: "Crisis/Shared Resources (8th House)",
        9: "Travel/Worldview (9th House)",
        10: "Career/Status (10th House)",
        11: "Friends/Plans (11th House)",
        12: "Subconscious/Secrets (12th House)"
    }
}

ASPECT_KEYWORDS = {
    "ru": {
        "Conjunction": "сливается с энергией",
        "Sextile": "дает возможности для",
        "Square": "создает конфликт с",
        "Trine": "гармонично поддерживает",
        "Opposition": "противостоит"
    },
    "en": {
        "Conjunction": "merges with the energy of",
        "Sextile": "gives opportunities for",
        "Square": "creates conflict with",
        "Trine": "harmoniously supports",
        "Opposition": "opposes"
    }
}

# База точных интерпретаций
INTERPRETATIONS_DB = {
    "ru": {
        "Pluto Conjunction Sun": "🔥 [Раз в жизни] Полная перезагрузка личности. Старое 'Я' умирает, рождается новое. Период колоссальной власти, но и давления обстоятельств.",
        "Pluto Square Sun": "⚠️ [Раз в жизни] Битва за выживание и власть. Ваше эго подвергается жесткому давлению.",
        "Saturn Conjunction Sun": "🧱 [Раз в 29 лет] Период взросления и ответственности. Жизнь становится серьезной.",
        # ... (other existing RU entries would go here)
    },
    "en": {
        "Pluto Conjunction Sun": "🔥 [Once in a lifetime] Complete personality reset. The old 'I' dies, a new one is born. A period of colossal power, but also pressure of circumstances.",
        "Pluto Square Sun": "⚠️ [Once in a lifetime] Battle for survival and power. Your ego is under severe pressure.",
        "Saturn Conjunction Sun": "🧱 [Once in 29 years] A period of maturity and responsibility. Life becomes serious.",
    }
}

# Шаблоны для генерации
TEMPLATES = {
    "ru": {
        "Tense": [
            "Напряженный период. {t_name} бросает вызов {n_name}. Возможен конфликт между сферами: {t_desc} и {n_desc}.",
            "Конфликт интересов: {t_name} в сфере '{t_house_desc}' нарушает планы {n_name} в сфере '{n_house_desc}'.",
        ],
        "Harmonic": [
            "✨ Гармоничный поток. {t_name} удачно поддерживает {n_name}. Легко решаются вопросы, связанные с: {n_desc}.",
            "Успех через взаимодействие: {t_name} из сферы '{t_house_desc}' помогает реализации {n_name} в '{n_house_desc}'.",
        ],
        "Neutral": [
            "Соединение энергий. {t_name} и {n_name} действуют заодно. Результат зависит от вашего выбора.",
            "Акцент года: {t_name} в '{t_house_desc}' соединяется с {n_name} ({n_house_desc}).",
        ]
    },
    "en": {
        "Tense": [
            "Tense period. {t_name} challenges {n_name}. Possible conflict between: {t_desc} and {n_desc}.",
            "Conflict of interests: {t_name} in the sphere of '{t_house_desc}' disrupts the plans of {n_name} in '{n_house_desc}'.",
        ],
        "Harmonic": [
            "✨ Harmonious flow. {t_name} successfully supports {n_name}. Matters related to {n_desc} are easily resolved.",
            "Success through interaction: {t_name} from the sector of '{t_house_desc}' helps the realization of {n_name} in '{n_house_desc}'.",
        ],
        "Neutral": [
            "Merging of energies. {t_name} and {n_name} act together. The result depends on your conscious choice.",
            "Year highlight: {t_name} in '{t_house_desc}' conjuncts {n_name} ({n_house_desc}). Important event in these sectors.",
        ]
    }
}

def get_aspect_nature(aspect, t_planet):
    if aspect in ["Square", "Opposition"]: return "Tense"
    if aspect in ["Trine", "Sextile"]: return "Harmonic"
    if aspect == "Conjunction":
        if t_planet in ["Mars", "Saturn", "Uranus", "Neptune", "Pluto"]: return "Tense"
        return "Neutral"
    return "Neutral"

def get_interpretation(t_name, aspect, n_name, t_house=None, n_house=None, lang="ru"):
    key = f"{t_name} {aspect} {n_name}"
    
    # 1. Search in DB
    db = INTERPRETATIONS_DB.get(lang, INTERPRETATIONS_DB["ru"])
    if key in db: return db[key]
    if lang != "ru" and key in INTERPRETATIONS_DB["ru"]: return INTERPRETATIONS_DB["ru"][key]
    
    # 2. Generator
    nature = get_aspect_nature(aspect, t_name)
    lang_templates = TEMPLATES.get(lang, TEMPLATES["ru"])
    
    t_desc = KEYWORDS.get(lang, KEYWORDS["ru"]).get(t_name, t_name)
    n_desc = KEYWORDS.get(lang, KEYWORDS["ru"]).get(n_name, n_name)
    
    h_db = HOUSE_KEYWORDS.get(lang, HOUSE_KEYWORDS["ru"])
    t_house_desc = h_db.get(t_house, f"{t_house} house") if t_house else "Transit"
    n_house_desc = h_db.get(n_house, f"{n_house} house") if n_house else "Natal"
    
    idx = hash(key + str(t_house) + str(n_house)) % len(lang_templates[nature])
    template = lang_templates[nature][idx]
    
    return template.format(
        t_name=t_name, n_name=n_name, 
        t_desc=t_desc, n_desc=n_desc,
        t_house_desc=t_house_desc, n_house_desc=n_house_desc
    )

def get_planet_rarity(t_name, lang="ru"):
    rarity_map = {
        "ru": {
            "Sun": "1 раз в год", "Mercury": "1 раз в год", "Venus": "1 раз в год",
            "Mars": "1 раз в 2 года", "Jupiter": "1 раз в 12 лет", "Saturn": "1 раз в 29 лет",
            "Uranus": "1 раз в 84 года", "Neptune": "1 раз в 165 лет", "Pluto": "1 раз в 248 лет"
        },
        "en": {
            "Sun": "Once a year", "Mercury": "Once a year", "Venus": "Once a year",
            "Mars": "Once in 2 years", "Jupiter": "Once in 12 years", "Saturn": "Once in 29 years",
            "Uranus": "Once in 84 years", "Neptune": "Once in 165 years", "Pluto": "Once in 248 years"
        }
    }
    return rarity_map.get(lang, rarity_map["ru"]).get(t_name, None)
