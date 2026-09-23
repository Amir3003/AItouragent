/**
 * VoyageAI: Autonomous Travel Concierge
 * Frontend Client Application
 */

// ── Complete Multilingual Dictionary (EN / RU) ──────────────────────────────
const TRANSLATIONS = {
  EN: {
    // Header & Showcase
    tag_showcase:      'Digital Bridge 2026 Showcase',
    new_itinerary:     'New Itinerary',

    // Hero Section
    hero_eyebrow:      'AUTONOMOUS LUXURY TRAVEL · 24/7 CONCIERGE',
    hero_title:        'VoyageAI —<br><span>Your Autonomous</span><br>Travel Concierge',
    hero_desc:         'Bespoke itinerary curation powered by Google Gemini. Direct roundtrip flights, handpicked 5-star suites, and transparent pricing in USD & KZT with zero commission markups.',
    hero_cta:          'Start Curation',

    // Hero Stats
    stat_concierge:    'Autonomous Concierge',
    stat_resorts:      'Elite World Resorts',
    stat_destinations: 'Top Global Destinations',
    stat_commission:   'Hidden Commission',

    // Section Intro
    section_intro_eyebrow: 'VOYAGEAI CONCIERGE',
    section_intro_title:   'Where shall we take you?',
    section_intro_desc:    'A single conversational prompt replaces tedious multi-step search engines. VoyageAI interprets your travel style, selects non-stop flight routes, and matches real suites.',

    // Chat Panel
    panel_status:      'VoyageAI Active · Real-time Parameter Extraction',
    panel_sub:         'Natural Language Parsing',
    welcome_msg:       'Welcome to VoyageAI! I am your autonomous travel concierge. Where would you like to travel, for how many nights, and what is your preferred budget and party size?',
    send_btn:          'Send ↗',
    input_placeholder: 'e.g. Solo luxury escape to Dubai from Astana for 7 nights, 5★, $3,500 budget',

    // Demo Quick-Launch Chips
    chip_antalya:      '🌴 Family holiday in Antalya, 7 nights',
    chip_dubai:        '🏙️ Solo trip to Dubai, 5 nights',
    chip_phuket:       '🏖️ Phuket vacation, 8 nights',
    spec_beach:        'Beach',
    spec_board:        'Meal Plan',
    spec_in_room:      'In Room',
    spec_children:     'For Children',
    spec_territory:    'Hotel Grounds',
    flex_dates_label:  'Flexible departure dates:',

    // Right Column: HOW IT WORKS
    how_label:         'HOW IT WORKS',
    how_title:         'Your Vision.<br>Our Autonomous Engine.',
    how_step1:         'State your vision in natural conversational language',
    how_step2:         'VoyageAI extracts dates, direct flights &amp; suite tiers',
    how_step3:         'Receive Top 5 curated vacation packages with flight tickets',
    how_note:          'Synchronized with live scheduled airline routes &amp; verified resort suites.',
    how_cta:           'View Curated Packages',

    // Results Section
    bespoke_label:     'BESPOKE SELECTION',
    top5_heading:      'Top 5 Tailored Packages',
    awaiting:          'Awaiting your request',
    analyzing:         'Analyzing travel criteria & flight schedules...',
    empty_heading:     'Your bespoke matches will appear here',
    empty_sub:         'Send a message to VoyageAI above or select one of the sample itineraries.',
    results_found:     (n) => `Top ${n} Bespoke Matches`,
    complete_msg:      'Here are your Top 5 bespoke curated options. Compare packages and select your preferred suite.',
    error_msg:         'VoyageAI is currently refreshing connection. Please resend your message in a few moments.',

    // Hotel Card Elements
    instant_confirm:   'Instant Confirmation',
    explore_suites:    'Explore Suite Options & Details',
    wa_share:          '📲 Share via WhatsApp',
    flight_direct:     'Direct Flight',
    flight_nonstop:    'non-stop',
    flight_included:   '✓ Flight Included in Package',
    flight_baggage:    '23 kg check-in + 8 kg cabin baggage',

    // Drawer / Modal Elements
    modal_dates_label: 'Tour Dates',
    modal_flight_title:'Included Direct Roundtrip Flight',
    modal_flex_title:  'Flexible Dates (±1-2 days)',
    modal_flex_sub:    'Live confirmed fares',
    modal_rooms_title: 'Available Suites & Rooms',
    modal_categories:  'Categories',
    modal_total_label: 'Total Package (Suite + Direct Flights for all guests):',
    modal_reserve_btn: 'Book Package',
    modal_curator_highlights: 'Curator Highlights:',
    modal_room_base:   'Standard Base',
    modal_from:        'from',

    // VIP Booking Modal
    booking_eyebrow:   'VOYAGEAI VIP RESERVATION',
    booking_title:     'Confirm Itinerary',
    booking_label_name:'Primary Guest Full Name',
    booking_name_placeholder: 'Alexander Vance',
    booking_label_phone:'WhatsApp / Mobile Phone (with country code)',
    booking_cta:       'Confirm Reservation with Concierge',
    booking_success_title: 'Reservation Request Received',
    booking_success_desc: 'Your dedicated VoyageAI Concierge Officer will contact you within 5 minutes via WhatsApp to finalize your luxury flight and suite booking.',
    booking_success_close: 'Close Window',

    // Session Reset
    session_reset_msg: 'Session refreshed. Tell me about your dream vacation: destination, dates, budget and party size.',
  },

  RU: {
    // Header & Showcase
    tag_showcase:      'Digital Bridge 2026 Экспо',
    new_itinerary:     'Новый маршрут',

    // Hero Section
    hero_eyebrow:      'АВТОНОМНЫЙ ПРЕМИУМ-ТРЕВЕЛ · КОНСЬЕРЖ 24/7',
    hero_title:        'VoyageAI —<br><span>Ваш автономный</span><br>тревел-консьерж',
    hero_desc:         'Персональный подбор туров на базе Google Gemini. Прямые рейсы в обе стороны, проверенные 5★ отели и прозрачные цены в тенге и долларах без скрытых наценок.',
    hero_cta:          'Подобрать тур',

    // Hero Stats
    stat_concierge:    'АВТОНОМНЫЙ СЕРВИС',
    stat_resorts:      'ЛУЧШИХ КУРОРТОВ',
    stat_destinations: 'ПОПУЛЯРНЫХ НАПРАВЛЕНИЙ',
    stat_commission:   'СКРЫТЫХ КОМИССИЙ',

    // Section Intro
    section_intro_eyebrow: 'КОНСЬЕРЖ VOYAGEAI',
    section_intro_title:   'Куда бы вы хотели отправиться?',
    section_intro_desc:    'Один текстовый запрос заменяет сложные формы поиска. VoyageAI понимает пожелания, подбирает прямые рейсы и лучшие номера.',

    // Chat Panel
    panel_status:      'VoyageAI Активен · Извлечение параметров в реальном времени',
    panel_sub:         'Анализ на естественном языке',
    welcome_msg:       'Добро пожаловать в VoyageAI! Я ваш автономный тревел-консьерж. Куда желаете полететь, на сколько ночей и каков ваш бюджет?',
    send_btn:          'Отправить ↗',
    input_placeholder: 'Напр.: Один в Дубай на 7 ночей из Астаны, бюджет $3 500',

    // Demo Quick-Launch Chips
    chip_antalya:      '🌴 Семейный отдых в Анталье на 7 ночей',
    chip_dubai:        '🏙️ Соло-поездка в Дубай на 5 ночей',
    chip_phuket:       '🏖️ Отдых на Пхукете на 8 ночей',
    spec_beach:        'Пляж',
    spec_board:        'Питание',
    spec_in_room:      'В номере',
    spec_children:     'Для детей',
    spec_territory:    'Территория',
    flex_dates_label:  'Соседние даты вылета:',

    // Right Column: HOW IT WORKS
    how_label:         'КАК ЭТО РАБОТАЕТ',
    how_title:         'Ваш запрос.<br>Наш автономный движок.',
    how_step1:         'Опишите пожелания к поездке на обычном языке',
    how_step2:         'VoyageAI подберёт даты, прямые рейсы и категории номеров',
    how_step3:         'Получите топ-5 индивидуальных пакетов с перелётом',
    how_note:          'Синхронизировано с расписанием рейсов и проверенными отелями.',
    how_cta:           'Смотреть варианты',

    // Results Section
    bespoke_label:     'ПОДБОРКА ДЛЯ ВАС',
    top5_heading:      'Топ-5 персональных пакетов',
    awaiting:          'Ожидание запроса',
    analyzing:         'Анализ параметров путешествия и расписания рейсов...',
    empty_heading:     'Ваши персональные подборки появятся здесь',
    empty_sub:         'Отправьте сообщение VoyageAI или выберите один из сценариев выше.',
    results_found:     (n) => `Топ-${n} персональных туров`,
    complete_msg:      'Вот топ-5 подобранных вариантов под ваши критерии. Сравните пакеты и выберите подходящий номер.',
    error_msg:         'VoyageAI обновляет соединение. Пожалуйста, повторите запрос через несколько секунд.',

    // Hotel Card Elements
    instant_confirm:   'Мгновенное подтверждение',
    explore_suites:    'Выбрать номер и детали',
    wa_share:          '📲 Отправить в WhatsApp',
    flight_direct:     'Прямой рейс',
    flight_nonstop:    'без пересадок',
    flight_included:   '✓ Рейс включен в стоимость пакета',
    flight_baggage:    'Багаж: 23 кг + 8 кг ручная кладь',

    // Drawer / Modal Elements
    modal_dates_label: 'Даты тура',
    modal_flight_title:'Включенный прямой рейс (туда и обратно)',
    modal_flex_title:  'Соседние даты (±1-2 дня)',
    modal_flex_sub:    'Гарантированные тарифы',
    modal_rooms_title: 'Доступные категории номеров',
    modal_categories:  'категорий',
    modal_total_label: 'Итого за тур (Номер + Авиабилеты на всех гостей):',
    modal_reserve_btn: 'Забронировать тур',
    modal_curator_highlights: 'Особенности отеля:',
    modal_room_base:   'Базовый номер',
    modal_from:        'от',

    // VIP Booking Modal
    booking_eyebrow:   'VIP-БРОНИРОВАНИЕ VOYAGEAI',
    booking_title:     'Подтверждение бронирования',
    booking_label_name:'ФИО основного гостя',
    booking_name_placeholder: 'Александр Иванов',
    booking_label_phone:'WhatsApp / Номер телефона',
    booking_cta:       'Подтвердить бронирование',
    booking_success_title: 'Заявка на бронирование принята',
    booking_success_desc: 'Ваш персональный консьерж VoyageAI свяжется с вами в WhatsApp в течение 5 минут для подтверждения рейса и категории номера.',
    booking_success_close: 'Закрыть окно',

    // Session Reset
    session_reset_msg: 'Сессия сброшена. Расскажите о вашем путешествии: направление, даты, бюджет и состав гостей.',
  },
};

const DEFAULT_PROMPTS = {
  EN: [
    'Solo luxury trip to Dubai from Astana departing Oct 20 for 5 nights: 1 adult, $2,500 budget',
    'Family holiday in Antalya from Astana departing Oct 14 for 7 nights: 2 adults, 1 child (age 6), $2,800 budget',
    'Phuket vacation from Almaty departing Nov 10 for 8 nights: 2 adults, $2,200 budget',
    'Romantic Maldives overwater villa from Almaty departing Nov 5 for 7 nights, all-inclusive, $5,500 budget',
  ],
  RU: [
    'Соло-поездка в Дубай из Астаны с 20 октября на 5 ночей, 1 взрослый, бюджет $2 500',
    'Семейный отдых в Анталье из Астаны с 14 октября на 7 ночей: 2 взрослых, 1 ребёнок (6 лет), бюджет $2 800',
    'Отдых на Пхукете из Алматы с 10 ноября на 8 ночей: 2 взрослых, бюджет 1 800 000 ₸',
    'Отдых на Мальдивах из Алматы с 5 ноября на 7 ночей: вилла на воде, всё включено, бюджет $5 500',
  ],
};

const CHIP_QUERIES = {
  chip_dubai: {
    en: 'Solo luxury trip to Dubai from Astana departing Oct 20 for 5 nights: 1 adult, $2,500 budget',
    ru: 'Соло-поездка в Дубай из Астаны с 20 октября на 5 ночей, 1 взрослый, бюджет $2 500',
  },
  chip_antalya: {
    en: 'Family holiday in Antalya from Astana departing Oct 14 for 7 nights: 2 adults, 1 child (age 6), $2,800 budget',
    ru: 'Семейный отдых в Анталье из Астаны с 14 октября на 7 ночей: 2 взрослых, 1 ребёнок (6 лет), бюджет $2 800',
  },
  chip_phuket: {
    en: 'Phuket vacation from Almaty departing Nov 10 for 8 nights: 2 adults, $2,200 budget',
    ru: 'Отдых на Пхукете из Алматы с 10 ноября на 8 ночей: 2 взрослых, бюджет 1 800 000 ₸',
  },
};

const AMENITY_TRANSLATIONS = {
  'Кондиционер': 'Climate control',
  'Сейф (бесплатно)': 'Digital safe (free)',
  'Wi-Fi': 'High-speed Wi-Fi',
  'Фен': 'Hairdryer',
  'Ванна / душ': 'Bath & Rain shower',
  'Ванна/душ': 'Bath & Rain shower',
  'ТВ': 'Smart TV',
  'Набор для чая/кофе': 'Tea/coffee set',
  'Балкон / терраса': 'Furnished balcony / terrace',
  'Балкон/терраса': 'Furnished balcony / terrace',
  'Мини-бар (платно)': 'Minibar (surcharge)',
  'Халаты и тапочки': 'Bathrobes & slippers',
  'Гарантированный вид на море': 'Guaranteed sea view',
  'Балкон с видом на море': 'Furnished sea-view balcony',
  'Две раздельные спальни': 'Two separate bedrooms',
  'Две ванные комнаты': 'Two en-suite bathrooms',
  'Детские стульчики / кроватка': 'Baby cot & highchairs',
  'Детский клуб без доплат': 'Kids club complimentary',
  'Гостиная зона': 'Dedicated living area',
  'Панорамный балкон': 'Panoramic balcony',
  'Ванна и тропический душ': 'Bathtub & rain shower',
  'Кофемашина': 'Espresso coffee machine',
  'Приоритетное заселение': 'Priority check-in',
  'Поздний выезд (при наличии)': 'Late check-out (subject to availability)',
};

function translateAmenity(text, isRu) {
  if (isRu || !text) return text;
  const trimmed = text.trim();
  return AMENITY_TRANSLATIONS[trimmed] || trimmed;
}

const ROOM_DESC_TRANSLATIONS = {
  'Стандартный номер с видом на сад или территорию отеля. Кондиционер, ванная комната, балкон.':
    'Standard room with garden or resort view. Air conditioning, private bathroom, furnished balcony.',
  'Улучшенный номер с прямым или частичным видом на море, балконом и ванной комнатой.':
    'Superior room with direct or partial sea view, private balcony, and en-suite bathroom.',
  'Семейный двухкомнатный номер: 2 спальни, 2 ванные комнаты, балкон, детский набор.':
    'Family two-bedroom suite: 2 bedrooms, 2 bathrooms, private balcony, complimentary kids welcome pack.',
  'Просторный полулюкс с отдельной гостиной зоной и панорамным балконом с видом на море.':
    'Spacious junior suite with dedicated living area and panoramic sea-view balcony.',
  'Пляжное бунгало в окружении пальм с прямым выходом к песчаному пляжу и лагуне.':
    'Beachfront bungalow surrounded by tropical palms with direct access to the sandy beach and lagoon.',
  'Вилла на сваях над бирюзовой лагуной с собственной террасой для загара и спуском в воду.':
    'Overwater villa perched over the turquoise lagoon with private sun deck and direct ocean staircase.',
  'Просторная пляжная вилла с 2 спальнями, открытой террасой и выходом на пляж.':
    'Two-bedroom beachfront villa with expansive sundeck and steps from the white sand beach.',
  'Премиальный водный павильон над лагуной с просторной террасой и панорамными видами.':
    'Presidential lagoon pavilion with expansive overwater deck and panoramic sunset views.',
  'Улучшенный номер с видом на город. Кондиционер, рабочий стол, сейф, ванная комната.':
    'Superior room with skyline city view. Climate control, work desk, electronic safe, en-suite bathroom.',
  'Делюкс с панорамным видом на море или залив, балконом и отдельной ванной.':
    'Deluxe room with panoramic sea or bay view, private balcony, and deep soaking tub.',
  'Семейный люкс с 2 отдельными спальнями, гостиной зоной и 2 ванными комнатами.':
    'Family two-bedroom suite with 2 bedrooms, dedicated lounge, and 2 en-suite bathrooms.',
  'Представительский люкс с панорамным видом, просторной гостиной и доступом в лаунж.':
    'Executive suite featuring panoramic city views, grand living room, and club lounge access.',
};

function getRoomDescription(room, isRu) {
  if (isRu || !room || !room.description) return room ? (room.description || '') : '';
  const trimmed = room.description.trim();
  return ROOM_DESC_TRANSLATIONS[trimmed] || trimmed;
}

function formatCapacity(cap, isRu) {
  if (!cap) return isRu ? '1–2 гостя' : 'Up to 2 Guests';
  if (isRu) {
    if (cap.toLowerCase().includes('гост')) return cap;
    if (cap === 'Up to 2 Guests') return '1–2 гостя';
    if (cap === 'Up to 4 Guests') return 'До 4 гостей';
    return cap;
  }
  const clean = cap.trim();
  if (clean.includes('1–2') || clean.includes('1-2') || clean.includes('1 - 2')) return 'Up to 2 Guests';
  if (clean.includes('1–3') || clean.includes('1-3') || clean.includes('2+1')) return 'Up to 3 Guests';
  if (clean.includes('2–4') || clean.includes('2-4') || clean.includes('До 4') || clean.includes('4')) return 'Up to 4 Guests';
  if (clean.includes('1 Гость') || clean.includes('1 гость')) return '1 Guest';
  return clean.replace(/Гостя|гостя|Гостей|гостей/gi, 'Guests').replace(/До/g, 'Up to');
}

function formatBedType(bed, isRu) {
  if (!bed) return isRu ? '1 большая двуспальная кровать' : '1 King Bed';
  if (isRu) return bed;
  const clean = bed.trim();
  if (clean.includes('1 King Bed или 2 Twin Beds')) return '1 King Bed or 2 Twin Beds';
  if (clean.includes('1 King Bed + 2 Twin Beds')) return '1 King Bed + 2 Twin Beds';
  if (clean.includes('1 King Bed (180x200)')) return '1 King Bed (180x200)';
  if (clean.includes('1 King Bed (200x200)')) return '1 King Bed (200x200)';
  if (clean.includes('1 Super King Bed (220x220)')) return '1 Super King Bed (220x220)';
  return clean;
}

function getHotelSpecs(hotel, isRu) {
  if (isRu) {
    return {
      beach: hotel.beach || '1-я линия, собственный песчано-галечный пляж, шезлонги и зонты бесплатно',
      board: hotel.board_desc || hotel.meal_type || 'Всё включено (трехразовое питание, напитки)',
      in_room: hotel.in_room || 'Кондиционер, Сейф (бесплатно), Wi-Fi, Фен, Ванна/душ, ТВ, балкон/терраса, мини-бар, набор для чая/кофе',
      children: hotel.for_children || 'Детский бассейн, мини-клуб, игровая площадка, детские стульчики в ресторане, кроватка по запросу',
      territory: hotel.territory || 'Открытый бассейн, SPA-центр, ресторан a-la carte, фитнес-зал, круглосуточная стойка регистрации, бесплатная парковка',
    };
  } else {
    let boardDescEn = hotel.board_desc_en;
    if (!boardDescEn) {
      const meal = (hotel.meal_type || '').toUpperCase();
      if (meal.includes('UAI') || meal.includes('ULTRA')) {
        boardDescEn = 'Ultra All Inclusive — 24/7 all-inclusive (gourmet meals, premium beverages, snacks)';
      } else if (meal.includes('AI') || meal.includes('ALL')) {
        boardDescEn = 'All-inclusive (all meals, snacks, soft and alcoholic drinks)';
      } else if (meal.includes('BB') || meal.includes('BREAKFAST')) {
        boardDescEn = 'Bed & Breakfast (morning buffet included)';
      } else if (meal.includes('HB') || meal.includes('HALF')) {
        boardDescEn = 'Half Board (breakfast + dinner buffet)';
      } else if (meal.includes('FB') || meal.includes('FULL')) {
        boardDescEn = 'Full Board (breakfast, lunch, dinner buffet)';
      } else if (meal.includes('RO')) {
        boardDescEn = 'Room Only (no meals included)';
      } else {
        boardDescEn = `${hotel.meal_type} — Standard hotel board`;
      }
    }

    return {
      beach: hotel.beach_en || '1st coastline, private sandy beach, complimentary sun loungers & umbrellas',
      board: boardDescEn,
      in_room: hotel.in_room_en || 'Air conditioning, Digital safe (free), Wi-Fi, Hairdryer, Bath/shower, TV, Balcony/terrace, Minibar, Tea/coffee set',
      children: hotel.for_children_en || 'Kids club, shallow pool, baby cot upon request, high chairs in restaurant',
      territory: hotel.territory_en || 'Swimming pool, a la carte restaurants, fitness center, landscaped gardens, free Wi-Fi',
    };
  }
}

let currentLang = localStorage.getItem('voyageai-lang') || 'EN';
let lastResults = [];
let lastFlight = null;

// ── DOM References ───────────────────────────────────────────────────────────
const searchForm = document.getElementById('search-form');
const messages = document.getElementById('agent-messages');
const input = document.getElementById('user-input');
const quickPrompts = document.getElementById('quick-prompts');
const results = document.getElementById('results');
const resultCount = document.getElementById('results-count');
const bookingModal = document.getElementById('booking-modal');
const detailModal = document.getElementById('hotel-modal') || document.getElementById('room-detail-modal');
const detailContent = document.getElementById('hotel-modal-content') || document.getElementById('room-detail-content') || (detailModal ? detailModal.querySelector('.detail-drawer, .modal-content, .modal-card') : null);

function getHotelModal() {
  return document.getElementById('hotel-modal') || document.getElementById('room-detail-modal') || detailModal;
}

function getHotelModalContent() {
  const m = getHotelModal();
  return document.getElementById('hotel-modal-content') || document.getElementById('room-detail-content') || (m ? m.querySelector('.detail-drawer, .modal-content, .modal-card') : null) || detailContent;
}
const hotelCounter = document.getElementById('hero-hotels-count');
const showResultsButton = document.getElementById('show-results-button');
const flightContainer = document.getElementById('flight-summary-container');
const resetSessionButton = document.getElementById('reset-session-button');

let sessionId = getSessionId();
let activeHotel = null;
let selectedRoom = null;
let currentFlight = null;

const moneyKzt = new Intl.NumberFormat('en-US');
const moneyUsd = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });

// ── Language Controller ──────────────────────────────────────────────────────
function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem('voyageai-lang', lang);
  const t = TRANSLATIONS[lang];

  // Update button classes
  document.querySelectorAll('.lang-btn').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });

  // Translate all [data-i18n]
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.dataset.i18n;
    if (t[key] !== undefined) {
      if (key === 'send_btn') {
        el.innerHTML = (lang === 'RU') ? 'Отправить <span>↗</span>' : 'Send <span>↗</span>';
      } else if (key === 'how_title' || key === 'hero_title') {
        el.innerHTML = t[key];
      } else if (key === 'hero_cta') {
        el.innerHTML = `${t[key]} <span>→</span>`;
      } else if (key === 'booking_cta') {
        el.innerHTML = `${t[key]} <span>↗</span>`;
      } else if (key === 'how_cta') {
        el.innerHTML = t[key];
      } else {
        el.textContent = t[key];
      }
    }
  });

  // Translate placeholders
  document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    const key = el.dataset.i18nPlaceholder;
    if (t[key] !== undefined) el.placeholder = t[key];
  });

  // Translate demo chips
  document.querySelectorAll('[data-i18n-chip]').forEach((el) => {
    const key = el.dataset.i18nChip;
    if (t[key] !== undefined) el.textContent = t[key];
  });

  // Re-render quick prompts if default
  renderPrompts(DEFAULT_PROMPTS[lang]);

  // Re-render results if already loaded
  if (lastResults && lastResults.length > 0) {
    renderResults(lastResults, lastFlight);
  } else if (resultCount) {
    resultCount.textContent = t.awaiting;
  }

  // Translate modal reserve button if open
  const reserveBtn = document.querySelector('[data-book-detail]');
  if (reserveBtn) {
    reserveBtn.innerHTML = `${t.modal_reserve_btn} <span>→</span>`;
  }

  // Re-render modal if open
  const modal = getHotelModal();
  if (modal && !modal.classList.contains('hidden') && modal.style.display !== 'none' && activeHotel) {
    openHotelModal(activeHotel);
  }
}

// Language switcher clicks
document.querySelectorAll('.lang-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    setLanguage(btn.dataset.lang);
  });
});

// Demo chips click handlers
document.querySelectorAll('.demo-chip').forEach((chip) => {
  chip.addEventListener('click', () => {
    const isRu = (currentLang || 'EN').toUpperCase() === 'RU';
    const chipKey = chip.dataset.i18nChip;
    const query = (CHIP_QUERIES[chipKey] && CHIP_QUERIES[chipKey][isRu ? 'ru' : 'en'])
      || (isRu ? chip.dataset.queryRu : chip.dataset.queryEn)
      || chip.textContent.trim();
    input.value = '';
    const chatSection = document.getElementById('ai-chat-section');
    if (chatSection) chatSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    sendMessage(query);
  });
});

// Show results button click handler
if (showResultsButton) {
  showResultsButton.addEventListener('click', () => {
    const resultsSection = document.querySelector('.results-section') || document.getElementById('results');
    if (lastResults && lastResults.length > 0) {
      if (resultsSection) {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } else {
      const isRu = currentLang === 'RU';
      addMessage('assistant', isRu
        ? 'Пожалуйста, отправьте запрос или выберите один из сценариев выше, чтобы подобрать варианты.'
        : 'Please send a message or select a scenario above to curate vacation packages.');
      const chatSection = document.getElementById('ai-chat-section');
      if (chatSection) {
        chatSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      if (input) input.focus();
    }
  });
}

// Reset session handler
if (resetSessionButton) {
  resetSessionButton.addEventListener('click', () => {
    window.sessionStorage.removeItem('voyageai-session-id');
    sessionId = getSessionId();
    messages.innerHTML = '';
    const t = TRANSLATIONS[currentLang];
    addMessage('assistant', t.session_reset_msg);
    if (results) {
      results.innerHTML = `
        <div class="empty-state">
          <strong>${escapeHtml(t.empty_heading)}</strong>
          <p>${escapeHtml(t.empty_sub)}</p>
        </div>`;
    }
    if (flightContainer) flightContainer.innerHTML = '';
    if (resultCount) resultCount.textContent = t.awaiting;
    lastResults = [];
    lastFlight = null;
    currentFlight = null;
  });
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function getSessionId() {
  const key = 'voyageai-session-id';
  const current = window.sessionStorage.getItem(key);
  if (current) return current;
  const created = `voyage-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
  window.sessionStorage.setItem(key, created);
  return created;
}

function escapeHtml(val) {
  return String(val ?? '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

function formatShortDate(iso) {
  if (!iso) return '';
  const parts = iso.split('-');
  if (parts.length === 3) return `${parts[2]}.${parts[1]}`;
  return iso;
}

function getFlexDateLabel(fd, isSelected, isRu) {
  const baseLabel = fd.date_label || formatShortDate(fd.departure_date) || '';
  if (isSelected) {
    return `${baseLabel} (${isRu ? 'Выбрано' : 'Selected'})`;
  }
  return baseLabel;
}

function addMessage(role, text) {
  const item = document.createElement('div');
  item.className = `agent-message ${role}`;
  item.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
  messages.appendChild(item);
  messages.scrollTop = messages.scrollHeight;
}

function renderPrompts(prompts) {
  if (!quickPrompts) return;
  quickPrompts.innerHTML = (prompts || []).slice(0, 4).map((p) => `
    <button class="prompt-chip" type="button" data-prompt="${escapeHtml(p)}">${escapeHtml(p)}</button>
  `).join('');
  quickPrompts.querySelectorAll('[data-prompt]').forEach((chip) => {
    chip.addEventListener('click', () => {
      input.value = chip.dataset.prompt;
      document.getElementById('ai-chat-section').scrollIntoView({ behavior: 'smooth', block: 'center' });
      sendMessage(chip.dataset.prompt);
    });
  });
}

function translateGuestBadge(badge, isRu) {
  if (!isRu || !badge) return badge;
  if (badge.includes('Solo Traveler')) return 'Соло-путешественник · 1 взрослый';
  if (badge.includes('Couple Escape')) return 'Для двоих · 2 взрослых';
  if (badge.includes('Family Package')) {
    return badge.replace('Family Package ·', 'Семейный тур ·')
      .replace('Adults', 'взрослых').replace('Adult', 'взрослый')
      .replace('Children', 'детей').replace('Child', 'ребёнок');
  }
  if (badge.includes('Group Package')) return badge.replace('Group Package ·', 'Группа ·').replace('Guests', 'гостей');
  return badge;
}

function buildWhatsAppText(hotel) {
  const isRu = currentLang === 'RU';
  const usdVal = hotel.total_price_usd || Math.round(hotel.total_price_kzt / 500);
  const stars = '★'.repeat(hotel.stars || 5);
  const room = hotel.room_options && hotel.room_options[0] ? hotel.room_options[0].name : (isRu ? 'Номер Deluxe' : 'Deluxe Suite');
  const fl = hotel.flight || currentFlight || lastFlight;
  let flightLine = isRu ? 'Прямой рейс туда и обратно включен в тур' : 'Direct Roundtrip Flight Included';
  if (fl) {
    flightLine = `${fl.airline} ${fl.flight_number_outbound} · ${fl.departure_airport}→${fl.arrival_airport} · ${fl.departure_date} (${fl.departure_time}) ➔ ${fl.return_date} (${fl.return_departure_time})`;
  }
  return [
    `🌴 *VoyageAI: ${hotel.hotel_name} ${stars}*`,
    `📍 ${hotel.country_city}`,
    `✈️ ${flightLine}`,
    `🏨 ${isRu ? 'Номер' : 'Suite'}: ${room}`,
    `💰 ${isRu ? 'Итого' : 'Total'}: ${moneyKzt.format(hotel.total_price_kzt)} ₸ (~$${moneyKzt.format(usdVal)})`,
    `🔗 VoyageAI Concierge — voyageai.kz`,
  ].join('\n');
}

function selectFlexibleDate(hotel, dateObj) {
  hotel.total_price_kzt = dateObj.total_kzt;
  hotel.total_price_usd = dateObj.total_usd;
  const isRu = currentLang === 'RU';

  if (hotel.flight) {
    hotel.flight.departure_date = dateObj.departure_date;
    hotel.flight.return_date = dateObj.return_date;
  }

  // Update pills active state and display text across all cards and modal
  document.querySelectorAll(`.flex-date-pill[data-hotel-id="${hotel.id}"]`).forEach((p) => {
    const isSelected = (p.dataset.dep === dateObj.departure_date);
    p.classList.toggle('active', isSelected);
    const strong = p.querySelector('strong');
    const base = p.dataset.baseLabel || formatShortDate(p.dataset.dep);
    if (strong && base) {
      strong.textContent = isSelected ? `${base} (${isRu ? 'Выбрано' : 'Selected'})` : base;
    }
  });

  const depShort = formatShortDate(dateObj.departure_date);
  const retShort = formatShortDate(dateObj.return_date);

  // Update dates in hotel card flight block (e.g. 13.10 – 20.10)
  const datesEl = document.getElementById(`flight-dates-${hotel.id}`);
  if (datesEl) {
    datesEl.textContent = ` (${depShort} – ${retShort})`;
  }

  // Update price in hotel card
  const priceKztEl = document.getElementById(`card-price-kzt-${hotel.id}`);
  if (priceKztEl) {
    priceKztEl.textContent = `${moneyKzt.format(dateObj.total_kzt)} ₸`;
  }
  const priceUsdEl = document.getElementById(`card-price-usd-${hotel.id}`);
  if (priceUsdEl) {
    priceUsdEl.textContent = `($${moneyKzt.format(dateObj.total_usd)})`;
  }

  // If modal is currently open for this hotel, update modal flight details and range
  if (activeHotel && String(activeHotel.id) === String(hotel.id)) {
    const content = getHotelModalContent();
    if (content) {
      const depTextEl = content.querySelector('[data-modal-flight-dep]');
      if (depTextEl && hotel.flight) {
        depTextEl.textContent = `🛫 ${hotel.flight.departure_city} (${hotel.flight.departure_airport}) ${hotel.flight.departure_time} ➔ ${hotel.flight.arrival_city} (${hotel.flight.arrival_airport}) ${hotel.flight.arrival_time} · ${dateObj.departure_date} (${depShort})`;
      }
      const retTextEl = content.querySelector('[data-modal-flight-ret]');
      if (retTextEl && hotel.flight) {
        retTextEl.textContent = `🔄 ${isRu ? 'Обратный рейс' : 'Return flight'}: ${hotel.flight.arrival_airport} ➔ ${hotel.flight.departure_airport} · ${dateObj.return_date} (${retShort}) (${hotel.flight.return_departure_time} ➔ ${hotel.flight.return_arrival_time})`;
      }
      const modalDatesEl = content.querySelector('[data-modal-flight-dates]');
      if (modalDatesEl) {
        modalDatesEl.textContent = ` (${depShort} – ${retShort})`;
      }
    }
    updateDetailTotal();
  }
}

// ── Hotel Card Component with Embedded Flight Ticket ─────────────────────────
function hotelCard(hotel, index) {
  const isRu = currentLang === 'RU';
  const t = TRANSLATIONS[currentLang];
  const usdVal = hotel.total_price_usd || Math.round(hotel.total_price_kzt / 500);
  const flight = hotel.flight || currentFlight || lastFlight;

  // Embedded flight block HTML
  let flightBlockHtml = '';
  if (flight) {
    const depShort = formatShortDate(flight.departure_date);
    const retShort = formatShortDate(flight.return_date);
    const datesSpan = depShort && retShort ? ` (${depShort} – ${retShort})` : '';
    const routeText = `✈️ ${t.flight_direct}: <b>${escapeHtml(flight.departure_airport)}</b> ➔ <b>${escapeHtml(flight.arrival_airport)}</b><span id="flight-dates-${escapeHtml(hotel.id)}">${datesSpan}</span>, ${t.flight_nonstop}`;
    const baggageText = isRu ? 'Багаж: 23 кг + 8 кг' : '23 kg + 8 kg';

    flightBlockHtml = `
      <div class="hotel-flight-card">
        <div class="hfc-header">
          <div class="hfc-airline">
            <span class="hfc-code">${escapeHtml(flight.airline_code || 'KC')}</span>
            <span class="hfc-name">${escapeHtml(flight.airline)} · ${escapeHtml(flight.aircraft || 'Airbus A321')}</span>
          </div>
          <span class="hfc-badge">${t.flight_included}</span>
        </div>
        <div class="hfc-route">
          <span class="hfc-route-text">${routeText}</span>
          <span class="hfc-duration">${escapeHtml(flight.duration || '4h 30m')}</span>
        </div>
        <div class="hfc-meta">
          <span>🛫 ${escapeHtml(flight.departure_time || '08:30')} ➔ 🛬 ${escapeHtml(flight.arrival_time || '11:45')}</span>
          <span>🧳 ${baggageText}</span>
        </div>
      </div>
    `;
  }

  // Interactive Flexible Dates in Card
  let flexDatesCardHtml = '';
  if (hotel.flexible_dates && hotel.flexible_dates.length) {
    flexDatesCardHtml = `
      <div class="card-flex-dates" data-card-hotel="${escapeHtml(hotel.id)}">
        <span class="cfd-label">${t.flex_dates_label || (isRu ? 'Соседние даты:' : 'Flexible dates:')}</span>
        <div class="cfd-pills">
          ${hotel.flexible_dates.map((fd) => {
            const isSelected = hotel.flight ? (fd.departure_date === hotel.flight.departure_date) : fd.is_base;
            const label = getFlexDateLabel(fd, isSelected, isRu);
            return `
              <button type="button" class="flex-date-pill ${isSelected ? 'active' : ''}"
                data-hotel-id="${escapeHtml(hotel.id)}"
                data-base-label="${escapeHtml(fd.date_label || formatShortDate(fd.departure_date))}"
                data-dep="${escapeHtml(fd.departure_date)}"
                data-ret="${escapeHtml(fd.return_date)}"
                data-kzt="${fd.total_kzt}"
                data-usd="${fd.total_usd}">
                <strong>${escapeHtml(label)}</strong>
                <span>${moneyKzt.format(fd.total_kzt)} ₸</span>
              </button>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }

  const guestBadgeText = translateGuestBadge(hotel.guests_badge, isRu);
  const highlightBadgeText = isRu ? (hotel.highlight_badge || '').replace('Highest Rating', 'Высокий рейтинг') : hotel.highlight_badge;

  return `
    <article class="hotel-card" style="--delay:${index * 80}ms">
      <div class="hotel-card-image">
        <img src="${escapeHtml(hotel.image_url)}" alt="${escapeHtml(hotel.hotel_name)}" loading="lazy">
        <span class="hotel-badge">${escapeHtml(highlightBadgeText)}</span>
        <span class="match-badge">${hotel.match_score}% Affinity</span>
        <span class="guest-badge">${escapeHtml(guestBadgeText)}</span>
      </div>
      <div class="hotel-card-body">
        <div class="hotel-card-heading">
          <div>
            <h3>${escapeHtml(hotel.hotel_name)}</h3>
            <p>${escapeHtml(hotel.country_city)} · ${hotel.stars}★ · ${escapeHtml(hotel.meal_type)}</p>
          </div>
          <div class="rating-badge">★ ${hotel.rating}</div>
        </div>

        <!-- Embedded Compact Flight Ticket -->
        ${flightBlockHtml}

        <!-- Interactive Flexible Dates in Card -->
        ${flexDatesCardHtml}

        <div class="price-box">
          <div class="price-main">
            <div>
              <strong id="card-price-kzt-${escapeHtml(hotel.id)}">${moneyKzt.format(hotel.total_price_kzt)} ₸</strong>
              <span class="price-usd" id="card-price-usd-${escapeHtml(hotel.id)}">($${moneyKzt.format(usdVal)})</span>
            </div>
            <small style="color:var(--green)">${t.instant_confirm}</small>
          </div>
          <div class="price-breakdown">${escapeHtml(hotel.price_breakdown || (isRu ? 'Прямой перелет и номер включены' : 'Roundtrip flights & verified suite included'))}</div>
        </div>

        <div class="card-actions">
          <button class="room-button btn-explore-details" type="button" data-action="explore-details" data-hotel-id="${escapeHtml(hotel.id)}">
            <span>${t.explore_suites}</span>
            <span>→</span>
          </button>
          <button class="wa-button" type="button" data-wa-id="${escapeHtml(hotel.id)}">${t.wa_share}</button>
        </div>
      </div>
    </article>
  `;
}

// ── Render Results ───────────────────────────────────────────────────────────
function renderResults(items, flight) {
  lastResults = items || [];
  if (flight) {
    lastFlight = flight;
    currentFlight = flight;
  }
  // Clear any old standalone flight container as requested
  if (flightContainer) {
    flightContainer.innerHTML = '';
  }

  const t = TRANSLATIONS[currentLang];

  if (!items || !items.length) {
    results.innerHTML = `
      <div class="empty-state">
        <strong>${escapeHtml(t.empty_heading)}</strong>
        <p>${escapeHtml(t.empty_sub)}</p>
      </div>`;
    resultCount.textContent = t.awaiting;
    return;
  }

  resultCount.textContent = t.results_found(items.length);
  results.innerHTML = items.map((h, idx) => hotelCard(h, idx)).join('');

  items.forEach((hotel) => {
    // Specifically target explore button using .btn-explore-details or .room-button
    const exploreBtn = results.querySelector(`.btn-explore-details[data-hotel-id="${CSS.escape(hotel.id)}"]`) ||
                       results.querySelector(`button.room-button[data-hotel-id="${CSS.escape(hotel.id)}"]`);
    if (exploreBtn) {
      exploreBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        openHotelModal(hotel);
      });
    }

    const waBtn = results.querySelector(`[data-wa-id="${CSS.escape(hotel.id)}"]`);
    if (waBtn) {
      waBtn.addEventListener('click', () => {
        const text = buildWhatsAppText(hotel);
        const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
        window.open(url, '_blank', 'noopener,noreferrer');
      });
    }

    const pills = results.querySelectorAll(`.card-flex-dates[data-card-hotel="${CSS.escape(hotel.id)}"] .flex-date-pill`);
    pills.forEach((pill) => {
      pill.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        selectFlexibleDate(hotel, {
          departure_date: pill.dataset.dep,
          return_date: pill.dataset.ret,
          total_kzt: Number(pill.dataset.kzt),
          total_usd: Number(pill.dataset.usd),
        });
      });
    });
  });
}

// ── Suite & Room Details Modal (Hotel Modal) ───────────────────────────────────
function openHotelModal(hotel) {
  if (!hotel) return;
  activeHotel = hotel;
  const isRu = currentLang === 'RU';
  const t = TRANSLATIONS[currentLang];
  const rooms = hotel.room_options || [];
  const firstRoom = rooms[0];
  selectedRoom = firstRoom;

  const modal = getHotelModal();
  const content = getHotelModalContent();
  if (!modal || !content) return;

  const gallery = hotel.gallery_images && hotel.gallery_images.length ? hotel.gallery_images : [hotel.image_url];
  const flight = hotel.flight || currentFlight || lastFlight;

  // Flight Box in Modal
  let flightModalHtml = '';
  if (flight) {
    const depShort = formatShortDate(flight.departure_date);
    const retShort = formatShortDate(flight.return_date);
    const datesSpan = depShort && retShort ? ` <span data-modal-flight-dates>(${depShort} – ${retShort})</span>` : '';
    const baggageText = isRu ? 'Багаж: 23 кг + 8 кг ручная кладь' : '23 kg check-in + 8 kg cabin';
    flightModalHtml = `
      <div class="modal-flight-box">
        <div class="modal-flight-box-title">
          <span>✈️ ${t.modal_flight_title}${datesSpan}</span>
          <span class="hfc-badge">${t.flight_included}</span>
        </div>
        <div style="display:flex;justify-content:space-between;color:var(--white);font-weight:600;margin-bottom:6px;font-size:0.88rem">
          <span>${escapeHtml(flight.airline)} (${escapeHtml(flight.airline_code)}) · ${escapeHtml(flight.aircraft)}</span>
          <span style="color:var(--cyan)">${escapeHtml(flight.duration)} (${t.flight_nonstop})</span>
        </div>
        <div style="font-size:0.8rem;color:var(--muted-light);display:flex;justify-content:space-between">
          <span data-modal-flight-dep>🛫 ${escapeHtml(flight.departure_city)} (${escapeHtml(flight.departure_airport)}) ${escapeHtml(flight.departure_time)} ➔ ${escapeHtml(flight.arrival_city)} (${escapeHtml(flight.arrival_airport)}) ${escapeHtml(flight.arrival_time)} · ${escapeHtml(flight.departure_date)} (${depShort})</span>
          <span>🧳 ${baggageText}</span>
        </div>
        <div style="font-size:0.75rem;color:var(--muted);margin-top:6px">
          <span data-modal-flight-ret>🔄 ${isRu ? 'Обратный рейс' : 'Return flight'}: ${escapeHtml(flight.arrival_airport)} ➔ ${escapeHtml(flight.departure_airport)} · ${escapeHtml(flight.return_date)} (${retShort}) (${escapeHtml(flight.return_departure_time)} ➔ ${escapeHtml(flight.return_arrival_time)})</span>
        </div>
      </div>
    `;
  }

  // Interactive Flexible Dates Box in Modal (TourVisor real calendar dates)
  let flexDatesHtml = '';
  if (hotel.flexible_dates && hotel.flexible_dates.length) {
    flexDatesHtml = `
      <div class="modal-flight-box" style="margin-top:10px">
        <div class="modal-flight-box-title">
          <span>🗓️ ${t.modal_flex_title}</span>
          <small style="color:var(--muted);font-weight:normal">${t.modal_flex_sub}</small>
        </div>
        <div class="modal-flex-dates">
          ${hotel.flexible_dates.map((f) => {
            const isSelected = hotel.flight ? (f.departure_date === hotel.flight.departure_date) : f.is_base;
            const label = getFlexDateLabel(f, isSelected, isRu);
            return `
              <button type="button" class="flex-date-pill ${isSelected ? 'active' : ''}"
                data-hotel-id="${escapeHtml(hotel.id)}"
                data-base-label="${escapeHtml(f.date_label || formatShortDate(f.departure_date))}"
                data-dep="${escapeHtml(f.departure_date)}"
                data-ret="${escapeHtml(f.return_date)}"
                data-kzt="${f.total_kzt}"
                data-usd="${f.total_usd}">
                <strong>${escapeHtml(label)}</strong>
                <span>${moneyKzt.format(f.total_kzt)} ₸</span>
              </button>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }

  const highlightBadgeText = isRu ? (hotel.highlight_badge || '').replace('Highest Rating', 'Высокий рейтинг') : hotel.highlight_badge;
  const specs = getHotelSpecs(hotel, isRu);

  content.innerHTML = `
    <div class="detail-head">
      <div>
        <span class="eyebrow cyan">${escapeHtml(highlightBadgeText)} · ${hotel.match_score}% Affinity</span>
        <h2>${escapeHtml(hotel.hotel_name)}</h2>
        <p>${escapeHtml(hotel.country_city)} · ${hotel.stars}★ · ${isRu ? 'Рейтинг' : 'Rated'} ${hotel.rating}/5 (${hotel.reviews_count} ${isRu ? 'отзывов' : 'reviews'})</p>
      </div>
      <button class="icon-button close-button" type="button" data-close-detail aria-label="Close">×</button>
    </div>
    <div class="detail-layout">
      <div>
        <div class="room-gallery">
          <img id="hotel-main-image" src="${escapeHtml(gallery[0])}" alt="${escapeHtml(hotel.hotel_name)}">
          <div class="gallery-thumbs">
            ${gallery.map((img, i) => `
              <button type="button" class="gallery-thumb ${i === 0 ? 'active' : ''}" data-gallery-img="${escapeHtml(img)}">
                <img src="${escapeHtml(img)}" alt="Gallery image ${i + 1}">
              </button>
            `).join('')}
          </div>
        </div>

        <!-- Integrated Flight & Flexible Dates in Modal -->
        ${flightModalHtml}
        ${flexDatesHtml}

        <p class="detail-summary" style="margin-top:16px">${escapeHtml(hotel.summary)}</p>
        <div style="background:rgba(15,23,42,0.5);border:1px solid var(--line);border-radius:12px;padding:14px;margin-top:14px">
          <strong style="font-size:0.88rem;color:var(--white);display:block;margin-bottom:6px">${t.modal_curator_highlights}</strong>
          <ul style="margin:0;padding-left:18px;font-size:0.8rem;color:var(--muted-light);line-height:1.5">
            ${(hotel.pros || []).map((p) => `<li>${escapeHtml(p)}</li>`).join('')}
          </ul>
        </div>
      </div>

      <div>
        <!-- TourVisor Hotel Specification Grid -->
        <div class="hotel-spec-grid">
          <div class="hotel-spec-card">
            <span class="hotel-spec-title">🏖️ ${t.spec_beach || (isRu ? 'Пляж' : 'Beach')}</span>
            <span class="hotel-spec-desc">${escapeHtml(specs.beach)}</span>
          </div>
          <div class="hotel-spec-card">
            <span class="hotel-spec-title">🍽️ ${t.spec_board || (isRu ? 'Питание' : 'Meal Plan')}</span>
            <span class="hotel-spec-desc">${escapeHtml(specs.board)}</span>
          </div>
          <div class="hotel-spec-card">
            <span class="hotel-spec-title">🛏️ ${t.spec_in_room || (isRu ? 'В номере' : 'In Room')}</span>
            <span class="hotel-spec-desc">${escapeHtml(specs.in_room)}</span>
          </div>
          <div class="hotel-spec-card">
            <span class="hotel-spec-title">👶 ${t.spec_children || (isRu ? 'Для детей' : 'For Children')}</span>
            <span class="hotel-spec-desc">${escapeHtml(specs.children)}</span>
          </div>
          <div class="hotel-spec-card" style="grid-column: 1 / -1">
            <span class="hotel-spec-title">🏛️ ${t.spec_territory || (isRu ? 'Территория' : 'Hotel Grounds')}</span>
            <span class="hotel-spec-desc">${escapeHtml(specs.territory)}</span>
          </div>
        </div>

        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
          <h3 style="font-size:1.2rem">${t.modal_rooms_title}</h3>
          <span style="font-size:0.75rem;color:var(--cyan)">${rooms.length} ${t.modal_categories}</span>
        </div>
        <div class="room-list">
          ${rooms.map((room, idx) => roomOption(room, idx, firstRoom && room.id === firstRoom.id, isRu)).join('')}
        </div>
      </div>
    </div>
    <div class="detail-footer">
      <div>
        <small style="color:var(--muted);display:block">${t.modal_total_label}</small>
        <strong data-detail-total></strong>
      </div>
      <button class="primary-cta" type="button" data-book-detail>
        ${t.modal_reserve_btn} <span>→</span>
      </button>
    </div>
  `;

  modal.classList.remove('hidden');
  modal.classList.add('is-open', 'active', 'open');
  modal.style.display = 'flex';
  bindDetailEvents();
}

function closeHotelModal() {
  const modal = getHotelModal();
  if (modal) {
    modal.classList.remove('is-open', 'active', 'open');
    modal.classList.add('hidden');
    modal.style.display = 'none';
  }
}

const openRoomDetails = openHotelModal;
const closeRoomDetails = closeHotelModal;
window.openHotelModal = openHotelModal;
window.closeHotelModal = closeHotelModal;
window.openRoomDetails = openHotelModal;
window.closeRoomDetails = closeHotelModal;

function roomOption(room, index, selected, isRu) {
  const inc = (room.amenities_included || []).map(
    (a) => `<li class="room-amenity included"><span class="amenity-icon">✓</span>${escapeHtml(translateAmenity(a, isRu))}</li>`
  ).join('');

  const exc = (room.amenities_excluded || []).map(
    (a) => `<li class="room-amenity excluded"><span class="amenity-icon">✗</span>${escapeHtml(translateAmenity(a, isRu))} <em>(${isRu ? 'не включено' : 'not included'})</em></li>`
  ).join('');

  const deltaText = room.price_delta_kzt
    ? `+${moneyKzt.format(room.price_delta_kzt)} ₸`
    : (isRu ? 'Базовый тариф' : 'Standard Rate');

  const capacityText = formatCapacity(room.capacity, isRu);
  const bedTypeText = formatBedType(room.bed_type, isRu);
  const descriptionText = getRoomDescription(room, isRu);

  return `
    <button type="button" class="room-option ${selected ? 'selected' : ''}" data-room-index="${index}">
      <div class="room-option-main">
        <div style="display:flex;justify-content:space-between;align-items:baseline">
          <strong class="room-name">${escapeHtml(room.name)}</strong>
          <span class="room-price">${escapeHtml(deltaText)}</span>
        </div>
        <span class="room-meta">${room.sqm} m² · ${escapeHtml(bedTypeText)} · ${escapeHtml(capacityText)}</span>
        <span class="room-desc">${escapeHtml(descriptionText)}</span>
        <ul class="room-amenity-list">
          ${inc}
          ${exc}
        </ul>
      </div>
    </button>
  `;
}

function bindDetailEvents() {
  const content = getHotelModalContent();
  if (!content) return;

  content.querySelectorAll('[data-close-detail], .close-button').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      closeHotelModal();
    });
  });

  content.querySelectorAll('.gallery-thumb').forEach((thumb) => {
    thumb.addEventListener('click', () => {
      const mainImg = content.querySelector('#hotel-main-image');
      if (mainImg) mainImg.src = thumb.dataset.galleryImg;
      content.querySelectorAll('.gallery-thumb').forEach((t) => t.classList.remove('active'));
      thumb.classList.add('active');
    });
  });

  content.querySelectorAll('.room-option').forEach((opt) => {
    opt.addEventListener('click', () => {
      const idx = Number(opt.dataset.roomIndex);
      if (activeHotel && activeHotel.room_options && activeHotel.room_options[idx]) {
        selectedRoom = activeHotel.room_options[idx];
      }
      content.querySelectorAll('.room-option').forEach((o) => o.classList.remove('selected'));
      opt.classList.add('selected');
      updateDetailTotal();
    });
  });

  content.querySelectorAll('.modal-flex-dates .flex-date-pill').forEach((pill) => {
    pill.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      selectFlexibleDate(activeHotel, {
        departure_date: pill.dataset.dep,
        return_date: pill.dataset.ret,
        total_kzt: Number(pill.dataset.kzt),
        total_usd: Number(pill.dataset.usd),
      });
    });
  });

  const bookBtn = content.querySelector('[data-book-detail]');
  if (bookBtn) {
    bookBtn.addEventListener('click', () => {
      openBooking(activeHotel, selectedRoom);
    });
  }

  updateDetailTotal();
}

function updateDetailTotal() {
  const content = getHotelModalContent();
  if (!content) return;
  const totalEl = content.querySelector('[data-detail-total]');
  if (totalEl && activeHotel && selectedRoom) {
    const totalKzt = activeHotel.total_price_kzt + (selectedRoom.price_delta_kzt || 0);
    const totalUsd = Math.round(totalKzt / 500);
    totalEl.textContent = `${moneyKzt.format(totalKzt)} ₸ ($${moneyKzt.format(totalUsd)} USD)`;
  }
}

// ── VIP Booking Flow ─────────────────────────────────────────────────────────
function openBooking(hotel, room) {
  activeHotel = hotel;
  selectedRoom = room;
  closeHotelModal();
  const isRu = currentLang === 'RU';

  const totalKzt = hotel.total_price_kzt + (room.price_delta_kzt || 0);
  const totalUsd = Math.round(totalKzt / 500);

  const fl = hotel.flight || currentFlight || lastFlight;
  const flightDetails = fl
    ? (isRu
        ? `Рейс: ${fl.airline} (${fl.departure_airport} ➔ ${fl.arrival_airport}) · ${fl.departure_date} – ${fl.return_date}`
        : `Flight: ${fl.airline} (${fl.departure_airport} ➔ ${fl.arrival_airport}) · ${fl.departure_date} – ${fl.return_date}`)
    : (isRu ? 'Прямой рейс включен в тур' : 'Direct Roundtrip Flight Included');

  document.getElementById('booking-summary').innerHTML = `
    <strong>${escapeHtml(hotel.hotel_name)}</strong><br>
    ${isRu ? 'Выбранный номер:' : 'Selected Suite:'} <em>${escapeHtml(room.name)}</em><br>
    ${escapeHtml(flightDetails)}<br>
    ${isRu ? 'Итоговая стоимость тура:' : 'Total Package:'} <span style="color:var(--cyan);font-weight:700">${moneyKzt.format(totalKzt)} ₸ ($${moneyKzt.format(totalUsd)} USD)</span>
  `;

  document.getElementById('booking-form-view').classList.remove('hidden');
  document.getElementById('booking-success').classList.add('hidden');
  bookingModal.classList.remove('hidden');
  bookingModal.classList.add('is-open');
}

function closeBooking() {
  if (bookingModal) {
    bookingModal.classList.remove('is-open');
    bookingModal.classList.add('hidden');
  }
}

// ── Chat Messaging Loop ──────────────────────────────────────────────────────
async function sendMessage(message) {
  const cleanMessage = message.trim();
  if (!cleanMessage) return;
  const isRu = (currentLang || 'EN').toUpperCase() === 'RU';
  const t = TRANSLATIONS[currentLang];
  addMessage('user', cleanMessage);
  input.value = '';
  resultCount.textContent = t.analyzing;

  try {
    const res = await fetch('/api/agent/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: cleanMessage,
        session_id: sessionId,
        lang: isRu ? 'ru' : 'en',
      }),
    });
    const data = await res.json();
    if (data.reply) {
      addMessage('assistant', data.reply);
    }
    renderPrompts(data.prompts);

    if (data.state === 'COMPLETE') {
      renderResults(data.results || [], data.flight);
      addMessage('assistant', t.complete_msg);
      if (showResultsButton) showResultsButton.classList.remove('hidden');
    }
  } catch (err) {
    addMessage('assistant', t.error_msg);
  }
}

// ── Event Bindings ───────────────────────────────────────────────────────────
if (searchForm) {
  searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage(input.value);
  });
}

const modalCloseBtn = document.getElementById('modal-close');
if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeBooking);

const successCloseBtn = document.getElementById('success-close');
if (successCloseBtn) successCloseBtn.addEventListener('click', closeBooking);

if (bookingModal) {
  bookingModal.addEventListener('click', (e) => {
    if (e.target === bookingModal) closeBooking();
  });
}

const modalEl = getHotelModal();
if (modalEl) {
  modalEl.addEventListener('click', (e) => {
    if (e.target === modalEl) closeHotelModal();
  });
}

// Delegation on results container for reliable modal triggers
if (results) {
  results.addEventListener('click', (e) => {
    const exploreBtn = e.target.closest('.btn-explore-details, .room-button, [data-action="explore-details"]');
    if (exploreBtn) {
      const hotelId = exploreBtn.dataset.hotelId || exploreBtn.getAttribute('data-hotel-id');
      const hotel = (lastResults || []).find((h) => String(h.id) === String(hotelId));
      if (hotel) {
        e.preventDefault();
        e.stopPropagation();
        openHotelModal(hotel);
      }
    }
  });
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeBooking();
    closeHotelModal();
  }
});

// Phone formatting
const phoneInput = document.getElementById('guest-phone');
if (phoneInput) {
  phoneInput.addEventListener('input', (e) => {
    const digits = e.target.value.replace(/\D/g, '');
    if (digits.startsWith('7') || digits.startsWith('8')) {
      let r = '+7';
      if (digits.length > 1) r += ` ${digits.slice(1, 4)}`;
      if (digits.length > 4) r += ` ${digits.slice(4, 7)}`;
      if (digits.length > 7) r += ` ${digits.slice(7, 9)}`;
      if (digits.length > 9) r += ` ${digits.slice(9, 11)}`;
      e.target.value = r;
    }
  });
}

const bookingForm = document.getElementById('booking-form');
if (bookingForm) {
  bookingForm.addEventListener('submit', (e) => {
    e.preventDefault();
    document.getElementById('booking-form-view').classList.add('hidden');
    document.getElementById('booking-success').classList.remove('hidden');
  });
}

// Ping agent on load to synchronize seasonal prompts
fetch('/api/agent/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: '',
    session_id: sessionId,
    lang: ((currentLang || 'EN').toUpperCase() === 'RU') ? 'ru' : 'en',
  }),
})
  .then((r) => r.json())
  .then((d) => {
    if (d && d.prompts) renderPrompts(d.prompts);
  })
  .catch(() => {});

// Initialize application language
setLanguage(currentLang);
