/**
 * Smart Date Indication — continuous color timeline
 *
 * Вместо жёстких диапазонов — один мастер-градиент по оси времени.
 * Пост "едет" по нему: чем старше, тем дальше сдвигается "окно" цветов.
 *
 * Мастер-ось (день → цвет):
 *   0  дней  →  #BCFF00  (салатовый)
 *   2  дня   →  #45D0C1  (светлая бирюза)
 *   6  дней  →  #00CED1  (насыщенная бирюза)
 *   14 дней  →  #91219E  (фиолетовый)
 *   21 день  →  #FF2D78  (ярко-розовый)
 *   28 дней  →  #8B00FF  (глубокий фиолет)
 *   40 дней  →  #808080  (серый, финал)
 */

// Keyframes: [dayThreshold, [r, g, b]]
const TIMELINE = [
  [0,  [188, 255,   0]],   // #BCFF00 — lime
  [2,  [ 69, 208, 193]],   // #45D0C1 — light teal
  [6,  [  0, 206, 209]],   // #00CED1 — dark teal
  [14, [145,  33, 158]],   // #91219E — purple
  [21, [255,  45, 120]],   // #FF2D78 — hot pink
  [28, [139,   0, 255]],   // #8B00FF — deep violet
  [40, [128, 128, 128]],   // #808080 — neutral gray
];

/** Линейно интерполирует число */
function lerp(a, b, t) {
  return a + (b - a) * t;
}

/** Интерполирует [r,g,b] между двумя соседними keyframe по оси дней */
function colorAtDay(days) {
  // Зажимаем на последнем keyframe
  if (days >= TIMELINE[TIMELINE.length - 1][0]) {
    return TIMELINE[TIMELINE.length - 1][1];
  }
  if (days <= 0) {
    return TIMELINE[0][1];
  }

  for (let i = 0; i < TIMELINE.length - 1; i++) {
    const [d0, c0] = TIMELINE[i];
    const [d1, c1] = TIMELINE[i + 1];

    if (days >= d0 && days < d1) {
      const t = (days - d0) / (d1 - d0);  // 0..1 внутри сегмента
      return [
        Math.round(lerp(c0[0], c1[0], t)),
        Math.round(lerp(c0[1], c1[1], t)),
        Math.round(lerp(c0[2], c1[2], t)),
      ];
    }
  }

  return TIMELINE[TIMELINE.length - 1][1];
}

/** RGB массив → hex строка */
function toHex([r, g, b]) {
  return '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('');
}

/**
 * Возвращает { gradient, iconColor } для поста.
 *
 * "Окно" градиента — это отрезок [days, days + window] на мастер-оси.
 * Чем старше пост, тем дальше оба цвета сдвинулись по спектру.
 * При diffDays > 40 — статичный серый (градиент не нужен).
 */
export function getDateColorInfo(dateStr) {
  const now = new Date();
  const diffDays = (now - new Date(dateStr)) / (1000 * 60 * 60 * 24);

  // После 40 дней — нейтральный серый
  if (diffDays >= 40) {
    return {
      gradient: null,
      iconColor: '#808080',
      label: 'old',
    };
  }

  // "Ширина окна" градиента — фиксированная в днях.
  // Позволяет видеть плавный переход вокруг текущей позиции.
  const WINDOW = 8;

  const startDay = Math.max(0, diffDays - WINDOW / 2);
  const endDay   = Math.min(39, diffDays + WINDOW / 2);

  const colorStart = toHex(colorAtDay(startDay));
  const colorEnd   = toHex(colorAtDay(endDay));

  // Иконка — цвет левого края градиента (startDay)
  const iconColor = colorStart;

  const label =
    diffDays < 2  ? 'fresh'  :
    diffDays < 14 ? 'recent' :
    diffDays < 28 ? 'weeks'  : 'fading';

  return {
    gradient: `linear-gradient(90deg, ${colorStart}, ${colorEnd})`,
    iconColor,
    label,
  };
}
