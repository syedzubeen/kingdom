const timelineSteps = document.querySelectorAll('.timeline-step');
function markProgress(count) { timelineSteps.forEach((step, index) => step.classList.toggle('active', index < count)); }
const scrollExplore = document.querySelector('.scroll-mark');
scrollExplore?.addEventListener('click', () => document.querySelector('#artifactShowcase')?.scrollIntoView({behavior: 'smooth'}));
const showcase = document.querySelector('#artifactShowcase');
const showcaseCards = document.querySelectorAll('.showcase-card');
window.addEventListener('scroll', () => { const progress = window.scrollY - (showcase?.offsetTop || 0); showcaseCards.forEach((card, index) => card.style.setProperty('--parallax', `${Math.max(-42, Math.min(42, progress * (index % 2 ? -0.055 : 0.04)))}px`)); }, {passive: true});

document.querySelector('#generateButton').addEventListener('click', () => {
  markProgress(2);
  setTimeout(() => markProgress(3), 950);
});

document.querySelector('#copyDeployCommand').addEventListener('click', () => {
  navigator.clipboard?.writeText('docker compose up --build').catch(() => {});
  showToast('Deployment command copied');
});

document.querySelector('#regenerateButton').addEventListener('click', () => {
  const button = document.querySelector('#regenerateButton');
  button.textContent = 'REGENERATING ◌';
  markProgress(2);
  setTimeout(() => { button.textContent = 'REGENERATE ↻'; markProgress(3); showToast(`${document.querySelector('#artifactTitle').textContent} regenerated`); }, 800);
});

document.querySelector('#explainButton').addEventListener('click', () => {
  const artifact = artifacts.find((item) => item.name === document.querySelector('#artifactTitle').textContent);
  showToast(artifact ? artifact.desc : 'This artifact is derived from repository analysis.');
});

document.querySelector('#downloadAllButton').addEventListener('click', () => {
  const entries = artifacts.map((artifact) => ({name: artifact.name.replaceAll('\\', '/'), content: artifact.code}));
  entries.push({name: 'analysis.json', content: JSON.stringify({language: 'Go', framework: 'net/http', port: 8080, healthEndpoint: '/health'}, null, 2)});
  const url = URL.createObjectURL(createZip(entries));
  const link = document.createElement('a');
  link.href = url;
  link.download = 'kingdom-deployment-kit.zip';
  link.click();
  URL.revokeObjectURL(url);
  showToast('Deployment kit downloaded');
});

// Minimal dependency-free ZIP writer. Files are stored without compression so
// the static Vercel UI can create a real archive without a package install.
function crc32(bytes) { let crc = 0xffffffff; for (const byte of bytes) { crc ^= byte; for (let bit = 0; bit < 8; bit += 1) crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0); } return (crc ^ 0xffffffff) >>> 0; }
function createZip(entries) {
  const encoder = new TextEncoder();
  const files = [];
  const central = [];
  let offset = 0;
  entries.forEach(({name, content}) => {
    const nameBytes = encoder.encode(name);
    const data = encoder.encode(content);
    const local = new Uint8Array(30 + nameBytes.length + data.length);
    const view = new DataView(local.buffer);
    view.setUint32(0, 0x04034b50, true); view.setUint16(4, 20, true); view.setUint32(14, crc32(data), true);
    view.setUint32(22, data.length, true); view.setUint32(26, data.length, true); view.setUint16(28, nameBytes.length, true);
    local.set(nameBytes, 30); local.set(data, 30 + nameBytes.length); files.push(local);
    const record = new Uint8Array(46 + nameBytes.length); const recordView = new DataView(record.buffer);
    recordView.setUint32(0, 0x02014b50, true); recordView.setUint16(4, 20, true); recordView.setUint16(6, 20, true); recordView.setUint16(20, data.length, true); recordView.setUint32(16, crc32(data), true); recordView.setUint32(24, data.length, true); recordView.setUint16(28, nameBytes.length, true); recordView.setUint32(42, offset, true); record.set(nameBytes, 46); central.push(record); offset += local.length;
  });
  const centralSize = central.reduce((total, item) => total + item.length, 0);
  const end = new Uint8Array(22); const endView = new DataView(end.buffer);
  endView.setUint32(0, 0x06054b50, true); endView.setUint16(8, entries.length, true); endView.setUint16(10, entries.length, true); endView.setUint32(12, centralSize, true); endView.setUint32(16, offset, true);
  return new Blob([...files, ...central, end], {type: 'application/zip'});
}
