"""
phase5_to_9_setup.py — Completes Phases 5–9 in one run.

Phase 5: Frontend shell (index.html, navbar, sidebar, footer, api-config)
Phase 6: Frontend components + services (JS modules)
Phase 7: Frontend pages wired to API (dashboard, menu, new-order, billing, receipts)
Phase 8: Additional backend endpoints (customers, tables, rooms, inventory, reports)
Phase 9: Docs, run scripts, README, Dockerfile

Run from: C:\\Users\\user\\OneDrive\\Desktop\\scaffold.sh\\backend
    python phase5_to_9_setup.py
"""

from pathlib import Path
import json


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote  {path}")


def touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch()
        print(f"  touch  {path}")


# ===========================================================================
# PHASE 5 — FRONTEND SHELL
# ===========================================================================

FRONTEND_INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Hotel Billing System</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="/css/output.css" />
</head>
<body class="bg-gray-50 min-h-screen flex flex-col">
  <div id="navbar-mount"></div>
  <div class="flex flex-1">
    <div id="sidebar-mount" class="hidden lg:block"></div>
    <main id="app" class="flex-1 p-6"></main>
  </div>
  <div id="footer-mount"></div>
  <div id="toast-root" class="fixed top-4 right-4 z-50 space-y-2"></div>

  <script type="module" src="/js/main.js"></script>
</body>
</html>
"""


FRONTEND_MAIN_JS = r"""// frontend/js/main.js — app bootstrap
import { mountNavbar } from "./components/navbar.js";
import { mountSidebar } from "./components/sidebar.js";
import { mountFooter } from "./components/footer.js";
import { loadPage } from "./router.js";

(async function bootstrap() {
  await mountNavbar();
  await mountSidebar();
  await mountFooter();
  await loadPage();
  window.addEventListener("hashchange", loadPage);
})();
"""


FRONTEND_ROUTER_JS = r"""// frontend/js/router.js — hash-based page router
const routes = {
  "/":              "/pages/dashboard/dashboard.html",
  "/dashboard":     "/pages/dashboard/dashboard.html",
  "/menu":          "/pages/menu/food-menu.html",
  "/menu/drinks":   "/pages/menu/drinks-menu.html",
  "/orders/new":    "/pages/orders/new-order.html",
  "/orders":        "/pages/orders/live-orders.html",
  "/billing":       "/pages/billing/billing.html",
  "/receipts":      "/pages/billing/receipts.html",
  "/invoices":      "/pages/billing/invoices.html",
  "/payments":      "/pages/billing/payments.html",
  "/customers":     "/pages/customers/customer-list.html",
  "/tables":        "/pages/tables/table-management.html",
  "/rooms":         "/pages/rooms/room-management.html",
  "/inventory":     "/pages/inventory/stock-dashboard.html",
};

export async function loadPage() {
  const path = location.hash.replace(/^#/, "") || "/";
  const htmlPath = routes[path];

  const app = document.getElementById("app");
  if (!htmlPath) {
    app.innerHTML = `<div class="p-8 text-center">
      <h1 class="text-2xl font-bold text-red-600">404 — Page not found</h1>
      <p class="text-gray-500 mt-2">Path: ${path}</p>
      <a href="#/" class="text-blue-600 hover:underline mt-4 inline-block">Go home</a>
    </div>`;
    return;
  }

  try {
    const res = await fetch(htmlPath);
    const html = await res.text();
    app.innerHTML = html;

    // Extract module path from <script data-page> if present
    const scriptTag = app.querySelector("script[data-page-module]");
    if (scriptTag) {
      const modPath = scriptTag.getAttribute("data-page-module");
      const mod = await import(`../${modPath}`);
      if (mod.init) mod.init();
    }
  } catch (e) {
    app.innerHTML = `<div class="p-8 text-red-600">Error loading page: ${e.message}</div>`;
  }
}
"""


FRONTEND_NAVBAR_HTML = r"""<nav class="bg-white shadow-sm px-6 py-3 flex items-center justify-between">
  <a href="#/" class="font-bold text-xl text-blue-600">HotelPOS</a>
  <div class="flex gap-4 text-gray-700 text-sm">
    <a href="#/dashboard" class="hover:text-blue-600">Dashboard</a>
    <a href="#/menu" class="hover:text-blue-600">Menu</a>
    <a href="#/orders/new" class="hover:text-blue-600">New Order</a>
    <a href="#/billing" class="hover:text-blue-600">Billing</a>
    <span id="user-badge" class="px-2 py-1 bg-gray-100 rounded">Guest</span>
  </div>
</nav>
"""


FRONTEND_SIDEBAR_HTML = r"""<aside class="w-56 bg-white border-r border-gray-200 min-h-screen">
  <nav class="p-4 space-y-1 text-sm">
    <a href="#/dashboard" class="block px-3 py-2 rounded hover:bg-gray-100">📊 Dashboard</a>
    <a href="#/menu" class="block px-3 py-2 rounded hover:bg-gray-100">🍽 Menu</a>
    <a href="#/orders/new" class="block px-3 py-2 rounded hover:bg-gray-100">➕ New Order</a>
    <a href="#/orders" class="block px-3 py-2 rounded hover:bg-gray-100">📋 Live Orders</a>
    <a href="#/billing" class="block px-3 py-2 rounded hover:bg-gray-100">💵 Billing</a>
    <a href="#/receipts" class="block px-3 py-2 rounded hover:bg-gray-100">🧾 Receipts</a>
    <a href="#/customers" class="block px-3 py-2 rounded hover:bg-gray-100">👥 Customers</a>
    <a href="#/tables" class="block px-3 py-2 rounded hover:bg-gray-100">🍴 Tables</a>
    <a href="#/rooms" class="block px-3 py-2 rounded hover:bg-gray-100">🛏 Rooms</a>
    <a href="#/inventory" class="block px-3 py-2 rounded hover:bg-gray-100">📦 Inventory</a>
  </nav>
</aside>
"""


FRONTEND_FOOTER_HTML = r"""<footer class="bg-white border-t border-gray-200 px-6 py-3 text-center text-xs text-gray-500">
  Hotel Billing System &middot; v1.0
</footer>
"""


FRONTEND_NAVBAR_JS = r"""// frontend/js/components/navbar.js
export async function mountNavbar() {
  const res = await fetch("/components/navbar.html");
  document.getElementById("navbar-mount").innerHTML = await res.text();
}
"""


FRONTEND_SIDEBAR_JS = r"""// frontend/js/components/sidebar.js
export async function mountSidebar() {
  const res = await fetch("/components/sidebar.html");
  document.getElementById("sidebar-mount").innerHTML = await res.text();
}
"""


FRONTEND_FOOTER_JS = r"""// frontend/js/components/footer.js
export async function mountFooter() {
  const res = await fetch("/components/footer.html");
  document.getElementById("footer-mount").innerHTML = await res.text();
}
"""


FRONTEND_API_CONFIG_JS = r"""// frontend/js/config/api-config.js
export const API_BASE = "http://localhost:5000/api/v1";

export async function api(path, opts = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}
"""


FRONTEND_TOAST_JS = r"""// frontend/js/utils/notifications.js
export function showToast(message, type = "info") {
  const colors = { info: "bg-blue-600", success: "bg-green-600", error: "bg-red-600" };
  const root = document.getElementById("toast-root");
  const el = document.createElement("div");
  el.className = `${colors[type]} text-white px-4 py-2 rounded shadow-lg`;
  el.textContent = message;
  root.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}
"""


FRONTEND_FORMAT_JS = r"""// frontend/js/utils/formatter.js
export const money = (v) => `KES ${Number(v).toFixed(2)}`;
export const date = (v) => new Date(v).toLocaleString();
"""


# ===========================================================================
# PHASE 6/7 — PAGES
# ===========================================================================

PAGE_DASHBOARD_HTML = r"""<div>
  <h1 class="text-2xl font-bold mb-4">Dashboard</h1>
  <div id="stats" class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6"></div>
  <div id="recent" class="bg-white rounded shadow p-4">
    <h2 class="font-semibold mb-2">Recent Orders</h2>
    <p class="text-gray-500 text-sm">Loading…</p>
  </div>
  <script type="module" data-page-module="js/pages/dashboard.js"></script>
</div>
"""


PAGE_DASHBOARD_JS = r"""// frontend/js/pages/dashboard.js
import { api } from "../config/api-config.js";
import { showToast } from "../utils/notifications.js";

export async function init() {
  try {
    const [menu, orders] = await Promise.all([
      api("/menu"),
      api("/orders"),
    ]);
    document.getElementById("stats").innerHTML = `
      <div class="bg-white rounded shadow p-4">
        <div class="text-gray-500 text-sm">Menu Items</div>
        <div class="text-2xl font-bold">${menu.length}</div>
      </div>
      <div class="bg-white rounded shadow p-4">
        <div class="text-gray-500 text-sm">Orders</div>
        <div class="text-2xl font-bold">${orders.length}</div>
      </div>
      <div class="bg-white rounded shadow p-4">
        <div class="text-gray-500 text-sm">Status</div>
        <div class="text-2xl font-bold text-green-600">Online</div>
      </div>
    `;
    const recent = document.getElementById("recent");
    if (orders.length === 0) {
      recent.innerHTML = '<p class="text-gray-500 text-sm">No orders yet.</p>';
    } else {
      recent.innerHTML = '<h2 class="font-semibold mb-2">Recent Orders</h2>' +
        orders.slice(-5).reverse().map(o => `
          <div class="flex justify-between border-b py-2 text-sm">
            <span>#${o.id} — ${o.items.length} items</span>
            <span class="font-semibold">KES ${o.total}</span>
          </div>`).join("");
    }
  } catch (e) {
    showToast(`Failed to load dashboard: ${e.message}`, "error");
  }
}
"""


PAGE_MENU_HTML = r"""<div>
  <h1 class="text-2xl font-bold mb-4">Menu</h1>
  <div id="menu-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"></div>
  <script type="module" data-page-module="js/pages/menu.js"></script>
</div>
"""


PAGE_MENU_JS = r"""// frontend/js/pages/menu.js
import { api } from "../config/api-config.js";
import { showToast } from "../utils/notifications.js";
import { money } from "../utils/formatter.js";

export async function init() {
  try {
    const items = await api("/menu?available=true");
    const grid = document.getElementById("menu-grid");
    grid.innerHTML = items.map(i => `
      <div class="bg-white rounded shadow p-4 flex flex-col justify-between">
        <div>
          <h3 class="font-semibold">${i.name}</h3>
          <p class="text-gray-500 text-sm">${i.category}</p>
          <p class="text-blue-600 font-bold mt-2">${money(i.price)}</p>
        </div>
        <button data-id="${i.id}" data-name="${i.name}" data-price="${i.price}"
                class="add-btn mt-3 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm">
          Add to order
        </button>
      </div>`).join("");

    grid.querySelectorAll(".add-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const item = {
          id: Number(btn.dataset.id),
          name: btn.dataset.name,
          price: Number(btn.dataset.price),
        };
        addToCart(item);
        showToast(`Added ${item.name}`, "success");
      });
    });
  } catch (e) {
    showToast(`Failed to load menu: ${e.message}`, "error");
  }
}

function addToCart(item) {
  const cart = JSON.parse(localStorage.getItem("cart") || "[]");
  const existing = cart.find(c => c.menu_item_id === item.id);
  if (existing) existing.quantity += 1;
  else cart.push({ menu_item_id: item.id, name: item.name,
                   price: item.price, quantity: 1 });
  localStorage.setItem("cart", JSON.stringify(cart));
}
"""


PAGE_NEW_ORDER_HTML = r"""<div>
  <h1 class="text-2xl font-bold mb-4">New Order</h1>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
    <div class="lg:col-span-2 bg-white rounded shadow p-4">
      <h2 class="font-semibold mb-2">Cart</h2>
      <div id="cart-list" class="space-y-2"></div>
      <div class="mt-4 text-right font-bold text-lg">Total: <span id="cart-total">KES 0.00</span></div>
    </div>
    <div class="bg-white rounded shadow p-4">
      <h2 class="font-semibold mb-2">Actions</h2>
      <button id="submit-order" class="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded">
        Place order
      </button>
      <button id="clear-cart" class="w-full mt-2 border border-red-300 text-red-600 hover:bg-red-50 px-4 py-2 rounded">
        Clear cart
      </button>
    </div>
  </div>
  <script type="module" data-page-module="js/pages/orders.js"></script>
</div>
"""


PAGE_NEW_ORDER_JS = r"""// frontend/js/pages/orders.js
import { api } from "../config/api-config.js";
import { showToast } from "../utils/notifications.js";
import { money } from "../utils/formatter.js";

export function init() {
  renderCart();

  document.getElementById("clear-cart").addEventListener("click", () => {
    localStorage.removeItem("cart");
    renderCart();
  });

  document.getElementById("submit-order").addEventListener("click", async () => {
    const cart = JSON.parse(localStorage.getItem("cart") || "[]");
    if (cart.length === 0) {
      showToast("Cart is empty", "error");
      return;
    }
    try {
      const order = await api("/orders", {
        method: "POST",
        body: JSON.stringify({
          items: cart.map(c => ({ menu_item_id: c.menu_item_id, quantity: c.quantity })),
        }),
      });
      localStorage.removeItem("cart");
      showToast(`Order #${order.id} created`, "success");
      location.hash = `#/billing?order=${order.id}`;
    } catch (e) {
      showToast(`Error: ${e.message}`, "error");
    }
  });
}

function renderCart() {
  const cart = JSON.parse(localStorage.getItem("cart") || "[]");
  const list = document.getElementById("cart-list");
  if (cart.length === 0) {
    list.innerHTML = '<p class="text-gray-500 text-sm">Cart is empty. Add items from Menu.</p>';
    document.getElementById("cart-total").textContent = "KES 0.00";
    return;
  }
  list.innerHTML = cart.map(c => `
    <div class="flex justify-between border-b py-2 text-sm">
      <span>${c.name} × ${c.quantity}</span>
      <span class="font-semibold">${money(c.price * c.quantity)}</span>
    </div>`).join("");
  const total = cart.reduce((s, c) => s + c.price * c.quantity, 0);
  document.getElementById("cart-total").textContent = money(total);
}
"""


PAGE_BILLING_HTML = r"""<div>
  <h1 class="text-2xl font-bold mb-4">Billing & Payment</h1>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <div class="bg-white rounded shadow p-4">
      <h2 class="font-semibold mb-2">Order Summary</h2>
      <div id="order-summary" class="text-sm text-gray-600">Loading…</div>
    </div>
    <div class="bg-white rounded shadow p-4">
      <h2 class="font-semibold mb-2">Payment</h2>
      <div class="mb-3">
        <label class="block text-sm text-gray-600 mb-1">Amount</label>
        <input id="pay-amount" type="number" step="0.01" min="0"
               class="w-full border border-gray-300 rounded px-3 py-2" placeholder="0.00" />
      </div>
      <div class="mb-3">
        <label class="block text-sm text-gray-600 mb-1">Method</label>
        <select id="pay-method" class="w-full border border-gray-300 rounded px-3 py-2">
          <option value="cash">Cash</option>
          <option value="card">Card</option>
          <option value="mpesa">M-Pesa</option>
          <option value="bank">Bank</option>
        </select>
      </div>
      <button id="pay-btn" class="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
        Submit payment
      </button>
      <div id="balance-info" class="mt-3 text-sm"></div>
    </div>
  </div>
  <script type="module" data-page-module="js/pages/billing.js"></script>
</div>
"""


PAGE_BILLING_JS = r"""// frontend/js/pages/billing.js
import { api } from "../config/api-config.js";
import { showToast } from "../utils/notifications.js";
import { money } from "../utils/formatter.js";

let orderId = null;

export async function init() {
  // Determine order id from URL query or latest order
  const params = new URLSearchParams(location.hash.split("?")[1] || "");
  orderId = Number(params.get("order"));

  if (!orderId) {
    try {
      const orders = await api("/orders");
      if (orders.length === 0) {
        document.getElementById("order-summary").innerHTML =
          '<p class="text-gray-500">No orders yet. <a href="#/menu" class="text-blue-600">Create one</a>.</p>';
        return;
      }
      orderId = orders[orders.length - 1].id;
    } catch (e) {
      showToast(`Error: ${e.message}`, "error");
      return;
    }
  }

  await refresh();
  document.getElementById("pay-btn").addEventListener("click", submitPayment);
}

async function refresh() {
  try {
    const receipt = await api(`/billing/receipt/${orderId}`);
    document.getElementById("order-summary").innerHTML = `
      <p class="mb-2 text-base font-semibold">Order #${receipt.order_id}</p>
      ${receipt.items.map(i => `
        <div class="flex justify-between border-b py-1">
          <span>${i.name} × ${i.qty}</span>
          <span>${money(i.subtotal)}</span>
        </div>`).join("")}
      <div class="flex justify-between mt-2 font-bold">
        <span>Total</span><span>${money(receipt.total)}</span>
      </div>
      <div class="flex justify-between text-sm">
        <span>Paid</span><span>${money(receipt.total_paid)}</span>
      </div>
      <div class="flex justify-between text-sm ${receipt.is_fully_paid ? 'text-green-600' : 'text-red-600'}">
        <span>${receipt.is_fully_paid ? 'Change' : 'Balance'}</span>
        <span>${receipt.is_fully_paid ? money(receipt.change) : money(receipt.balance)}</span>
      </div>`;

    document.getElementById("balance-info").innerHTML = receipt.is_fully_paid
      ? `<div class="text-green-600 font-semibold">✓ Fully paid. Change: ${money(receipt.change)}</div>
         <a href="#/receipts?order=${receipt.order_id}" class="text-blue-600 text-sm">View receipt →</a>`
      : `<div class="text-orange-600">Balance remaining: ${money(receipt.balance)}</div>`;
  } catch (e) {
    document.getElementById("order-summary").innerHTML = `<p class="text-red-600">${e.message}</p>`;
  }
}

async function submitPayment() {
  const amount = document.getElementById("pay-amount").value;
  const method = document.getElementById("pay-method").value;
  if (!amount || Number(amount) <= 0) {
    showToast("Enter a valid amount", "error");
    return;
  }
  try {
    const res = await api("/payments", {
      method: "POST",
      body: JSON.stringify({ order_id: orderId, amount, method }),
    });
    showToast(`Payment received. ${res.is_fully_paid ? 'Fully paid!' : 'Balance: ' + money(res.balance)}`, "success");
    document.getElementById("pay-amount").value = "";
    await refresh();
  } catch (e) {
    showToast(`Error: ${e.message}`, "error");
  }
}
"""


PAGE_RECEIPTS_HTML = r"""<div>
  <h1 class="text-2xl font-bold mb-4">Receipts</h1>
  <div class="bg-white rounded shadow p-6 max-w-2xl mx-auto" id="receipt-box">
    <p class="text-gray-500">Loading…</p>
  </div>
  <div class="text-center mt-4">
    <button onclick="window.print()" class="bg-gray-800 text-white px-4 py-2 rounded">
      🖨 Print
    </button>
  </div>
  <script type="module" data-page-module="js/pages/receipts.js"></script>
</div>
"""


PAGE_RECEIPTS_JS = r"""// frontend/js/pages/receipts.js
import { api } from "../config/api-config.js";
import { money, date } from "../utils/formatter.js";

export async function init() {
  const params = new URLSearchParams(location.hash.split("?")[1] || "");
  let orderId = Number(params.get("order"));

  if (!orderId) {
    const orders = await api("/orders");
    if (orders.length === 0) {
      document.getElementById("receipt-box").innerHTML =
        '<p class="text-gray-500">No orders yet.</p>';
      return;
    }
    orderId = orders[orders.length - 1].id;
  }

  try {
    const r = await api(`/billing/receipt/${orderId}`);
    document.getElementById("receipt-box").innerHTML = `
      <div class="text-center mb-4">
        <h2 class="text-xl font-bold">HOTEL BILLING</h2>
        <p class="text-sm text-gray-500">Receipt #${r.order_id} — ${date(new Date())}</p>
      </div>
      <table class="w-full text-sm">
        <thead class="border-b">
          <tr><th class="text-left py-1">Item</th><th class="text-center">Qty</th><th class="text-right">Subtotal</th></tr>
        </thead>
        <tbody>
          ${r.items.map(i => `
            <tr class="border-b">
              <td class="py-1">${i.name}</td>
              <td class="text-center">${i.qty}</td>
              <td class="text-right">${money(i.subtotal)}</td>
            </tr>`).join("")}
        </tbody>
      </table>
      <div class="mt-4 text-sm">
        <div class="flex justify-between font-bold text-base border-t pt-2">
          <span>TOTAL</span><span>${money(r.total)}</span>
        </div>
        <div class="flex justify-between mt-1"><span>Paid</span><span>${money(r.total_paid)}</span></div>
        ${r.is_fully_paid
          ? `<div class="flex justify-between text-green-600 font-semibold"><span>CHANGE</span><span>${money(r.change)}</span></div>`
          : `<div class="flex justify-between text-red-600 font-semibold"><span>BALANCE</span><span>${money(r.balance)}</span></div>`}
      </div>
      <div class="mt-4 text-xs text-gray-500 text-center">
        Payments: ${r.payments.length} record(s)
      </div>
      <div class="mt-6 text-center text-xs text-gray-400">Thank you for dining with us!</div>`;
  } catch (e) {
    document.getElementById("receipt-box").innerHTML = `<p class="text-red-600">${e.message}</p>`;
  }
}
"""


# ===========================================================================
# PHASE 8 — EXTRA ENDPOINTS (stubs but functional)
# ===========================================================================

CUSTOMERS_ENDPOINT = r'''"""Customer endpoints."""
from flask import Blueprint, jsonify, request
from app.repositories.customer_repository import CustomerRepository
from app.models.customer import Customer

customers_bp = Blueprint("customers", __name__)

@customers_bp.get("")
@customers_bp.get("/")
def list_customers():
    return jsonify([c.to_dict() for c in CustomerRepository().list_all()])

@customers_bp.post("")
@customers_bp.post("/")
def create_customer():
    body = request.get_json(silent=True) or {}
    c = CustomerRepository().create(Customer(
        full_name=body.get("full_name", ""),
        phone=body.get("phone", ""),
        email=body.get("email", ""),
    ))
    return jsonify(c.to_dict()), 201
'''

TABLES_ENDPOINT = r'''"""Table endpoints."""
from flask import Blueprint, jsonify
from app.repositories.table_repository import TableRepository

tables_bp = Blueprint("tables", __name__)

@tables_bp.get("")
@tables_bp.get("/")
def list_tables():
    return jsonify([t.to_dict() for t in TableRepository().list_all()])
'''

ROOMS_ENDPOINT = r'''"""Room endpoints."""
from flask import Blueprint, jsonify
from app.repositories.room_repository import RoomRepository

rooms_bp = Blueprint("rooms", __name__)

@rooms_bp.get("")
@rooms_bp.get("/")
def list_rooms():
    return jsonify([r.to_dict() for r in RoomRepository().list_all()])
'''

INVENTORY_ENDPOINT = r'''"""Inventory endpoints."""
from flask import Blueprint, jsonify
from app.repositories.inventory_repository import InventoryRepository

inventory_bp = Blueprint("inventory", __name__)

@inventory_bp.get("")
@inventory_bp.get("/")
def list_inventory():
    return jsonify([i.to_dict() for i in InventoryRepository().list_all()])

@inventory_bp.get("/low-stock")
def low_stock():
    return jsonify([i.to_dict() for i in InventoryRepository().find_low_stock()])
'''

REPORTS_ENDPOINT = r'''"""Reports endpoints."""
from flask import Blueprint, jsonify
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository

reports_bp = Blueprint("reports", __name__)

@reports_bp.get("/summary")
def summary():
    orders = OrderRepository().list_all()
    payments = PaymentRepository().list_all()
    return jsonify({
        "orders_count": len(orders),
        "payments_count": len(payments),
        "revenue": str(sum(p.amount for p in payments)),
    })
'''


# ===========================================================================
# PHASE 9 — DOCS, README, RUNNERS
# ===========================================================================

BACKEND_README = r"""# Hotel Billing System — Backend

Flask REST API with clean architecture:

    app/
      core/         → enums, exceptions, config
      models/       → pure domain entities (dataclasses)
      schemas/      → (unused in phase 1–4; reserved for Phase 8+)
      database/     → JsonStore (persistence)
      repositories/ → data access (10 repos)
      services/     → business logic (5 services)
      api/v1/       → HTTP endpoints

## Setup

    python -m pip install flask flask-cors pytest
    python scripts/seed_menu.py
    python run.py

Server starts on http://localhost:5000.

## Run tests

    python -m pytest tests\ -v

## API

| Method | Path | Description |
|---|---|---|
| GET | /api/v1/health | Service status |
| GET | /api/v1/menu | List menu |
| POST | /api/v1/orders | Create order |
| POST | /api/v1/payments | Add payment |
| GET | /api/v1/billing/receipt/<id> | Get receipt |
| POST | /api/v1/auth/register | Register user |
| POST | /api/v1/auth/login | Login |
"""

FRONTEND_README = r"""# Hotel Billing System — Frontend

Static HTML + Tailwind (CDN) + ES modules.

## Run

The backend serves the frontend as static files:

    cd backend
    python run.py

Then open: http://localhost:5000/

## Structure

    index.html              → shell
    components/             → navbar, sidebar, footer HTML partials
    pages/<section>/*.html  → individual pages
    js/config/api-config.js → API base URL + fetch helper
    js/router.js            → hash-based page router
    js/pages/*.js           → page controllers
"""

ROOT_README = r"""# Hotel Billing System

Multi-item orders, multi-payment support, balance + change, receipts.

## Quick start

    cd backend
    pip install -r requirements.txt
    python scripts/seed_menu.py
    python run.py

Open http://localhost:5000

## Requirements

- Python 3.10+
- Flask, flask-cors, pytest

## End-to-end example

1. Menu page → add items → cart
2. New Order → place order
3. Billing → pay partial → see balance → pay again → see change
4. Receipts → print view

## Tests

    cd backend
    python -m pytest tests\ -v
"""

DOCKERFILE = r"""FROM python:3.12-slim

WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/
COPY frontend/ /app/frontend/
WORKDIR /app/backend
EXPOSE 5000
CMD ["python", "run.py"]
"""

RUN_SH = r"""#!/usr/bin/env bash
cd "$(dirname "$0")/backend"
python run.py
"""


# ===========================================================================
# BUILD
# ===========================================================================
def build() -> None:
    root = Path.cwd()
    if not (root / "app").exists():
        print(f"ERROR: no 'app' folder in {root}")
        print("       Run from C:\\Users\\user\\OneDrive\\Desktop\\scaffold.sh\\backend")
        return

    project_root = root.parent  # scaffold.sh/
    frontend = project_root / "frontend"

    print(f"\nPhase 5–9 setup in: {project_root}\n")

    # ---- Phase 5: frontend shell ----
    print("[Phase 5] Frontend shell...")
    write(frontend / "index.html", FRONTEND_INDEX_HTML)
    write(frontend / "js" / "main.js", FRONTEND_MAIN_JS)
    write(frontend / "js" / "router.js", FRONTEND_ROUTER_JS)
    write(frontend / "js" / "config" / "api-config.js", FRONTEND_API_CONFIG_JS)
    write(frontend / "components" / "navbar.html", FRONTEND_NAVBAR_HTML)
    write(frontend / "components" / "sidebar.html", FRONTEND_SIDEBAR_HTML)
    write(frontend / "components" / "footer.html", FRONTEND_FOOTER_HTML)

    # ---- Phase 6: components + services ----
    print("\n[Phase 6] Frontend components and utilities...")
    write(frontend / "js" / "components" / "navbar.js", FRONTEND_NAVBAR_JS)
    write(frontend / "js" / "components" / "sidebar.js", FRONTEND_SIDEBAR_JS)
    write(frontend / "js" / "components" / "footer.js", FRONTEND_FOOTER_JS)
    write(frontend / "js" / "utils" / "notifications.js", FRONTEND_TOAST_JS)
    write(frontend / "js" / "utils" / "formatter.js", FRONTEND_FORMAT_JS)

    # ---- Phase 7: pages ----
    print("\n[Phase 7] Frontend pages...")
    write(frontend / "pages" / "dashboard" / "dashboard.html", PAGE_DASHBOARD_HTML)
    write(frontend / "js" / "pages" / "dashboard.js", PAGE_DASHBOARD_JS)
    write(frontend / "pages" / "menu" / "food-menu.html", PAGE_MENU_HTML)
    write(frontend / "js" / "pages" / "menu.js", PAGE_MENU_JS)
    write(frontend / "pages" / "orders" / "new-order.html", PAGE_NEW_ORDER_HTML)
    write(frontend / "js" / "pages" / "orders.js", PAGE_NEW_ORDER_JS)
    write(frontend / "pages" / "billing" / "billing.html", PAGE_BILLING_HTML)
    write(frontend / "js" / "pages" / "billing.js", PAGE_BILLING_JS)
    write(frontend / "pages" / "billing" / "receipts.html", PAGE_RECEIPTS_HTML)
    write(frontend / "js" / "pages" / "receipts.js", PAGE_RECEIPTS_JS)

    # ---- Phase 8: extra endpoints ----
    print("\n[Phase 8] Extra endpoints (customers, tables, rooms, inventory, reports)...")
    ep = root / "app" / "api" / "v1" / "endpoints"
    write(ep / "customers.py", CUSTOMERS_ENDPOINT)
    write(ep / "tables.py", TABLES_ENDPOINT)
    write(ep / "rooms.py", ROOMS_ENDPOINT)
    write(ep / "inventory.py", INVENTORY_ENDPOINT)
    write(ep / "reports.py", REPORTS_ENDPOINT)

    # Update the router to register these
    router_py = root / "app" / "api" / "v1" / "router.py"
    extra_router = r'''"""Registers all API blueprints under /api/v1."""
from __future__ import annotations

from flask import Flask

from app.api.v1.endpoints.menu      import menu_bp
from app.api.v1.endpoints.orders    import orders_bp
from app.api.v1.endpoints.payments  import payments_bp
from app.api.v1.endpoints.billing   import billing_bp
from app.api.v1.endpoints.auth      import auth_bp
from app.api.v1.endpoints.customers import customers_bp
from app.api.v1.endpoints.tables    import tables_bp
from app.api.v1.endpoints.rooms     import rooms_bp
from app.api.v1.endpoints.inventory import inventory_bp
from app.api.v1.endpoints.reports   import reports_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp,      url_prefix="/api/v1/auth")
    app.register_blueprint(menu_bp,      url_prefix="/api/v1/menu")
    app.register_blueprint(orders_bp,    url_prefix="/api/v1/orders")
    app.register_blueprint(payments_bp,  url_prefix="/api/v1/payments")
    app.register_blueprint(billing_bp,   url_prefix="/api/v1/billing")
    app.register_blueprint(customers_bp, url_prefix="/api/v1/customers")
    app.register_blueprint(tables_bp,    url_prefix="/api/v1/tables")
    app.register_blueprint(rooms_bp,     url_prefix="/api/v1/rooms")
    app.register_blueprint(inventory_bp, url_prefix="/api/v1/inventory")
    app.register_blueprint(reports_bp,   url_prefix="/api/v1/reports")
'''
    write(router_py, extra_router)

    # ---- Phase 9: docs ----
    print("\n[Phase 9] Docs and deployment files...")
    write(root / "README.md", BACKEND_README)
    write(frontend / "README.md", FRONTEND_README)
    write(project_root / "README.md", ROOT_README)
    write(project_root / "Dockerfile", DOCKERFILE)
    write(project_root / "run.sh", RUN_SH)

    # Serve frontend as static folder
    main_py = root / "app" / "main.py"
    if main_py.exists():
        main_content = main_py.read_text()
        if "static_folder" not in main_content:
            patched = main_content.replace(
                'app = Flask(__name__)',
                f'app = Flask(__name__, static_folder=r"{frontend}", static_url_path="")'
            )
            main_py.write_text(patched, encoding="utf-8")
            print(f"  patched {main_py} to serve frontend/")

    print("\n" + "=" * 60)
    print("Phase 5–9 setup COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("  1) python -m pytest tests\\ -v             (should still be 46)")
    print("  2) python run.py")
    print("  3) Open http://localhost:5000              (frontend!)")
    print("  4) Navigate: #/menu → add items → #/orders/new →")
    print("     place order → #/billing → pay 2x → #/receipts")
    print("\nIf frontend CSS doesn't load, use the Tailwind CDN in")
    print("frontend/index.html (already enabled).")
    print()


if __name__ == "__main__":
    build()