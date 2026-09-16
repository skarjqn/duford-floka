/* Static export boundary. No visual styles or theme effects are changed. */
(() => {
  'use strict';
  document.addEventListener('submit', (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const message = 'This is a static Floka demo. No information has been sent. Connect your own backend to use forms, search, accounts or checkout.';
    const feedback = form.querySelector('.wpcf7-response-output');
    if (feedback) {
      feedback.textContent = message;
      feedback.hidden = false;
      feedback.style.display = 'block';
      feedback.setAttribute('aria-hidden','false');
    } else window.alert(message);
  }, true);
  document.addEventListener('click', (event) => {
    const target = event.target.closest?.('a,button');
    if (!target) return;
    const href=target.getAttribute('href') || '';
    if (/add-to-cart=|wc-ajax=/.test(href) || target.matches('.ajax_add_to_cart,.single_add_to_cart_button,.woosw-btn,.woosc-btn')) {
      event.preventDefault();event.stopImmediatePropagation();
      window.alert('Static demo only. Shopping, comparison and wishlist storage require your own backend.');
    }
  }, true);
})();
