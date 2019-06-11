/**
* Script para parchear JS de la pagina
* 
* Snipets:
*   grecaptcha.reset()
*   $('[name="g-recaptcha-response"]').val()
*/

_patch_js_web_page = () => {
  if ( !confirm('Ya tienes el Google Captcha visible?') ){
    alert('Pues activalo!!!')
    return
  }

  window.originalHandle = () => {}
  window.handleAjaxComplete = () => {}
  window.salirSinAjax = () => {}
  window.cerrarModalExpira = () => {}
  window.mostrarModalExpira = () => {}
  clearTimeout(ajaxTimer)
  clearTimeout(sessionTimer)
  clearTimeout(sessionCloseTimer)
  sessionTimeoutSecs = 1000000
  
  $(document.getElementById('formRegistroCitaExtranjero:buscarCita')).prop('disabled', 'disabled')
  $(document.getElementById('formRegistroCitaExtranjero:limpiarCita')).prop('disabled', 'disabled')
}

_patch_js_web_page()
