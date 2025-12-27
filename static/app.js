document.addEventListener('DOMContentLoaded', ()=>{
  // RSVP submit flow
  const form = document.getElementById('rsvp-form');
  if(form){
    form.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const data = new FormData(form);
      const res = await fetch('/enter', {method:'POST', body: data, credentials: 'same-origin'});
      const msg = document.getElementById('rsvp-message');
      const body = await res.json().catch(()=>({ok:false,error:'Error'}));
      if(res.ok && body.status === 'pending'){
        msg.textContent = 'Thanks — your RSVP is pending approval by an administrator.';
      } else if(res.ok && body.status === 'approved'){
        // redirect to declare where the session is used
        window.location.href = '/declare';
      } else {
        msg.textContent = body.error || 'Submission error.';
      }
    });
  }

  // check status form
  const checkForm = document.getElementById('check-status-form');
  if(checkForm){
    checkForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const data = new FormData(checkForm);
      const res = await fetch('/enter-status', {method:'POST', body: data, credentials: 'same-origin'});
      const msg = document.getElementById('status-message');
      const body = await res.json().catch(()=>({ok:false,error:'Error'}));
      if(res.ok && body.status === 'approved'){
        // session should be set by server; redirect to declare page where user can add items
        window.location.href = '/declare';
      } else if(res.status===404){
        msg.textContent = 'We could not find your RSVP.';
      } else {
        msg.textContent = 'Status: ' + (body.status || 'pending');
      }
    })
  }

  // bring form submit
  const bringForm = document.getElementById('bring-form');
  if(bringForm){
    bringForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const data = new FormData(bringForm);
      const res = await fetch('/bring', {method:'POST', body: data, credentials: 'same-origin'});
      const body = await res.json().catch(()=>({ok:false,error:'Error'}));
      const msg = document.getElementById('bring-message');
      if(res.ok && body.ok){
        msg.textContent = 'Item saved. Thank you!';
        bringForm.reset();
      } else {
        msg.textContent = body.error || 'Error saving item.';
      }
    })
  }

  // side panel / nav toggle (left panel)
  const navToggle = document.getElementById('nav-toggle');
  const sidePanel = document.getElementById('side-panel');
  const sideClose = document.getElementById('side-close');
  const overlayEl = document.getElementById('panel-overlay');
  function openPanel(){
    sidePanel.classList.add('open');
    sidePanel.setAttribute('aria-hidden','false');
    if(overlayEl) overlayEl.classList.add('show');
  }
  function closePanel(){
    sidePanel.classList.remove('open');
    sidePanel.setAttribute('aria-hidden','true');
    if(overlayEl) overlayEl.classList.remove('show');
  }
  if(navToggle && sidePanel){
    navToggle.addEventListener('click', ()=>{
      if(sidePanel.classList.contains('open')) closePanel(); else openPanel();
    })
  }
  if(sideClose && sidePanel){
    sideClose.addEventListener('click', closePanel);
  }
  if(overlayEl){
    overlayEl.addEventListener('click', closePanel);
  }

  // menu toggle (mobile)
  const menuToggle = document.getElementById('menu-toggle');
  const nav = document.querySelector('.nav');
  if(menuToggle && nav){
    menuToggle.addEventListener('click', ()=> nav.classList.toggle('show'))
  }

  // service worker registration for PWA
  if('serviceWorker' in navigator){
    navigator.serviceWorker.register('/static/service-worker.js').catch(()=>{});
  }
});
