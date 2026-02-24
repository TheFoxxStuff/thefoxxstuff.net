/**
 * Smart Date Indication
 * Returns gradient & icon color info based on how recent the date is.
 */

export function getDateColorInfo(dateStr) {
  const now = new Date();
  const date = new Date(dateStr);
  const diffMs = now - date;
  const diffDays = diffMs / (1000 * 60 * 60 * 24);

  if (diffDays < 2) {
    // Up to 2 days — lime → teal
    return {
      gradient: 'linear-gradient(90deg, #BCFF00, #45D0C1)',
      iconColor: '#BCFF00',
      label: 'fresh'
    };
  } else if (diffDays < 14) {
    if (diffDays < 6) {
      // 2–6 days — teal → purple
      return {
        gradient: 'linear-gradient(90deg, #00CED1, #91219E)',
        iconColor: '#00CED1',
        label: 'recent'
      };
    } else {
      // 6 days – 2 weeks — teal → purple (same range as spec)
      return {
        gradient: 'linear-gradient(90deg, #00CED1, #91219E)',
        iconColor: '#00CED1',
        label: 'recent'
      };
    }
  } else if (diffDays < 30) {
    // 2–4 weeks — bright pink → purple
    return {
      gradient: 'linear-gradient(90deg, #FF2D78, #8B00FF)',
      iconColor: '#FF2D78',
      label: 'weeks'
    };
  } else {
    // Older — neutral gray
    return {
      gradient: null,
      iconColor: '#808080',
      label: 'old'
    };
  }
}
