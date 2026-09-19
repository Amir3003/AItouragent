const searchForm = document.getElementById('search-form');
const messages = document.getElementById('agent-messages');
const input = document.getElementById('user-input');
const quickPrompts = document.getElementById('quick-prompts');
const results = document.getElementById('results');
const resultCount = document.getElementById('results-count');
const bookingModal = document.getElementById('booking-modal');
const detailModal = document.getElementById('room-detail-modal');
const detailContent = document.getElementById('room-detail-content');
const hotelCounter = document.getElementById('hero-hotels-count');
const showResultsButton = document.getElementById('show-results-button');
const sessionId = getSessionId();
let activeHotel = null;
let selectedRoom = null;

if (hotelCounter) {
  fetch('/api/v1/meta')
    .then((response) => response.json())
    .then((meta) => {
      if (meta && typeof meta.hotels_total === 'number') {
        hotelCounter.textContent = meta.hotels_total;
      }
    })
    .catch(() => {});
}

const money = new Intl.NumberFormat('ru-RU');
const ACKNOWLEDGEMENT = 'Собираю вариант по вашему запросу...';

if (showResultsButton) {
  showResultsButton.addEventListener('click', () => {
    document.querySelector('.results-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

function getSessionId() {
  const key = 'zari-travel-session';
  const current = window.sessionStorage.getItem(key);
  if (current) return current;
  const created = `web-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  window.sessionStorage.setItem(key, created);
  return created;
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

function addMessage(role, text) {
  const item = document.createElement('div');
  item.className = `agent-message ${role}`;
  item.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
  messages.appendChild(item);
  messages.scrollTop = messages.scrollHeight;
}

function showAcknowledgement() {
  addMessage('assistant', ACKNOWLEDGEMENT);
}

function renderPrompts(prompts) {
  quickPrompts.innerHTML = (prompts || []).slice(0, 4).map((prompt) => `
    <button class="prompt-chip" type="button" data-prompt="${escapeHtml(prompt)}">${escapeHtml(prompt)}</button>
  `).join('');
  quickPrompts.querySelectorAll('[data-prompt]').forEach((chip) => {
    chip.addEventListener('click', () => {
      input.value = chip.dataset.prompt;
      document.getElementById('ai-chat-section').scrollIntoView({ behavior: 'smooth', block: 'center' });
      sendMessage(chip.dataset.prompt);
    });
  });
}

function showResultsHint() {
  if (showResultsButton) showResultsButton.classList.remove('hidden');
}

function hotelCard(hotel, index) {
  return `<article class="hotel-card" style="--delay:${index * 70}ms">
    <div class="hotel-card-image"><img src="${escapeHtml(hotel.image_url)}" alt="${escapeHtml(hotel.hotel_name)}" loading="lazy"><span class="hotel-badge">${escapeHtml(hotel.highlight_badge)}</span><span class="match-badge">${hotel.match_score}% совпадение</span></div>
    <div class="hotel-card-body"><div class="hotel-card-heading"><div><h3>${escapeHtml(hotel.hotel_name)}</h3><p>${escapeHtml(hotel.country_city)} · ${hotel.stars}★ · ${escapeHtml(hotel.meal_type)}</p></div><div class="rating-badge">★ ${hotel.rating}</div></div>
    <div class="hotel-meta"><span>от ${money.format(hotel.total_price_kzt)} ₸</span><small>${escapeHtml(hotel.seats_hotel)}</small></div>
    <button class="room-button" type="button" data-hotel-id="${escapeHtml(hotel.id)}">Посмотреть варианты номеров <span>→</span></button></div>
  </article>`;
}

function renderResults(items) {
  if (!items.length) {
    results.innerHTML = '<div class="empty-state"><strong>Подходящих вариантов не найдено</strong><p>Попробуем расширить бюджет или выбрать другой курорт.</p></div>';
    resultCount.textContent = '0 вариантов';
    return;
  }
  resultCount.textContent = 'Топ-5 подобрано';
  results.innerHTML = items.map(hotelCard).join('');
  items.forEach((hotel) => {
    const button = results.querySelector(`[data-hotel-id="${CSS.escape(hotel.id)}"]`);
    button.addEventListener('click', () => openRoomDetails(hotel));
  });
}

function openRoomDetails(hotel) {
  activeHotel = hotel;
  const rooms = hotel.room_options || [];
  const firstAvailable = rooms.find((room) => room.availability === 'Есть места') || rooms[0];
  selectedRoom = firstAvailable;
  detailContent.innerHTML = `<div class="detail-head"><div><span class="eyebrow">${escapeHtml(hotel.highlight_badge)}</span><h2>${escapeHtml(hotel.hotel_name)}</h2><p>${escapeHtml(hotel.country_city)} · ${hotel.stars}★ · ${hotel.rating}/5</p></div><button class="icon-button" type="button" data-close-detail aria-label="Закрыть">×</button></div>
    <div class="detail-layout"><div class="room-gallery"><img id="room-main-image" src="${escapeHtml(firstAvailable.images[0])}" alt="${escapeHtml(firstAvailable.name)}"><div class="gallery-thumbs">${firstAvailable.images.map((image, index) => `<button type="button" class="gallery-thumb ${index === 0 ? 'active' : ''}" data-image="${escapeHtml(image)}"><img src="${escapeHtml(image)}" alt="Фото номера ${index + 1}"></button>`).join('')}</div></div>
    <div><p class="detail-summary">${escapeHtml(hotel.summary)}</p><div class="room-list">${rooms.map((room, index) => roomOption(room, index, room.id === firstAvailable.id)).join('')}</div></div></div>`;
  detailModal.classList.remove('hidden');
  detailModal.classList.add('is-open');
  bindDetailEvents();
}

function roomOption(room, index, selected) {
  const available = room.availability === 'Есть места';
  const included = (room.amenities_included || []).slice(0, 4).map((item) => `<span class="room-tag included">+ ${escapeHtml(item)}</span>`).join('');
  const excluded = (room.amenities_excluded || []).slice(0, 2).map((item) => `<span class="room-tag excluded">− ${escapeHtml(item)}</span>`).join('');
  const vip = room.vip_privileges?.length ? `<small class="room-vip">👑 ${escapeHtml(room.vip_privileges.join(' · '))}</small>` : '';
  return `<button type="button" class="room-option ${selected ? 'selected' : ''} ${available ? '' : 'unavailable'}" data-room-index="${index}" ${available ? '' : 'disabled'}><span><strong>${escapeHtml(room.name)}</strong><small>${room.sqm} м² · ${escapeHtml(room.capacity)}</small><small>${available ? 'Есть места' : 'Нет мест'}</small><span class="room-tags">${included}${excluded}</span>${vip}</span><b>${room.price_delta_kzt ? `+${money.format(room.price_delta_kzt)} ₸` : 'База'}</b></button>`;
}

function bindDetailEvents() {
  detailContent.querySelector('[data-close-detail]').addEventListener('click', closeRoomDetails);
  detailContent.querySelectorAll('.gallery-thumb').forEach((thumb) => thumb.addEventListener('click', () => {
    detailContent.querySelector('#room-main-image').src = thumb.dataset.image;
    detailContent.querySelectorAll('.gallery-thumb').forEach((item) => item.classList.remove('active'));
    thumb.classList.add('active');
  }));
  detailContent.querySelectorAll('.room-option:not([disabled])').forEach((option) => option.addEventListener('click', () => {
    selectedRoom = activeHotel.room_options[Number(option.dataset.roomIndex)];
    detailContent.querySelectorAll('.room-option').forEach((item) => item.classList.remove('selected'));
    option.classList.add('selected');
    const image = selectedRoom.images[0];
    detailContent.querySelector('#room-main-image').src = image;
    detailContent.querySelectorAll('.gallery-thumb').forEach((thumb, index) => {
      thumb.querySelector('img').src = selectedRoom.images[index];
      thumb.dataset.image = selectedRoom.images[index];
      thumb.classList.toggle('active', index === 0);
    });
    updateDetailTotal();
  }));
  detailContent.insertAdjacentHTML('beforeend', '<div class="detail-footer"><div><small>Итоговая цена</small><strong data-detail-total></strong></div><button class="primary-cta" type="button" data-book-detail>Забронировать тур</button></div>');
  updateDetailTotal();
  detailContent.querySelector('[data-book-detail]').addEventListener('click', () => openBooking(activeHotel, selectedRoom));
}

function updateDetailTotal() {
  const total = detailContent.querySelector('[data-detail-total]');
  if (total && activeHotel && selectedRoom) {
    total.textContent = `${money.format(activeHotel.total_price_kzt + selectedRoom.price_delta_kzt)} ₸`;
  }
}

function closeRoomDetails() {
  detailModal.classList.remove('is-open');
  detailModal.classList.add('hidden');
}

function openBooking(hotel, room) {
  activeHotel = hotel;
  selectedRoom = room;
  closeRoomDetails();
  document.getElementById('booking-summary').textContent = `${hotel.hotel_name} · ${room.name} · ${money.format(hotel.total_price_kzt + room.price_delta_kzt)} ₸`;
  document.getElementById('booking-form-view').classList.remove('hidden');
  document.getElementById('booking-success').classList.add('hidden');
  bookingModal.classList.remove('hidden');
  bookingModal.classList.add('is-open');
}

function closeBooking() {
  bookingModal.classList.remove('is-open');
  bookingModal.classList.add('hidden');
}

async function sendMessage(message) {
  const cleanMessage = message.trim();
  if (!cleanMessage) return;
  addMessage('user', cleanMessage);
  input.value = '';
  resultCount.textContent = 'Анализирую предложения...';
  try {
    const response = await fetch('/api/agent/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: cleanMessage, session_id: sessionId }) });
    const data = await response.json();
    if (data.reply) {
      addMessage('assistant', data.reply);
    }
    renderPrompts(data.prompts);
    if (data.state === 'COMPLETE') {
      renderResults(data.results || []);
      addMessage('assistant', 'Ниже — подборка из 5 лучших вариантов. Сравните отели и выберите подходящий.');
      showResultsHint();
    }
  } catch (error) {
    addMessage('assistant', 'Сервис временно недоступен. Попробуйте отправить запрос ещё раз.');
  }
}

searchForm.addEventListener('submit', (event) => { event.preventDefault(); sendMessage(input.value); });
document.getElementById('modal-close').addEventListener('click', closeBooking);
document.getElementById('success-close').addEventListener('click', closeBooking);
bookingModal.addEventListener('click', (event) => { if (event.target === bookingModal) closeBooking(); });
detailModal.addEventListener('click', (event) => { if (event.target === detailModal) closeRoomDetails(); });
document.addEventListener('keydown', (event) => { if (event.key === 'Escape') { closeBooking(); closeRoomDetails(); } });
document.getElementById('guest-phone').addEventListener('input', (event) => {
  const digits = event.target.value.replace(/\D/g, '').replace(/^8/, '7').slice(0, 11);
  let result = '+7';
  if (digits.length > 1) result += ` ${digits.slice(1, 4)}`;
  if (digits.length > 4) result += ` ${digits.slice(4, 7)}`;
  if (digits.length > 7) result += ` ${digits.slice(7, 9)}`;
  if (digits.length > 9) result += ` ${digits.slice(9, 11)}`;
  event.target.value = result;
});
document.getElementById('booking-form').addEventListener('submit', (event) => {
  event.preventDefault();
  if (document.getElementById('guest-phone').value.replace(/\D/g, '').length < 11) {
    document.getElementById('booking-error').textContent = 'Введите полный номер WhatsApp.';
    document.getElementById('booking-error').classList.remove('hidden');
    return;
  }
  document.getElementById('booking-form-view').classList.add('hidden');
  document.getElementById('booking-success').classList.remove('hidden');
});

renderPrompts([
  'Семейный тур в Турции из Астаны с 2026-10-10 на 7 ночей: 2 взрослых, ребенок 4 года, до 1 400 000 ₸',
  'Тихий отдых в Египте из Астаны с 2026-10-10 на 7 ночей: 2 взрослых, ребенок 4 года, до 1 200 000 ₸',
  'Премиум отдых в ОАЭ из Алматы с 2026-10-10 на 7 ночей: 2 взрослых, ребенок 8 лет, 5 звезд, до 2 000 000 ₸',
  'Отдых в Турции из Астаны с 2026-10-10 на 9 ночей: 2 взрослых, ребенок 6 лет, до 1 500 000 ₸'
]);
fetch('/api/agent/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: '', session_id: sessionId }) }).then((response) => response.json()).then((data) => renderPrompts(data.prompts)).catch(() => {});
