export const formatCurrency = (paise) => {
  if (paise === null || paise === undefined) return '₹0.00';
  const inr = paise / 100;
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
  }).format(inr);
};

export const formatDistance = (meters) => {
  if (!meters && meters !== 0) return '';
  if (meters < 1000) {
    return `${Math.round(meters)} m`;
  }
  return `${(meters / 1000).toFixed(1)} km`;
};

export const formatDateTime = (dateStr) => {
  if (!dateStr) return '';
  try {
    const d = new Date(dateStr);
    return d.toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
};

export const formatDuration = (mins) => {
  if (!mins) return '';
  const hrs = Math.floor(mins / 60);
  const remainingMins = mins % 60;
  if (hrs > 0 && remainingMins > 0) return `${hrs}h ${remainingMins}m`;
  if (hrs > 0) return `${hrs} hr${hrs > 1 ? 's' : ''}`;
  return `${remainingMins} mins`;
};
