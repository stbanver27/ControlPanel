// static/js/main.js

// ── Modal helpers ──────────────────────────────────────────────
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

// Close modal on backdrop click
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-backdrop')) {
    e.target.classList.remove('open');
  }
});

// Close modal on Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-backdrop.open').forEach(m => m.classList.remove('open'));
  }
});

// ── Delete confirm modal ───────────────────────────────────────
function confirmDelete(formId, message) {
  const modal = document.getElementById('deleteModal');
  const msgEl = document.getElementById('deleteModalMessage');
  const confirmBtn = document.getElementById('deleteModalConfirm');

  if (!modal || !msgEl || !confirmBtn) return;

  msgEl.textContent = message || '¿Estás seguro de que deseas eliminar este registro?';
  confirmBtn.onclick = () => {
    const form = document.getElementById(formId);
    if (form) form.submit();
  };
  modal.classList.add('open');
}

// ── Plan autocompletion in subscription form ───────────────────
function initPlanAutocomplete() {
  const planSelect = document.getElementById('plan_id');
  const pantallasInput = document.getElementById('pantallas');
  const precioInput = document.getElementById('precio');
  const duracionInput = document.getElementById('duracion_hint');
  const fechaInicioInput = document.getElementById('fecha_inicio');
  const fechaVencimientoInput = document.getElementById('fecha_vencimiento');

  if (!planSelect) return;

  async function loadPlan(planId) {
    if (!planId) return;
    try {
      const res = await fetch(`/plans/api/${planId}`);
      if (!res.ok) return;
      const data = await res.json();
      if (pantallasInput) pantallasInput.value = data.pantallas;
      if (precioInput) precioInput.value = data.precio.toFixed(2);
      if (duracionInput) duracionInput.textContent = `${data.duracion_dias} días`;

      // Auto-calculate fecha_vencimiento from fecha_inicio + duracion
      if (fechaInicioInput && fechaVencimientoInput && data.duracion_dias) {
        const inicio = fechaInicioInput.value;
        if (inicio) {
          const d = new Date(inicio + 'T00:00:00');
          d.setDate(d.getDate() + data.duracion_dias);
          fechaVencimientoInput.value = d.toISOString().split('T')[0];
        }
      }
    } catch (err) {
      console.error('Error loading plan:', err);
    }
  }

  planSelect.addEventListener('change', () => loadPlan(planSelect.value));

  // Also update vencimiento when inicio changes
  if (fechaInicioInput) {
    fechaInicioInput.addEventListener('change', () => {
      if (planSelect.value) loadPlan(planSelect.value);
    });
  }

  // Load on page open if plan already selected
  if (planSelect.value) loadPlan(planSelect.value);
}

// ── Filter subscriptions by customer in payments form ─────────
function initSubscriptionFilter() {
  const customerSelect = document.getElementById('customer_id');
  const subSelect = document.getElementById('subscription_id');
  if (!customerSelect || !subSelect) return;

  const allOptions = Array.from(subSelect.querySelectorAll('option[data-customer]'));

  function filterSubs(customerId) {
    allOptions.forEach(opt => {
      if (!customerId || opt.dataset.customer === String(customerId)) {
        opt.style.display = '';
      } else {
        opt.style.display = 'none';
        if (opt.selected) {
          opt.selected = false;
          subSelect.value = '';
        }
      }
    });
  }

  customerSelect.addEventListener('change', () => filterSubs(customerSelect.value));
  filterSubs(customerSelect.value);
}

// ── Sidebar toggle (mobile) ────────────────────────────────────
function initSidebarToggle() {
  const toggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  if (!toggle || !sidebar) return;

  toggle.addEventListener('click', () => sidebar.classList.toggle('open'));

  document.addEventListener('click', (e) => {
    if (sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) &&
        e.target !== toggle) {
      sidebar.classList.remove('open');
    }
  });
}

// ── Auto-dismiss flash messages ────────────────────────────────
function initFlashDismiss() {
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });
}

// ── Init ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initPlanAutocomplete();
  initSubscriptionFilter();
  initSidebarToggle();
  initFlashDismiss();
});
