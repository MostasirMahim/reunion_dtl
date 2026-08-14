/*!
 * searchable-select.js — BSS Reunion
 * Upgrades any <select data-searchable="true"> into a type-to-search combobox.
 * No dependencies. Progressive enhancement: if JS is off, the native select works.
 */
(function () {
  "use strict";

  function fireChange(el) {
    var ev;
    try {
      ev = new Event("change", { bubbles: true });
    } catch (e) {
      ev = document.createEvent("Event");
      ev.initEvent("change", true, false);
    }
    el.dispatchEvent(ev);
  }

  function enhance(select) {
    if (select.dataset.comboReady === "1") return;
    select.dataset.comboReady = "1";

    var placeholder = select.getAttribute("data-placeholder") || "Type to search…";

    /* ---- build DOM ---- */
    var wrap = document.createElement("div");
    wrap.className = "combo";

    var input = document.createElement("input");
    input.type = "text";
    input.className = "form-input combo-input";
    input.placeholder = placeholder;
    input.autocomplete = "off";
    input.setAttribute("role", "combobox");
    input.setAttribute("aria-autocomplete", "list");
    input.setAttribute("aria-expanded", "false");
    input.setAttribute("inputmode", "numeric");
    if (select.id) input.id = select.id + "_combo";

    var caret = document.createElement("span");
    caret.className = "combo-caret";
    caret.setAttribute("aria-hidden", "true");
    caret.innerHTML = "&#9662;";

    var list = document.createElement("ul");
    list.className = "combo-list";
    list.setAttribute("role", "listbox");
    list.hidden = true;
    if (select.id) list.id = select.id + "_list";
    input.setAttribute("aria-controls", list.id || "");

    select.parentNode.insertBefore(wrap, select);
    wrap.appendChild(select);
    wrap.appendChild(input);
    wrap.appendChild(caret);
    wrap.appendChild(list);

    select.classList.add("combo-native");
    select.setAttribute("tabindex", "-1");
    select.setAttribute("aria-hidden", "true");
    // Native validation would target a visually hidden control; the server validates instead.
    select.removeAttribute("required");

    // Point the field's <label> at the visible input.
    if (select.id) {
      var lbl = document.querySelector('label[for="' + select.id + '"]');
      if (lbl && input.id) lbl.setAttribute("for", input.id);
    }

    /* ---- data ---- */
    var options = [];
    Array.prototype.forEach.call(select.options, function (o) {
      if (o.value === "") return; // skip the blank placeholder option
      options.push({ value: o.value, label: o.text });
    });

    var filtered = options.slice();
    var activeIndex = -1;

    function labelFor(value) {
      for (var i = 0; i < options.length; i++) {
        if (options[i].value === String(value)) return options[i].label;
      }
      return "";
    }

    function setActive(i) {
      activeIndex = i;
      var nodes = list.querySelectorAll(".combo-option");
      for (var n = 0; n < nodes.length; n++) {
        nodes[n].classList.toggle("is-active", n === i);
      }
      if (i > -1 && nodes[i]) {
        var node = nodes[i];
        if (node.offsetTop < list.scrollTop) {
          list.scrollTop = node.offsetTop;
        } else if (node.offsetTop + node.offsetHeight > list.scrollTop + list.clientHeight) {
          list.scrollTop = node.offsetTop + node.offsetHeight - list.clientHeight;
        }
      }
    }

    function render(query) {
      var q = (query || "").trim().toLowerCase();
      filtered = q
        ? options.filter(function (o) {
            return o.label.toLowerCase().indexOf(q) !== -1;
          })
        : options.slice();

      list.innerHTML = "";

      if (!filtered.length) {
        var empty = document.createElement("li");
        empty.className = "combo-empty";
        empty.textContent = "No matching year";
        list.appendChild(empty);
        activeIndex = -1;
        return;
      }

      var selectedPos = -1;
      filtered.forEach(function (o, i) {
        var li = document.createElement("li");
        li.className = "combo-option";
        li.setAttribute("role", "option");
        li.setAttribute("data-value", o.value);
        li.textContent = o.label;
        if (o.value === select.value) {
          li.classList.add("is-selected");
          li.setAttribute("aria-selected", "true");
          selectedPos = i;
        }
        li.addEventListener("mousedown", function (e) {
          e.preventDefault(); // keep focus so blur doesn't cancel the pick
          choose(o.value);
        });
        li.addEventListener("mouseenter", function () {
          setActive(i);
        });
        list.appendChild(li);
      });

      setActive(selectedPos > -1 ? selectedPos : 0);
    }

    function open(query) {
      render(typeof query === "string" ? query : "");
      if (list.hidden) {
        list.hidden = false;
        wrap.classList.add("is-open");
        input.setAttribute("aria-expanded", "true");
      }
      // keep the current pick in view
      var nodes = list.querySelectorAll(".combo-option.is-selected");
      if (nodes.length) list.scrollTop = Math.max(0, nodes[0].offsetTop - 60);
    }

    function close() {
      if (list.hidden) return;
      list.hidden = true;
      wrap.classList.remove("is-open");
      input.setAttribute("aria-expanded", "false");
      activeIndex = -1;
    }

    function choose(value) {
      select.value = value;
      input.value = labelFor(value);
      close();
      fireChange(select);
    }

    function commit() {
      var typed = input.value.trim().toLowerCase();

      if (!typed) {
        if (select.value !== "") {
          select.value = "";
          fireChange(select);
        }
        input.value = "";
        return;
      }
      // exact match first, then the first partial match
      var exact = null,
        partial = null;
      for (var i = 0; i < options.length; i++) {
        var lab = options[i].label.toLowerCase();
        if (lab === typed) { exact = options[i]; break; }
        if (!partial && lab.indexOf(typed) !== -1) partial = options[i];
      }
      var pick = exact || partial;
      if (pick) {
        if (select.value !== pick.value) {
          select.value = pick.value;
          fireChange(select);
        }
        input.value = pick.label;
      } else {
        // nothing matched — fall back to whatever was already selected
        input.value = labelFor(select.value);
      }
    }

    /* ---- events ---- */
    input.addEventListener("focus", function () {
      input.select();
      open("");
    });

    input.addEventListener("click", function () {
      open(list.hidden ? "" : input.value);
    });

    input.addEventListener("input", function () {
      open(input.value);
    });

    input.addEventListener("keydown", function (e) {
      var key = e.key;

      if (key === "ArrowDown" || key === "ArrowUp") {
        e.preventDefault();
        if (list.hidden) { open(input.value); return; }
        if (!filtered.length) return;
        var next = activeIndex + (key === "ArrowDown" ? 1 : -1);
        if (next < 0) next = filtered.length - 1;
        if (next >= filtered.length) next = 0;
        setActive(next);
        return;
      }

      if (key === "Enter") {
        if (!list.hidden) {
          e.preventDefault();
          if (activeIndex > -1 && filtered[activeIndex]) choose(filtered[activeIndex].value);
          else commit();
        }
        return;
      }

      if (key === "Escape" || key === "Esc") {
        if (!list.hidden) {
          e.preventDefault();
          close();
          input.value = labelFor(select.value);
        }
        return;
      }

      if (key === "Tab") {
        if (!list.hidden && activeIndex > -1 && filtered[activeIndex]) {
          choose(filtered[activeIndex].value);
        } else {
          commit();
          close();
        }
      }
    });

    input.addEventListener("blur", function () {
      window.setTimeout(function () {
        close();
        commit();
      }, 80);
    });

    caret.addEventListener("mousedown", function (e) {
      e.preventDefault();
      if (list.hidden) {
        input.focus();
      } else {
        close();
      }
    });

    document.addEventListener("mousedown", function (e) {
      if (!wrap.contains(e.target)) close();
    });

    // Keep the visible input in sync if anything sets the select programmatically.
    select.addEventListener("change", function () {
      var lab = labelFor(select.value);
      if (input.value !== lab) input.value = lab;
    });

    /* ---- initial state (e.g. after a form validation error) ---- */
    input.value = labelFor(select.value);
  }

  function init() {
    var nodes = document.querySelectorAll('select[data-searchable="true"]');
    Array.prototype.forEach.call(nodes, enhance);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.initSearchableSelects = init;
})();
