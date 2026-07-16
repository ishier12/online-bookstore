/** 格式化价格 */
export function formatPrice(price: number): string {
  return `¥${price.toFixed(2)}`;
}

/** 格式化日期（只显示年月日） */
export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
}

/** 截断字符串 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}
