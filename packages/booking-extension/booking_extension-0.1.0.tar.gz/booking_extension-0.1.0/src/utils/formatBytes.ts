export function formatBytes(bytes: number) {
  if (bytes < 0) {
    throw new Error('Bytes value must be non-negative');
  }

  const units = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const threshold = 1024;

  if (bytes < threshold) {
    return `${bytes} ${units[0]}`;
  }

  let unitIndex = 0;
  while (bytes >= threshold && unitIndex < units.length - 1) {
    bytes /= threshold;
    unitIndex++;
  }

  // Round to 2 decimal places and remove trailing .00 if needed
  const formattedValue =
    bytes % 1 === 0 ? bytes.toString() : bytes.toFixed(2).replace(/\.?0+$/, '');

  return `${formattedValue} ${units[unitIndex]}`;
}
