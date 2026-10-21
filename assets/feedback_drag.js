(() => {
  // Preserve only the launcher's position within this browser tab.
  const selector = '.st-key-global_feedback_launcher';
  const storageKey = 'medicare-feedback-position';
  window.__medicareFeedbackDragCleanup?.();
  let position = null;
  try { position = JSON.parse(sessionStorage.getItem(storageKey)); } catch (_) {}
  if (!Number.isFinite(position?.x) || !Number.isFinite(position?.y)) position = null;
  let current = null;
  let bindings = null;

  function place(root, x, y) {
    const rect = root.getBoundingClientRect();
    const margin = 12;
    position = {
      x: Math.max(margin, Math.min(x, window.innerWidth - rect.width - margin)),
      y: Math.max(margin, Math.min(y, window.innerHeight - rect.height - margin)),
    };
    Object.assign(root.style, {
      left: `${position.x}px`, top: `${position.y}px`, right: 'auto', bottom: 'auto',
    });
  }

  function bind() {
    const root = document.querySelector(selector);
    const button = root?.querySelector('button');
    if (!button || button === current) return;
    bindings?.abort();
    current = button;
    bindings = new AbortController();
    const options = { signal: bindings.signal };
    let gesture = null;
    let suppressClickUntil = 0;
    if (position) place(root, position.x, position.y);

    button.addEventListener('pointerdown', event => {
      if (!event.isPrimary || event.button !== 0) return;
      const rect = root.getBoundingClientRect();
      gesture = { id: event.pointerId, x: event.clientX, y: event.clientY,
        left: rect.left, top: rect.top, dragging: false };
    }, options);
    button.addEventListener('pointermove', event => {
      if (!gesture || event.pointerId !== gesture.id) return;
      const dx = event.clientX - gesture.x;
      const dy = event.clientY - gesture.y;
      if (!gesture.dragging && Math.hypot(dx, dy) < 6) return;
      if (!gesture.dragging) button.setPointerCapture(event.pointerId);
      gesture.dragging = true;
      event.preventDefault();
      place(root, gesture.left + dx, gesture.top + dy);
    }, options);
    function finish(event) {
      if (!gesture || event.pointerId !== gesture.id) return;
      if (gesture.dragging) {
        suppressClickUntil = performance.now() + 500;
        event.preventDefault();
        try { sessionStorage.setItem(storageKey, JSON.stringify(position)); } catch (_) {}
      }
      if (button.hasPointerCapture(event.pointerId)) button.releasePointerCapture(event.pointerId);
      gesture = null;
    }
    button.addEventListener('pointerup', finish, options);
    button.addEventListener('pointercancel', finish, options);
    button.addEventListener('click', event => {
      // Keyboard activation must remain usable immediately after a drag.
      if (event.detail !== 0 && performance.now() < suppressClickUntil) {
        event.preventDefault();
        event.stopImmediatePropagation();
      }
    }, { ...options, capture: true });
    window.addEventListener('resize', () => {
      if (position) place(root, position.x, position.y);
    }, options);
  }
  const observer = new MutationObserver(bind);
  observer.observe(document.body, { childList: true, subtree: true });
  bind();
  window.__medicareFeedbackDragCleanup = () => {
    observer.disconnect();
    bindings?.abort();
  };
})();
